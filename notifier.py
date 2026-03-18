# notifier.py
import platform
import subprocess
import requests
import json
import time
from config import WECHAT_WEBHOOK


def play_sound():
    """
    根据不同的操作系统播放系统提示音
    """
    sys_plat = platform.system()

    try:
        if sys_plat == "Windows":
            import winsound
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)

        elif sys_plat == "Darwin":  # macOS
            subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"], check=False)

        elif sys_plat == "Linux":
            subprocess.run(["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"], check=False)
    except Exception as e:
        print(f"播放音效失败: {e}")


def send_system_notification(message_text):
    """
    发送跨平台系统桌面弹窗通知
    """
    sys_plat = platform.system()
    try:
        if sys_plat == "Darwin":
            apple_script = f'display notification "{message_text}" with title "网站更新通知"'
            subprocess.run(["osascript", "-e", apple_script], check=False)
        else:
            from plyer import notification
            notification.notify(
                title="网站更新通知",
                message=message_text,
                app_name="网站监听助手",
                timeout=10
            )
    except Exception as e:
        print(f"发送系统通知失败: {e}")


def send_wechat_bot(site_name, url):
    """
    发送企业微信群机器人通知
    """
    if not WECHAT_WEBHOOK:
        print("未配置企业微信机器人 Webhook 地址，已跳过企微通知。")
        return

    headers = {"Content-Type": "application/json"}

    # 构建 Markdown 格式的消息内容
    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": f"**网站更新通知**\n> 网站名称：<font color=\"info\">{site_name}</font>\n> 网站链接：[点击访问]({url})\n> 状态：内容刚刚发生了更新，请及时查看！"
        }
    }

    try:
        response = requests.post(WECHAT_WEBHOOK, headers=headers, data=json.dumps(data), timeout=10)
        response.raise_for_status()
        result = response.json()
        if result.get("errcode") != 0:
            print(f"企业微信机器人发送失败: {result.get('errmsg')}")
        else:
            print("企业微信机器人消息发送成功！")
    except Exception as e:
        print(f"企业微信机器人网络请求失败: {e}")


def send_alert(site_name, url, notify_modes):
    """
    统一的通知分发中心，根据配置的策略触发通知
    notify_modes: 通知方式列表，例如 [1, 2, 3]
    """
    # 如果包含0，则不进行任何通知
    if 0 in notify_modes:
        return

    message_text = f"{site_name}有更新"

    # 在控制台打印输出
    print(f"\n==============================")
    print(f"[!!! 通知 !!!] {message_text}")
    print(f"==============================\n")

    # 根据用户配置触发具体的通知方式
    if 1 in notify_modes:
        play_sound()

    if 2 in notify_modes:
        send_system_notification(message_text)

    if 3 in notify_modes:
        send_wechat_bot(site_name, url)


# ==========================================
# 独立测试模块 (仅在直接运行此文件时执行)
# ==========================================
if __name__ == "__main__":
    print("=== 通知功能独立测试模块已启动 ===")
    print("1. 测试系统提示音效")
    print("2. 测试系统桌面通知")
    print("3. 测试企业微信机器人")
    print("4. 测试音效+通知+企微")
    print("0. 退出测试")
    print("==============================")

    while True:
        try:
            choice = input("\n请输入要测试的功能编号 (0-4): ").strip()

            if choice == "0":
                print("退出测试模块。")
                break

            elif choice == "1":
                print("正在测试系统提示音效...")
                play_sound()
                print("音效触发指令已执行完毕，请检查是否听到声音。")

            elif choice == "2":
                print("正在测试桌面弹窗通知...")
                send_system_notification("这是一条来自网站监听助手的测试弹窗。")
                print("桌面弹窗指令已发送，请检查是否收到来自系统的通知。")

            elif choice == "3":
                if not WECHAT_WEBHOOK:
                    print("警告: config.py 中未配置 WECHAT_WEBHOOK。")
                    print("请先去 config.py 中填入 Webhook 地址后再测。")
                else:
                    print("正在测试企业微信机器人...")
                    send_wechat_bot("自动化测试网站", "https://www.baidu.com")

            elif choice == "4":
                print("正在进行音效+通知+企微组合测试...")
                send_alert("组合测试", "https://www.baidu.com", [1, 2, 3])
                print("组合测试全部执行完毕。")

            else:
                print("无效输入。")

            time.sleep(1)  # 稍作停顿，防止刷屏太快

        except KeyboardInterrupt:
            print("\n用户手动中断，退出测试。")
            break