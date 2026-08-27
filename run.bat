@echo off
setlocal
start "SIH26142 Backend" /min cmd /c ".venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"
pushd frontend
start "SIH26142 Frontend" /min cmd /c "npm run dev -- --host 127.0.0.1"
popd
echo Judge prototype starting at http://localhost:5173
