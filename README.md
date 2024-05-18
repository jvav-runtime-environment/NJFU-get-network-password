# 暴力破解校园网密码

> [!CAUTION]
> 免责声明: 本程序仅用于技术交流，使用本程序前请仔细考虑，使用本程序所造成的任何后果由使用者自行承担!

## 原理
* 对校园网服务器发送包含用户名和密码的请求，可以通过对响应里`success`的值来判断用户名和密码是否正确

## 目录说明
`username.txt`为储存用户名的文件

`password.txt`为密码字典

`result.json`为结果和执行进度的储存文件，结构:
```json
{
    "current_username": 0,  //记录目前正在破解的用户名(索引)
    "current_password": 0,  //记录目前正在破解的密码(索引)
    "<username>": "<password>",  //记录结果
    ...
}
```

## 使用方法
* 先根据需要生成密码字典(如果不全会爆不出来)和用户名文件(不用在开头加w)，分别置于`password.txt`和`username.txt`内
* 设置`password.py`内的`MAXTHREADNUM`，用来控制最大线程数量，默认为1 (不要设置太大，会影响服务器)
* 运行`password.py`，等待结果