@ECHO off

set "script_path=%~dp0"
set "script_path=%script_path%worker"

celery -A app.celery worker
PAUSE