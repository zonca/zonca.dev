---
title: Use VS Code on Expanse
date: 2025-08-08
tags:
- VS Code
- Expanse
- HPC
- SSH
- sdsc
---

Using VS Code directly on Expanse, or other HPC systems, is generally not recommended due to the high resource usage of the IDE itself. These systems are optimized for computational tasks, not for running graphical applications on login nodes.

The popular "Remote - SSH" extension for VS Code, which allows you to connect to a remote server and develop as if your code was local, also faces challenges. This extension attempts to install a VS Code server on the remote machine. On Expanse's login nodes, this server often consumes too much memory, leading to connection issues or system instability.

However, there is a viable workaround using the "SSH FS" extension. This extension allows you to mount a remote filesystem over SSH, making it appear as a local folder in VS Code. You can then edit files directly, and VS Code will handle the file transfers in the background. This approach avoids running a full VS Code server on the remote machine, making it much more lightweight and suitable for HPC environments. You are only getting the files from Expanse, but if you run any code, you are running locally, not using the Expanse resources.

Here's an example configuration for the "SSH FS" extension in your VS Code `settings.json` file:

```json
"sshfs.configs": [
  {
    "name": "Expanse",
    "host": "login.expanse.sdsc.edu",
    "username": "your_username",
    "root": "/home/your_username",
    "port": 22,
    "privateKeyPath": "/path/to/your/ssh/private_key"
  }
]
```

Remember to replace `"your_username"` with your actual Expanse username and `"/path/to/your/ssh/private_key"` with the correct path to your SSH private key file. This setup allows you to leverage VS Code's powerful editing features while respecting the resource constraints of the Expanse HPC system.
