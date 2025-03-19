import sys
import logging
import json
from lib_vm_p2 import VM,RED

#Creativa 1 hecho por el grupo 04 (Alberto Marín Cuesta y César Escobar Angeles) para la asignatura de CDPS 2024-2025
#Creamos valores iniciales:
#Arrays con valores que vamos a usar para cada equipo ["nombre",["IP de Eth0","MASK de Eth0", Gateway de Eth0","IP de Eth1","MASK de Eth1"],"LANX"]
array_inicial = [
    ["c1",["10.1.1.2","255.255.255.0","10.1.1.1"],"LAN1"],
    ["lb",["10.1.1.1","255.255.255.0","10.1.1.1","10.1.2.1","255.255.255.0"],"LAN1"], #Este tiene más puertos pero la configuración lo haremos más tarde
    ["s1",["10.1.2.11","255.255.255.0","10.1.2.1"],"LAN2"]
]
# Lista de redes que se van a crear
array_net = ["LAN1", "LAN2"]
#Numero de servidores permitidos
serv_min = 1
serv_max = 5
#Boleano de Debug
mode_debug = False
#Imagen base
base_image = "cdps-vm-base-pc1.qcow2"
#Plantilla base
base_plantilla = "plantilla-vm-pc1.xml"


#Funcion en el que pasamos debug y cambiamos la configuración de logging
def conf_logging(mode_debug):
    if mode_debug == True:
        logging.basicConfig(level = logging.DEBUG, format = "%(levelname)s, %(message)s" ) # con esto ultimo muestra el nivel y el mensajeç

    else:
        logging.basicConfig(level = logging.INFO, format = "%(levelname)s, %(message)s")


def read_json_and_change_array():
    global mode_debug,array_inicial #Para acceder y poder modificar las variables fuera de la funcion
    try:
        with open("manage-p2.json","r") as file:
            datos = json.load(file) #Lee el archivo y lo convierte en un diccionario de python
            numero_de_servidores = datos["number_of_servers"] # Obtenemos el valor
                    
            if numero_de_servidores < serv_min or numero_de_servidores > serv_max:
                print(f"Error: El número de servidores debe estar entre {serv_min} y {serv_max}.")
                sys.exit(1) #Salir del programa con codigo de error
            
            mode_debug = datos.get("debug", False) #Obtenemos el valor de debug o dejamos por defecto False

    except json.JSONDecodeError:
        print("Error al obtener el valor de \"number_of_servers\" debido a un error en el archivo de formato JSON.")
        sys.exit(1) # Salimos del programa con codigo de error

    #Añadimos servidores adicionales en el array_inicial
    if numero_de_servidores > 1:
        for i in range(2, numero_de_servidores + 1):
            servidor = [f"s{i}", [f"10.1.2.{10 + i}","255.255.255.0","10.1.2.1"],"LAN2"]
            array_inicial.append(servidor)
    

if __name__ == "__main__":
    read_json_and_change_array()
    conf_logging(mode_debug)
    
    # Verifica que al menos se proporcione una orden
    if len(sys.argv) < 2:
        print("Uso: python3 manage-p2.py <orden> [nombre_vm]")
        print("<orden> puede ser: create, start, stop, destroy")
        sys.exit(1)

    order = sys.argv[1].lower()  # Convertir la orden a minúsculas para evitar problemas de mayúsculas
    len_sys_argv = len(sys.argv)

    if len_sys_argv == 2:  # Sin argumentos adicionales
        if order == "create":
            for i in array_inicial:
                mv = VM(i[0], base_image, base_plantilla)
                mv.create_vm(i[2])  # Crear la VM con su red asociada
            logging.info("Máquinas virtuales creadas correctamente")

            for net in array_net:
                red = RED(net)
                red.create_net()
            logging.info("Redes creadas correctamente")

        elif order == "start":
            for i in array_inicial:
                mv = VM(i[0], base_image, base_plantilla)
                mv.start_vm(i[1])
            logging.info("Máquinas virtuales arrancadas correctamente")

        elif order == "stop":
            for i in array_inicial:
                mv = VM(i[0], base_image, base_plantilla)
                mv.stop_vm()
            logging.info("Máquinas virtuales detenidas correctamente")

        elif order == "destroy":
            for i in array_inicial:
                mv = VM(i[0], base_image, base_plantilla)
                mv.destroy_vm()
            logging.info("Máquinas virtuales eliminadas correctamente")

            for net in array_net:
                red = RED(net)
                red.destroy_net()
            logging.info("Redes eliminadas correctamente")

        else:
            print("Orden no reconocida. Órdenes posibles: create, start, stop, destroy")
            sys.exit(1)
        
    elif len_sys_argv == 3:  # Con tercer argumento: nombre de la VM
        command_order = sys.argv[2]
        logging.info(f"Inicio de comando OPCIONAL para {command_order}")

        # Buscar la VM específica
        mv = next((mvs for mvs in array_inicial if mvs[0] == command_order), None)
        
        if mv is None:  # Si no se encontró la VM
            print(f"Error: Máquina virtual '{command_order}' no encontrada.")
            sys.exit(1)

        if order == "start":
            mv_arg_3 = VM(mv[0], base_image, base_plantilla)
            mv_arg_3.start_vm(mv[1])
            logging.info(f"Se ha arrancado correctamente {command_order}")

        elif order == "stop":
            mv_arg_3 = VM(mv[0], base_image, base_plantilla)
            mv_arg_3.stop_vm()
            logging.info(f"Se ha detenido correctamente {command_order}")

        else:
            print("Orden no reconocida. Órdenes posibles con una VM específica: start, stop")
            sys.exit(1)

    else:  # Si se proporcionan demasiados argumentos o una combinación inválida
        print("Uso: python3 manage-p2.py <orden> [nombre_vm]")
        print("<orden> puede ser: create, start, stop, destroy")
        sys.exit(1)