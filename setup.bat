@echo off
setlocal
.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
pushd frontend
call npm install --cache .npm-cache
popd
echo Setup complete. Run run.bat
