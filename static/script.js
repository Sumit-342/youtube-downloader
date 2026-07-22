let selectedFormat = null;
let currentUrl = null;

document.getElementById('fetch-btn').addEventListener('click', async () => {
    const url = document.getElementById('url-input').value.trim();
    if (!url) {
        showError('Please enter a YouTube URL');
        return;
    }
    
    currentUrl = url;
    
    document.getElementById('loading').style.display = 'block';
    document.getElementById('video-info').style.display = 'none';
    document.getElementById('error').style.display = 'none';
    document.getElementById('download-btn').disabled = true;
    
    try {
        const response = await fetch('/api/info', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({url: url})
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to fetch video info');
        }
        
        const data = await response.json();
        displayVideoInfo(data);
        
    } catch (error) {
        showError(error.message || 'Failed to fetch video info. Please check the URL.');
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
});

function displayVideoInfo(data) {
    document.getElementById('video-info').style.display = 'block';
    document.getElementById('thumbnail').src = data.thumbnail || 'https://via.placeholder.com/480x360?text=No+Thumbnail';
    document.getElementById('video-title').textContent = data.title || 'Unknown Title';
    
    const grid = document.getElementById('quality-grid');
    grid.innerHTML = '';
    selectedFormat = null;
    
    if (!data.formats || data.formats.length === 0) {
        showError('No downloadable formats found for this video');
        return;
    }
    
    data.formats.forEach(format => {
        const btn = document.createElement('button');
        const quality = format.quality;
        const size = format.filesize ? ` (${(format.filesize / (1024 * 1024)).toFixed(1)} MB)` : '';
        const audio = format.has_audio ? ' 🎵' : ' 🎬';
        btn.className = 'quality-btn';
        btn.textContent = quality + audio + size;
        btn.dataset.formatId = format.format_id;
        
        btn.addEventListener('click', () => {
            document.querySelectorAll('.quality-btn').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            selectedFormat = format.format_id;
            document.getElementById('download-btn').disabled = false;
        });
        
        grid.appendChild(btn);
    });
    
    // Select first quality by default
    const firstBtn = grid.querySelector('.quality-btn');
    if (firstBtn) {
        firstBtn.click();
    }
    
    document.getElementById('download-btn').disabled = false;
}

document.getElementById('download-btn').addEventListener('click', async () => {
    if (!selectedFormat) {
        showError('Please select a quality first');
        return;
    }
    
    if (!currentUrl) {
        showError('No video URL found');
        return;
    }
    
    try {
        document.getElementById('download-btn').disabled = true;
        document.getElementById('download-btn').textContent = '⏳ Downloading...';
        
        const response = await fetch('/api/download', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                url: currentUrl,
                format_id: selectedFormat
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Download failed');
        }
        
        // Get the filename from Content-Disposition header
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'video.mp4';
        if (contentDisposition) {
            const match = contentDisposition.match(/filename="?([^"]+)"?/);
            if (match) filename = match[1];
        }
        
        // Download the file
        const blob = await response.blob();
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(link.href);
        
        document.getElementById('download-btn').textContent = '✅ Downloaded!';
        setTimeout(() => {
            document.getElementById('download-btn').textContent = '⬇️ Download Selected Quality';
            document.getElementById('download-btn').disabled = false;
        }, 3000);
        
    } catch (error) {
        showError(error.message || 'Download failed. Please try again.');
        document.getElementById('download-btn').disabled = false;
        document.getElementById('download-btn').textContent = '⬇️ Download Selected Quality';
    }
});

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

// Enter key to submit
document.getElementById('url-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        document.getElementById('fetch-btn').click();
    }
});