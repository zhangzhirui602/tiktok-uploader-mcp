<p align="center">
<img src="https://github.com/wkaisertexas/tiktok-uploader/assets/27795014/f991fdc7-287a-4c3b-9a84-22c7ad8a57bf" alt="video working" />
</p>

<h1 align="center"> ⬆️ TikTok 自动上传工具 </h1>
<p align="center">基于 <strong>Playwright</strong> 的 <strong>TikTok</strong> 视频自动上传工具</p>

<p align="center">
  <img alt="Forks" src="https://img.shields.io/github/forks/wkaisertexas/tiktok-uploader" />
  <img alt="Stars" src="https://img.shields.io/github/stars/wkaisertexas/tiktok-uploader" />
  <img alt="Watchers" src="https://img.shields.io/github/watchers/wkaisertexas/tiktok-uploader" />
</p>

<h1>目录</h1>

- [安装](#installation)
  - [MacOS、Windows 和 Linux](#macos-windows-and-linux)
    - [从 PyPI 安装（推荐）](#pypi)
    - [从源码构建](#building-from-source)
- [使用方法](#usage)
  - [💻 命令行界面（CLI）](#cli)
  - [⬆ 上传视频](#uploading-videos)
  - [🫵 提及与话题标签](#mentions-and-hashtags)
  - [🪡 缝合、合拍与评论](#stitches-duets-and-comments)
  - [🌐 代理](#proxy)
  - [📆 定时发布](#schedule)
  - [🖼️ 封面图](#covers)
  - [🎵 背景音乐](#sound)
  - [🛍️ 商品链接](#product-link)
  - [🔐 身份认证](#authentication)
  - [👀 浏览器选择](#browser-selection)
  - [🤯 无头浏览器](#headless)
  - [🔨 初始配置](#initial-setup)
- [♻️ 示例](#examples)
- [📝 注意事项](#notes)

<h1 id="installation">安装</h1>

使用本工具前，需要先安装 [Playwright](https://playwright.dev/) 浏览器。

<h2 id="macos-windows-and-linux">MacOS、Windows 和 Linux</h2>

从 [python.org](https://www.python.org/downloads/) 安装 Python 3 或更高版本。

<h3 id="pypi">从 PyPI 安装（推荐）</h3>

使用 `pip` 安装 `tiktok-uploader`：

```bash
pip install tiktok-uploader
playwright install
```

<h3 id="building-from-source">从源码构建</h3>

从源码安装可以更灵活地修改代码以扩展默认行为。

首先安装 [`uv`](https://docs.astral.sh/uv/getting-started/installation/)，一个高速 Python 包管理器：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

然后克隆仓库，进入目录并运行：

```bash
git clone https://github.com/wkaisertexas/tiktok-uploader
cd tiktok-uploader
uv sync
uv run playwright install
uv run tiktok-uploader
```

安装完成后，你会看到类似如下的输出：

```console
usage: tiktok-uploader [-h] -v VIDEO [-d DESCRIPTION] [-t SCHEDULE] [--proxy PROXY] [--product-id PRODUCT_ID]
                       [-c COOKIES] [-s SESSIONID] [-u USERNAME] [-p PASSWORD] [--attach]
```

<h1 id="usage">使用方法</h1>

`tiktok-uploader` 通过复制你浏览器的 **cookies** 来欺骗 **TikTok**，使其认为你在一个远程控制的浏览器上已登录。

<h2 id="cli"> 💻 命令行界面（CLI）</h2>

只需指定视频路径（`-v`）、描述（`-d`）和 cookies 文件（`-c`）即可使用：

```bash
tiktok-uploader -v video.mp4 -d "这是我的视频描述" -c cookies.txt

# 添加背景音乐
tiktok-uploader -v video.mp4 -d "这是我的视频描述" -c cookies.txt --sound-name "Min plan" --sound-artist "Jacub"
```

```python
from tiktok_uploader.upload import TikTokUploader

# 上传单个视频
uploader = TikTokUploader(cookies='cookies.txt')
uploader.upload_video('video.mp4', description='这是我的描述')

# 批量上传多个视频
videos = [
    {
        'path': 'video.mp4',
        'description': '这是第一个视频的描述'
    },
    {
        'path': 'video2.mp4',
        'description': '这是第二个视频的描述'
    }
]

uploader = TikTokUploader(cookies='cookies.txt')
uploader.upload_videos(videos=videos)
```

<h2 id="uploading-videos"> ⬆ 上传视频</h2>

本库的核心是 `TikTokUploader` 类，其 `upload_videos` 函数接受一个包含**文件名**和**描述**的视频列表：

```python
from tiktok_uploader.upload import TikTokUploader

videos = [
    {
        'video': 'video0.mp4',
        'description': '视频1的内容是...'
    },
    {
        'video': 'video1.mp4',
        'description': '视频2的内容是...'
    }
]

uploader = TikTokUploader(cookies='cookies.txt')
failed_videos = uploader.upload_videos(videos=videos)

for video in failed_videos:  # 打印每个上传失败的视频
    print(f"{video['video']} 上传失败，描述为：{video['description']}")
```

<h2 id="mentions-and-hashtags"> 🫵 提及与话题标签</h2>

提及（@）和话题标签（#）现在可以正常使用，但需要在其后跟一个空格。**请确认**提及的用户或话题标签真实存在再发布。

```python
from tiktok_uploader.upload import TikTokUploader

uploader = TikTokUploader(cookies='cookies.txt')
uploader.upload_video('video.mp4', description='#fyp @icespicee')
```

<h2 id="stitches-duets-and-comments"> 🪡 缝合、合拍与评论</h2>

通过向 `upload_video` 或 `upload_videos` 传入 `comment`、`stitch` 和/或 `duet` 关键字参数，可以控制视频是否允许评论、缝合和合拍：

```python
uploader = TikTokUploader(cookies='cookies.txt')
uploader.upload_video(..., comment=True, stitch=True, duet=True)
```

> 评论、缝合和合拍**默认全部开启**

<h2 id="proxy"> 🌐 代理</h2>

设置代理（目前仅支持 Chrome 浏览器），支持用户名/密码认证：

```python
# proxy = {'user': 'myuser', 'pass': 'mypass', 'host': '111.111.111', 'port': '99'}  # 带认证
proxy = {'host': '111.111.111', 'port': '99'}

uploader = TikTokUploader(cookies='cookies.txt', proxy=proxy)
uploader.upload_video(...)
```

<h2 id="schedule"> 📆 定时发布</h2>

定时发布使用 UTC 时区。发布时间必须至少在当前时间 **20 分钟后**，最多提前 **10 天**，且分钟数必须是 **5 的倍数**（如 10:00、10:05、10:10）。

**单个视频定时发布（CLI）：**

```bash
# Windows PowerShell
uv run tiktok-uploader -v video.mp4 -d "视频描述" -c cookies.txt -t "2026-03-25 10:00" --attach
```

**批量视频定时发布（CLI）：**

```powershell
# Windows PowerShell（用反引号 ` 换行）
uv run tiktok-uploader-batch `
  -v video1.mp4 `
  -v video2.mp4 `
  -v video3.mp4 `
  -d "第一个视频描述" `
  -d "第二个视频描述" `
  -d "第三个视频描述" `
  --schedule-from "2026-03-25 10:00" `
  --schedule-interval 1440 `
  --timezone "Europe/Stockholm" `
  -c cookies.txt `
  --attach
```

**批量视频 + 定时发布 + 背景音乐（每个视频不同音乐）：**

```powershell
uv run tiktok-uploader-batch `
  -v video1.mp4 -v video2.mp4 -v video3.mp4 `
  -d "描述1" -d "描述2" -d "描述3" `
  --sound-name "歌曲A" --sound-name "歌曲B" --sound-name "歌曲C" `
  --sound-artist "歌手A" --sound-artist "歌手B" --sound-artist "歌手C" `
  --schedule-from "2026-03-25 10:00" --schedule-interval 1440 `
  --timezone "Europe/Stockholm" -c cookies.txt --attach
```

**所有视频使用同一首音乐（只传一次）：**

```powershell
uv run tiktok-uploader-batch `
  -v video1.mp4 -v video2.mp4 -v video3.mp4 `
  -d "描述1" -d "描述2" -d "描述3" `
  --sound-name "Min plan" --sound-artist "Jacub" `
  --schedule-from "2026-03-25 10:00" --schedule-interval 1440 `
  --timezone "Europe/Stockholm" -c cookies.txt --attach
```

| 参数 | 说明 | 默认值 |
|---|---|---|
| `-v` | 视频文件路径，每个视频重复一次 | 必填 |
| `-d` | 视频描述，顺序对应 `-v` | 可选 |
| `--sound-name` | 背景音乐歌名，重复传入对应每个视频，传一次则所有视频共用 | 可选 |
| `--sound-artist` | 背景音乐歌手，同上 | 可选 |
| `--schedule-from` | 第一个视频的发布时间（`YYYY-MM-DD HH:MM`）| 不填则立即发布 |
| `--schedule-interval` | 每个视频之间的间隔分钟数 | `1440`（24小时）|
| `--timezone` | `--schedule-from` 所用时区，格式如 `Europe/Stockholm`、`Asia/Shanghai` | `Europe/Copenhagen` |
| `-c` | cookies 文件路径 | 可选 |
| `--attach` | 显示浏览器窗口（调试用） | 默认无头模式 |

**Python API：**

```python
import datetime
from tiktok_uploader.upload import TikTokUploader

schedule = datetime.datetime(2026, 3, 25, 10, 0)  # UTC 时间

uploader = TikTokUploader(cookies='cookies.txt')
uploader.upload_video('video.mp4', description='视频描述', schedule=schedule)
```

批量定时发布：

```python
import datetime
from tiktok_uploader.upload import TikTokUploader

videos = [
    {'path': 'video1.mp4', 'description': '第一个视频', 'schedule': datetime.datetime(2026, 3, 25, 10, 0)},
    {'path': 'video2.mp4', 'description': '第二个视频', 'schedule': datetime.datetime(2026, 3, 26, 10, 0)},
    {'path': 'video3.mp4', 'description': '第三个视频', 'schedule': datetime.datetime(2026, 3, 27, 10, 0)},
]

uploader = TikTokUploader(cookies='cookies.txt')
uploader.upload_videos(videos=videos)
```

<h2 id="covers"> 🖼️ 封面图</h2>

上传视频时可以指定自定义封面图，支持 `.png`、`.jpeg` 和 `.jpg` 格式：

```python
my_cover = "my_cover.jpg"

uploader = TikTokUploader(cookies='cookies.txt')
uploader.upload_video(..., cover=my_cover)
```

<h2 id="sound"> 🎵 背景音乐</h2>

上传视频时可以从 TikTok 音乐库中添加背景音乐。

通过 `sound_name` 搜索并匹配目标歌曲，可选填 `sound_artist` 进行更精确的过滤。

**匹配逻辑：**
- 遍历所有搜索结果，找到第一条歌名与 `sound_name` 完全匹配（不区分大小写）的结果
- 如果提供了 `sound_artist`，还会检查歌手名是否包含该字符串
- 如果没有找到匹配结果，会自动选择第一条并打印警告

> **重要：** 请使用 TikTok Sounds 面板中显示的**准确歌名和歌手名**，以确保匹配正确。

> **局限性：** TikTok 每次搜索只加载约 10–20 条结果。如果目标歌曲排在这批结果之外，则不会出现在列表中，上传工具会自动 fallback 到第一条。建议使用知名度较高的歌曲，或同时提供歌手名以帮助 TikTok 更准确地返回目标歌曲。

**CLI 单视频：**

```bash
tiktok-uploader -v video.mp4 -d "描述" -c cookies.txt --sound-name "Min plan" --sound-artist "Jacub"
```

**Python API：**

```python
from tiktok_uploader.upload import TikTokUploader

uploader = TikTokUploader(cookies='cookies.txt')

# 仅按歌名匹配
uploader.upload_video('video.mp4', description='...', sound_name='Min plan')

# 同时指定歌手名（推荐，更精确）
uploader.upload_video('video.mp4', description='...', sound_name='Min plan', sound_artist='Jacub')
```

批量上传时，在每个视频字典中加入 `sound_name` 和 `sound_artist`：

```python
videos = [
    {
        'path': 'video.mp4',
        'description': '我的视频',
        'sound_name': 'Min plan',
        'sound_artist': 'Jacub'
    }
]

uploader.upload_videos(videos=videos)
```

<h2 id="product-link"> 🛍️ 商品链接</h2>

上传视频时可以自动添加商品链接。

**前提条件：**

- 你的 TikTok 账号需要具备添加橱窗商品的资格
- 需要提前获取商品 ID：
    1. 在浏览器中打开 TikTok 上传页面
    2. 点击"添加链接"按钮并选择"商品"
    3. 弹出的对话框中会显示你的橱窗商品及其 ID
    4. 复制你想要链接的商品 ID

**命令行：**

```bash
tiktok-uploader -v video.mp4 -d "这是我的描述" -c cookies.txt --product-id 你的商品ID
```

**Python：**

```python
from tiktok_uploader.upload import TikTokUploader

uploader = TikTokUploader(cookies='cookies.txt')

# 单个视频
uploader.upload_video('video.mp4',
            description='这是我的描述',
            product_id='你的商品ID')

# 多个视频
videos = [
    {
        'path': 'video.mp4',
        'description': '这是我的描述',
        'product_id': '商品ID_1'
    },
    {
        'path': 'video2.mp4',
        'description': '这也是我的描述'  # 该视频不添加商品链接
    }
]

uploader.upload_videos(videos=videos)
```

<h2 id="authentication"> 🔐 身份认证</h2>

身份认证通过浏览器 cookies 实现。这是由于 TikTok 对 Playwright 控制的浏览器登录有更严格的限制而采用的变通方案。

认证只需要你的 `sessionid`，可以作为参数传入几乎所有函数。

[🍪 Get cookies.txt](https://github.com/kairi003/Get-cookies.txt-LOCALLY) 插件可以帮助你以 [NetScape cookies 格式](http://fileformats.archiveteam.org/wiki/Netscape_cookies.txt) 导出 cookies。

安装后，在 [TikTok.com](https://tiktok.com/) 上打开扩展菜单，点击 `🍪 Get cookies.txt`，然后选择 `Export As ⇩` 保存文件。

**或者**，不想使用插件的话，可以在 TikTok.com 的开发者控制台（F12）中执行以下 JavaScript：

1. 复制以下代码：
```javascript
(function(){const c=document.cookie.split("; ").map(x=>{const i=x.indexOf("=");return ".tiktok.com\tTRUE\t/\tFALSE\t2147483647\t"+x.substring(0,i)+"\t"+x.substring(i+1)}).join("\n");const b=new Blob([c],{type:"text/plain"});const a=document.createElement("a");a.href=URL.createObjectURL(b);a.download="cookies.txt";a.textContent="Download cookies.txt";a.style="position:fixed;top:20px;right:20px;z-index:9999;padding:10px;background:#fe2c55;color:white;border-radius:5px;text-decoration:none;font-weight:bold;font-family:sans-serif;";document.body.appendChild(a);if(!document.cookie.includes("sessionid"))alert("⚠️ sessionid is missing (HttpOnly). You must add it manually!");})();
```
2. 粘贴到控制台并按 Enter
3. 页面右上角会出现"Download cookies.txt"按钮，点击下载
4. 如果提示 `sessionid` 缺失，请按以下步骤手动添加

> **⚠️ 重要：** 浏览器通常会对 JavaScript 隐藏 `sessionid` cookie（HttpOnly）。如果脚本提示缺失：
> 1. 打开 DevTools → **Application** → **Cookies**
> 2. 找到 `sessionid` 并复制其值
> 3. 手动添加到 `cookies.txt`：`.tiktok.com	TRUE	/	FALSE	2147483647	sessionid	你的SESSION_ID`

```python
uploader = TikTokUploader(cookies='cookies.txt')
uploader.upload_video(...)
```

也可以使用 `cookies_list`，传入包含 `name`、`value`、`domain`、`path` 和 `expiry` 键的字典列表：

```python
cookies_list = [
    {
        'name': 'sessionid',
        'value': '你的 session id',
        'domain': 'https://tiktok.com',
        'path': '/',
        'expiry': '10/8/2023, 12:18:58 PM'
    },
    # 其余 cookies
]

uploader = TikTokUploader(cookies_list=cookies_list)
uploader.upload_video(...)
```

<h2 id="browser-selection"> 👀 浏览器选择</h2>

**Google Chrome** 是 TikTokUploader 的首选浏览器，内置的反检测措施针对 Chrome 进行了优化。如需使用其他浏览器，可在 `TikTokUploader` 中指定 `browser` 参数：

```python
from tiktok_uploader.upload import TikTokUploader
from random import choice

BROWSERS = [
    'chrome',
    'safari',
    'chromium',
    'edge',
    'firefox'
]

# 随机选择一个浏览器
uploader = TikTokUploader(cookies='cookies.txt', browser=choice(BROWSERS))
uploader.upload_video(...)
```

✅ 支持的浏览器：

- **Chrome**（推荐）
- **Safari**
- **Chromium**
- **Edge**
- **FireFox**

<h2 id="headless"> 🤯 无头浏览器</h2>

使用 Chrome 时，通过 CLI 添加 `--headless` 标志，或向 `TikTokUploader` 传入 `headless=True` 即可启用无头模式：

```python
uploader = TikTokUploader(cookies='cookies.txt', headless=True)
uploader.upload_video(...)
```

<h2 id="initial-setup"> 🔨 初始配置</h2>

必须先安装 Playwright 浏览器：

```bash
playwright install
```

<h2 id="examples"> ♻ 示例</h2>

- **[基础上传示例](examples/basic_upload.py)：** 使用 `upload_video` 发布单个视频
- **[批量上传示例](examples/multiple_videos_at_once.py)：** 使用 `upload_videos` 多次上传同一视频
- **[系列上传示例](examples/series_upload.py)：** 从 CSV 文件读取视频列表，成功上传后标记为已完成

<h2 id="notes"> 📝 注意事项</h2>

本工具**并非万无一失**。虽然目前没有收到官方封禁，但上传次数过多后视频可能上传失败。测试发现，等待数小时后即可恢复正常。因此，请将本工具视为 TikTok 视频的**定时发布工具**，而非**刷量机器人**。

> [!IMPORTANT]
> 如果你喜欢这个项目，请在 GitHub 上给它点个 ⭐ 支持一下！❤️
