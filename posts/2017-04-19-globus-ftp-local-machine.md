---
aliases:
- /2017/04/globus-ftp-local-machine
categories:
- globus
- linux
date: 2017-04-19 12:00
layout: post
slug: globus-ftp-local-machine
title: Run Globus Connect Personal on Linux from the command line

---

Globus Connect Personal is a client that turns any machine (e.g. your laptop) into a Globus Endpoint, so you can transfer data to/from any other Globus Endpoint (e.g. a Supercomputer).

It is designed to run with a GUI, but it works also headless.

* Download the TGZ from the website and extract it
* Run `./globusconnectpersonal -setup`, this gives you a link to visit to get an authentication code
* Paste the auth code back in the terminal
* Enter a name for the Endpoint
* It exits

Now `~/.globusonline/lta/config-paths` contains the list of folders that are Read/Write accessible (default `~/` and `/tmp`), edit this file to allow Globus to write where you want.

Then run:

    ./globusconnectpersonal -start &

And verify it is running checking if the endpoint is "Active" on the Globus website.

You can also use the CLI to manage transfers, see (link removed as Globus Toolkit is retired)
