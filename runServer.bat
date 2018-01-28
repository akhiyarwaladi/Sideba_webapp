@ECHO off

set "script_path=%~dp0"
set "script_path=%script_path%server.py"

python %script_path% %*