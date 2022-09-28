---
aliases:
- /2008/04/netcat-quickly-send-binaries-through
categories:
- linux
date: 2008-04-29 12:25
layout: post
slug: netcat-quickly-send-binaries-through
title: netcat, quickly send binaries through network

---

<p>
 just start nc in server mode on localhost:
 <br/>
 <br/>
 [sourcecode language='python'] nc -l -p 3333 [/sourcecode]
 <br/>
 <br/>
 send a string to localhost on port 3333:
 <br/>
 <br/>
 [sourcecode language='python'] echo "hello world" | nc localhost 3333 [/sourcecode]
 <br/>
 <br/>
 you'll see on server side appearing the string you sent.
 <br/>
 <br/>
 very useful for sending binaries, see
 <a href="http://www.g-loaded.eu/2006/11/06/netcat-a-couple-of-useful-examples/">
  examples
 </a>
 .
</p>
