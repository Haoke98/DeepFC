from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from wechat_scanner import WeChatScanner
import os
import subprocess

app = FastAPI()

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scanner = WeChatScanner()

@app.get("/scan")
async def scan_files(min_size: int = 10):
    scanner.scan_message_files(min_size_mb=min_size)
    return {
        "accounts": scanner.accounts,
        "total_size": sum(account["total_size"] for account in scanner.accounts.values()),
        "total_files": len(scanner.large_files)
    }

@app.get("/files")
async def get_files(sort_by: str = "size", group_by: str = None):
    files = scanner.large_files
    
    if group_by == "account":
        return scanner.accounts
    elif group_by == "type":
        files_by_type = {}
        for file in files:
            files_by_type.setdefault(file['type'], []).append(file)
        return files_by_type
    
    return sorted(files, key=lambda x: x[sort_by], reverse=True)

@app.post("/file/action/{action}")
async def file_action(action: str, file_path: str):
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    if action == "preview":
        subprocess.run(["open", file_path])
    elif action == "reveal":
        subprocess.run(["open", "-R", file_path])
    elif action == "delete":
        os.remove(file_path)
    
    return {"status": "success"} 