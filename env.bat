:: =============================================================================
:: This batch file is used to set up the Go development environment for this
:: project
@echo off

if "%__HUGOENV__%"=="1" (
    echo environment already set
    goto end
)

set _THISDIR=%~dp0
set GOPATH=%_THISDIR:~0,-1%
set PATH=%PATH%;%GOPATH%\bin

echo Go environment set for %GOPATH%

set __HUGOENV__=1

:end
