
<div align="center">

# 🎬 Aparat Playlist Downloader 🚀

[![Python](https://img.shields.io/badge/Python-3.6+-FF6B6B?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20|%20Linux%20|%20macOS-4ECDC4?style=for-the-badge)](https://github.com)
[![License](https://img.shields.io/badge/License-MIT-45B7D1?style=for-the-badge)](LICENSE)
[![Downloads](https://img.shields.io/badge/Downloads-10K+-96CEB4?style=for-the-badge)](https://github.com)

### 🔥 Professional Aparat Playlist Downloader with Dual Interface 🔥
*CLI & GUI - Built for Power Users*

![Demo GIF](https://via.placeholder.com/800x400/1a1a2e/ffffff?text=🎬+APARAT+DOWNLOADER+🚀)

</div>

---

## ✨ Features That Rock

<table>
<tr>
<td width="50%">

### 🎯 **Core Features**
- 🚀 **Lightning Fast** downloads
- 🎨 **Modern GUI** with PyQt5
- 💻 **Powerful CLI** interface
- 📱 **Multi-platform** support
- 🔧 **Quality Selection** (144p-1080p)

</td>
<td width="50%">

### 🌟 **Advanced Capabilities**
- 📋 **Batch Processing** playlists
- 📁 **Custom Output** paths
- 🔗 **Link Extraction** mode
- ⚡ **Concurrent Downloads**
- 🛡️ **Error Handling**

</td>
</tr>
</table>

---

## 🛠️ Prerequisites

<div align="center">

| Requirement | Version | Status |
|-------------|---------|--------|
| 🐍 Python | 3.6+ | ✅ Required |
| 📦 pip | Latest | ✅ Required |
| 🌐 Internet | Stable | ✅ Required |

</div>

---

## 🚀 Quick Start

### 🔥 One-Line Installation

```bash
git clone https://github.com/ali-0315/aparat_playlist_downloader.git && cd aparat_playlist_downloader && pip install -r requirements.txt
```

### 📦 Alternative Methods

<details>
<summary>🖥️ <strong>Full Installation (GUI + CLI)</strong></summary>

```bash
git clone https://github.com/ali-0315/aparat_playlist_downloader.git
cd aparat_playlist_downloader
pip install -r requirements.txt
```

</details>

<details>
<summary>⌨️ <strong>CLI Only Installation</strong></summary>

```bash
git clone https://github.com/ali-0315/aparat_playlist_downloader.git
cd aparat_playlist_downloader
pip install -r cli_requirements.txt
```

</details>

---

## 🎮 Usage Guide

### 🖼️ GUI Mode - The Visual Experience

```bash
python gui.py
```

<div align="center">

#### 🔥 **5-Step Process** 🔥

</div>

| Step | Action | Description |
|------|--------|-------------|
| 1️⃣ | **Select Operation** | Choose Download or Link Extraction |
| 2️⃣ | **Enter Playlist ID** | Support for ID (`822374`) or URL |
| 3️⃣ | **Pick Quality** | From 144p to 1080p |
| 4️⃣ | **Choose Destination** | Custom output folder |
| 5️⃣ | **Hit Execute** | Watch the magic happen! |

### ⌨️ CLI Mode - For Terminal Warriors

```bash
python cli.py
```

<div align="center">

**🎯 Interactive Experience**

</div>

```bash
🎬 Aparat Playlist Downloader CLI 🚀
=====================================

📺 Playlist ID: 822374
🎥 Quality (144|240|360|480|720|1080): 720
📋 Create link file? (y/n): n
📁 Destination (./Downloads): ./MyAwesomeVideos

⚡ Starting download...
✅ Download complete!
```

---

## 📁 Project Architecture

```
🎬 aparat_playlist_downloader/
├── 🧠 core.py                 # Brain of the operation
├── 🎨 gui.py                  # Beautiful PyQt5 interface
├── ⌨️  cli.py                  # Terminal interface
├── 📋 requirements.txt        # Full dependencies
├── 📋 cli_requirements.txt    # Minimal dependencies
└── 📖 README.md              # This awesome doc
```

### 🧩 Component Breakdown

<details>
<summary>🧠 <strong>core.py - The Engine</strong></summary>

```python
class AparatDownloader:
    def __init__(self, playlist_id, quality, for_download_manager, destination_path)
    def download_playlist()        # 🚀 Full playlist download
    def download_video()           # 📹 Single video download
    def get_video_download_urls()  # 🔗 Extract download links
```

</details>

---

## 🔌 API Integration

<div align="center">

### 🌐 **Aparat API Endpoints**

</div>

| Endpoint | Purpose | Response |
|----------|---------|----------|
| 📋 **Playlist Info** | `GET /api/fa/v1/video/playlist/one/playlist_id/{id}` | Playlist metadata |
| 🎥 **Video Links** | `GET /api/fa/v1/video/video/show/videohash/{uid}` | Download URLs |

<details>
<summary>📊 <strong>Sample API Response</strong></summary>

```json
{
  "data": {
    "attributes": {
      "title": "🎬 Awesome Playlist",
      "file_link_all": [
        {
          "profile": "720p",
          "urls": ["https://example.com/video.mp4"]
        }
      ]
    }
  },
  "included": [/* 🎥 Video collection */]
}
```

</details>

---

## 💻 Developer API

<div align="center">

### 🔥 **Code Like a Pro** 🔥

</div>

```python
from core import AparatDownloader

# 🚀 Initialize the beast
downloader = AparatDownloader(
    playlist_id="822374",
    quality="720",
    for_download_manager=False,  # True for link extraction
    destination_path="./Downloads"
)

# 🎬 Start the magic
try:
    downloader.download_playlist()
    print("🎉 Mission accomplished!")
except Exception as e:
    print(f"💥 Houston, we have a problem: {e}")
```

---

## 🤝 Contributing

<div align="center">

### 🌟 **Join the Revolution** 🌟

</div>

| Step | Command | Description |
|------|---------|-------------|
| 1️⃣ | `git fork` | Fork this awesome repo |
| 2️⃣ | `git checkout -b feature/epic-feature` | Create your feature branch |
| 3️⃣ | `git commit -m 'Add epic feature'` | Commit your changes |
| 4️⃣ | `git push origin feature/epic-feature` | Push to branch |
| 5️⃣ | Create **Pull Request** | Submit for review |

---

## 🏆 Hall of Fame

<div align="center">

### 🙏 **Legends Who Made This Possible** 🙏

<table>
<tr>
<td align="center">
<a href="https://github.com/AliAkbarSobhanpour">
<img src="https://github.com/AliAkbarSobhanpour.png" width="100px;" alt="علی اکبر سبحانپور"/>
<br />
<sub><b>🔥 علی اکبر سبحانپور</b></sub>
</a>
</td>
<td align="center">
<a href="https://github.com/AlirezaSakhtemanian">
<img src="https://github.com/AlirezaSakhtemanian.png" width="100px;" alt="علیرضا"/>
<br />
<sub><b>⚡ علیرضا ساختمانیان</b></sub>
</a>
</td>
<td align="center">
<a href="https://github.com/shayanghad0">
<img src="https://github.com/shayanghad0.png" width="100px;" alt="شایان"/>
<br />
<sub><b>🚀 شایان قدمیان</b></sub>
</a>
</td>
</tr>
</table>

</div>

---

<div align="center">

## 🎯 **Support the Project**

[![⭐ Star this repo](https://img.shields.io/badge/⭐-Star%20this%20repo-FFD700?style=for-the-badge)](https://github.com/ali-0315/aparat_playlist_downloader)
[![🐛 Report Bug](https://img.shields.io/badge/🐛-Report%20Bug-FF6B6B?style=for-the-badge)](https://github.com/ali-0315/aparat_playlist_downloader/issues)
[![💡 Request Feature](https://img.shields.io/badge/💡-Request%20Feature-4ECDC4?style=for-the-badge)](https://github.com/ali-0315/aparat_playlist_downloader/issues)

### 🚀 **Built with** ❤️ **and lots of** ☕

---

## 🏷️ **Tags**

`#aparat` `#downloader` `#playlist` `#python` `#pyqt5` `#gui` `#cli` `#video-downloader` `#iranian` `#opensource`

</div>

---

<div align="center">

**🎬 Ready to download like a pro? Let's go! 🚀**

*Made with 🔥 by the community, for the community*

</div>
