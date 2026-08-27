@echo off
.venv\Scripts\python.exe --version
node --version
npm --version
.venv\Scripts\python.exe -c "import fastapi, PIL, numpy; print('Backend dependencies available')"
