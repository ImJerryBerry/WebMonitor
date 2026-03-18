# main.py
import time
from config import WEBSITES
from monitor import SiteMonitor


def main():
    print("=== 网站状态多线程监听系统已启动 ===")

    # 检查 config.py 中是否配置了网站
    if not WEBSITES:
        print("未在 config.py 中配置任何网站！")
        return

    monitors = []

    # 遍历配置，为每个网站创建一个独立的监听线程
    for site_config in WEBSITES:
        monitor_thread = SiteMonitor(site_config)
        monitors.append(monitor_thread)
        monitor_thread.start()

    try:
        # 守护主线程，确保监听始终进行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n=== 监视器被用户手动停止 ===")


if __name__ == "__main__":
    main()