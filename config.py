# config.py

# 在这里配置企业微信机器人的Webhook地址，留空则表示不使用企业微信机器人
WECHAT_WEBHOOK = ""

# 在这里配置想要监听的网站列表
WEBSITES = [
    {
        "name": "百度",                   # 自定义网站名称
        "url": "https://www.baidu.com/", # 目标网页链接
        "interval": 60,                  # 刷新间隔（秒），默认60秒
        "save_mode": 1,                  # 网页快照保存模式（详见README说明）
        "notify_modes": [1, 2, 3]        # 通知模式（详见README说明）
    }
]

# 全局默认请求头，防止被目标网站的反爬虫机制拦截
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"'
}