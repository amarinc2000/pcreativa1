#!/usr/bin/python3
import os          #  proporciona funciones para interactuar con el sistema operativo

import subprocess  #  ejecutar comandos
import sys         #  acceder a argumentos de línea de comandos y realizar interacciones básicas
import json
import logging
from libreria import VM, Red

class VM:

    def __init__(self, name):
     self.name = name
 # Función para inicializar las máquinas virtuales
    def create_vms():
        logging.info("Inicializando el escenario...")
        
        # Crear imágenes de disco para cada máquina virtual
        for vm in VM_NAMES:
            nombre_disco = f"{vm}.qcow2"  # Usar f-string para interpolar la variable 'vm'
            


            try:
                subprocess.run(
                ["qemu-img", "create", "-F", "qcow2", "-f", "qcow2", "-b",BASE_IMAGE, nombre_disco],
                
                )
                print(f"Disco creado:{nombre_disco} ")
            except subprocess.CalledProcessError as e: #subprocess.CalledProcessError. Esta excepción es específica para capturar errores relacionados con la ejecución de procesos a través del módulo subprocess
                print(f"Error al crear el disco para {nombre_disco}: {e}")
                logging.error("no se ha creadi la maquina virtual correctamente")
    # FALTARIA PONER LA PARTE DE SUDO VIRSH DEFINE (EJ:sudo virsh define s1.xml ) !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Función para arrancar las máquinas virtuales y mostrar su consola
    def start_vms():
        for vm in VM_NAMES:
            nombre_mv = f"{vm}"

            try:
                subprocess.run(
                    ["sudo", "virsh", "start",nombre_mv]
                )
                subprocess.run(
                    ["xterm","-e", "sudo", "virsh", "console",nombre_mv, "&"] #Recomendación: Usa subprocess.Popen() en lugar de subprocess.run() si necesitas ejecutar procesos en segundo plano.
                    #tambien me dice el chat que el & habria que quitarlo XDD
                )
            except subprocess.CalledProcessError as e:
                print (f"Error en el Start  o al abrir consola")

    # Función para parar las maquinas virtuales
    def stop_vms():
        for vm in VM_NAMES:
            try:
                subprocess.run(["sudo", "virsh", "shutdown", vm], chek= True) #Esto ultimo asegura que si el comando falla, se levante una excepcion
                print (f"La Maquina Virtual:{vm} se ha detenido correctamente")
            except subprocess.CalledProcessError as e:
                print(f"Error al intentar detener la Maquina Virtual {vm}: {e}" )

    # Función para liberar el espacio, borrando todos los archivos
    def destroy_vms():
        for vm in VM_NAMES:
            try:
                subprocess.run(["sudo", "virsh", "destroy", vm], chek= True) #Esto ultimo asegura que si el comando falla, se levante una excepcion
                print (f"Los ficheros de la maquina virtua: {vm}, se han eliminado correctamente")
            except subprocess.CalledProcessError as e:
                print(f"Error al eliminarlos ficheros" )
    #<--------------------------------------------- FALTARIA INTRODUCIR LA ELIMINACION DE LOS ARCHIVOS .XML se me ha ocurrido de dos formas, o crear un array al principio con todos los .xml e ir borrando
    # o buscar de alguna manera que se puedan borrar todos los docs de la carpeta p1Creativa exceptuando los archivo con x nombre (esos nombres son los de las plntillas y el .py)

class Red:
