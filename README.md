# Electronic Table Saw Fence

## Getting started

Before you start download and write the image for Linux CNC Raspberry pi 4 to a memory card, and ensure the raspberry pi boots.



### Raspbery pi harware setup

After installing linuxcnc run `menu-config` to finsh setting up the raspberry pi for the keyboard / locale settings you need.

To allow the Raspberry PI to set the screen resolution, follow the instructions below.

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


### Software setup

Clone this repo `https://github.com/andyalexander/electronic_table_saw.git` into `/home/cnc/linuxcnc`

**Configure XFCE:**
1. Enable auto-login:
   * `sudo nano /etc/lightdm/lightdm.conf`
   * In the `[Seat:*]` section uncomment and edit `autologin-user=CNC`  
   * In the `[Seat:*]` section uncomment the line `autologin-user-timeout=0`

2. Let LinuxCNC start automatically with your config after turning on the computer:
   * Go to System > Preferences > Sessions > Startup Applications, click Add. 
   * Browse to your config and select the `.ini` file. When the file picker dialog closes, add `linuxcnc` and a space in front of the path to your `.ini` file in the 'command'.

3. Set screen blanking
   * Edit `.profile` in the home directory, and add the line `xset s 60` to the bottom, this will blank the screen after 60 seconds.  
   * You may also want to disable 'Display power management' on the 'Display' tab of 'Power Manager'.

4. Add the following line to the end of `.profile`, it will do a git pull each login, change to your cloned repo / config location: 
```commandline
git -C /home/cnc/electronic_table_saw pull
```

If you want to overwrite use:
```commandline
git -C /home/cnc/electronic_table_saw fetch --all
git -C /home/cnc/electronic_table_saw reset --hard origin/main
```


5. In 'Power manager' under the 'Security' tab
   * Uncheck the 'Lock screen when system is going to sleep' option to avoid needing password when it wakes
   * Change 'Automatically lock the session' to 'Never'

#### Raspbery Pi 5

* You need to make sure the SPI isn't being used by the system (check if `gpioinfo` shows lines 7/8 as used or unused).
* If used, run `menu-config` and edit `config.txt` via the kernel menu option. Comment out the line `dtparam=spi=on`

### Installing Arduino level sensor
If you want to use this, you will need to enable the commented line in the `.hal` file.  Note that you will also need to:

* Copy the two `.rules` files to `/etc/udev/rules.d` (you will need to be `root` to do this).
* You may need to run `sudo udevadm control --reload` to reload the rules

Useful commands to help diagnose permission issues:

* `udevadm monitor --kernel --udev --property | tee udev.log`
* Manually load the usr module, run `halrun` then enter `loadusr -W hal_input -KRAL SparkFun`



### Development setup 

If you are developing on the Raspberry pi

* Install QTVCP designer by running `/usr/lib/python3/dist-packages/qtvcp/designer/install_script` selecting Option 3 - 'package installation' when asked.
* Use `designer -qt=5` to run the UI designer

If you are developing on the mac, run: `open -a designer`





## Useful references

### Hardware

* `gpioinfo`shows the line <> pin mappings
* https://pinout.xyz/ site with more pin mapping info

### LinuxCNC

* `halshow`
* `halscope`
* `halmeter`


### Useful HAL components / pins

* `motion.motion-enabled` power button


### Useful links

* https://linuxcnc.org/docs/devel/html/drivers/hal_gpio.html
* https://linuxcnc.org/docs/html/motion/tweaking-steppers.html
* https://linuxcnc.org/docs/2.6/html/common/python-interface.html
* https://github.com/cli/cli/blob/trunk/docs/install_linux.md

### G-code
* G90 Xxx Yxx Zxx - absolute move
* G91 Xxx Yxx Zxx - incremental move



## My config

### DM556T
* ENA ahead of DIR by 200ms.  ENA high
* DIR ahead of PUL by 5us
* Pulse width >= 2.5us
* Low level width >= 2.5us



