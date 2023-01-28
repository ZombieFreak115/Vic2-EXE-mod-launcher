# Vic2 EXE mod launcher
 A launcher for vic2 which allows the launching of EXE mods, made in Python.
 
 ## Installation
 
 To install, download the newest (or any after 3.8) version of Python for your OS here: https://www.python.org/downloads/.
 Make sure you do a **Custom Install** and checkmark the following features: 
 - Add python to PATH
 - pip
 - py launcher
 - Add python to environment variables
 - Associate files with python
 
 After that, download the newest version/release from here, extract it, and run the InstallDependencies.bat once. It will install all the Python packages required.
 
 Once that is done, make a folder called "exemods" in your root Vic2 directory, then copy the Launcher.py to your root Vic directory and run!
 
 
 ## Usage
 
 The exemods folder, as it alludes to, is the one which the "mods" are loaded from. It accepts any text file format (.txt, .ini, or hell even .v2) though .txt is preffered.
 
 You can then use the GUI to select which mods from the folder you'd want to load. Then you run the Launcher.py and start witht he mods it will launch the regular Vic2 launcher, where you can then also select which "regular" mods you want to load.
 
 I have included 2 EXE mods i have made in the "examplemods" folder in the download aswell. Simply put em in your exemods folder and select to run them.
 
 Keep in mind to NOT close the program while Vic2 is running, or else it won't be able to restore your exe back to normal again.
 ## Documentation
 
 The "exemods" are really just textfiles with byte overrides to the exectutable code, here i will explain the (very simple) format and syntax
 
 
 A typical exe mod may look like this:
 
 ```
 desc="This mod fixes a basegame oddity in which brigades in a stack will reinforce less and less the bigger the stack is if you are below 100% supply, now they will all reinforce as if they were individual brigades"

#NOP's out the instruction which tells the game to  put the variable in for the next brigade in stack, effectively making all brigades act as if they are the 1st one

1C809B={\x90}

1C809C={\x90}

1C809D={\x90}

1C809E={\x90}
```
As you can see, it also supports Python-style comments

In the first line, we can see a description, which is shown in the launcher when selected. The syntax is desc="description here".

Now for the actual code, it is contructed in a key:value pair, seperated by equals sign (=) in which the key is the hex file offset (which instruction it should modify), and the value is the byte opcode it should be changed *to*.

So, for instance, if we wanted to change the byte at offset 1BF95E to 90, which is the opcode for "no instruction", we would write it like this:
```
1BF95E={\x90}
```

Keep in mind the curly brackets and the \\x before the number is needed.

In order to get the offsets, most hex editors or disassemblers will show the offsets, for example in Ghidra you just have to hover over the address and it will tell you.

All this requires a fair bit of knowlegde on how to dissassemble, reverse engineer etc. so if you are interested in learning it i cannot recommend this video enough: https://www.youtube.com/watch?v=cwBoUuy4nGc, really helped me understand the ins and outs.


## How it works (technical stuff)

So how does it work? Some of you may have noticed it isn't a typical code injection method into the process, as it usually done with these types of things. The launcher actually modifies the EXE to be modded, and then restores it at the end of the play session with a backup.

The reason i used this method instead of the usual process injection, is because code/dll injection does not seem to affect the checksum when done in runtime, whereas executable changes does. This is obv. fine for singleplayer and testing, but for stuff which requires consistent checksums it can be a huge issue, and also opens the possibility of cheating (since its the same checksum no matter what you have loaded)

A side-effect of this is you have to have it running in the backround while playing, so that when the game is quit it can automatically restore the unmodded exe.