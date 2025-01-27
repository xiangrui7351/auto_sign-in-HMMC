import re
import os
import time
import requests
import tkinter as tk
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from tkinter import simpledialog
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By

# 自定义对话框类
class CustomDialog(simpledialog.Dialog):
    def body(self, master):
        self.geometry("400x200")  # 设置对话框大小
        self.title("输入账号和密码")

        tk.Label(master, text="请输入账号：").grid(row=0)
        tk.Label(master, text="请输入密码：").grid(row=1)

        self.e1 = tk.Entry(master)
        self.e2 = tk.Entry(master, show="*")

        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        return self.e1  # initial focus

    def apply(self):
        self.result = (self.e1.get(), self.e2.get())


# 初始化Tkinter窗口
root = tk.Tk()
root.title("运行状态")
root.geometry("400x200")
root.withdraw()  # 隐藏主窗口

status_label = tk.Label(root, text="初始化...", wraplength=300)
status_label.pack(pady=20)


def update_status(message):
    status_label.config(text=message)
    root.update()


# WebDriver路径
script_dir = os.path.dirname(os.path.abspath(__file__))
webdriver_path = os.path.join(script_dir, 'WebDriver', 'msedgedriver.exe')
# Construct account save file path
account_file = os.path.join(script_dir, 'Account_save.txt')
# Initialize account and password
Account = None
Password = None

update_status("检查账户保存文件...")
# If the account save file exists, read the account and password
if os.path.exists(account_file):
    with open(account_file, 'r') as file:
        lines = file.readlines()
        if len(lines) >= 2:
            Account = lines[0].strip()
            Password = lines[1].strip()

# If account and password are not set, prompt user to input and save to file
if not Account or not Password:
    root.deiconify()  # 显示主窗口

    dialog = CustomDialog(root)
    Account, Password = dialog.result

    # Save account and password to file
    with open(account_file, 'w') as file:
        file.write(f"{Account}\n{Password}")

root.deiconify()  # Show the main window again
update_status("读取签到日志...")
filename = 'diary.txt'  # 执行日志
if not os.path.exists(filename):
    with open(filename, 'w') as file:
        file.write("2025-01-25    已完成签到")  # 可以在这里写入初始内容
with open(filename, 'r') as f:  # 打开文件
    lines = f.readlines()  # 读取所有行
    first_line = lines[0]  # 取第一行
    last_line = lines[-1]  # 取最后一行
if len(lines) > 50:
    with open(filename, 'w') as f:
        f.write(last_line)
# Adjust regex pattern to match the new date format
pattern = r'(\d{4})-(\d{1,2})-(\d{1,2})'
match = re.search(pattern, last_line)
# Initialize year, month, and day with default values
year = None
month = None
day = None
if match:
    year = match.group(1)
    month = match.group(2)
    day = match.group(3)

url = "https://www.beijing-time.org/t/time.asp"

# 创建一个session
session = requests.Session()

# 设置重试策略
retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
session.mount('http://', HTTPAdapter(max_retries=retries))
session.mount('https://', HTTPAdapter(max_retries=retries))
# 添加请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
# 发送请求
response = session.get(url, headers=headers)
# 检查响应状态
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    # 提取文字内容
    text_content = soup.get_text()
    # 使用正则表达式筛选出年份、月份和日期
    match_year = re.search(r"nyear=(\d+);", text_content)
    match_month = re.search(r"nmonth=(\d+);", text_content)
    match_day = re.search(r"nday=(\d+);", text_content)

    if match_year and match_month and match_day:
        nyear = match_year.group(1)
        nmonth = match_month.group(1)
        nday = match_day.group(1)
        nmonth = nmonth.zfill(2)
        nday = nday.zfill(2)
if year == nyear and month == nmonth and day == nday:
    update_status("你已签到了，不需要进行任何操作。")
    time.sleep(5)
else:
    update_status("打开浏览器并访问网页...")
    #打开浏览器并访问网页
    try:
        # 设置Edge浏览器的驱动
        service = Service(executable_path=webdriver_path)
        driver = webdriver.Edge(service=service)
        url = "https://www.yunmc.vip/login"  # 访问指定的网页
        driver.get(url)
        update_status("访问登录页面...")
        time.sleep(5)
        # 使用XPath查找元素并输入值
        email_input = driver.find_element(By.XPATH, '//*[@id="emailInp"]')
        email_input.send_keys(Account)
        password_input = driver.find_element(By.XPATH, '//*[@id="emailPwdInp"]')
        password_input.send_keys(Password)
        update_status("输入账号和密码...")
        time.sleep(5)
        # 使用XPath查找按钮并点击
        login_button = driver.find_element(By.XPATH, '//*[@id="yangmduiloginemail"]/form/div[3]/div/button')
        login_button.click()
        update_status("点击登录按钮...")
        login_button = driver.find_element(By.XPATH, '//*[@id="left-drawer1"]/ul/li[16]/a')
        login_button.click()
        login_button = driver.find_element(By.XPATH, '//*[@id="QIANDAO"]/div[1]/div[1]/div/div[5]/div[4]/div/button')
        login_button.click()
        update_status("完成签到...")
        # 等待几秒钟以便查看结果
        time.sleep(5)
        new_content = nyear + "-" + nmonth + "-" + nday + "    已完成签到"
        with open(filename, 'a') as file:
            file.write("\n" + new_content)
        update_status("签到成功，已保存到相关日志。")
    finally:
        # 关闭浏览器
        driver.quit()
        update_status("浏览器已关闭。")

