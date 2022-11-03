def sum(l:list[dict],key=""):
    res = 0
    for i in l:
        res+=i[key]
    return res

def storageFormat(v):
    """
    存储大小标准打印工具
    :param v: 存储大小的值（注：转换成Byte字节时的数值）,永远只接受正数和零。
    :return: 可打印的字符串形式
    """
    if v<0:
        raise Exception("该方法不接受负数")
    a = v/1024
    if a < 1:
        return f"{v}B"
    elif a>1 and a<1024:
        return f"{a}KB"
    else:
        b = a/1024
        if b>1 and b<1024:
            return f"{b}MB"
        elif b >1024:
            c = b/1024
            if c>1 and c< 1024:
                return f"{c}GB"
            elif c> 1024:
                d = c/1024
                return f"{d}TB"