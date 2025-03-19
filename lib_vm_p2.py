import logging
import subprocess
import os
from lxml import etree

log = logging.getLogger('manage-p2')
directorio_trabajo = os.getcwd()

#Modificamos valores de un archivo REVISAR
def modificador_archivos(archivo,nombre, puente, is_lb_boleano = False):
    global directorio_trabajo
    tree = etree.parse(archivo) #Cargamos el archivo y lo convertimos en un arbol XML
    root = tree.getroot() #Obtenmos el nodo raiz

     # Modificar el valor de <name>
    name_elem = root.find(".//name")
    if name_elem is not None:
        name_elem.text = nombre
    
    # Modificar el valor de <source file='...'>
    source_file_elem = root.xpath(".//source[@file]")
    if source_file_elem:
        source_file_elem[0].attrib['file'] = f"{directorio_trabajo}/{nombre}.qcow2"



    # Modificar todas las interfaces existentes
    interfaces = root.xpath(".//interface[@type='bridge']")
    for interface in interfaces:
        # Modificar el valor de <source bridge='...'>
        source_bridge_elem = root.xpath(".//source[@bridge]")
        if source_bridge_elem:
            source_bridge_elem[0].attrib['bridge'] = puente

        # Añadir la etiqueta <virtualport type='openvswitch'/> si no existe ya (Para todas la interfaces)
        if interface.find(".//virtualport") is None:
            etree.SubElement(interface, "virtualport", type="openvswitch")


    # Si el nombre es 'lb' (balanceador de carga), agregar una segunda interfaz de red
    if is_lb_boleano:
         # Crear una nueva interfaz para el puente LAN2
        new_interface = etree.Element("interface", type="bridge")
        # Aquí agregamos directamente el <source> dentro de la nueva interfaz
        etree.SubElement(new_interface, "source", bridge="LAN2")
        # Agregar el modelo de la interfaz
        etree.SubElement(new_interface, "model", type="virtio")
        # Añadir la etiqueta <virtualport type='openvswitch'/>
        etree.SubElement(new_interface, "virtualport", type="openvswitch")

        # Buscar la sección de <devices> y agregar la nueva interfaz
        devices_elem = root.find(".//devices")
        if devices_elem is not None:
            devices_elem.append(new_interface)

    # Guardar el archivo modificado
    tree.write(archivo, pretty_print=True, xml_declaration=True, encoding="utf-8")

