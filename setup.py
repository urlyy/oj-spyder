import os
import subprocess
import sys

# 设置环境变量，不让驱动下到c盘
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(os.getcwd(), "driver")


# 安装环境
if __name__ == '__main__':

    #### 如果使用conda
    env_name = "oj-spyder"
    subprocess.run(f"conda activate {env_name}".split(" "))
    ####
    #### 如果使用venv
    # if sys.platform.startswith('win'):
    #     subprocess.run(os.path.join(os.getcwd(), "venv/Scripts/activate.bat"))
    # elif sys.platform.startswith('linux'):
    #     subprocess.run("source " + os.path.join(os.getcwd(), "venv/bin/activate"))
    # else:
    #     print("Unknown operating system")
    ###
    # 安装playwright的插件(因为是模拟浏览器环境)
    subprocess.run("pip install playwright".split(" "))
    subprocess.run("playwright install chromium".split(" "))
    subprocess.run("playwright install firefox".split(" "))
    subprocess.run("pip install requests".split(" "))
    subprocess.run("pip install bs4".split(" "))
    subprocess.run("pip install lxml".split(" "))
    
    # 安装验证码识别库
    subprocess.run("pip install ddddocr".split(" "))
    subprocess.run("pip uninstall -y Pillow".split(" "))
    subprocess.run("pip install Pillow==9.5.0".split(" "))
    
    subprocess.run('pip install cryptography'.split(' '))
    subprocess.run('pip install pyyaml'.split(' '))