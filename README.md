# electronic_table_saw
ElectronicTableSaw

Clone this repo `https://github.com/andyalexander/electronic_table_saw.git` into `/home/cnc/linuxcnc`

Run the config by running `linuxcnc /home/cnc/`

After installing linuc cnc run `menu-config` to finsh setting up the raspberry pi

To enable auto-login, `sudo /etc/lightdm/lightdm.conf`, and uncomment `autologin-user=CNC`

To have LinuxCNC start automatically with your config after turning on the computer go to System > Preferences > Sessions > Startup Applications, click Add. Browse to your config and select the `.ini` file. When the file picker dialog closes, add `linuxcnc` and a space in front of the path to your `.ini` file.
 
## Setup 

* Install QTVCP designer `/usr/lib/python3/dist-packages/qtvcp/designer/install_script`
* #`sudo apt install python3-pip`
* sudo apt install python3-gst-1.0

### Raspbery pi config

You will need to edit the `config.txt` to add the following lines (For Elecrow RC070S)

```
hdmi_force_hotplug=1
max_usb_current=1
hdmi_group=2
hdmi_mode=1
hdmi_mode=87
hdmi_cvt 1024 600 60 6 0 0 0
hdmi_drive=2
```

You will also need to disable `dtoverlay=vc4-kms-v3d`


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
* https://github.com/cli/cli/blob/trunk/docs/install_linux.md




## Stepper config

### DM556T
* ENA ahead of DIR by 200ms.  ENA high
* DIR ahead of PUL by 5us
* Pulse width >= 2.5us
* Low level width >= 2.5us



## Useful gcode
* G90 Xxx Yxx Zxx - absolute move
* G91 Xxx Yxx Zxx - incremental move
