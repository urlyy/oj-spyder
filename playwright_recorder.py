import os
import subprocess

# 设置环境变量，不让驱动下到c盘
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(os.getcwd(), "driver")
#### 如果使用conda
env_name = "oj-spyder"
subprocess.run(f"conda activate {env_name}".split(" "))

def start_record(url):
    output_file = "playwright_script.py"
    subprocess.run(f"playwright codegen -o {output_file} --target=python -b firefox {url}".split(" "))


if __name__ == "__main__":
    start_record("https://leetcode.cn/accounts/login/?next=%2F")
