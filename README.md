# rpgmakertrans
A fork of the abandoned project rpgmakertrans https://bitbucket.org/rpgmakertrans/rpgmakertrans/src/master/

This project focuses on the CLI version of rpgmakertrans and provides an easy way to run or build applications from sourcecode, considering the python version requirements and dependencies used to run this application are very outdated.

## What improved / changed
- All texts that are previously uneditable, now editable. Such as. Map's name, event's name, comments. Why? Because some developer use ruby script to include texts that are not normally viewable in-game, viewable. They put those texts inside that previously mentioned fields.
- Event's labels are no longer translatable, since there is no reason to translate it as it would cause harm more than benefits.
- Ruby scripts are included literally.

## How to run
```shell
cd rpgmakertrans
..\python3.4\python.exe .\rpgmt.py path\to\your\rpgmaker\game
```
