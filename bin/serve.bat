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
