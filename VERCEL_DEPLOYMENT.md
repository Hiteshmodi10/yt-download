# 🚀 Vercel Deployment Guide

## Quick Deploy to Vercel

### Option 1: One-Click Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/yt-download)

### Option 2: Manual Deployment

#### Prerequisites

1. **GitHub Account** - Upload your code to GitHub
2. **Vercel Account** - Sign up at [vercel.com](https://vercel.com)

#### Step-by-Step Deployment

1. **Push to GitHub:**

   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/yt-download.git
   git push -u origin main
   ```

2. **Deploy on Vercel:**

   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will automatically detect the configuration
   - Click "Deploy"

3. **Access Your App:**
   - Vercel will provide a URL like: `https://your-app.vercel.app`
   - Your YouTube downloader is now live!

## 📁 Project Structure for Vercel

```
tdownload/
├── api/
│   └── index.py          # Flask API (serverless function)
├── static/
│   └── index.html        # Frontend (static files)
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies
└── README.md
```

## ⚙️ How It Works on Vercel

### Backend (Serverless Functions)

- **Location**: `/api/index.py`
- **Runtime**: Python 3.9
- **Function**: Processes YouTube URLs and returns direct download links
- **Timeout**: 300 seconds (5 minutes)

### Frontend (Static Files)

- **Location**: `/static/index.html`
- **Served**: Directly by Vercel's CDN
- **Performance**: Fast global delivery

## 🎯 Key Features for Vercel Deployment

### ✅ What Works:

- ✅ **Direct Download Links** - Get instant download URLs
- ✅ **Quality Selection** - Choose video quality (4K, 1080p, 720p, audio)
- ✅ **Fast Processing** - Serverless functions for quick response
- ✅ **Mobile Friendly** - Responsive design works on all devices
- ✅ **No Storage Needed** - No server storage requirements

### ⚠️ Limitations:

- ⚠️ **No File Hosting** - Files aren't stored on Vercel (direct download only)
- ⚠️ **5-Minute Timeout** - Large video processing has time limits
- ⚠️ **Cold Starts** - First request may be slower

## 🔧 Configuration Files

### `vercel.json`

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/index.py"
    },
    {
      "src": "/(.*)",
      "dest": "/static/$1"
    }
  ]
}
```

### Environment Variables (Optional)

You can set these in Vercel dashboard:

- `PYTHONPATH=/var/task`

## 🛠️ Local Development

```bash
# Install Vercel CLI
npm i -g vercel

# Start local development
vercel dev
```

## 🚀 Production Optimizations

1. **Caching**: Vercel automatically caches static files
2. **CDN**: Global edge network for fast delivery
3. **Compression**: Automatic gzip compression
4. **HTTPS**: Automatic SSL certificates

## 📊 Performance Tips

1. **Quality Selection**: Choose appropriate quality for faster processing
2. **URL Validation**: App validates YouTube URLs before processing
3. **Error Handling**: Comprehensive error messages
4. **Mobile Optimization**: Touch-friendly interface

## 🔄 Updates

To update your deployed app:

```bash
git add .
git commit -m "Update app"
git push
```

Vercel automatically redeploys on git push!

## 📞 Support

- **Vercel Docs**: [vercel.com/docs](https://vercel.com/docs)
- **yt-dlp Docs**: [github.com/yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp)

## 🎉 You're Done!

Your YouTube downloader is now live on Vercel with:

- ⚡ Serverless architecture
- 🌍 Global CDN delivery
- 📱 Mobile-responsive design
- 🔒 HTTPS security
- 🚀 Automatic deployments
