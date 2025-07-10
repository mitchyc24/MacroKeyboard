@echo off
REM Activate your virtual environment if needed
REM call .venv\Scripts\activate

REM Start rshell, then copy files interactively
rshell -p COM4
REM At the rshell prompt, run:
REM cp profiles/openfront.profile /pyboard/macro.profile
