<p align="center">
<img src="https://github.com/wkaisertexas/tiktok-uploader/assets/27795014/f991fdc7-287a-4c3b-9a84-22c7ad8a57bf" alt="video working" />
</p>

<h1 align="center"> ⬆️ TikTok Uploader </h1>
<p align="center">A <strong>Playwright</strong>-based automated <strong>TikTok</strong> video uploader</p>

<p align="center">
  <img alt="Forks" src="https://img.shields.io/github/forks/wkaisertexas/tiktok-uploader" />
  <img alt="Stars" src="https://img.shields.io/github/stars/wkaisertexas/tiktok-uploader" />
  <img alt="Watchers" src="https://img.shields.io/github/watchers/wkaisertexas/tiktok-uploader" />
</p>

<h1>Table of Contents</h1>

- [Installation](#installation)
  - [MacOS, Windows and Linux](#macos-windows-and-linux)
    - [Downloading from PyPI (Recommended)](#pypi)
    - [Building from source](#building-from-source)
- [Usage](#usage)
  - [💻 Command Line Interface (CLI)](#cli)
  - [⬆ Uploading Videos](#uploading-videos)
  - [🫵 Mentions and Hashtags](#mentions-and-hashtags)
  - [🪡 Stitches, Duets and Comments](#stitches-duets-and-comments)
  - [🌐 Proxy](#proxy)
  - [📆 Schedule](#schedule)
  - [🎵 Sound / Music](#sound)
  - [🛍️ Product Link](#product-link)
  - [🔐 Authentication](#authentication)
  - [👤 Persistent Browser Profile](#persistent-profile)
  - [👀 Browser Selection](#browser-selection)
  - [🤯 Headless Browsers](#headless)
  - [🔨 Initial Setup](#initial-setup)
- [♻️ Examples](#examples)
- [📝 Notes](#notes)
- [Accounts made with](#made-with)

# Installation

A prerequisite to using this program is the installation of [Playwright](https://playwright.dev/) browsers.

<h2 id="macos-windows-and-linux">MacOS, Windows and Linux</h2>

Install Python 3 or greater from [python.org](https://www.python.org/downloads/)

<h3 id="pypi">Downloading from PyPI (Recommended)</h3>

Install `tiktok-uploader` using `pip`

```bash
pip install tiktok-uploader
playwright install
```

<h3 id="building-from-source">Building from source</h3>

Installing from source allows greater flexibility to modify the module's code to extend default behavior.

First, install [`uv`](https://docs.astral.sh/uv/getting-started/installation/) a really fast python package manager.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Next, clone the repository using `git`. Then change directories and run the project with `uv run tiktok-uploader`.

```bash
git clone https://github.com/wkaisertexas/tiktok-uploader
cd tiktok-uploader
uv sync
uv run playwright install
uv run tiktok-uploader
```

After `uv` installs the required packages, you should see something like the following:

```console
usage: tiktok-uploader [-h] -v VIDEO [-d DESCRIPTION] [-t SCHEDULE] [--proxy PROXY] [--product-id PRODUCT_ID]
                       [-c COOKIES] [-s SESSIONID] [-u USERNAME] [-p PASSWORD] [--attach]
```

<h1 id="usage">Usage</h1>

`tiktok-uploader` works by duplicating your browser's **cookies** which tricks **TikTok** into believing you are logged in on a remote-controlled browser.

<h2 id="cli"> 💻 Command Line Interface (CLI)</h2>

Using the CLI is as simple as calling `tiktok-uploader` with your videos: `path` (-v), `description`(-d), and `cookies` (-c).

```bash
tiktok-uploader -v video.mp4 -d "this is my escaped \"description\"" -c cookies.txt

# With background music
tiktok-uploader -v video.mp4 -d "my description" -c cookies.txt --sound-name "Min plan" --sound-artist "Jacub"
```

```python
from tiktok_uploader.upload import TikTokUploader

# single video
uploader = TikTokUploader(cookies='cookies.txt')
uploader.upload_video('video.mp4', description='this is my description')

# Multiple Videos
videos = [
    {
        'path': 'video.mp4',
        'description': 'this is my description'
    },
    {
        'path': 'video2.mp4',
        'description': 'this is also my description'
    }
]

uploader = TikTokUploader(cookies='cookies.txt')
uploader.upload_videos(videos=videos)
```

<h2 id="uploading-videos"> ⬆ Uploading Videos</h2>

This library revolves around the `TikTokUploader` class which has a `upload_videos` function which takes in a list of videos which have **filenames** and **descriptions** and are passed as follows:

```python
from tiktok_uploader.upload import TikTokUploader

videos = [
    {
        'video': 'video0.mp4',
        'description': 'Video 1 is about ...'
    },
    {
        'video': 'video1.mp4',
        'description': 'Video 2 is about ...'
    }
]

uploader = TikTokUploader(cookies='cookies.txt')
failed_videos = uploader.upload_videos(videos=videos)

for video in failed_videos:  # each input video object which failed
    print(f"{video['video']} with description {video['description']} failed")
```

<h2 id="mentions-and-hashtags"> 🫵 Mentions and Hashtags</h2>

Mentions and Hashtags now work so long as they are followed by a space. However, **you** as the user **are responsible** for verifying a mention or hashtag exists before posting

```python
from tiktok_uploader.upload import TikTokUploader

uploader = TikTokUploader(cookies='cookies.txt')
uploader.upload_video('video.mp4', description='#fyp @icespicee')
```

<h2 id="stitches-duets-and-comments"> 🪡 Stitches, Duets and Comments</h2>

To set whether or not a video uploaded allows stitches, comments or duet, simply specify `comment`, `stitch` and/or `duet` as keyword arguments to `upload_video` or `upload_videos`.

```python
uploader = TikTokUploader(cookies='cookies.txt')
uploader.upload_video(..., comment=True, stitch=True, duet=True)
```

> Comments, Stitches and Duets are allowed by **default**

<h2 id="proxy"> 🌐 Proxy</h2>

To set a proxy, currently only works with chrome as the browser, allow user:pass auth.

```python
# proxy = {'user': 'myuser', 'pass': 'mypass', 'host': '111.111.111', 'port': '99'}  # user:pass
proxy = {'host': '111.111.111', 'port': '99'}

uploader = TikTokUploader(cookies='cookies.txt', proxy=proxy)
uploader.upload_video(...)
```

<h2 id="schedule"> 📆 Schedule</h2>

The scheduled datetime must be at least **20 minutes** in the future, a maximum of **10 days** ahead, and the minutes must be a **multiple of 5** (e.g. 10:00, 10:05, 10:10).

**Single video (CLI):**

```bash
# Windows PowerShell
uv run tiktok-uploader -v video.mp4 -d "my description" -c cookies.txt -t "2026-03-25 10:00" --attach
```

**Batch videos with scheduled posting (CLI):**

```powershell
uv run tiktok-uploader-batch `
  -v video1.mp4 `
  -v video2.mp4 `
  -v video3.mp4 `
  -d "description 1" `
  -d "description 2" `
  -d "description 3" `
  --schedule-from "2026-03-25 10:00" `
  --schedule-interval 1440 `
  --timezone "Europe/Stockholm" `
  -c cookies.txt `
  --attach
```

| Parameter | Description | Default |
|---|---|---|
| `-v` | Video file path, repeat for each video | required |
| `-d` | Description for each video, in order | optional |
| `--sound-name` | Background music name per video (repeat to match `-v`, or pass once for all) | optional |
| `--sound-artist` | Background music artist per video | optional |
| `--schedule-from` | Publish time for the first video (`YYYY-MM-DD HH:MM`) | post immediately |
| `--schedule-interval` | Minutes between each video's publish time | `1440` (24 h) |
| `--timezone` | Timezone for `--schedule-from`, e.g. `Europe/Stockholm`, `Asia/Shanghai` | `Europe/Copenhagen` |
| `-c` | Path to cookies file | optional |
| `--attach` | Show browser window (useful for debugging) | headless by default |

> **Timezone format:** `--timezone` must use the `Region/City` format (e.g. `Europe/Stockholm`). Passing only a city name (e.g. `Stockholm`) will cause an error.

> **Batch interval only:** Batch upload supports evenly-spaced scheduling only. To set a different time for each video individually, use the Python API.

> **Failure behaviour:** If the schedule setting fails, the upload is aborted — it will **not** fall back to posting immediately.

**Python API:**

```python
import datetime
from tiktok_uploader.upload import TikTokUploader

schedule = datetime.datetime(2026, 3, 25, 10, 0)  # UTC time

uploader = TikTokUploader(cookies='cookies.txt')
uploader.upload_video('video.mp4', description='my description', schedule=schedule)
```

Batch with individual schedules:

```python
import datetime
from tiktok_uploader.upload import TikTokUploader

videos = [
    {'path': 'video1.mp4', 'description': 'first video', 'schedule': datetime.datetime(2026, 3, 25, 10, 0)},
    {'path': 'video2.mp4', 'description': 'second video', 'schedule': datetime.datetime(2026, 3, 26, 10, 0)},
    {'path': 'video3.mp4', 'description': 'third video', 'schedule': datetime.datetime(2026, 3, 27, 10, 0)},
]

uploader = TikTokUploader(cookies='cookies.txt')
uploader.upload_videos(videos=videos)
```

<h2 id="covers"> 🖼️ Covers</h2>

You can add a custom cover image when uploading a video. <br>
TikTok supports ".png", ".jpeg" and ".jpg".

```python
my_cover = "crazy_cover.jpg"

uploader = TikTokUploader(cookies='cookies.txt')
uploader.upload_video(..., cover=my_cover)
```

<h2 id="sound"> 🎵 Sound / Music</h2>

You can add background music from TikTok's sound library when uploading a video.

Provide `sound_name` to search and select a matching track. Optionally provide `sound_artist` to filter results more precisely.

**Matching logic:**
- Traverses all search results and picks the first one whose title matches `sound_name` (case-insensitive)
- If `sound_artist` is provided, also checks that the artist name contains the given string
- If no match is found, falls back to the first result with a warning

> **Important:** Use the exact song title and artist name as they appear in TikTok's Sounds panel. The spelling must be exact (case-insensitive), otherwise the uploader falls back to the first search result.

> **Limitation:** TikTok only loads approximately 10–20 results per search. If your target song ranks outside this initial batch, it will not appear in the list and the uploader will fall back to the first result. For best results, use well-known tracks or include the artist name to help TikTok surface the correct song.

> **Batch upload note:** Passing `--sound-name` once applies the same song to all videos. To assign different music to each video, repeat `--sound-name` (and optionally `--sound-artist`) once per video in order. If the count does not match `-v`, extra videos will have no music added.

**CLI:**

```bash
tiktok-uploader -v video.mp4 -d "my description" -c cookies.txt --sound-name "Min plan" --sound-artist "Jacub"
```

**Batch — same song for all videos:**

```powershell
uv run tiktok-uploader-batch `
  -v video1.mp4 -v video2.mp4 -v video3.mp4 `
  --sound-name "Min plan" --sound-artist "Jacub" `
  -c cookies.txt --attach
```

**Batch — different song per video:**

```powershell
uv run tiktok-uploader-batch `
  -v video1.mp4 -v video2.mp4 -v video3.mp4 `
  --sound-name "Song A" --sound-name "Song B" --sound-name "Song C" `
  --sound-artist "Artist A" --sound-artist "Artist B" --sound-artist "Artist C" `
  -c cookies.txt --attach
```

**Python API:**

```python
from tiktok_uploader.upload import TikTokUploader

uploader = TikTokUploader(cookies='cookies.txt')

# Match by song title only
uploader.upload_video('video.mp4', description='...', sound_name='Min plan')

# Match by both title and artist (recommended for accuracy)
uploader.upload_video('video.mp4', description='...', sound_name='Min plan', sound_artist='Jacub')
```

When using `upload_videos`, add `sound_name` and `sound_artist` to each video dictionary:

```python
videos = [
    {
        'path': 'video.mp4',
        'description': 'My video',
        'sound_name': 'Min plan',
        'sound_artist': 'Jacub'
    }
]

uploader.upload_videos(videos=videos)
```

<h2 id="product-link"> 🛍️ Product Link</h2>

You can automatically add a product link to your uploaded video.

**Prerequisites:**

*   Your TikTok account must be eligible to add showcase products to your videos.
*   You need to obtain the product ID beforehand. To do this:
    1. Go to the TikTok upload page in your browser.
    2. Click the "Add link" button and select "Product".
    3. A modal will appear showing your available showcase products along with their IDs.
    4. Copy the ID of the product you want to link.

**Usage:**

Provide the `product_id` when calling the uploader.

**Command Line:**

```bash
tiktok-uploader -v video.mp4 -d "this is my description" -c cookies.txt --product-id YOUR_PRODUCT_ID
```

**Python:**

```python
from tiktok_uploader.upload import TikTokUploader

uploader = TikTokUploader(cookies='cookies.txt')

# Single video
uploader.upload_video('video.mp4',
            description='this is my description',
            product_id='YOUR_PRODUCT_ID')

# Multiple videos
videos = [
    {
        'path': 'video.mp4',
        'description': 'this is my description',
        'product_id': 'YOUR_PRODUCT_ID_1' # Add product link to this video
    },
    {
        'path': 'video2.mp4',
        'description': 'this is also my description' # No product link for this video
    }
]

uploader.upload_videos(videos=videos)
```

<h2 id="authentication"> 🔐 Authentication</h2>

Authentication uses your browser's cookies. This workaround was done due to TikTok's stricter stance on authentication by a Playwright-controlled browser.

> **Managing multiple accounts or avoiding cookie expiry?** See [👤 Persistent Browser Profile](#persistent-profile) to bootstrap a long-lived browser profile from your cookies file — no cookie refresh needed afterwards.

Your `sessionid` is all that is required for authentication and can be passed as an argument to nearly any function

[🍪 Get cookies.txt](https://github.com/kairi003/Get-cookies.txt-LOCALLY) makes getting cookies in a [NetScape cookies format](http://fileformats.archiveteam.org/wiki/Netscape_cookies.txt).

After installing, open the extensions menu on [TikTok.com](https://tiktok.com/) and click `🍪 Get cookies.txt` to reveal your cookies. Select `Export As ⇩` and specify a location and name to save.

**Alternatively**, if you don't want to use an extension, you can use the following JavaScript line in the Developer Console (F12) on TikTok.com:

1. Copy the code below:
```javascript
(function(){const c=document.cookie.split("; ").map(x=>{const i=x.indexOf("=");return ".tiktok.com\tTRUE\t/\tFALSE\t2147483647\t"+x.substring(0,i)+"\t"+x.substring(i+1)}).join("\n");const b=new Blob([c],{type:"text/plain"});const a=document.createElement("a");a.href=URL.createObjectURL(b);a.download="cookies.txt";a.textContent="Download cookies.txt";a.style="position:fixed;top:20px;right:20px;z-index:9999;padding:10px;background:#fe2c55;color:white;border-radius:5px;text-decoration:none;font-weight:bold;font-family:sans-serif;";document.body.appendChild(a);if(!document.cookie.includes("sessionid"))alert("⚠️ sessionid is missing (HttpOnly). You must add it manually!");})();
```
2. Paste it into the console and press Enter.
3. A "Download cookies.txt" button will appear in the top-right corner. Click it to download your cookies file.
4. If alerted about the missing `sessionid`, follow the manual steps below.

> **⚠️ Important:** Browsers often hide the `sessionid` cookie from JavaScript (HttpOnly). If the script alerts you about this:
> 1. Go to **Application** > **Cookies** in DevTools.
> 2. Find `sessionid` and copy its value.
> 3. Manually add it to your downloaded `cookies.txt`: `.tiktok.com	TRUE	/	FALSE	2147483647	sessionid	YOUR_SESSION_ID`

```python
uploader = TikTokUploader(cookies='cookies.txt')
uploader.upload_video(...)
```

**Optionally**, `cookies_list` is a list of dictionaries with keys `name`, `value`, `domain`, `path` and `expiry` which allow you to pass your own browser cookies.

```python
cookies_list = [
    {
        'name': 'sessionid',
        'value': '**your session id**',
        'domain': 'https://tiktok.com',
        'path': '/',
        'expiry': '10/8/2023, 12:18:58 PM'
    },
    # the rest of your cookies all in a list
]

uploader = TikTokUploader(cookies_list=cookies_list)
uploader.upload_video(...)
```

<h2 id="persistent-profile"> 👤 Persistent Browser Profile</h2>

Instead of injecting cookies on every run, you can store a full browser profile on disk. TikTok then sees a consistent device identity across sessions, which keeps the session alive longer and removes the need to refresh cookies.

**Step 1 — Bootstrap the profile once from your existing cookies file:**

```bash
tiktok-profile-from-cookies --profile profiles/account_001 --cookies cookies.txt
```

This injects the cookies into a fresh Playwright profile, navigates to TikTok to activate the session, and saves everything to `profiles/account_001/`. You only need to do this once per account.

**Step 2 — Upload using the profile (no cookies file needed):**

```bash
tiktok-uploader -v video.mp4 -d "my description" --profile profiles/account_001
```

```bash
# Batch upload
tiktok-uploader-batch -v video1.mp4 -v video2.mp4 --profile profiles/account_001
```

**Python API:**

```python
from tiktok_uploader.upload import TikTokUploader

uploader = TikTokUploader(profile_dir='profiles/account_001')
uploader.upload_video('video.mp4', description='my description')
```

**Multi-account setup (100 accounts example):**

```bash
# Bootstrap each account once
tiktok-profile-from-cookies --profile profiles/account_001 --cookies account_001_cookies.txt
tiktok-profile-from-cookies --profile profiles/account_002 --cookies account_002_cookies.txt
# ...

# Then upload per account without any cookies file
tiktok-uploader -v video.mp4 --profile profiles/account_001
tiktok-uploader -v video.mp4 --profile profiles/account_002
```

> **Note:** `--profile` is mutually exclusive with `--cookies`, `--sessionid`, and `--username`/`--password`.

> **Session expiry detection:** On each run the uploader navigates to TikTok and checks whether the session is still valid. If TikTok redirects to the login or explore page the run fails immediately with a clear error:
> ```
> RuntimeError: Profile at 'profiles/account_001' session has expired (redirected to https://www.tiktok.com/login/...).
> Run 'tiktok-profile-setup' to log in again.
> ```
> When you see this, re-run `tiktok-profile-from-cookies` (or `tiktok-profile-setup`) for the affected profile.

> **Disk space:** Each profile directory is approximately 10–50 MB. Back up your `profiles/` folder — if it is lost you will need to re-run `tiktok-profile-from-cookies`.

> **Concurrency:** The same profile directory cannot be opened by two browser instances simultaneously. For parallel uploads, use a separate profile per account.

<h2 id="browser-selection"> 👀 Browser Selection</h2>

[Google Chrome](https://www.google.com/chrome) is the preferred browser for **TikTokUploader**. The default anti-detection techniques used in this packaged are optimized for this. However, if you wish to use a different browser you may specify the `browser` in `TikTokUploader`.

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

# randomly picks a web browser
uploader = TikTokUploader(cookies='cookies.txt', browser=choice(BROWSERS))
uploader.upload_video(...)
```

✅ Supported Browsers:

- **Chrome** (Recommended)
- **Safari**
- **Chromium**
- **Edge**
- **FireFox**

<h2 id="headless"> 🤯 Headless Browsers </h2>

When using Chrome, adding the `--headless` flag using the CLI or passing `headless` as a keyword argument to `TikTokUploader` is all that is required.

```python
uploader = TikTokUploader(cookies='cookies.txt', headless=True)
uploader.upload_video(...)
```

<h2 id="initial-setup"> 🔨 Initial Setup</h2>

You must install Playwright browsers:

```bash
playwright install
```

<h2 id="examples"> ♻ Examples</h2>

- **[Basic Upload Example](examples/basic_upload.py):** Uses `upload_video` to make one post.

- **[Multiple Videos At Once](examples/multiple_videos_at_once.py):** Uploads the same video multiple times using `upload_videos`.

- **[Series Upload Example](examples/series_upload.py):** Videos are read from a CSV file using [Pandas](https://pandas.pydata.org). A video upload attempt is made and **if and only if** it is successful will the video be marked as uploaded.

<h2 id="notes"> 📝 Notes</h2>

This bot is **not fool proof**. Though I have not gotten an official ban, the video will fail to upload after too many uploads. In testing, waiting several hours was sufficient to fix this problem. For this reason, please think of this more as a scheduled uploader for TikTok videos, rather than a **spam bot.**

> [!IMPORTANT]
> If you like this project, please ⭐ it on GitHub to show your support! ❤️

![Star History Chart](https://api.star-history.com/svg?repos=wkaisertexas/tiktok-uploader&type=Date)
