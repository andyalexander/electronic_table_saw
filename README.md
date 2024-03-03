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
   * Edit `sudo /etc/lightdm/lightdm.conf`, and uncomment `autologin-user=CNC` in the `[Seat:*]` section 
   * Uncommenting the line `autologin-user-timeout=0`


2. Let LinuxCNC start automatically with your config after turning on the computer:
   * Go to System > Preferences > Sessions > Startup Applications, click Add. 
   * Browse to your config and select the `.ini` file. When the file picker dialog closes, add `linuxcnc` and a space in front of the path to your `.ini` file.


3. Set screen blanking
   * Edit `.profile` in the home directory, and add the line `xset s 60` to the bottom, this will blank the screen after 60 seconds.  
   * You may also want to disable 'Display power management' on the 'Display' tab of 'Power Manager'.


4. Add the following line to the end of `.profile`, it will do a git pull each login, change to your cloned repo / confif location: `git -C /home/cnc/electronic_table_saw pull`


5. In 'Power manager' under the 'Security' tab
   * Uncheck the 'Lock screen when system is going to sleep' option to avoid needing password when it wakes
   * Change 'Automatically lock the session' to 'Never'

### Development setup 

If you are developing on the Raspberry pi

* Install QTVCP designer by running `/usr/lib/python3/dist-packages/qtvcp/designer/install_script` selecting Option 3 - 'package installation' when asked.
* Use `designer -qt=5` to run the UI designer

If you are developing on the mac, run: `open -a designer`





## Useful references

### Hardare

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



