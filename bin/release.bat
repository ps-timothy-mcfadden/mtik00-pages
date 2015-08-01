:: =============================================================================
:: Build the release files, commits any needed changes, and pushes the changes'
:: to the remote repository
call %~dp0make-release.bat
git add -A .
git commit -m"releasing"
git push

pushd %~dp0..\mtik00.github.io
git add -A .
git commit -m"releasing"
git push