/**
 * Professional Earth Globe for Green Vision
 * Realistic Earth with agricultural regions highlighting
 */

'use strict';

class EarthGlobe {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.animationId = null;
        this.isInitialized = false;
        
        // Earth elements
        this.earthGroup = null;
        this.earthMesh = null;
        this.atmosphereMesh = null;
        this.cloudsGroup = null;
        
        // Mouse interaction
        this.mouse = new THREE.Vector2();
        this.isDragging = false;
        this.previousMouse = new THREE.Vector2();
        
        // Animation properties
        this.clock = new THREE.Clock();
        this.rotationX = 0;
        this.rotationY = 0;
        this.targetRotationX = 0;
        this.targetRotationY = 0;
        
        this.init();
    }

    async init() {
        try {
            if (!window.THREE) {
                console.warn('Three.js not loaded yet, retrying...');
                setTimeout(() => this.init(), 100);
                return;
            }

            const container = document.getElementById('threejs-canvas');
            if (!container) {
                console.warn('Container not found, retrying...');
                setTimeout(() => this.init(), 100);
                return;
            }

            await this.setupScene(container);
            await this.createEarthGlobe();
            this.setupMouseInteraction();
            this.setupEventListeners();
            this.animate();
            
            this.hideLoading();
            this.isInitialized = true;
            
            console.log('Professional Earth Globe initialized successfully');
        } catch (error) {
            console.error('Failed to initialize 3D scene:', error);
            console.error('Error details:', error.message, error.stack);
            this.showError();
        }
    }

    async setupScene(container) {
        // Transparent scene for geometric sphere
        this.scene = new THREE.Scene();
        this.scene.background = null; // Transparent background

        // Camera positioned for Earth view
        const aspect = container.clientWidth / container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(60, aspect, 0.1, 1000);
        this.camera.position.set(0, 0, 6);
        this.camera.lookAt(0, 0, 0);

        // Renderer with transparent background
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: true, 
            alpha: true,
            powerPreference: "high-performance"
        });
        this.renderer.setClearColor(0x000000, 0); // Transparent clear color
        this.renderer.setSize(container.clientWidth, container.clientHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.outputEncoding = THREE.sRGBEncoding;
        
        container.appendChild(this.renderer.domElement);

        // Professional lighting for Earth
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
        this.scene.add(ambientLight);
        
        // Directional light (sun)
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1.0);
        directionalLight.position.set(5, 3, 5);
        this.scene.add(directionalLight);
        
        // Point light for highlight
        const pointLight = new THREE.PointLight(0x4dd0d0, 0.5, 10);
        pointLight.position.set(2, 2, 4);
        this.scene.add(pointLight);
    }

    async createEarthGlobe() {
        try {
            console.log('Creating Earth Globe...');
            this.earthGroup = new THREE.Group();
            
            const radius = 2.2;
            
            // Create Earth sphere
            console.log('Creating Earth sphere...');
            await this.createEarthSphere(radius);
            
            // Create atmosphere
            console.log('Creating atmosphere...');
            await this.createAtmosphere(radius);
            
            // Create clouds
            console.log('Creating clouds...');
            await this.createClouds(radius);
            
            // Create agricultural highlights
            console.log('Creating agricultural highlights...');
            await this.createAgriculturalHighlights(radius);
            
            this.scene.add(this.earthGroup);
            console.log('Earth Globe created successfully');
        } catch (error) {
            console.error('Error creating Earth Globe:', error);
            // Fallback to simple sphere
            this.createSimpleFallbackSphere();
        }
    }
    
    async createEarthSphere(radius) {
        // Perfect sphere with high resolution for smooth roundness
        const geometry = new THREE.SphereGeometry(radius, 128, 128);
        
        // Theme-matching Earth material with neon colors
        const earthMaterial = new THREE.MeshPhongMaterial({
            map: this.createThemedEarthTexture(),
            normalMap: this.createNormalTexture(),
            normalScale: new THREE.Vector2(0.5, 0.5),
            shininess: 100,
            transparent: false,
            emissive: new THREE.Color(0x001122),
            emissiveIntensity: 0.1
        });
        
        this.earthMesh = new THREE.Mesh(geometry, earthMaterial);
        this.earthGroup.add(this.earthMesh);
    }
    
    createThemedEarthTexture() {
        const canvas = document.createElement('canvas');
        const size = 1024;
        canvas.width = size;
        canvas.height = size;
        const ctx = canvas.getContext('2d');
        
        // Create themed ocean with neon teal colors (matching website)
        const oceanGradient = ctx.createRadialGradient(size/2, size/2, 0, size/2, size/2, size/2);
        oceanGradient.addColorStop(0, '#1a4a5c'); // Dark teal
        oceanGradient.addColorStop(0.5, '#0d2d3a'); // Darker teal  
        oceanGradient.addColorStop(1, '#0a1f2a'); // Very dark teal
        
        ctx.fillStyle = oceanGradient;
        ctx.fillRect(0, 0, size, size);
        
        // Add subtle neon glow to oceans
        this.addThemedOceanEffects(ctx, size);
        
        // Create themed landmasses with neon agricultural regions
        this.drawThemedContinents(ctx, size);
        
        const texture = new THREE.CanvasTexture(canvas);
        texture.wrapS = THREE.RepeatWrapping;
        texture.wrapT = THREE.RepeatWrapping;
        texture.flipY = false;
        
        return texture;
    }
    
    addThemedOceanEffects(ctx, size) {
        // Add neon teal ocean effects matching website theme
        for (let i = 0; i < 30; i++) {
            const x = Math.random() * size;
            const y = Math.random() * size;
            const radius = Math.random() * 25 + 15;
            
            const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius);
            gradient.addColorStop(0, 'rgba(77, 208, 208, 0.2)'); // Neon teal
            gradient.addColorStop(0.5, 'rgba(77, 208, 208, 0.1)');
            gradient.addColorStop(1, 'rgba(77, 208, 208, 0)');
            
            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(x, y, radius, 0, Math.PI * 2);
            ctx.fill();
        }
    }
    
    drawThemedContinents(ctx, size) {
        // Africa with neon green agriculture
        this.drawThemedContinent(ctx, [
            [0.48 * size, 0.25 * size], [0.52 * size, 0.22 * size], 
            [0.56 * size, 0.28 * size], [0.58 * size, 0.35 * size],
            [0.57 * size, 0.45 * size], [0.54 * size, 0.55 * size],
            [0.51 * size, 0.62 * size], [0.48 * size, 0.58 * size],
            [0.45 * size, 0.52 * size], [0.44 * size, 0.42 * size],
            [0.46 * size, 0.32 * size]
        ], '#2a3d1a', [
            [0.50 * size, 0.40 * size], [0.52 * size, 0.48 * size], 
            [0.48 * size, 0.50 * size]
        ]);
        
        // Europe with neon agricultural regions
        this.drawThemedContinent(ctx, [
            [0.47 * size, 0.18 * size], [0.52 * size, 0.16 * size],
            [0.55 * size, 0.20 * size], [0.53 * size, 0.25 * size],
            [0.49 * size, 0.28 * size], [0.45 * size, 0.25 * size]
        ], '#1a2d0f', [
            [0.50 * size, 0.22 * size], [0.47 * size, 0.24 * size]
        ]);
        
        // Asia with major agricultural zones
        this.drawThemedContinent(ctx, [
            [0.52 * size, 0.20 * size], [0.75 * size, 0.18 * size],
            [0.78 * size, 0.25 * size], [0.76 * size, 0.35 * size],
            [0.70 * size, 0.42 * size], [0.65 * size, 0.38 * size],
            [0.58 * size, 0.35 * size], [0.55 * size, 0.28 * size]
        ], '#2a3d1a', [
            [0.68 * size, 0.28 * size], [0.62 * size, 0.32 * size], 
            [0.58 * size, 0.36 * size]
        ]);
        
        // North America
        this.drawThemedContinent(ctx, [
            [0.12 * size, 0.20 * size], [0.35 * size, 0.15 * size],
            [0.38 * size, 0.25 * size], [0.36 * size, 0.35 * size],
            [0.32 * size, 0.45 * size], [0.25 * size, 0.42 * size],
            [0.18 * size, 0.38 * size], [0.15 * size, 0.28 * size]
        ], '#1a2d0f', [
            [0.25 * size, 0.30 * size], [0.30 * size, 0.35 * size]
        ]);
        
        // South America
        this.drawThemedContinent(ctx, [
            [0.28 * size, 0.48 * size], [0.36 * size, 0.45 * size],
            [0.38 * size, 0.55 * size], [0.37 * size, 0.65 * size],
            [0.34 * size, 0.72 * size], [0.30 * size, 0.70 * size],
            [0.26 * size, 0.62 * size], [0.25 * size, 0.52 * size]
        ], '#0f2a0a', [
            [0.32 * size, 0.52 * size], [0.30 * size, 0.58 * size], 
            [0.33 * size, 0.66 * size]
        ]);
        
        // Australia
        this.drawThemedContinent(ctx, [
            [0.72 * size, 0.65 * size], [0.80 * size, 0.62 * size],
            [0.82 * size, 0.68 * size], [0.78 * size, 0.72 * size],
            [0.74 * size, 0.70 * size]
        ], '#2a3d1a', [
            [0.76 * size, 0.67 * size]
        ]);
    }
    
    drawThemedContinent(ctx, points, baseColor, agriAreas) {
        // Create dark themed landmass
        const gradient = ctx.createLinearGradient(
            Math.min(...points.map(p => p[0])), 
            Math.min(...points.map(p => p[1])),
            Math.max(...points.map(p => p[0])), 
            Math.max(...points.map(p => p[1]))
        );
        gradient.addColorStop(0, baseColor);
        gradient.addColorStop(0.5, this.lightenColor(baseColor, 30));
        gradient.addColorStop(1, this.darkenColor(baseColor, 20));
        
        // Draw landmass with smooth curves
        ctx.fillStyle = gradient;
        ctx.beginPath();
        if (points.length > 0) {
            ctx.moveTo(points[0][0], points[0][1]);
            for (let i = 1; i < points.length; i++) {
                const cp1x = (points[i-1][0] + points[i][0]) / 2;
                const cp1y = (points[i-1][1] + points[i][1]) / 2;
                ctx.quadraticCurveTo(points[i-1][0], points[i-1][1], cp1x, cp1y);
            }
            ctx.quadraticCurveTo(
                points[points.length-1][0], points[points.length-1][1], 
                points[0][0], points[0][1]
            );
        }
        ctx.closePath();
        ctx.fill();
        
        // Add neon green agricultural regions
        agriAreas.forEach(area => {
            // Main neon green area
            const agriGradient = ctx.createRadialGradient(
                area[0], area[1], 0, 
                area[0], area[1], 50
            );
            agriGradient.addColorStop(0, '#4dd084'); // Website neon green
            agriGradient.addColorStop(0.4, '#00ff88'); // Brighter green
            agriGradient.addColorStop(0.7, 'rgba(77, 208, 132, 0.6)');
            agriGradient.addColorStop(1, 'rgba(77, 208, 132, 0.2)');
            
            ctx.fillStyle = agriGradient;
            ctx.beginPath();
            ctx.arc(area[0], area[1], 45, 0, Math.PI * 2);
            ctx.fill();
            
            // Add glowing effect
            const glowGradient = ctx.createRadialGradient(
                area[0], area[1], 0, 
                area[0], area[1], 60
            );
            glowGradient.addColorStop(0, 'rgba(0, 255, 136, 0.3)');
            glowGradient.addColorStop(0.5, 'rgba(0, 255, 136, 0.15)');
            glowGradient.addColorStop(1, 'rgba(0, 255, 136, 0)');
            
            ctx.fillStyle = glowGradient;
            ctx.beginPath();
            ctx.arc(area[0], area[1], 55, 0, Math.PI * 2);
            ctx.fill();
            
            // Add smaller satellite agricultural spots
            for (let i = 0; i < 4; i++) {
                const angle = (i / 4) * Math.PI * 2;
                const distance = Math.random() * 30 + 20;
                const spotX = area[0] + Math.cos(angle) * distance;
                const spotY = area[1] + Math.sin(angle) * distance;
                const spotSize = Math.random() * 10 + 8;
                
                const smallGradient = ctx.createRadialGradient(
                    spotX, spotY, 0, spotX, spotY, spotSize
                );
                smallGradient.addColorStop(0, '#4dd084');
                smallGradient.addColorStop(0.6, 'rgba(77, 208, 132, 0.4)');
                smallGradient.addColorStop(1, 'rgba(77, 208, 132, 0)');
                
                ctx.fillStyle = smallGradient;
                ctx.beginPath();
                ctx.arc(spotX, spotY, spotSize, 0, Math.PI * 2);
                ctx.fill();
            }
        });
    }
    
    drawAdvancedContinent(ctx, points, baseColor, agriColor, agriAreas) {
        // Create realistic landmass with gradients
        const gradient = ctx.createLinearGradient(
            Math.min(...points.map(p => p[0])), 
            Math.min(...points.map(p => p[1])),
            Math.max(...points.map(p => p[0])), 
            Math.max(...points.map(p => p[1]))
        );
        gradient.addColorStop(0, baseColor);
        gradient.addColorStop(0.5, this.lightenColor(baseColor, 20));
        gradient.addColorStop(1, this.darkenColor(baseColor, 15));
        
        // Draw base landmass with smooth curves
        ctx.fillStyle = gradient;
        ctx.beginPath();
        if (points.length > 0) {
            ctx.moveTo(points[0][0], points[0][1]);
            for (let i = 1; i < points.length; i++) {
                const cp1x = (points[i-1][0] + points[i][0]) / 2;
                const cp1y = (points[i-1][1] + points[i][1]) / 2;
                ctx.quadraticCurveTo(points[i-1][0], points[i-1][1], cp1x, cp1y);
            }
            ctx.quadraticCurveTo(
                points[points.length-1][0], points[points.length-1][1], 
                points[0][0], points[0][1]
            );
        }
        ctx.closePath();
        ctx.fill();
        
        // Add detailed agricultural regions
        agriAreas.forEach(area => {
            const agriGradient = ctx.createRadialGradient(
                area[0], area[1], 0, 
                area[0], area[1], 40
            );
            agriGradient.addColorStop(0, agriColor);
            agriGradient.addColorStop(0.7, this.fadeColor(agriColor, 0.8));
            agriGradient.addColorStop(1, this.fadeColor(agriColor, 0.3));
            
            ctx.fillStyle = agriGradient;
            ctx.beginPath();
            ctx.arc(area[0], area[1], 35, 0, Math.PI * 2);
            ctx.fill();
            
            // Add smaller agricultural spots around main areas
            for (let i = 0; i < 5; i++) {
                const angle = (i / 5) * Math.PI * 2;
                const distance = Math.random() * 25 + 15;
                const spotX = area[0] + Math.cos(angle) * distance;
                const spotY = area[1] + Math.sin(angle) * distance;
                const spotSize = Math.random() * 8 + 4;
                
                ctx.fillStyle = this.fadeColor(agriColor, 0.6);
                ctx.beginPath();
                ctx.arc(spotX, spotY, spotSize, 0, Math.PI * 2);
                ctx.fill();
            }
        });
        
        // Add terrain elevation details
        this.addTerrainDetails(ctx, points, baseColor);
    }
    
    addTerrainDetails(ctx, points, baseColor) {
        // Add mountain ranges and terrain features
        const darkTerrain = this.darkenColor(baseColor, 30);
        const lightTerrain = this.lightenColor(baseColor, 15);
        
        for (let i = 0; i < points.length; i++) {
            if (Math.random() > 0.6) { // 40% chance for terrain features
                const x = points[i][0] + (Math.random() - 0.5) * 30;
                const y = points[i][1] + (Math.random() - 0.5) * 30;
                
                // Mountain ranges
                ctx.fillStyle = darkTerrain;
                ctx.beginPath();
                ctx.arc(x, y, Math.random() * 8 + 3, 0, Math.PI * 2);
                ctx.fill();
                
                // Highlands
                ctx.fillStyle = lightTerrain;
                ctx.beginPath();
                ctx.arc(x + 5, y + 5, Math.random() * 6 + 2, 0, Math.PI * 2);
                ctx.fill();
            }
        }
    }
    
    lightenColor(color, percent) {
        const r = parseInt(color.slice(1, 3), 16);
        const g = parseInt(color.slice(3, 5), 16);
        const b = parseInt(color.slice(5, 7), 16);
        
        const newR = Math.min(255, Math.floor(r + (255 - r) * percent / 100));
        const newG = Math.min(255, Math.floor(g + (255 - g) * percent / 100));
        const newB = Math.min(255, Math.floor(b + (255 - b) * percent / 100));
        
        return `#${newR.toString(16).padStart(2, '0')}${newG.toString(16).padStart(2, '0')}${newB.toString(16).padStart(2, '0')}`;
    }
    
    darkenColor(color, percent) {
        const r = parseInt(color.slice(1, 3), 16);
        const g = parseInt(color.slice(3, 5), 16);
        const b = parseInt(color.slice(5, 7), 16);
        
        const newR = Math.floor(r * (100 - percent) / 100);
        const newG = Math.floor(g * (100 - percent) / 100);
        const newB = Math.floor(b * (100 - percent) / 100);
        
        return `#${newR.toString(16).padStart(2, '0')}${newG.toString(16).padStart(2, '0')}${newB.toString(16).padStart(2, '0')}`;
    }
    
    fadeColor(color, opacity) {
        const r = parseInt(color.slice(1, 3), 16);
        const g = parseInt(color.slice(3, 5), 16);
        const b = parseInt(color.slice(5, 7), 16);
        
        return `rgba(${r}, ${g}, ${b}, ${opacity})`;
    }
    
    createNormalTexture() {
        const canvas = document.createElement('canvas');
        const size = 512;
        canvas.width = size;
        canvas.height = size;
        const ctx = canvas.getContext('2d');
        
        // Create detailed normal map for realistic terrain
        const imageData = ctx.createImageData(size, size);
        
        for (let y = 0; y < size; y++) {
            for (let x = 0; x < size; x++) {
                const index = (y * size + x) * 4;
                
                // Create varied terrain normals
                const heightValue = this.generateHeightNoise(x / size, y / size);
                const normalX = 128 + (heightValue - 0.5) * 50;
                const normalY = 128 + Math.sin(x * 0.1) * 30;
                const normalZ = 200; // Mostly pointing up
                
                imageData.data[index] = normalX;     // Red (X normal)
                imageData.data[index + 1] = normalY; // Green (Y normal)
                imageData.data[index + 2] = normalZ; // Blue (Z normal)
                imageData.data[index + 3] = 255;     // Alpha
            }
        }
        
        ctx.putImageData(imageData, 0, 0);
        return new THREE.CanvasTexture(canvas);
    }
    
    createRoughnessTexture() {
        const canvas = document.createElement('canvas');
        const size = 256;
        canvas.width = size;
        canvas.height = size;
        const ctx = canvas.getContext('2d');
        
        // Oceans are smooth, land is rough
        ctx.fillStyle = '#222222'; // Smooth oceans
        ctx.fillRect(0, 0, size, size);
        
        // Rough landmasses
        this.drawSimplifiedLand(ctx, size, '#888888');
        
        return new THREE.CanvasTexture(canvas);
    }
    
    drawSimplifiedLand(ctx, size, color) {
        ctx.fillStyle = color;
        
        // Simplified landmass shapes for roughness map
        const landAreas = [
            [0.48, 0.25, 0.08, 0.35], // Africa
            [0.47, 0.18, 0.08, 0.12], // Europe
            [0.55, 0.20, 0.25, 0.25], // Asia
            [0.15, 0.20, 0.25, 0.28], // North America
            [0.28, 0.48, 0.12, 0.25], // South America
            [0.75, 0.65, 0.08, 0.08]  // Australia
        ];
        
        landAreas.forEach(area => {
            const x = area[0] * size;
            const y = area[1] * size;
            const w = area[2] * size;
            const h = area[3] * size;
            
            ctx.beginPath();
            ctx.ellipse(x, y, w, h, 0, 0, Math.PI * 2);
            ctx.fill();
        });
    }
    
    generateHeightNoise(x, y) {
        // Multi-octave noise for realistic terrain
        let value = 0;
        let amplitude = 1;
        let frequency = 1;
        
        for (let i = 0; i < 4; i++) {
            value += amplitude * Math.sin(x * frequency * Math.PI * 4) * Math.cos(y * frequency * Math.PI * 4);
            amplitude *= 0.5;
            frequency *= 2;
        }
        
        return (value + 1) / 2; // Normalize to 0-1
    }
    
    
    async createAtmosphere(radius) {
        // Themed atmosphere with website colors
        const atmosphereGeometry = new THREE.SphereGeometry(radius * 1.06, 64, 64);
        const atmosphereMaterial = new THREE.ShaderMaterial({
            uniforms: {
                time: { value: 0 },
                glowColor: { value: new THREE.Color(0x4dd0d0) }, // Website neon teal
                secondaryColor: { value: new THREE.Color(0x4dd084) } // Website neon green
            },
            vertexShader: `
                varying vec3 vNormal;
                varying vec3 vPosition;
                void main() {
                    vNormal = normalize(normalMatrix * normal);
                    vPosition = position;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `,
            fragmentShader: `
                uniform float time;
                uniform vec3 glowColor;
                uniform vec3 secondaryColor;
                varying vec3 vNormal;
                varying vec3 vPosition;
                
                void main() {
                    float intensity = pow(0.7 - dot(vNormal, vec3(0.0, 0.0, 1.0)), 2.5);
                    
                    // Animated glow mixing website theme colors
                    float pulse = sin(time * 1.5) * 0.5 + 0.5;
                    vec3 finalColor = mix(glowColor, secondaryColor, pulse * 0.3);
                    
                    intensity += sin(time * 3.0) * 0.05;
                    gl_FragColor = vec4(finalColor, intensity * 0.25);
                }
            `,
            side: THREE.BackSide,
            blending: THREE.AdditiveBlending,
            transparent: true
        });
        
        this.atmosphereMesh = new THREE.Mesh(atmosphereGeometry, atmosphereMaterial);
        this.earthGroup.add(this.atmosphereMesh);
    }
    
    async createClouds(radius) {
        this.cloudsGroup = new THREE.Group();
        
        // Create realistic cloud layer
        const cloudGeometry = new THREE.SphereGeometry(radius * 1.015, 64, 32);
        const cloudMaterial = new THREE.MeshLambertMaterial({
            map: this.createAdvancedCloudTexture(),
            transparent: true,
            opacity: 0.6,
            alphaMap: this.createCloudAlphaTexture(),
            side: THREE.DoubleSide
        });
        
        const cloudMesh = new THREE.Mesh(cloudGeometry, cloudMaterial);
        this.cloudsGroup.add(cloudMesh);
        
        // Add secondary cloud layer for depth
        const cloudGeometry2 = new THREE.SphereGeometry(radius * 1.018, 64, 32);
        const cloudMaterial2 = new THREE.MeshLambertMaterial({
            map: this.createAdvancedCloudTexture(),
            transparent: true,
            opacity: 0.3,
            alphaMap: this.createCloudAlphaTexture()
        });
        
        const cloudMesh2 = new THREE.Mesh(cloudGeometry2, cloudMaterial2);
        cloudMesh2.rotation.y = Math.PI * 0.5; // Offset rotation
        this.cloudsGroup.add(cloudMesh2);
        
        this.earthGroup.add(this.cloudsGroup);
    }
    
    createAdvancedCloudTexture() {
        const canvas = document.createElement('canvas');
        const size = 512;
        canvas.width = size;
        canvas.height = size;
        const ctx = canvas.getContext('2d');
        
        // Create base cloud color
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, size, size);
        
        // Generate realistic cloud formations
        this.generateCloudFormations(ctx, size);
        
        return new THREE.CanvasTexture(canvas);
    }
    
    createCloudAlphaTexture() {
        const canvas = document.createElement('canvas');
        const size = 512;
        canvas.width = size;
        canvas.height = size;
        const ctx = canvas.getContext('2d');
        
        // Start with transparent
        ctx.fillStyle = 'rgba(0, 0, 0, 0)';
        ctx.fillRect(0, 0, size, size);
        
        // Create cloud alpha patterns
        for (let i = 0; i < 60; i++) {
            const x = Math.random() * size;
            const y = Math.random() * size;
            const radius = Math.random() * 30 + 15;
            const opacity = Math.random() * 0.8 + 0.2;
            
            const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius);
            gradient.addColorStop(0, `rgba(255, 255, 255, ${opacity})`);
            gradient.addColorStop(0.5, `rgba(255, 255, 255, ${opacity * 0.5})`);
            gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
            
            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(x, y, radius, 0, Math.PI * 2);
            ctx.fill();
        }
        
        return new THREE.CanvasTexture(canvas);
    }
    
    generateCloudFormations(ctx, size) {
        // Generate weather patterns and cloud formations
        const formations = [
            { type: 'cumulus', count: 25, size: [20, 40] },
            { type: 'cirrus', count: 35, size: [10, 25] },
            { type: 'stratus', count: 15, size: [40, 80] }
        ];
        
        formations.forEach(formation => {
            for (let i = 0; i < formation.count; i++) {
                const x = Math.random() * size;
                const y = Math.random() * size;
                const width = Math.random() * (formation.size[1] - formation.size[0]) + formation.size[0];
                const height = width * (0.5 + Math.random() * 0.5);
                
                this.drawCloudFormation(ctx, x, y, width, height, formation.type);
            }
        });
    }
    
    drawCloudFormation(ctx, x, y, width, height, type) {
        const gradient = ctx.createRadialGradient(x, y, 0, x, y, Math.max(width, height));
        
        switch (type) {
            case 'cumulus':
                gradient.addColorStop(0, 'rgba(255, 255, 255, 0.9)');
                gradient.addColorStop(0.6, 'rgba(240, 248, 255, 0.7)');
                gradient.addColorStop(1, 'rgba(200, 220, 255, 0.3)');
                break;
            case 'cirrus':
                gradient.addColorStop(0, 'rgba(255, 255, 255, 0.6)');
                gradient.addColorStop(0.4, 'rgba(250, 250, 255, 0.4)');
                gradient.addColorStop(1, 'rgba(220, 230, 255, 0.1)');
                break;
            case 'stratus':
                gradient.addColorStop(0, 'rgba(245, 245, 245, 0.8)');
                gradient.addColorStop(0.7, 'rgba(230, 230, 240, 0.5)');
                gradient.addColorStop(1, 'rgba(200, 200, 220, 0.2)');
                break;
        }
        
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.ellipse(x, y, width, height, Math.random() * Math.PI, 0, Math.PI * 2);
        ctx.fill();
    }
    
    async createAgriculturalHighlights(radius) {
        // Create glowing agricultural spots
        const agriSpots = [
            { lat: 40, lon: -100, size: 0.2 }, // North America plains
            { lat: 50, lon: 10, size: 0.15 },   // Europe
            { lat: 30, lon: 110, size: 0.25 },  // China
            { lat: -20, lon: -55, size: 0.2 },  // South America
            { lat: -30, lon: 25, size: 0.18 },  // Africa
            { lat: 25, lon: 80, size: 0.2 }     // India
        ];
        
        agriSpots.forEach(spot => {
            const spotMesh = this.createAgriculturalSpot(radius, spot.lat, spot.lon, spot.size);
            this.earthGroup.add(spotMesh);
        });
    }
    
    createAgriculturalSpot(radius, lat, lon, size) {
        // Convert lat/lon to 3D coordinates
        const phi = (90 - lat) * (Math.PI / 180);
        const theta = (lon + 180) * (Math.PI / 180);
        
        const x = -(radius * 1.008) * Math.sin(phi) * Math.cos(theta);
        const y = (radius * 1.008) * Math.cos(phi);
        const z = (radius * 1.008) * Math.sin(phi) * Math.sin(theta);
        
        const geometry = new THREE.SphereGeometry(size, 16, 12);
        const material = new THREE.MeshBasicMaterial({
            color: 0x4dd084, // Website neon green
            transparent: true,
            opacity: 0.9,
            emissive: 0x00ff88, // Bright neon green emission
            emissiveIntensity: 0.4
        });
        
        const spot = new THREE.Mesh(geometry, material);
        spot.position.set(x, y, z);
        
        // Add pulsing animation
        spot.userData = {
            originalSize: size,
            pulseSpeed: Math.random() * 0.5 + 1.5
        };
        
        return spot;
    }
    
    createSimpleFallbackSphere() {
        console.log('Creating simple fallback sphere...');
        this.earthGroup = new THREE.Group();
        
        // Simple but beautiful sphere
        const geometry = new THREE.SphereGeometry(2.2, 64, 64);
        const material = new THREE.MeshPhongMaterial({
            color: 0x1a4a5c,
            emissive: 0x4dd084,
            emissiveIntensity: 0.1,
            shininess: 100
        });
        
        this.earthMesh = new THREE.Mesh(geometry, material);
        this.earthGroup.add(this.earthMesh);
        
        // Add simple atmosphere
        const atmGeometry = new THREE.SphereGeometry(2.35, 32, 32);
        const atmMaterial = new THREE.MeshBasicMaterial({
            color: 0x4dd0d0,
            transparent: true,
            opacity: 0.2,
            side: THREE.BackSide
        });
        
        this.atmosphereMesh = new THREE.Mesh(atmGeometry, atmMaterial);
        this.earthGroup.add(this.atmosphereMesh);
        
        this.scene.add(this.earthGroup);
        console.log('Fallback sphere created successfully');
    }

    setupMouseInteraction() {
        const canvas = this.renderer.domElement;
        
        // Mouse move for rotation
        canvas.addEventListener('mousemove', (event) => {
            const rect = canvas.getBoundingClientRect();
            this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
            this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
            
            // Smooth rotation based on mouse position
            this.targetRotationY = this.mouse.x * 1.5;
            this.targetRotationX = this.mouse.y * 1.0;
        });
        
        // Touch support for mobile
        canvas.addEventListener('touchmove', (event) => {
            if (event.touches.length === 1) {
                const rect = canvas.getBoundingClientRect();
                this.mouse.x = ((event.touches[0].clientX - rect.left) / rect.width) * 2 - 1;
                this.mouse.y = -((event.touches[0].clientY - rect.top) / rect.height) * 2 + 1;
                
                this.targetRotationY = this.mouse.x * 1.5;
                this.targetRotationX = this.mouse.y * 1.0;
            }
        });
        
        // Auto rotation when mouse leaves
        canvas.addEventListener('mouseleave', () => {
            this.targetRotationX = 0;
            this.targetRotationY = 0;
        });
    }

    addManualControls() {
        let isDragging = false;
        let previousMousePosition = { x: 0, y: 0 };
        
        const canvas = this.renderer.domElement;
        
        canvas.addEventListener('mousedown', (e) => {
            isDragging = true;
            previousMousePosition = { x: e.clientX, y: e.clientY };
        });
        
        canvas.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            
            const deltaMove = {
                x: e.clientX - previousMousePosition.x,
                y: e.clientY - previousMousePosition.y
            };
            
            // Rotate camera around the scene
            const rotationSpeed = 0.005;
            this.camera.position.x = this.camera.position.x * Math.cos(deltaMove.x * rotationSpeed) + this.camera.position.z * Math.sin(deltaMove.x * rotationSpeed);
            this.camera.position.z = this.camera.position.z * Math.cos(deltaMove.x * rotationSpeed) - this.camera.position.x * Math.sin(deltaMove.x * rotationSpeed);
            
            this.camera.lookAt(0, 0, 0);
            previousMousePosition = { x: e.clientX, y: e.clientY };
        });
        
        canvas.addEventListener('mouseup', () => {
            isDragging = false;
        });
        
        // Touch support
        canvas.addEventListener('touchstart', (e) => {
            if (e.touches.length === 1) {
                isDragging = true;
                previousMousePosition = { x: e.touches[0].clientX, y: e.touches[0].clientY };
            }
        });
        
        canvas.addEventListener('touchmove', (e) => {
            if (!isDragging || e.touches.length !== 1) return;
            
            const deltaMove = {
                x: e.touches[0].clientX - previousMousePosition.x,
                y: e.touches[0].clientY - previousMousePosition.y
            };
            
            const rotationSpeed = 0.005;
            const spherical = new THREE.Spherical();
            spherical.setFromVector3(this.camera.position);
            spherical.theta -= deltaMove.x * rotationSpeed;
            spherical.phi += deltaMove.y * rotationSpeed;
            spherical.phi = Math.max(0.1, Math.min(Math.PI - 0.1, spherical.phi));
            
            this.camera.position.setFromSpherical(spherical);
            this.camera.lookAt(0, 0, 0);
            
            previousMousePosition = { x: e.touches[0].clientX, y: e.touches[0].clientY };
        });
        
        canvas.addEventListener('touchend', () => {
            isDragging = false;
        });
    }

    setupEventListeners() {
        // Control buttons
        document.getElementById('view-earth')?.addEventListener('click', () => this.setView('earth'));
        document.getElementById('view-satellites')?.addEventListener('click', () => this.setView('satellites'));
        document.getElementById('view-data')?.addEventListener('click', () => this.setView('data'));
        document.getElementById('auto-rotate')?.addEventListener('click', () => this.toggleAutoRotate());
        
        // Resize handler
        window.addEventListener('resize', () => this.handleResize());
        
        // Performance monitoring
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pause();
            } else {
                this.resume();
            }
        });
        
        // Reduced motion support
        const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
        mediaQuery.addListener((e) => {
            if (e.matches) {
                this.autoRotate = false;
                if (this.controls) this.controls.autoRotate = false;
                // Reduce animation speeds
                this.satellites.forEach(sat => {
                    if (sat.userData) sat.userData.orbitSpeed *= 0.1;
                });
            }
        });
        
        // Performance adaptation based on device
        this.adaptToDevice();
    }

    adaptToDevice() {
        // Detect device performance level
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        
        if (!gl) {
            console.warn('WebGL not supported, using reduced quality');
            this.useReducedQuality();
            return;
        }
        
        // Check for mobile device
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        
        if (isMobile) {
            this.optimizeForMobile();
        }
        
        // Check memory and performance
        const renderer = gl.getParameter(gl.RENDERER);
        const isLowPower = renderer && renderer.toLowerCase().includes('intel');
        
        if (isLowPower) {
            this.useReducedQuality();
        }
    }

    optimizeForMobile() {
        // Reduce satellite count
        const targetCount = Math.min(6, this.satellites.length);
        while (this.satellites.length > targetCount) {
            const satellite = this.satellites.pop();
            this.scene.remove(satellite);
        }
        
        // Reduce data points
        const targetDataPoints = Math.min(25, this.dataPoints.length);
        while (this.dataPoints.length > targetDataPoints) {
            const point = this.dataPoints.pop();
            this.scene.remove(point);
        }
        
        // Reduce renderer quality
        if (this.renderer) {
            this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
        }
    }

    useReducedQuality() {
        // Disable shadows
        if (this.renderer) {
            this.renderer.shadowMap.enabled = false;
        }
        
        // Reduce star count
        if (this.stars && this.stars.geometry) {
            const positions = this.stars.geometry.attributes.position.array;
            const reducedPositions = new Float32Array(positions.length * 0.5);
            for (let i = 0; i < reducedPositions.length; i++) {
                reducedPositions[i] = positions[i * 2];
            }
            this.stars.geometry.setAttribute('position', new THREE.BufferAttribute(reducedPositions, 3));
        }
        
        // Disable some visual effects
        this.autoRotate = false;
    }

    setView(view) {
        this.currentView = view;
        
        // Update button states
        document.querySelectorAll('.control-btn').forEach(btn => btn.classList.remove('active'));
        document.getElementById(`view-${view}`)?.classList.add('active');
        
        // Animate camera to new position
        this.animateCamera(view);
        
        // Update visibility of objects
        this.updateObjectVisibility(view);
    }

    animateCamera(view) {
        const duration = 2000;
        const startPosition = this.camera.position.clone();
        const startTime = Date.now();
        
        let targetPosition;
        
        switch (view) {
            case 'earth':
                targetPosition = new THREE.Vector3(0, 0, 3);
                break;
            case 'satellites':
                targetPosition = new THREE.Vector3(2, 2, 3);
                break;
            case 'data':
                targetPosition = new THREE.Vector3(1, 1, 2);
                break;
            default:
                targetPosition = new THREE.Vector3(0, 0, 3);
        }
        
        const animateToTarget = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easeProgress = 1 - Math.pow(1 - progress, 3); // ease-out cubic
            
            this.camera.position.lerpVectors(startPosition, targetPosition, easeProgress);
            
            if (progress < 1) {
                requestAnimationFrame(animateToTarget);
            }
        };
        
        animateToTarget();
    }

    updateObjectVisibility(view) {
        switch (view) {
            case 'earth':
                this.earth.visible = true;
                this.atmosphere.visible = true;
                this.satellites.forEach(sat => sat.visible = true);
                this.dataPoints.forEach(point => point.visible = false);
                break;
            case 'satellites':
                this.satellites.forEach(sat => sat.visible = true);
                this.dataPoints.forEach(point => point.visible = false);
                break;
            case 'data':
                this.dataPoints.forEach(point => point.visible = true);
                this.satellites.forEach(sat => sat.visible = true);
                break;
        }
    }

    toggleAutoRotate() {
        this.autoRotate = !this.autoRotate;
        if (this.controls) {
            this.controls.autoRotate = this.autoRotate;
        }
        
        const btn = document.getElementById('auto-rotate');
        if (btn) {
            btn.classList.toggle('active', this.autoRotate);
        }
    }

    animate() {
        if (!this.isInitialized) return;
        
        this.animationId = requestAnimationFrame(() => this.animate());
        
        const deltaTime = this.clock.getDelta();
        const elapsedTime = this.clock.getElapsedTime();
        
        // Smooth rotation based on mouse
        this.rotationX += (this.targetRotationX - this.rotationX) * 0.05;
        this.rotationY += (this.targetRotationY - this.rotationY) * 0.05;
        
        // Apply rotation to Earth group
        if (this.earthGroup) {
            this.earthGroup.rotation.x = this.rotationX;
            this.earthGroup.rotation.y = this.rotationY;
            
            // Add continuous slow rotation when not being controlled
            if (Math.abs(this.targetRotationX) < 0.1 && Math.abs(this.targetRotationY) < 0.1) {
                this.earthGroup.rotation.y += deltaTime * 0.1;
            }
        }
        
        // Rotate clouds slightly faster than Earth
        if (this.cloudsGroup) {
            this.cloudsGroup.rotation.y += deltaTime * 0.05;
        }
        
        // Animate atmosphere glow with shader
        if (this.atmosphereMesh && this.atmosphereMesh.material.uniforms) {
            this.atmosphereMesh.material.uniforms.time.value = elapsedTime;
        }
        
        // Render
        this.renderer.render(this.scene, this.camera);
    }

    updateStats() {
        // Simple stats update - no complex calculations needed for geometric sphere
        // Stats can be updated by other parts of the app if needed
    }

    animateNumber(element, from, to, suffix = '') {
        const duration = 1000;
        const startTime = Date.now();
        
        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const current = from + (to - from) * progress;
            
            element.textContent = (suffix === 'M' ? current.toFixed(1) : Math.round(current)) + suffix;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        animate();
    }

    handleResize() {
        const container = document.getElementById('threejs-canvas');
        if (!container || !this.renderer || !this.camera) return;
        
        const width = container.clientWidth;
        const height = container.clientHeight;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }

    hideLoading() {
        const loading = document.getElementById('model-loading');
        if (loading) {
            loading.classList.add('hidden');
            setTimeout(() => {
                loading.style.display = 'none';
            }, 500);
        }
        
        // Show 3D container and hide old sphere
        document.body.classList.add('threejs-active');
    }

    showError() {
        const loading = document.getElementById('model-loading');
        if (loading) {
            loading.innerHTML = `
                <div class="loading-animation">
                    <i class="fas fa-exclamation-triangle" style="color: #ff6b6b;"></i>
                </div>
                <p style="color: #ff6b6b;">Failed to load 3D environment</p>
                <button onclick="location.reload()" style="
                    background: rgba(77, 208, 208, 0.2);
                    border: 1px solid var(--neon-teal);
                    color: var(--neon-teal);
                    padding: 8px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    margin-top: 10px;
                ">Reload</button>
            `;
        }
    }

    pause() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }

    resume() {
        if (!this.animationId && this.isInitialized) {
            this.animate();
        }
    }

    destroy() {
        this.pause();
        
        if (this.renderer) {
            this.renderer.dispose();
        }
        
        // Clean up geometries and materials
        this.scene?.traverse(object => {
            if (object.geometry) object.geometry.dispose();
            if (object.material) {
                if (Array.isArray(object.material)) {
                    object.material.forEach(material => material.dispose());
                } else {
                    object.material.dispose();
                }
            }
        });
        
        this.isInitialized = false;
    }
}

// Initialize when DOM is ready
let scene3D;

function init3DScene() {
    if (typeof THREE !== 'undefined') {
        scene3D = new EarthGlobe();
    } else {
        console.warn('Three.js not loaded, retrying...');
        setTimeout(init3DScene, 100);
    }
}

// Initialize on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init3DScene);
} else {
    init3DScene();
}

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (scene3D) {
        scene3D.destroy();
    }
});

// Export for external use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EarthGlobe;
}
