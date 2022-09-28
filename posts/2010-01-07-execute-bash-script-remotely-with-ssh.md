---
aliases:
- /2010/01/execute-bash-script-remotely-with-ssh
categories:
- linux
date: 2010-01-07 14:37
layout: post
slug: execute-bash-script-remotely-with-ssh
title: execute bash script remotely with ssh

---

<p>
 a bash script launched remotely via ssh does not load the environment, if this is an issue it is necessary to specify --login when calling bash:
 <br/>
 <br/>
 <code>
  ssh user@remoteserver.com 'bash --login life_om/cronodproc' | mail your@email.com -s cronodproc
 </code>
</p>
