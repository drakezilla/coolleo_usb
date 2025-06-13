import datetime

def logger(type, message: str):
    print(f"[{datetime.datetime.now()}][{type.upper()}]: {message}")