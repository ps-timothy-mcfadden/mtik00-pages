pushd %~dp0..\site

:: We don't want to remove the public_html directory, or else all of the files
:: will have suspected changes and cause them all to be downloaded again during
:: the `git pull` on the web server.  Still not sure the best way to ensure a
:: "clean" public_html folder.
:: rmdir /q /s ..\public_html
:: sleep 1
python ..\bin\make-search-index.py && git add ..\site\static\js\lunr.index.json
hugo -d="..\mtik00.github.io"
popd
