<div align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/FastAPI-0.95.2-green.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/Status-Active-success.svg" alt="Status">
  <img src="https://img.shields.io/github/stars/Sumit-342/youtube-downloader?style=social" alt="GitHub Stars">
  <img src="https://img.shields.io/github/forks/Sumit-342/youtube-downloader?style=social" alt="GitHub Forks">
</div>

<br>

<div align="center">
  <h1>⚡ SnapDownload</h1>
  <p><strong>Download Any YouTube Video in Seconds</strong></p>
  <p>No signup • No ads • 100% Free • Open Source</p>
  
  <br>
  
  <a href="https://your-app.railway.app">
    <img src="https://img.shields.io/badge/🚀_Live_Demo-Click_Here-667eea?style=for-the-badge" alt="Live Demo">
  </a>
  
  <br><br>
</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🚀 **Lightning Fast** | Ready in seconds, not minutes |
| 🎬 **All Qualities** | 360p, 480p, 720p, 1080p, 4K |
| 🎵 **Audio Included** | Merges best audio with video automatically |
| 📱 **Any Device** | Works on mobile, tablet, laptop, desktop |
| 🔒 **100% Safe** | No ads, no malware, no signups |
| ⚡ **Progress Bar** | Real-time download progress tracking |
| 🌙 **Dark Theme** | Premium dark UI |
| 🆓 **Free Forever** | No hidden costs, open source |

---

## 🚀 Live Demo

**Try it now:** [your-app.railway.app](https://youtube-downloader-production-e24e.up.railway.app/)

> **Note:** First visit may take 30–50 seconds to wake up (free tier). After that, it's lightning fast!

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Backend API framework |
| **yt-dlp** | YouTube downloading engine |
| **Jinja2** | HTML templating |
| **Python 3.9+** | Core language |
| **Railway/Render** | Hosting platform |

---

## 📂 Project Structure

```
youtube-downloader/
├── app.py                 # Main FastAPI application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html         # Frontend HTML
├── static/
│   ├── style.css          # Styles (Dark Theme)
│   └── script.js          # JavaScript logic
└── README.md              # Project Documentation
```

---

## 🔧 Local Installation

### 1️⃣ Clone the Repository

```bash
git clone [https://github.com/Sumit-342/youtube-downloader.git](https://github.com/Sumit-342/youtube-downloader.git)
cd youtube-downloader
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run the Application

```bash
uvicorn app:app --reload
```

### 5️⃣ Open in Browser

```
http://localhost:8000
```

---

## 🚀 Deployment

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

---

## 🔐 Cookies Setup (For Bot Detection)

If you're getting YouTube bot detection errors, you need to add cookies:

### Step 1: Export Cookies
1. Install **Get cookies.txt LOCALLY** extension in your browser.
2. Log in to YouTube.
3. Click the extension icon → **Export** → Save as `cookies.txt`.

### Step 2: Encode to Base64

```bash
# On Mac/Linux
base64 -w 0 cookies.txt > cookies.b64

# On Windows PowerShell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("cookies.txt")) | Out-File -FilePath cookies.b64
```

### Step 3: Add to Environment Variables
In your Railway/Render Dashboard:
* **Variable Name:** `COOKIES_BASE64`
* **Variable Value:** *(paste full content from `cookies.b64`)*

---

## 📦 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `COOKIES_BASE64` | Optional | Base64 encoded YouTube cookies (bypasses bot detection) |

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

* [yt-dlp](https://github.com/yt-dlp/yt-dlp) - The ultimate YouTube downloader engine
* [FastAPI](https://fastapi.tiangolo.com/) - Modern high-performance web framework
* [Font Awesome](https://fontawesome.com/) - Visual assets and icons

---

## ⭐ Show Your Support

If you found this project helpful, please give it a star ⭐ on GitHub!

---

<div align="center">
  <p>Built with ❤️ by <a href="https://github.com/Sumit-342">Sumit Singh</a></p>
  <p>📥 YouTube Downloader • Open Source • Free Forever</p>
</div>