class VM:

    #Constructor del objeto VM
    def __init__(self,name,base_image,base_xml):
       self.name = name
       self.base_image = base_image
       self.base_xml = base_xml


    def create_vm(self,bridge):
        try:
            #Copiamos la imagen
            command_imagen = f"qemu-img create -F qcow2 -f qcow2 -b {self.base_image} {self.name}.qcow2"
            subprocess.call(command_imagen, shell = True)
            log.debug(f"Imagen de {self.name} copiada correctamente")

            #Copiamos la plantilla
            command_plantilla = f"cp {self.base_xml} {self.name}.xml"
            subprocess.call(command_plantilla, shell = True)
            log.debug(f"Plantilla de {self.name} copiada correctamente")

            #Modificamos plantilla con diccionario de datos a modificar
            is_lb_boleano = (self.name == "lb")
            modificador_archivos(f"{self.name}.xml", self.name, bridge, is_lb_boleano)
            log.debug(f"Se ha modificado la plantilla de {self.name} correctamente")

            #Terminamos de crear la MV
            command_define = f"sudo virsh define {self.name}.xml"
            subprocess.call(command_define, shell = True)
            log.debug(f"Máquina {self.name} se ha creado correctamente")

        except subprocess.CalledProcessError as e:
            print (f"Error en create_vm para {self.name}")


    def start_vm(self, interface):
        try:
            #Creamos archivo hostname y interfaces
            command_directorio = f"mkdir -p /mnt/tmp/temporal"
            command_hostname = f"echo \"{self.name}\" > /mnt/tmp/temporal/hostname"
            subprocess.call(command_directorio, shell = True)
            subprocess.call(command_hostname, shell = True)
            interface_modificada = f"""
            auto lo
            iface lo inet loopback

            auto eth0
            iface eth0 inet static
              address {interface[0]}
              netmask {interface[1]}
              gateway {interface[2]} 
            """
            #En el caso de que sea lb se añade la parte de eth1 en la interfaz y se realiza otra configuración
            if self.name == "lb":
                interface_modificada += f"""

                auto eth1
                iface eth1 inet static
                  address {interface[3]}
                  netmask {interface[4]}
                """  
                #Editamos fichero /etc/sysctl.conf antes de arrancar para que funcion el balanceador de trafico como un router
                command_lb = f"sudo virt-edit -a lb.qcow2 /etc/sysctl.conf -e 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/'"
                subprocess.call(command_lb, shell = True)
                log.debug("lb arrancado correctamente como router")
                   
            command_interfaces = f"echo \"{interface_modificada}\" > /mnt/tmp/temporal/interfaces"
            subprocess.call(command_interfaces, shell = True)
            log.debug(f"Interfaces {self.name} creadas en host correctamente")

            #Copiamos el archivo hostname en la maquina virtual
            command_cp_hostname = f"sudo virt-copy-in -a {self.name}.qcow2 /mnt/tmp/temporal/hostname /etc"  #copiar el fichero interfaces dentro de {self.name}.qcow2 en la carmepta /mnt/tmp/...
            subprocess.call(command_cp_hostname, shell = True)
            log.debug(f"Archivo hostname de {self.name} modificado correctamente")

            #Copiamos el archivo interfaces en la maquina virtual
            command_cp_interface = f"sudo virt-copy-in -a {self.name}.qcow2 /mnt/tmp/temporal/interfaces /etc/network"
            subprocess.call(command_cp_interface, shell = True)
            log.debug(f"Archivo interfaces de {self.name} modificado correctamente")

            #Borramos directorio temporal y su contenido
            command_delete_temporal = f"rm -r /mnt/tmp/temporal"
            subprocess.call(command_delete_temporal, shell = True)

            #Modificamos fichero /etc/hosts y ponemos el nombre de la VM
            command_change_hosts = f"sudo virt-edit -a {self.name}.qcow2 /etc/hosts -e 's/127.0.1.1.*/127.0.1.1 {self.name}/'"
            subprocess.call(command_change_hosts, shell = True)
            log.debug("Archivo /ect/hosts se ha modificado correctamente")

             #Arrancamos MV
            command_start = f"sudo virsh start {self.name}"
            subprocess.call(command_start, shell = True)
            log.debug(f"{self.name} arranca correctamente")

            command_console = f"xterm -e 'sudo virsh console {self.name}' &"
            subprocess.call(command_console , shell = True)
                 #Recomendación: Usa subprocess.Popen() en lugar de subprocess.run() si necesitas ejecutar procesos en segundo plano.
        except subprocess.CalledProcessError as e:
            print (f"Error en start_vm para {self.name}")

    def stop_vm(self):
        try:
            # Parar la máquina virtual
            command = f"sudo virsh shutdown {self.name}"
            subprocess.call(command, shell = True)
        except subprocess.CalledProcessError as e:
            print (f"Error en stop_vm para {self.name}")

    def destroy_vm(self):
        try:
            # Borrar la maquina, la imagen y la plantilla
            command = f"sudo virsh destroy {self.name}"  #podriamos probar con undefine
            subprocess.call(command, shell = True)
            log.debug(f"Máquina {self.name} borrada correctamente")

            command_imagen = f"rm {self.name}.qcow2"
            command_plantilla = f"rm {self.name}.xml"
            subprocess.call(command_imagen, shell = True)
            subprocess.call(command_plantilla, shell = True)
            log.debug(f"Archivos .qcow2 y .xml de {self.name} eliminados correctamente")

        except subprocess.CalledProcessError as e:
            print (f"Error en destroy_vm para {self.name}")

class RED:   

    #Constructor del objeto RED
    def __init__(self, bridge_name,):
       self.bridge_name =bridge_name

    #Funcion para crear la red   
    def create_net(self):
       try:
           comand_bridge = f"sudo ovs-vsctl add-br {self.bridge_name}"
           subprocess.run(comand_bridge, shell=True)
           log.debug(f"{self.bridge_name} creada correctamente")
       except subprocess.CalledProcessError as e:
           print (f"Error en create_net para {self.name}")


    #Funcion para eliminar la red
    def destroy_net(self):
       try:
          comand_destroy = f"sudo ovs-vsctl del-br {self.bridge_name}"
          subprocess.run(comand_destroy, shell = True)
          log.debug(f"{self.bridge_name} eliminada correctamente")
       except subprocess.CalledProcessError as e:
           print (f"Error en destroy_net para {self.name}")