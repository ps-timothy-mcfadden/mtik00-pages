:: =============================================================================
:: Pulls any new files from both the dev project and pages.
:: =============================================================================
pushd %~dp0..
pushd mtik00.github.io
git pull
popd
git pull
popd