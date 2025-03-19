#!/usr/bin/python3
import os          #  proporciona funciones para interactuar con el sistema operativo

import subprocess  #  ejecutar comandos
import sys         #  acceder a argumentos de línea de comandos y realizar interacciones básicas
import json
import logging

# Configuracion basica
BASE_IMAGE = "cdps-vm-base-pc1.qcow2"
PLANTILLA_XML = "plantilla-vmpc1.xml"

#Arrays con valores que vamos a usar para cada equipo ["nombre","LANX","IP de Eth0","Nº Bridges"]
array_inicial = [
    ["c1","LAN1",".2",1],
    ["lb","LAN1",".3",2,], #Este tiene más puertos pero la configuración lo haremos más tarde
    ["s1","LAN2",".11",1],
    ["s2","LAN2",".12",1],
    ["s3","LAN2",".13",1],
    ["s4","LAN2",".14",1],
    ["s5","LAN2",".15",1],
]
VM_NAMES = []
#Numero de servidores permitidos
serv_min = 1
serv_max = 5


def change_array_with_n_servers():
    with open("manage-p2.json","r") as file:
        for line in file:
            if '"number_of_servers":' in line:
                try:
                    datos = json.loads(line.strip()) #Cargamos solo la linea que contiene el valor IMPORTANTE S de LOADS
                    numero_de_servidores = datos.get("number_of_servers") # Obtenemos el valor

                    if numero_de_servidores < serv_min or numero_de_servidores > serv_max:
                        print(f"Error: El número de servidores debe estar entre {serv_min} y {serv_max}.")
                        sys.exit(1) #Salir del programa con codigo de error

                    break # Salimos del bucle
                except excepcion as e:
                    print ("Error:El archivo JSON tiene formato incorrecto")#<--------------------------------------------- CAMBIO REALIZADO REVISAR  
                sys.exit(1) # Salimos del programa con codigo de error

  #Eliminar elementos de array sobrantes (servidores)
    nElementos_array_eliminar = serv_max - numero_de_servidores
    del array_inicial[-nElementos_array_eliminar:] # Eliminamos los ultimos X elementos del array
    for item in array_inicial:
        VM_NAMES.append(item[0])

# Leer archivo de configuración para obtener la opción debug
def load_config():
    try:
        with open("manage-p2.json", "r") as file:
            config = json.load(file)
            return config
    except FileNotFoundError:                           #<------------------------------------ estos errorresson excepciones estandares de python, creo que tendriamos que poner algo menos pro
                                                        # rollo: except Error.Json print("no se pudo leer el json o no se encontro") y a mamarla
        print("Error: El archivo de configuración no se encontró.")
        return None
    except json.JSONDecodeError:
        print("Error: No se pudo leer correctamente el archivo de configuración JSON.")
        return None

# Configurar el logging segun el estado del .json
def conf_logging(debug)
    if debug == True
        logging.basicConfig(level = logging.DEBUG, format = "%(levelname)s, %(message)s" ) # con esto ultimo muestra el nivel y el mensajeç

    else
        logging.basicConfig(level = logging.INFO, format = "%(levelname)s, %(message)s")


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
    

# Función principal

def main():
    config = load_config()
     if config is None:
        print("No se pudo cargar la configuración.")
        return

    # Verificar el modo del .json
    mode = config.get("debug", false) # en caso de no existir , se asigna false en su defecto
    conf_logging(mode)

#-----------------------------------------------------------------------------------------------#

    logging.info("Ejecutando el script...")

    # Verifica si se proporcionó un argumento
    if len(sys.argv) < 2:
        print("Error: No se proporcionó ninguna orden")
        sys.exit(1)

    # Procesa el argumento
    command = sys.argv[1]

    if command == "create":
        logging.debug("creando las maquinas virtuales (debug)")
        change_array_with_n_servers()
        create_vms()
        
    elif command == "start":
        logging.debug("inicializando las MVS")
        start_vms()
    elif command == "stop": 
        logging.debug("empezando a parar las MVS sin destruir los archivos")
        stop_vms()
    elif command == "destroy":
        logging.debug("destruccion de archivos excepto plantillas")
        destroy_vms()
    else:
        print("Error: orden desconocida")

# Punto de entrada del script
if __name__ == "__main__":
    main()







