+++
categories = ["hugo", "web", "python"]
date = "2015-08-10T20:57:46-06:00"
title = "Testing Pipelined Static Content"
type = "post"
slug = "testing-pipelined-static-content"
+++

After working quite hard on my `pre` and `post` Hugo pipeline, I needed a way to test the actual content that will be pushed to the server.  Python (once again) to the rescue!<!--more-->

I *really* love Hugo's built-in server.  `hugo serve --watch` is truly a great time saver.  However, it has nothing to do with our pipeline (fingerprinting, compressing, etc).  If we want to see what the end result is going to look like, we need a way to serve that content.

Python has many built-in packages.  That's the main reason it's my language of choice.  Python has a simple web server ready to go.  I use `hugo serve --watch` when I'm creating my content.  When I want to check the output of my pipeline, I use the following on the command-line:

{{< highlight python >}}
cd <path to content> && python -m SimpleHTTPServer 8000
{{< /highlight >}}

`python -m SimpleHTTPServer 8000` tells Python to load the SimpleHTTPServer module and serve the content it finds in the current working directory on port 8000.  Technically, you are running `SimpleHTTPServer.__main__()`.

The great thing about this is that I can run both the Python server and the Hugo server at the same time, depending on what I need.

Here's the batch file I use for this:
{{< highlight batch >}}
@echo off
cd %~dp0..

echo %1|findstr /xr "p" >nul && (
  goto :python
) || (
  goto :hugo
)

:: =============================================================================
:: Run python on the already-built static pages.  This is for checking the end
:: result of the pipeline to ensure everything worked.
:python
pushd mtik00.github.io
start python -m SimpleHTTPServer 8000
popd
goto :end
:: =============================================================================

:: =============================================================================
:: Clean the Hugo build directory, then call Hugo to serve the content
:hugo
IF EXIST build (
    rmdir /q /s build
    sleep 1
)

start hugo server --watch --source="site" --bind="localhost"
goto :end
:: =============================================================================

:end
{{< /highlight >}}
