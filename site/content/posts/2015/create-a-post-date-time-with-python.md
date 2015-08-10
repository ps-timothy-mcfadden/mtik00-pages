+++
categories = ["hugo", "python"]
date = "2015-08-09T21:07:30-06:00"
title = "Create a Post Date/Time with Python"
type = "post"
slug = "create-a-post-date-time-with-python"
+++

I like to create draft posts as kind of *markers* for things I want to write about in the future.  Unfortunately, when I do a `hugo new post...`, the current date is already put in the front matter for me. That's **really** handy if I'm posting right away, but not so much if I have a *draft* for a really long time.<!--more-->

If you have Python installed on your system, here's a quick one-liner to print out the current [date/time](https://docs.python.org/2/library/time.html?highlight=time.strftime#time.strftime) in Hugo's (really Go's) format:

{{< highlight python >}}
python -c "import time; print time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime()) + '%+03i:00' % (-1*(time.altzone / 3600) if time.daylight else (-1*(time.timezone/3600)));"
{{< /highlight >}}

I have that line wrapped in a batch file that I can run called `htime.bat`.

It's quick and easy!  It's *slightly* easier than just changing it with your text editor.

NOTE: This command only takes into consideration timezones that change on the hour!  Sorry [India](http://www.timeanddate.com/worldclock/india/new-delhi) (and more)...
