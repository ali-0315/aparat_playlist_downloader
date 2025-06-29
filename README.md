# Aparat Playlist Downloader

![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20|%20Linux%20|%20macOS-lightgrey.svg)

دانلودر حرفه‌ای پلی‌لیست‌های آپارات با دو رابط کاربری CLI و GUI


## 🔧 پیش‌نیازها

- Python 3.6 یا بالاتر
- pip (Python package manager)
- اتصال به اینترنت

## 📦 نصب

### نصب سریع

```bash
git clone https://github.com/ali-0315/aparat_playlist_downloader.git
cd aparat_playlist_downloader
pip install -r requirements.txt
# یا اگر میخواهید فقط از cli استفاده کنید
pip install -r cli_requirements
```

## 🚀 نحوه استفاده

### رابط گرافیکی (GUI)

رابط گرافیکی مدرن و کاربرپسند با قابلیت‌های پیشرفته:

```bash
python gui.py
```

**مراحل استفاده:**
1. **انتخاب عملیات**: دانلود یا استخراج لینک
2. **وارد کردن شناسه**: یکی از فرمت‌های زیر:
   - شناسه عددی: `822374`
   - لینک کامل: `https://www.aparat.com/playlist/822374`
3. **انتخاب کیفیت**: 144, 240, 360, 480, 720, 1080
4. **انتخاب مسیر خروجی**: با کلیک روی "انتخاب"
5. **کلیک روی "اجرا"**

### خط فرمان (CLI)

برای استفاده ساده و سریع:

```bash
python cli.py
```

**نمونه اجرا:**
```
Give me a Aparat playlist id: 822374
Give me the quality: (Examples: 144 , 240 , 360 , 480 , 720 , 1080) :720
Type "y" if you want to create a .txt file that contain all the videos link otherwise type "n" to start download now:n
Give me the destination path (default: ./Downloads):./MyDownloads
```

## 📁 ساختار پروژه

```
aparat_playlist_downloader/
├── core.py                 # کلاس اصلی AparatDownloader
├── gui.py                  # رابط گرافیکی PyQt5
├── cli.py                  # رابط خط فرمان
├── requirements.txt        # وابستگی‌های کامل پروژه
├── cli_requirements.txt    # وابستگی‌های CLI فقط
└── README.md              # مستندات پروژه
```

### توضیحات فایل‌ها

#### `core.py` - هسته اصلی
```python
class AparatDownloader:
    def __init__(self, playlist_id, quality, for_download_manager, destination_path)
    def download_playlist()        # دانلود کامل پلی‌لیست
    def download_video()           # دانلود تک ویدئو
    def get_video_download_urls()  # دریافت لینک‌های دانلود
```

## 🔌 API آپارات

پروژه از API های زیر آپارات استفاده می‌کند:

```
# دریافت اطلاعات پلی‌لیست
GET https://www.aparat.com/api/fa/v1/video/playlist/one/playlist_id/{playlist_id}

# دریافت لینک‌های دانلود ویدئو
GET https://www.aparat.com/api/fa/v1/video/video/show/videohash/{video_uid}
```

**پاسخ نمونه API:**
```json
{
  "data": {
    "attributes": {
      "title": "نام پلی‌لیست",
      "file_link_all": [
        {
          "profile": "720p",
          "urls": ["https://example.com/video.mp4"]
        }
      ]
    }
  },
  "included": [/* ویدئوهای پلی‌لیست */]
}
```

## 🔄 نمونه استفاده برنامه‌نویسی

```python
from core import AparatDownloader

# ایجاد instance
downloader = AparatDownloader(
    playlist_id="822374",
    quality="720",
    for_download_manager=False,  # True برای txt فایل
    destination_path="./Downloads"
)

# شروع دانلود
try:
    downloader.download_playlist()
    print("دانلود با موفقیت انجام شد!")
except Exception as e:
    print(f"خطا: {e}")
```

## 🤝 مشارکت

### مراحل مشارکت

1. **Fork** کردن پروژه
2. ایجاد **branch** جدید:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit** تغییرات:
   ```bash
   git commit -m 'Add some amazing feature'
   ```
4. **Push** به branch:
   ```bash
   git push origin feature/amazing-feature
   ```
5. ایجاد **Pull Request**

## 🙏 تشکر و قدردانی
<div align="center">
  <h3>با تشکر ویژه از عزیزان</h3>
  <table>
    <tr>
      <td align="center">
        <a href="https://github.com/AliAkbarSobhanpour">
          <img src="https://github.com/AliAkbarSobhanpour.png" width="100px;" alt="علی اکبر سبحانپور"/>
          <br />
          <sub><b>علی اکبر سبحانپور</b></sub>
        </a>
      </td>
      <td align="center">
        <a href="https://github.com/AlirezaSakhtemanian">
          <img src="https://github.com/AlirezaSakhtemanian.png" width="100px;" alt="علیرضا"/>
          <br />
          <sub><b>علیرضا</b></sub>
        </a>
      </td>
    </tr>
  </table>
</div>

---

<div align="center">

**⭐ اگر این پروژه مفید بود، ستاره بدهید!**

`نوشته شده با ❤️ `

</div>

## 🏷️ تگ‌ها

`aparat` `downloader` `playlist` `python` `pyqt5` `gui` `cli` `video-downloader`