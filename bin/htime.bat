:: =============================================================================
:: This batch file prints out the current local time suitable for front-matter
:: `date` in Hugo content.
:: =============================================================================
@echo off
python -c "import time; print time.strftime('%%Y-%%m-%%dT%%H:%%M:%%S', time.localtime()) + '%%+03i:00' %% (-1*(time.altzone / 3600) if time.daylight else (-1*(time.timezone/3600)));"
