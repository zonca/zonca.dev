---
categories:
- nersc
date: '2023-02-24'
layout: post
title: Share data from NERSC publicly via web

---

NERSC allows to make data which is on their Community File System publicly available via a web interface.

This is handled via "Project folders", so the requirement is to be part of a "project", for example most scientists working on Cosmic Microwave Background are part of the `cmb` project (and of the `cmb` Unix group at NERSC):

    > groups
    zonca cmb

    > export PRJ=cmb

So you should be able to create folders on the Community File System, if not already present, also ma

    > mkdir -p /global/project/projectdirs/$PRJ/www

Also make sure it files are world-readable, folders are world-readable and world-executable:

    > chmod 755 !$
    > chmod 644 !$/*
    
Now any files and any subfolder of `www` will be available publicly displaying filenames and file sizes and will allow navigation at the address:

    > echo https://portal.nersc.gov/project/$PRJ

See for example:

    * <https://portal.nersc.gov/project/cmb/dirlist/>
