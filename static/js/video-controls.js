/**
 * Custom Video Controls for About Section
 * Futuristic-themed video player with custom controls
 */

document.addEventListener('DOMContentLoaded', function() {
    const video = document.getElementById('aboutVideo');
    const videoWrapper = document.querySelector('.custom-video-wrapper');
    const controls = document.querySelector('.custom-video-controls');
    const playPauseBtn = document.querySelector('.play-pause-btn');
    const progressBar = document.querySelector('.progress-bar');
    const progressFilled = document.querySelector('.progress-filled');
    const currentTimeDisplay = document.querySelector('.current-time');
    const durationDisplay = document.querySelector('.duration');
    const volumeBtn = document.querySelector('.volume-btn');
    const volumeSlider = document.querySelector('.volume-slider');
    const fullscreenBtn = document.querySelector('.fullscreen-btn');

    if (!video) return;

    // Initialize video
    video.volume = 1;
    let hideControlsTimeout;

    // Format time helper
    function formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    // Play/Pause functionality
    function togglePlayPause() {
        if (video.paused) {
            video.play();
            playPauseBtn.innerHTML = '<i class="fas fa-pause"></i>';
            playPauseBtn.setAttribute('aria-label', 'Pause video');
        } else {
            video.pause();
            playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
            playPauseBtn.setAttribute('aria-label', 'Play video');
        }
    }

    playPauseBtn.addEventListener('click', togglePlayPause);
    video.addEventListener('click', togglePlayPause);

    // Update progress bar
    video.addEventListener('timeupdate', function() {
        const percent = (video.currentTime / video.duration) * 100;
        progressFilled.style.width = `${percent}%`;
        currentTimeDisplay.textContent = formatTime(video.currentTime);
    });

    // Set duration when metadata loads
    video.addEventListener('loadedmetadata', function() {
        durationDisplay.textContent = formatTime(video.duration);
    });

    // Seek functionality
    progressBar.addEventListener('click', function(e) {
        const rect = progressBar.getBoundingClientRect();
        const percent = (e.clientX - rect.left) / rect.width;
        video.currentTime = percent * video.duration;
    });

    // Volume control
    volumeSlider.addEventListener('input', function() {
        video.volume = this.value / 100;
        updateVolumeIcon();
    });

    volumeBtn.addEventListener('click', function() {
        if (video.volume > 0) {
            video.dataset.previousVolume = video.volume;
            video.volume = 0;
            volumeSlider.value = 0;
        } else {
            video.volume = video.dataset.previousVolume || 1;
            volumeSlider.value = video.volume * 100;
        }
        updateVolumeIcon();
    });

    function updateVolumeIcon() {
        const volumeIcon = volumeBtn.querySelector('i');
        if (video.volume === 0) {
            volumeIcon.className = 'fas fa-volume-mute';
            volumeBtn.setAttribute('aria-label', 'Unmute');
        } else if (video.volume < 0.5) {
            volumeIcon.className = 'fas fa-volume-down';
            volumeBtn.setAttribute('aria-label', 'Mute');
        } else {
            volumeIcon.className = 'fas fa-volume-up';
            volumeBtn.setAttribute('aria-label', 'Mute');
        }
    }

    // Fullscreen functionality
    fullscreenBtn.addEventListener('click', function() {
        if (!document.fullscreenElement) {
            if (videoWrapper.requestFullscreen) {
                videoWrapper.requestFullscreen();
            } else if (videoWrapper.webkitRequestFullscreen) {
                videoWrapper.webkitRequestFullscreen();
            } else if (videoWrapper.msRequestFullscreen) {
                videoWrapper.msRequestFullscreen();
            }
            fullscreenBtn.innerHTML = '<i class="fas fa-compress"></i>';
            fullscreenBtn.setAttribute('aria-label', 'Exit fullscreen');
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) {
                document.msExitFullscreen();
            }
            fullscreenBtn.innerHTML = '<i class="fas fa-expand"></i>';
            fullscreenBtn.setAttribute('aria-label', 'Fullscreen');
        }
    });

    // Handle fullscreen change
    document.addEventListener('fullscreenchange', function() {
        if (!document.fullscreenElement) {
            fullscreenBtn.innerHTML = '<i class="fas fa-expand"></i>';
            fullscreenBtn.setAttribute('aria-label', 'Fullscreen');
        }
    });

    // Show/hide controls on hover and movement
    function showControls() {
        controls.classList.add('show');
        clearTimeout(hideControlsTimeout);
        
        if (!video.paused) {
            hideControlsTimeout = setTimeout(() => {
                controls.classList.remove('show');
            }, 3000);
        }
    }

    videoWrapper.addEventListener('mouseenter', showControls);
    videoWrapper.addEventListener('mousemove', showControls);
    videoWrapper.addEventListener('mouseleave', function() {
        if (!video.paused) {
            clearTimeout(hideControlsTimeout);
            hideControlsTimeout = setTimeout(() => {
                controls.classList.remove('show');
            }, 1000);
        }
    });

    // Keep controls visible when paused
    video.addEventListener('pause', function() {
        controls.classList.add('show');
        clearTimeout(hideControlsTimeout);
    });

    video.addEventListener('play', function() {
        hideControlsTimeout = setTimeout(() => {
            controls.classList.remove('show');
        }, 3000);
    });

    // Keyboard controls
    document.addEventListener('keydown', function(e) {
        if (!videoWrapper.matches(':hover')) return;

        switch(e.key) {
            case ' ':
            case 'k':
                e.preventDefault();
                togglePlayPause();
                break;
            case 'ArrowLeft':
                e.preventDefault();
                video.currentTime = Math.max(0, video.currentTime - 5);
                break;
            case 'ArrowRight':
                e.preventDefault();
                video.currentTime = Math.min(video.duration, video.currentTime + 5);
                break;
            case 'ArrowUp':
                e.preventDefault();
                video.volume = Math.min(1, video.volume + 0.1);
                volumeSlider.value = video.volume * 100;
                updateVolumeIcon();
                break;
            case 'ArrowDown':
                e.preventDefault();
                video.volume = Math.max(0, video.volume - 0.1);
                volumeSlider.value = video.volume * 100;
                updateVolumeIcon();
                break;
            case 'm':
                e.preventDefault();
                volumeBtn.click();
                break;
            case 'f':
                e.preventDefault();
                fullscreenBtn.click();
                break;
        }
    });

    // Add smooth scroll animation when clicking About link
    const aboutLinks = document.querySelectorAll('a[href="#about"]');
    aboutLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('about').scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        });
    });
});
