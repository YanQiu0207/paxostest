
import logging

if "g_Logger" not in globals():
    g_Logger = None

def InitLogger():
    global g_Logger

    if g_Logger:
        return

    # 创建一个 Formatter 对象
    formatter = logging.Formatter('%(asctime)s %(process)d %(thread)d %(filename)s:%(lineno)d %(levelname)s - %(message)s')

    # 创建一个 FileHandler 对象，并将 Formatter 对象添加到该 Handler 中
    file_handler = logging.FileHandler('log/paxos.log')
    file_handler.setFormatter(formatter)

    # 创建一个 StreamHandler 对象，并将 Formatter 对象添加到该 Handler 中
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # 创建一个 Logger 对象，将 FileHandler 和 StreamHandler 添加到该 Logger 中
    g_Logger = logging.getLogger()
    g_Logger.addHandler(file_handler)
    g_Logger.addHandler(stream_handler)
    g_Logger.setLevel(logging.DEBUG)

def GetLogger():
    global g_Logger
    return g_Logger

