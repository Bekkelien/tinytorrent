@echo off

for /f "delims== tokens=1" %%G in ('pip list --format=freeze ^| findstr /v "^\-e"') do (
    echo Upgrading package: %%G
    pip install --upgrade %%G
)
