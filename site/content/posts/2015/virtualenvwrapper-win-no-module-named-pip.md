+++
categories = ["python"]
date = "2015-09-09T10:16:16-06:00"
title = "virtualenvwrapper-win \"No module named pip\""
type = "post"
slug = "virtualenvwrapper-win-no-module-named-pip"
+++

If you use virtualenvwrapper on Windows, you may have come across an issue where the environment cannot be created properly due to "ImportError: No module named pip"<!--more-->

I'll let you Google the reason; here's a fix.  Basically, you need to create the environment *without* `setuptools`.  Here are the basic steps:

1.  `mkvirtualenv --no-setuptools --no-site-packages newenv`
1.  `wget --no-check-cert https://raw.github.com/pypa/pip/master/contrib/get-pip.py`
1.  `python get-pip.py`
1.  `del get-pip.py`

Because I do this every so often, I've implemented my own `mkvirtualenv` batch file like so:

{{< highlight batch >}}
@echo off
IF .%1 == . (
    echo Usage: mkvirtualenv 'env name'
    GOTO :eof
)

@echo on
call C:\Python27\Scripts\mkvirtualenv.bat --no-setuptools --no-site-packages %1
wget --no-check-cert https://raw.github.com/pypa/pip/master/contrib/get-pip.py
python get-pip.py
del get-pip.py
{{< /highlight >}}

FYI: I store batch files like this in `C:\bin`.  I then put `C:\bin` in my path, so they're available to all of my command-line activities.

The batch file is not perfect, since the path to the actual `mkvirtualenv` is hard coded, but it's *far* easier than trying to store the output of something like `python -c "import os,sys; print os.path.join(os.path.dirname(sys.executable), 'Scripts', 'mkvirtualenv.bat')"`.
