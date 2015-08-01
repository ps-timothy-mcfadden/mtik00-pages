@echo off
cd %~dp0..

IF EXIST build (
    rmdir /q /s build
    sleep 1
)

start hugo server --watch --source="site" --bind="localhost"
