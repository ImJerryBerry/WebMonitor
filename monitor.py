# monitor.py
import os
import re
import time
import threading
import requests
import hashlib
from datetime import datetime
from bs4 import BeautifulSoup

from config import HEADERS
from notifier import send_alert


class SiteMonitor(threading.Thread):
    def __init__(self, site_config):
        super().__init__()
        self.site_name = site_config.get("name")
        self.url = site_config.get("url")
        self.interval = site_config.get("interval", 60)
        self.save_modes = site_config.get("save_mode", 0)
        self.notify_modes = site_config.get("notify_modes", 0)

        self.last_hash = None
        self.last_saved_filepath = None
        self.daemon = True
        self.safe_site_name = re.sub(r'[\\/:*?"<>|]', '_', self.site_name)

        self.capture_dir = os.path.join(os.getcwd(), 'captures')
        os.makedirs(self.capture_dir, exist_ok=True)

        # 使用 Session 保持长连接和 Cookie
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def load_local_history(self):
        """
        启动时读取 captures 文件夹中的历史记录。
        设置为当前检测基准，并根据 save_mode 自动清理多余的旧文件。
        """
        if not os.path.exists(self.capture_dir):
            return

        files = os.listdir(self.capture_dir)
        # 筛选属于当前网站的html文件
        prefix = self.safe_site_name + "_"
        site_files = [f for f in files if f.startswith(prefix) and f.endswith(".html")]

        if not site_files:
            return

        # 时间戳格式保证了字母序就是时间排序，最后一个即为最新文件
        site_files.sort()
        latest_file = site_files[-1]
        latest_filepath = os.path.join(self.capture_dir, latest_file)

        # 读取最新文件并计算哈希作为初始基准
        try:
            with open(latest_filepath, 'r', encoding='utf-8') as f:
                raw_html = f.read()
            soup = BeautifulSoup(raw_html, 'html.parser')
            text_content = soup.get_text(strip=True)
            self.last_hash = hashlib.md5(text_content.encode('utf-8')).hexdigest()
            self.last_saved_filepath = latest_filepath
            print(f"[{self.site_name}] 已加载本地最新记录作为基准: {latest_file}")
        except Exception as e:
            print(f"[{self.site_name}] 读取本地历史记录失败: {e}")
            return

        # 模式1，只保留一份。如果本地有多份历史文件，启动时自动清理旧文件
        if self.save_modes == 1 and len(site_files) > 1:
            for old_file in site_files[:-1]:
                old_filepath = os.path.join(self.capture_dir, old_file)
                try:
                    os.remove(old_filepath)
                    print(f"[{self.site_name}] [模式1] 自动清理历史冗余文件: {old_file}")
                except Exception as e:
                    print(f"[{self.site_name}] 清理历史冗余文件失败: {e}")

    def fetch_content(self):
        """
        获取网页内容，返回 (文本的MD5哈希值, 原始HTML源码)
        """
        try:
            response = self.session.get(self.url, timeout=15)
            response.raise_for_status()

            response.encoding = response.apparent_encoding
            raw_html = response.text

            soup = BeautifulSoup(raw_html, 'html.parser')
            text_content = soup.get_text(strip=True)

            content_hash = hashlib.md5(text_content.encode('utf-8')).hexdigest()
            return content_hash, raw_html

        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 403:
                print(f"[{self.site_name}] 报错 403: 被目标网站的反爬虫机制拦截。")
            else:
                print(f"[{self.site_name}] HTTP 错误: {e}")
            return None, None
        except requests.RequestException as e:
            print(f"[{self.site_name}] 网络请求失败: {e}")
            return None, None

    def save_html(self, raw_html):
        """
        根据配置保存网页HTML到 captures 目录中
        """
        if self.save_modes == 0:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.safe_site_name}_{timestamp}.html"
        filepath = os.path.join(self.capture_dir, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(raw_html)
            print(f"[{self.site_name}] 网页变动已保存至: {filepath}")
        except Exception as e:
            print(f"[{self.site_name}] 保存HTML文件失败: {e}")
            return

        # 模式1时，如果存在上一次保存的文件，删除它
        if self.save_modes == 1 and self.last_saved_filepath and os.path.exists(self.last_saved_filepath):
            if self.last_saved_filepath != filepath:  # 防止同秒内重复调用删掉刚创建的文件
                try:
                    os.remove(self.last_saved_filepath)
                except Exception as e:
                    print(f"[{self.site_name}] 删除旧HTML文件失败: {e}")

        self.last_saved_filepath = filepath

    def run(self):
        """
        线程主循环
        """
        print(
            f"开始监听: {self.site_name} (URL: {self.url}, 间隔: {self.interval}秒, 保存模式: {self.save_modes}, 通知策略: {self.notify_modes})")

        # 首先尝试加载本地历史记录
        self.load_local_history()

        while True:
            current_hash, raw_html = self.fetch_content()

            if current_hash is None:
                # 抓取失败，静默等待下个周期
                time.sleep(self.interval)
                continue

            if self.last_hash is None:
                # 如果本地无历史记录，且首次抓取成功，将其设为初始基准
                self.last_hash = current_hash
                self.save_html(raw_html)
                print(f"[{self.site_name}] 首次获取最新网页内容，已设为基准。")

            elif current_hash != self.last_hash:
                # 网页哈希变动：发现更新！

                # 将网址也传给分发中心，方便企业微信发送 Markdown 超链接
                send_alert(self.site_name, self.url, self.notify_modes)
                self.save_html(raw_html)
                self.last_hash = current_hash

            else:
                # 内容未变动，打印包含当前时间的日志说明
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{current_time}] [{self.site_name}] 没有更新。")

            # 等待设定的间隔时间后进行下一次检查
            time.sleep(self.interval)