---
categories:
- jetstream
layout: post
date: 2024-12-04
slug: jetstream-windows-wsl
title: Run Windows and WSL on Jetstream

---

Need access to a Windows machine? You can leverage Jetstream 2, spin up a Virtual Machine with Windows Server 2022 and access the Windows graphical desktop through your browser on any operating system.

On Exosphere Launch a `m3.small` Windows Server 2022 instance backed by a 40GB disk,
it will stay forever in "Building" phase, not to worry.

Follow the [instructions on the Jetstream documentation](https://docs.jetstream-cloud.org/general/windows/?h=windows#retrieving-the-admin-password) for recovering the admin password (generally a SSH key is already in PEM format so no need to run the `ssh-keygen` command) and accessing the console via Horizon.
You can access same console also via Exosphere using the "Console" button.

Click on the "Send Ctrl-Alt-Delete" button to unlock the screen,
login with the administrator password, unfortunately copy-paste does not work so you need to type the password.

Reboot to apply the security updates, otherwise some of the next steps can be blocked by the system.

From the start menu choose "Windows Powershell"

    wsl --list --online

Most probably you should be using the default Ubuntu 22.04 with:

    wsl --update
    wsl --install

Reboot

Unfortunately I couldn't find a way to copy-paste between my system and the machine, therefore the best is to use the Windows browser to access whatever is the necessary documentation, copy and then paste into WSL with the middle button of the mouse (right+left click on trackpad).

It is also possible to activate OpenSSH Server in Windows and SSH into the VM, however WSL does not work inside that terminal so that does not seem to be an option.
