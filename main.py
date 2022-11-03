import os
import sys
import hashlib
from concurrent.futures import ThreadPoolExecutor,as_completed
from multiprocessing import Process, Pool

from tools import storageFormat

fileModels = {}
file_ext_list = []
fileExtModels = {}
TOTOAL = 0
FINISHED = 0


def handle(special_file,root,):
    # 如果指定前缀或者后缀
    tmpl = special_file.split(".")
    filename = tmpl[0]
    ext = tmpl[-1]
    # print(special_file, ext)
    if fileExtModels.keys().__contains__(ext):
        fileExtModels[ext] += 1
    else:
        fileExtModels.setdefault(ext, 0)
    absPath = os.path.join(root, special_file)
    with open(absPath, 'rb') as f:
        data = f.read()
    statinfo = os.stat(absPath)
    fMD5 = hashlib.md5(data).hexdigest()
    model = {
        "name": filename,
        "path": absPath,
        "ext": ext,
        "size": statinfo.st_size
    }
    if fileModels.keys().__contains__(fMD5):
        # errMsg = f"找到一样的文件:MD5:{fMD5}"+ \
        #          "\n            "+absPath+\
        #          "\n            "+fileModels[fMD5]["path"]
        # raise Exception(errMsg)
        fileModels[fMD5].append(model)
    else:
        fileModels.setdefault(fMD5, [model])


#         if postfix or prefix:
#             # 同时指定前缀和后缀
#             if postfix and prefix:
#                 if special_file.endswith(postfix) and special_file.startswith(prefix):
#                     file_list.append(os.path.join(root, special_file))
#                     continue
#
#             # 只指定后缀
#             elif postfix:
#                 if special_file.endswith(postfix):
#                     file_list.append(os.path.join(root, special_file))
#                     continue
#
#             # 只指定前缀
#             elif prefix:
#                 if special_file.startswith(prefix):
#                     file_list.append(os.path.join(root, special_file))
#                     continue
#
#         # 前缀后缀均未指定
#         else:
#             file_list.append(os.path.join(root, special_file))
#             continue
def ScanFile(directory):
    global fileModels,fileExtModels,TOTOAL,FINISHED
    pool = ThreadPoolExecutor(max_workers=10)
    futs = []
    for root, sub_dirs, files in os.walk(directory):
        print(root)
        for special_file in files:
            TOTOAL+=1
            print(TOTOAL,"|----------------------------------",special_file)
            if special_file in [".DS_Store"]:
                continue
            th = pool.submit(handle,special_file,root)
            futs.append(th)
    # # print(file_list)	# 打印出扫描到的文件路径
    # return file_list
    as_completed(futs)

    file_ext_list = sorted(fileExtModels.keys(),key=lambda item:len(item),reverse=True)
    print(f"Sum of Ext is {len(file_ext_list)}:")
    colNum = 10
    for r in range(0,len(file_ext_list),colNum):
        linetxt = "  ".join([f"({x},{fileExtModels[x]})" for x in file_ext_list[r: min(r+colNum,len(file_ext_list))]])
        print(linetxt)
    total=0
    md5s = sorted(fileModels.keys(), key=lambda item:fileModels[item][0]["size"]*len(fileModels[item]), reverse=True)
    clearableSpace = 0
    for md in md5s:
        fs = fileModels[md]
        count = len(fs)
        if count>1:
            total+=1
            _clearableSpace = fs[0]["size"]*(len(fs)-1)
            clearableSpace += _clearableSpace
            print(total,md,count,storageFormat(fs[0]["size"]),storageFormat(_clearableSpace),":")
            for f in fs:
                print("|-------------------",f["path"])
    print(f"There is {storageFormat(clearableSpace)} of space in you devices that can be clean.")

if __name__ == "__main__":
    # rootPath = input("请输入要扫描的路径：")
    rootPath = "J:\\SADAM"
    print(f"开始扫描[{rootPath}]......")
    ScanFile(rootPath)
