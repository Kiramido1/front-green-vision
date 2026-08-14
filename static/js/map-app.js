/**
 * Interactive Map Application
 * Green Vision Technology Map
 */

// Initialize map
let map;
let currentMarker;

// Initialize the map when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
    populateCountries();
    setupEventListeners();
});

// Initialize Leaflet map
function initializeMap() {
    // Create map centered on world view
    map = L.map('map').setView([20, 0], 2);
    
    // Add Satellite View using ESRI World Imagery
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
        maxZoom: 18,
        minZoom: 2
    }).addTo(map);
    
    // Add labels overlay for better readability
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors, &copy; CARTO',
        maxZoom: 18,
        minZoom: 2,
        pane: 'shadowPane'
    }).addTo(map);
    
    // Add custom styling to map container for better visibility
    const mapContainer = document.getElementById('map');
    mapContainer.style.filter = 'brightness(0.95) contrast(1.05)';
}

// Populate country dropdown
function populateCountries() {
    const countrySelect = document.getElementById('countrySelect');
    const countries = Object.keys(mapData).sort();
    
    countries.forEach(country => {
        const option = document.createElement('option');
        option.value = country;
        option.textContent = country;
        countrySelect.appendChild(option);
    });
}

// Setup event listeners
function setupEventListeners() {
    const countrySelect = document.getElementById('countrySelect');
    const citySelect = document.getElementById('citySelect');
    
    // Country selection
    countrySelect.addEventListener('change', function() {
        const selectedCountry = this.value;
        
        if (selectedCountry) {
            // Enable city dropdown
            citySelect.disabled = false;
            
            // Populate cities
            populateCities(selectedCountry);
            
            // Zoom to country
            const countryData = mapData[selectedCountry];
            map.setView(countryData.coords, countryData.zoom);
            
            // Add country marker
            addMarker(countryData.coords, selectedCountry, 'country');
        } else {
            // Reset
            citySelect.disabled = true;
            citySelect.innerHTML = '<option value="">First select a country...</option>';
            map.setView([20, 0], 2);
            removeMarker();
        }
    });
    
    // City selection
    citySelect.addEventListener('change', function() {
        const selectedCountry = countrySelect.value;
        const selectedCity = this.value;
        
        if (selectedCity && selectedCountry) {
            const cityCoords = mapData[selectedCountry].cities[selectedCity];
            
            // Zoom to city
            map.setView(cityCoords, 12);
            
            // Add city marker
            addMarker(cityCoords, selectedCity, 'city');
        }
    });
}

// Populate cities based on selected country
function populateCities(country) {
    const citySelect = document.getElementById('citySelect');
    citySelect.innerHTML = '<option value="">Select a city...</option>';
    
    const cities = mapData[country].cities;
    const cityNames = Object.keys(cities).sort();
    
    cityNames.forEach(city => {
        const option = document.createElement('option');
        option.value = city;
        option.textContent = city;
        citySelect.appendChild(option);
    });
}

// Add marker to map
function addMarker(coords, name, type) {
    // Remove existing marker
    removeMarker();
    
    // Create custom icon with better visibility on satellite view
    const iconHtml = type === 'city' 
        ? '<i class="fas fa-map-marker-alt" style="color: #6bc99d; font-size: 32px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.8)) drop-shadow(0 0 12px #6bc99d);"></i>'
        : '<i class="fas fa-flag" style="color: #5eb8b8; font-size: 28px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.8)) drop-shadow(0 0 12px #5eb8b8);"></i>';
    
    const customIcon = L.divIcon({
        html: iconHtml,
        className: 'custom-marker',
        iconSize: [30, 30],
        iconAnchor: [15, 30]
    });
    
    // Add marker
    currentMarker = L.marker(coords, { icon: customIcon }).addTo(map);
    
    // Add popup with better styling for satellite view
    const popupContent = `
        <div style="font-family: 'Poppins', sans-serif; text-align: center; padding: 5px;">
            <h4 style="color: #5eb8b8; margin: 0 0 8px 0; font-size: 1.1rem; font-weight: 600;">${name}</h4>
            <p style="margin: 0 0 5px 0; color: #333; font-size: 0.85rem;">
                <i class="fas fa-${type === 'city' ? 'city' : 'globe-americas'}" style="color: #6bc99d; margin-right: 5px;"></i>
                ${type === 'city' ? 'City Location' : 'Country View'}
            </p>
            <p style="margin: 0; color: #666; font-size: 0.75rem; font-family: 'Courier New', monospace;">
                <i class="fas fa-map-pin" style="color: #5eb8b8; margin-right: 3px;"></i>
                ${coords[0].toFixed(4)}°, ${coords[1].toFixed(4)}°
            </p>
        </div>
    `;
    
    currentMarker.bindPopup(popupContent, {
        className: 'custom-popup',
        maxWidth: 250
    }).openPopup();
    
    // Add pulsing animation
    addPulseAnimation(coords);
}

// Remove current marker
function removeMarker() {
    if (currentMarker) {
        map.removeLayer(currentMarker);
        currentMarker = null;
    }
    
    // Remove pulse animations
    document.querySelectorAll('.pulse-marker').forEach(el => el.remove());
}

// Add pulse animation around marker
function addPulseAnimation(coords) {
    const pulseIcon = L.divIcon({
        html: '<div class="pulse-ring"></div>',
        className: 'pulse-marker',
        iconSize: [60, 60],
        iconAnchor: [30, 30]
    });
    
    L.marker(coords, { icon: pulseIcon }).addTo(map);
    
    // Add CSS for pulse animation
    if (!document.getElementById('pulse-style')) {
        const style = document.createElement('style');
        style.id = 'pulse-style';
        style.textContent = `
            .custom-marker {
                background: none;
                border: none;
            }
            
            .pulse-marker {
                background: none;
                border: none;
                pointer-events: none;
            }
            
            .pulse-ring {
                width: 60px;
                height: 60px;
                border: 3px solid #5eb8b8;
                border-radius: 50%;
                animation: pulse 2s ease-out infinite;
                opacity: 0;
                box-shadow: 0 0 15px rgba(94, 184, 184, 0.6);
            }
            
            @keyframes pulse {
                0% {
                    transform: scale(0.3);
                    opacity: 1;
                }
                100% {
                    transform: scale(1);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

// Add some sample markers for demonstration
function addSampleMarkers() {
    // Add markers for major agricultural regions
    const agriculturalRegions = [
        { name: "Midwest USA", coords: [41.8781, -93.0977], info: "Corn Belt Region" },
        { name: "Punjab, India", coords: [31.1471, 75.3412], info: "Wheat Production" },
        { name: "Pampas, Argentina", coords: [-34.6037, -58.3816], info: "Cattle & Grain" }
    ];
    
    agriculturalRegions.forEach(region => {
        const icon = L.divIcon({
            html: '<i class="fas fa-tractor" style="color: #6bc99d; font-size: 22px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.8)) drop-shadow(0 0 10px #6bc99d);"></i>',
            className: 'custom-marker',
            iconSize: [22, 22]
        });
        
        const popupContent = `
            <div style="font-family: 'Poppins', sans-serif; text-align: center; padding: 3px;">
                <b style="color: #5eb8b8; font-size: 0.95rem;">${region.name}</b><br>
                <span style="color: #666; font-size: 0.8rem;">${region.info}</span>
            </div>
        `;
        
        L.marker(region.coords, { icon: icon })
            .addTo(map)
            .bindPopup(popupContent, { className: 'custom-popup' });
    });
}

// Call sample markers after a delay
setTimeout(addSampleMarkers, 1000);
