import os
import click
from pathlib import Path
from tools import storageFormat

class WeChatScanner:
    def __init__(self):
        self.wechat_path = os.path.expanduser("~/Library/Containers/com.tencent.xinWeChat/Data")
        self.cache_files = {}
        self.file_types = {}
        
    def scan_cache(self):
        if not os.path.exists(self.wechat_path):
            click.echo("WeChat directory not found!")
            return
            
        for root, _, files in os.walk(self.wechat_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(file_path)
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    # 统计文件类型
                    self.file_types[file_ext] = self.file_types.get(file_ext, 0) + 1
                    
                    # 记录大文件(>10MB)
                    if file_size > 10 * 1024 * 1024:
                        self.cache_files[file_path] = file_size
                        
                except (OSError, IOError):
                    continue
                    
    def print_statistics(self):
        click.echo("\n=== WeChat Cache Statistics ===")
        
        # 打印文件类型统计
        click.echo("\nFile Types:")
        for ext, count in sorted(self.file_types.items(), key=lambda x: x[1], reverse=True):
            click.echo(f"{ext}: {count} files")
            
        # 打印最大的文件
        click.echo("\nLargest Files:")
        sorted_files = sorted(self.cache_files.items(), key=lambda x: x[1], reverse=True)
        for path, size in sorted_files[:10]:
            click.echo(f"{path}: {storageFormat(size)}")
            
    def clean_cache(self):
        if not self.cache_files:
            click.echo("No large cache files found!")
            return
            
        total_size = sum(self.cache_files.values())
        click.echo(f"\nTotal cleanable cache: {storageFormat(total_size)}")
        
        if click.confirm("Do you want to clean these cache files?"):
            for file_path in self.cache_files:
                try:
                    os.remove(file_path)
                    click.echo(f"Removed: {file_path}")
                except OSError as e:
                    click.echo(f"Error removing {file_path}: {e}") 