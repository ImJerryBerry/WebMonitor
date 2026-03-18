# notifier.py
import platform
import subprocess


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


def send_alert(site_name):
    """
    发送系统桌面通知并播放声音
    """
    message_text = f"{site_name}有更新"
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

    # 在控制台打印醒目的提醒
    print(f"\n==============================")
    print(f"[!!! 通知 !!!] {message_text}")
    print(f"==============================\n")

    # 触发音效
    play_sound()