# The script to convert CentOS7 to AlmaLinux 8 with installed Plesk panel

## Introduction
This script utilizes the [AlmaLinux ELevate tool](https://wiki.almalinux.org/elevate/ELevate-quickstart-guide.html), which is based on the [leapp modernization framework](https://leapp.readthedocs.io/en/latest/), to perform the conversion of a server running Plesk on CentOS 7 to AlmaLinux 8.
The script includes additional repository and configuration support provided by Plesk. This is the official method for converting a server with Plesk from CentOS 7 to AlmaLinux 8.

## Preparation
Before using this script, it is important to take the following precautions:
1. Make sure that you have backed up all of your databases and have the means to restore them. We will be using standard mariadb and postgresql tools to upgrade the databases, and it is highly recommended to have backups in case something goes wrong.
2. Ensure that you have a way to restart the server in the event that the direct ssh connection is lost. There is a risk that the conversion process may hang in a temporary update distro that does not start any network interfaces. One way to mitigate this risk is to have a serial port connection to the server, which will allow you to monitor the upgrade distro and the first boot progress, and to reboot the server if necessary.
3. It may be helpful to have a snapshot that can be used as a recovery point in case the conversion process fails.

## Timing
The estimated time for the conversion process is between 30 to 60 minutes. Please note that **Plesk services, hosted sites, and emails will be unavailable during the entirety of the conversion process**. The conversion process itself will be divided into three stages:
- the Preparation stage, which will take between 15 to 25 minutes
- the Conversion stage, which will take between 15 to 30 minutes and during this stage, the server will not be available remotely, so you need to monitor the process through serial port console
- the Final stage, which will take between 5 to 10 minutes.

## Known problems
### Stoppers
The following factors should prevent you from using the script to perform a conversion as they may cause issues with essential services.
- **Qmail component is installed** - SMTP authentication is broken after the conversion
- **Ruby extension is installed** - Ruby applications not working after the conversion
- **PostgreSQL from 10.23 and newer is installed** - will now work after the conversion due to a downgrade
- **The distro is not CentOS 7** - the script has not been tested on other RHEL 7 based distributions. Therefore, the conversion process may have unexpected results when used on these other distros.
### Restrictions
The following restrictions should not prevent the conversion from taking place, but it's good to be aware of them. Most likely they will not be fixed in future.
- PHP from 5.4 to 7.1 will not receive any updates after the conversion. The versions are deprecated and not supported in AlmaLinux 8. It's important to note that these versions may have security vulnerabilities, so it's recommended to migrate to the latest versions of PHP.

## Requirements
- To perform the conversion process, you should have Plesk 18.0.42 or a later version installed
- You should have Centos 7.9 or greater installed. 
- Recommended to have at least 10 GB of free storage space to accommodate the packages required for the conversion
- The system should have at least 1 GB of RAM to ensure the process runs smoothly

## How to use the script

To use the script, simply run it without any arguments:
```shell
> ./distupgrader
```
This will start the conversion process. Please note that during this process, Plesk services will be temporarily shut down and hosted sites will not be accessible. At the end of the preparation process the server will be rebooted.
Next, a temporary distro will be used to convert your CentOS 7 system to AlmaLinux 8. This process is estimated to take approximately 20 minutes. Once completed, the server will undergo another reboot. The distupgrader script will then perform the final steps of reconfiguring and restoring Plesk-related services, configurations, and databases. This may take a significant amount of time if the databases contain a large amount of data.
Once the process is complete, the distupgrader script will reboot the server one final time, at which point it should be ready to use.

### Conversion stages
The conversion process can be divided into several stages: "prepare", "start", and "finish". Use the flag "-s" to run only one stage of the conversion process.
1. The "prepare" stage should always be called first. It installs ELevate and makes additional configurations for it. This stage does not disable any services, so it can be safely run at any time.
2. The "start" stage disables Plesk-related services and runs ELevate. This will result in the stopping of Plesk services and the rebooting of the server.
3. The "finish" stage should be called on the first boot of AlmaLinux 8. The distupgrader finish can be re-run if something goes wrong during the first boot to ensure that the problem is fixed and Plesk is ready to use."

### Other arguments

### Logs
In most cases, it is not necessary to check the logs. However, if something goes wrong, the logs can be used to identify the problem. The logs can also be used to check the status of the finish stage during the first boot.
The distupgrader logs can be found in '/var/log/plesk/distupgrader.log', and will also be written to stdout.
The ELevate debug logs can be found in '/var/log/leapp/leapp-upgrade.log', and reports can be found in '/var/log/leapp/leapp-report.txt' and '/var/log/leapp/leapp-report.json'.

## Possible problems

### Leapp unable to handle package
In some cases, leapp may not be able to handle certain installed packages, especially if they were installed from uncommon repositories. In this case, the distupgrader will fail while running leapp preupgrade or leapp upgrade with an explanatory message. The simplest way to fix this problem is to remove the old package and reinstall a similar package once the conversion is complete.
### Upgrade distro is hung
This problem may occur in rare situations, such as when a custom python installation is present. In this case, the conversion process will fail in the scope of the upgrade temporary distro, and the distro will hang without any notification. To identify the problem, you should connect to your instance using a serial port and check the status. To fix the problem, reboot the server. Note that an unfinished installation process may result in missing packages and other issues.

### Distupgrader finish failed on a first boot
The problem can be identified in the distupgrader log '/var/log/plesk/distupgrader.log'. If the distupgrader finish stage fails for any reason, you can rerun it with 'distupgrader -s finish' after addressing the cause of the failure.
