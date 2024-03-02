# electronic_table_saw
ElectronicTableSaw

Clone this repo `https://github.com/andyalexander/electronic_table_saw.git` into `/home/cnc/linuxcnc`

Run the config by running `linuxcnc /home/cnc/`
 
## Setup 

* Install QTVCP designer `/usr/lib/python3/dist-packages/qtvcp/designer/install_script`
* #`sudo apt install python3-pip`
* sudo apt install python3-gst-1.0

## Useful commands

### Command line

#### QTVCP
* `designer -qt=5` to run the designer

#### General

* `gpioinfo`shows the line <> pin mappings
* https://pinout.xyz/ site with more pin mapping info

#### LinuxCNC

* `halshow`
* `halscope`
* `halmeter`


## Useful HAL components / pins

* `motion.motion-enabled` power button


## Useful links

* https://linuxcnc.org/docs/devel/html/drivers/hal_gpio.html
* https://linuxcnc.org/docs/html/motion/tweaking-steppers.html
* https://linuxcnc.org/docs/2.6/html/common/python-interface.html




## Stepper config

### DM556T
* ENA ahead of DIR by 200ms.  ENA high
* DIR ahead of PUL by 5us
* Pulse width >= 2.5us
* Low level width >= 2.5us



## Useful gcode
* G90 Xxx Yxx Zxx - absolute move
* G91 Xxx Yxx Zxx - incremental move
