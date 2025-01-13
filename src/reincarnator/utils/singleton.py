from threading import Lock

# From Microsoft Copilot.
def Singleton(cls):
    instances = {}
    lock = Lock()

    def wrapper(*args, **kwargs):
        if cls not in instances:
            with lock:
                if cls not in instances:  # 双重检查锁定
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper