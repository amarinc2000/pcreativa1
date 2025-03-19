# Práctica Final del Primer Parcial

## Objetivos
La práctica final del primer parcial consiste en el desarrollo de un script en Python que automatice parcialmente la creación del escenario de pruebas del balanceador de tráfico de la segunda parte de la práctica 2. Opcionalmente, se podrá trabajar con otros escenarios virtuales de complejidad similar o que utilicen contenedores LXC o Docker en vez de máquinas virtuales KVM. En caso de trabajar sobre un escenario alternativo, se debe consultar previamente con los profesores de la asignatura.

## Requisitos Funcionales Mínimos del Script

### RQ1: Entorno de Ejecución
El script, denominado `manage-p2.py`, debe ejecutarse en un directorio que contenga:
- La imagen base utilizada por las máquinas virtuales (VM) del escenario: `cdps-vm-base-pc1.qcow2`
- La plantilla de VMs: `plantilla-vmpc1.xml`

Estos archivos están disponibles en el directorio `/lab/cdps/pc1` del laboratorio o en la web:
[https://idefix.dit.upm.es/download/cdps/pc1/](https://idefix.dit.upm.es/download/cdps/pc1/)

**Nota:** El script no debe copiar estos archivos; deben estar previamente copiados en el directorio de trabajo.

### RQ2: Operaciones Disponibles
El script `manage-p2.py` se ejecutará con un parámetro obligatorio que define la operación a realizar:
```bash
manage-p2.py <orden>
```
Donde `<orden>` puede tomar los siguientes valores:
- `create`: Inicializa las máquinas virtuales, creando las imágenes de diferencias (`*.qcow2`) y las especificaciones en XML de cada VM. También crea los bridges virtuales para las LAN del escenario.
- `start`: Arranca las máquinas virtuales y muestra su consola.
- `stop`: Detiene las máquinas virtuales (sin liberarlas).
- `destroy`: Libera el escenario, eliminando todos los archivos creados.

### RQ3: Configuración del Número de Servidores
El número de servidores web a iniciar debe ser configurable (de 1 a 5). Este valor se especifica en un archivo de configuración JSON (`manage-p2.json`) dentro del directorio de trabajo:
```json
{
 "number_of_servers": 2
}
```
El script debe validar este valor y generar un error si no es correcto.

### RQ4: Configuración de las VMs
Antes de arrancar las VMs, el script debe modificar los siguientes archivos en cada máquina:
- `/etc/hosts`
- `/etc/hostname`
- `/etc/network/interfaces`

Además, debe configurar el balanceador de carga (LB) para que funcione como router.

### RQ5: Creación de Imágenes de VMs
Las imágenes de las VMs deben crearse como archivos de diferencias (`qcow2`) respecto a la imagen base `cdps-vm-base-pc1.qcow2`.

### RQ6: Ejecución No Interactiva
El script debe ser completamente no interactivo, es decir, todos los parámetros necesarios deben proporcionarse a través de la línea de comandos. No se debe solicitar información al usuario durante la ejecución.

### RQ7: Registro de Actividad
El script debe utilizar el módulo `logging` de Python para generar trazas de depuración. Por defecto, debe mostrar mensajes breves sobre su actividad, pero si en el archivo `manage-p2.json` se define la variable `debug: true`, deberá proporcionar mensajes detallados:
```json
{
 "number_of_servers": 2,
 "debug": true
}
```

### RQ8: Librería en Python
Para la gestión de las máquinas y redes virtuales, se debe desarrollar una librería en Python que exporte dos objetos:
- `VM`: con métodos para crear, arrancar, mostrar la consola, parar y liberar VMs.
- `Red`: con métodos para crear y liberar redes.

### RQ9: Uso de Open vSwitch
Para la creación de los bridges virtuales que implementan las redes `LAN1` y `LAN2`, se debe utilizar el comando:
```bash
ovs-vsctl
```


