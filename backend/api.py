from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from wechat_scanner import WeChatScanner
import os
import subprocess
from pydantic import BaseModel
import shutil
import psutil

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

class FileAction(BaseModel):
    file_path: str
    base_path: str = ""

def get_base_path(path_type: str) -> str:
    base_paths = {
        'wechat': '~/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat',
        'photos': '~/Pictures',
        'yarn': '~/Library/Caches/Yarn',
        'jetbrains': '~/Library/Caches/JetBrains',
        'lark': '~/Library/Caches/LarkShell',
        'pip': '~/Library/Caches/pip',
        'google': '~/Library/Caches/Google'
    }
    return os.path.expanduser(base_paths.get(path_type, ''))

@app.get("/scan")
async def scan_files(min_size: int = 10, path: str = "wechat"):
    # 清空之���的扫描结果
    scanner.clear_scan_results()
    
    if path == "wechat":
        scanner.scan_message_files(min_size_mb=min_size)
    elif path == "photos":
        scanner.scan_photos_library(min_size_mb=min_size)
    elif path == "custom" and os.path.exists(path):
        scanner.scan_directory(path, min_size_mb=min_size)
    else:
        raise HTTPException(status_code=400, detail="Invalid path")
        
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
async def file_action(action: str, file_data: FileAction):
    # 使用文件的原始完整路径
    full_path = file_data.file_path
    
    if not os.path.exists(full_path):
        # ���试从 scanner 中获取完整路径
        for file in scanner.large_files:
            if file['relative_path'] == file_data.file_path:
                full_path = file['path']
                break
    
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail=f"File not found: {full_path}")
        
    if action == "preview":
        subprocess.run(["open", full_path])
    elif action == "reveal":
        subprocess.run(["open", "-R", full_path])
    elif action == "delete":
        os.remove(full_path)
        # 从 scanner 的文件列表中移除已删除的文件
        scanner.large_files = [f for f in scanner.large_files if f['path'] != full_path]
    
    return {"status": "success"}

@app.get("/disk-usage")
async def get_disk_usage():
    total, used, free = shutil.disk_usage("/")
    return {
        "total": total,
        "used": used,
        "free": free,
        "usage_percent": (used / total) * 100
    }

@app.get("/monitor")
async def get_system_monitor():
    # 磁盘使用情况
    disk = psutil.disk_usage("/")
    
    # 内存使用情况
    mem = psutil.virtual_memory()
    
    # 交换内存使用情况
    swap = psutil.swap_memory()
    
    return {
        "disk": {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        },
        "memory": {
            "total": mem.total,
            "used": mem.used,
            "free": mem.available,
            "percent": mem.percent
        },
        "swap": {
            "total": swap.total,
            "used": swap.used,
            "free": swap.free,
            "percent": swap.percent
        }
    } 