MOZ_OVERRIDE
============

This script is using the CppHeaderParser Module available here: https://pypi.python.org/pypi/CppHeaderParser/

This module is developped by senex (Jashua Cloutier) who does a real good job on it :)

You just need to install it
```
$>pip install cppheaderparser
```

MOZ_OVERRIDE is a script I developped for Mozilla
wich recreates the whole heritage tree for all classes in mozilla-central.

Of course it can be used anywhere, but is designed ofr mozilla.
The wiki will be updated soon to show how to adapt it to another behaviour.

It finds classes that inherits from a base class
and annotate them with MOZ_OVERRIDE (override in C++11).

I should be able to enhance it to be able to give some specific details on modules and/or classes
such as parents, childs, overrided methods, etc...

Used in Bugs:
 - https://bugzilla.mozilla.org/show_bug.cgi?id=733186
 - https://bugzilla.mozilla.org/show_bug.cgi?id=703068
 - https://bugzilla.mozilla.org/show_bug.cgi?id=856822
 - https://bugzilla.mozilla.org/show_bug.cgi?id=870516
 - https://bugzilla.mozilla.org/show_bug.cgi?id=875367
 - https://bugzilla.mozilla.org/show_bug.cgi?id=877746
 - https://bugzilla.mozilla.org/show_bug.cgi?id=973805
 - https://bugzilla.mozilla.org/show_bug.cgi?id=974687

Usage:

`./main.py Path [-v|-d] [--dryrun] [-h|--help] [-W] [-I header_from_idl_folder]`

> Path		  => Path to the files you want to add MOZ_OVERRIDE
> -v 		  => Verbose Mode
> -d 		  => Debug Mode
> --dryrun	  => Doesn't modify files, only simulation
> -h		  => Obvious
> -W		  => Shouldn't be used, unsafe
> -I idl_folder  => Another path to parse files but thoses won't be modified
>      		     very usefull if some of your classes in Path included files that aren't in the same folder

To get the best results, do this:

> clean, configure and generates IDL files

`~/m-c_folder>./mach clobber; ./mach configure && ./mach build export`

> Parse Files and annotate them.

`~/>./main.py ~/m-c_folder/<module> -I ~/m-c_folder`

This way you will generate all idl files, parse all headers used in m-c but only modify thoses in the <module> you want.

Feel free to open an issue if needed or mail me for a quick question.

I'm sometimes present on IRC irc.mozilla.org #developers [:Six]
