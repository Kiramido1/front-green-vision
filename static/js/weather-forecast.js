/**
 * Weather Forecast Feature
 * Handles map interaction and ML model predictions
 */

class WeatherForecast {
    constructor() {
        this.selectedLat = null;
        this.selectedLng = null;
        this.marker = null;
        this.init();
    }
    
    init() {
        // Wait for map to be initialized
        setTimeout(() => {
            this.setupMapClickHandler();
            this.setupFormHandler();
        }, 1000);
    }
    
    setupMapClickHandler() {
        if (typeof map === 'undefined') {
            console.error('Map not initialized');
            return;
        }
        
        // Add click handler to map
        map.on('click', (e) => {
            this.handleMapClick(e);
        });
    }
    
    handleMapClick(e) {
        this.selectedLat = e.latlng.lat;
        this.selectedLng = e.latlng.lng;
        
        // Remove previous marker
        if (this.marker) {
            map.removeLayer(this.marker);
        }
        
        // Add new marker with custom icon
        const iconHtml = '<i class="fas fa-map-marker-alt" style="color: #6bc99d; font-size: 32px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.8)) drop-shadow(0 0 12px #6bc99d);"></i>';
        
        const customIcon = L.divIcon({
            html: iconHtml,
            className: 'custom-marker',
            iconSize: [32, 32],
            iconAnchor: [16, 32]
        });
        
        this.marker = L.marker([this.selectedLat, this.selectedLng], { 
            icon: customIcon 
        }).addTo(map);
        
        // Update location display
        this.updateLocationDisplay();
        
        // Add popup
        const popupContent = `
            <div style="font-family: 'Poppins', sans-serif; text-align: center; padding: 5px;">
                <h4 style="color: #5eb8b8; margin: 0 0 8px 0; font-size: 1rem; font-weight: 600;">Selected Location</h4>
                <p style="margin: 0; color: #666; font-size: 0.85rem; font-family: 'Courier New', monospace;">
                    <i class="fas fa-map-pin" style="color: #6bc99d; margin-right: 3px;"></i>
                    ${this.selectedLat.toFixed(4)}°, ${this.selectedLng.toFixed(4)}°
                </p>
            </div>
        `;
        
        this.marker.bindPopup(popupContent, {
            className: 'custom-popup'
        }).openPopup();
    }
    
    updateLocationDisplay() {
        const locationEl = document.getElementById('selectedLocation');
        if (locationEl) {
            locationEl.innerHTML = `
                <i class="fas fa-map-marker-alt"></i>
                <span>Selected: ${this.selectedLat.toFixed(4)}°, ${this.selectedLng.toFixed(4)}°</span>
            `;
            locationEl.style.background = 'rgba(107, 201, 157, 0.1)';
            locationEl.style.borderLeft = '3px solid #6bc99d';
        }
    }
    
    setupFormHandler() {
        const form = document.getElementById('weatherForm');
        if (!form) return;
        
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handlePrediction();
        });
    }
    
    async handlePrediction() {
        // Check if location is selected
        if (this.selectedLat === null || this.selectedLng === null) {
            this.showError('Please select a location on the map first');
            return;
        }
        
        // Get form values
        const day = parseInt(document.getElementById('dayInput').value);
        const month = parseInt(document.getElementById('monthInput').value);
        const year = parseInt(document.getElementById('yearInput').value);
        
        // Validate inputs
        if (!day || !month || !year) {
            this.showError('Please fill in all date fields');
            return;
        }
        
        if (day < 1 || day > 31) {
            this.showError('Day must be between 1 and 31');
            return;
        }
        
        if (month < 1 || month > 12) {
            this.showError('Month must be between 1 and 12');
            return;
        }
        
        if (year < 2024 || year > 2100) {
            this.showError('Year must be between 2024 and 2100');
            return;
        }
        
        // Show loading
        this.showLoading();
        
        try {
            // Make API request
            const response = await fetch('/predict-weather/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    day: day,
                    month: month,
                    year: year,
                    latitude: this.selectedLat,
                    longitude: this.selectedLng
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showResults(data.prediction);
            } else {
                this.showError(data.error || 'Prediction failed');
            }
        } catch (error) {
            console.error('Prediction error:', error);
            this.showError('Network error. Please try again.');
        } finally {
            this.hideLoading();
        }
    }
    
    showLoading() {
        document.getElementById('weatherLoading').style.display = 'block';
        document.getElementById('weatherResults').style.display = 'none';
    }
    
    hideLoading() {
        document.getElementById('weatherLoading').style.display = 'none';
    }
    
    showResults(prediction) {
        // Update values
        document.getElementById('tempValue').textContent = prediction.temperature;
        document.getElementById('precipValue').textContent = prediction.precipitation;
        document.getElementById('humidityValue').textContent = prediction.humidity;
        
        // Update date and location
        const dateStr = `${prediction.date.day}/${prediction.date.month}/${prediction.date.year}`;
        const locationStr = `${prediction.location.latitude.toFixed(2)}°, ${prediction.location.longitude.toFixed(2)}°`;
        
        document.getElementById('predictionDate').textContent = dateStr;
        document.getElementById('predictionLocation').textContent = locationStr;
        
        // Show results with animation
        const resultsEl = document.getElementById('weatherResults');
        resultsEl.style.display = 'block';
        resultsEl.style.animation = 'fadeInUp 0.5s ease-out';
        
        // Scroll to results
        resultsEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    showError(message) {
        alert(message);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Wait a bit for map to initialize
    setTimeout(() => {
        window.weatherForecast = new WeatherForecast();
    }, 1500);
});

// Add fadeInUp animation
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);
