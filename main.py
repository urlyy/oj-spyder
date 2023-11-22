import os
# 设置环境变量，不让驱动下到c盘
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(os.getcwd(), "driver")


if __name__ == '__main__':
    pass