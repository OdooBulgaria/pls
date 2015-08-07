# Aeroo Report Installation
----------------------------------

## Install Git:
- `sudo apt-get install git`

## Install AerooLib:

-      `sudo apt-get install python-setuptools`
-      `sudo apt-get install python-genshi python-cairo python-lxml`
-      `sudo apt-get install libreoffice-script-provider-python`
-      `sudo mkdir /opt/aeroo`
-      `cd /opt/aeroo`
-      `sudo git clone https://github.com/aeroo/aeroolib.git`
-      `cd /opt/aeroo/aeroolib`
-      `sudo python setup.py install`

- 		Create Init Script for OpenOffice (Headless Mode) - (see: https://www.odoo.com/forum/help-1/question/how-to-install-aeroo-reports-2780 for original post from Ahmet):

	-	`sudo nano /etc/init.d/office`
	-   Copy and paste this:
`#!/bin/sh
/usr/bin/soffice --nologo --nofirststartwizard --headless --norestore --invisible "--accept=socket,host=localhost,port=8100,tcpNoDelay=1;urp;" &`

	-        sudo chmod +x /etc/init.d/office
	-	     sudo update-rc.d office defaults
	-        sudo /etc/init.d/office
	-        telnet localhost 8100
	-        You should see something like the following message (this means it has established a connection successfully):
`
Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.
e--'com.sun.star.bridge.XProtocolPropertiesUrpProtocolProperties.UrpProtocolPropertiesTidE--L`

	- If the

## Install AerooDOCS (see: https://github.com/aeroo/aeroo_docs/wiki/Installation-example-for-Ubuntu-14.04-LTS for original post):

-     `sudo apt-get install python3-pip`
-     `sudo pip3 install jsonrpc2 daemonize`
-     `cd /opt/aeroo`
-     `sudo git clone https://github.com/aeroo/aeroo_docs.git`
-     `sudo python3 /opt/aeroo/aeroo_docs/aeroo-docs start -c /etc/aeroo-docs.conf`
-     `sudo ln -s /opt/aeroo/aeroo_docs/aeroo-docs /etc/init.d/aeroo-docs`
-     `sudo update-rc.d aeroo-docs defaults`
-     `sudo service aeroo-docs start`
       `
                 [ ! ]  If you encounter and error "Unable to lock on the pidfile while trying #16 just restart your server (sudo shutdown -r now)                         and try #16 again after reboot.`

## Install Odoo from Source:

-     `cd /tmp`
-     `sudo wget https://raw.githubusercontent.com/lukebranch/odoo-install-scripts/master/odoo-saas4/ubuntu-14-04/odoo_install.sh`
-     `sudo sh odoo_install.sh`
-     `restart the server (sudo shutdown -r now)`

## Install Aeroo Reports:

-    `sudo apt-get install python-cups`
-    `sudo git clone -b master https://github.com/aeroo/aeroo_reports.git`
-	 `Copy all the modules from aeroo_report folder and paste it in your addons`

> After following the (above) steps in this guide you should have Aeroo Reports installed correctly on your server for Ubuntu 14.04 and Odoo 8.0. 
> You'll just need to create a database and install the required Aeroo reports modules you need for that database.

> [ ! ]    Do not have aeroo_report_sample in your addons directory or you will get an error message when updating module list:
>         Warning! Unmet python dependencies! No module named cups

## Install report_aeroo module in Odoo database:

-    Go to Settings >> Users >> Administrator in the backend of Odoo
-    Tick the box next to 'Technical Features' and Save, then refresh your browser window.
-    Go to Settings >> Update Modules List > Update
-    Go to Settings >> Local Modules > Search for: Aeroo
-    Install `report_aeroo`
-    You'll be confronted with an installation wizard, click: Continue >> Choose Simple Authentication from the Authentication dropdown list, and add username and password: anonymous

> [ ! ]     You can change the username and password in: /etc/aeroo-docs.conf if required.

-    Click Apply and Test. You should see the following message if it was successful:

> Success! Connection to the DOCS service was successfully established and PDF convertion is working.
> You now have a fully operational Aeroo Reports installation in Ubuntu 14.04. If for any reason this is not working for you please post back in the > comments and explain the error message you are seeing.


