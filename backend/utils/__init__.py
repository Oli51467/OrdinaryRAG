import random
import time


def hashstr(input_string, length=8, with_salt=False):
    # 添加时间戳作为干扰
    import hashlib
    if with_salt:
        input_string += str(time.time() + random.random())

    hash = hashlib.md5(str(input_string).encode()).hexdigest()
    return hash[:length]