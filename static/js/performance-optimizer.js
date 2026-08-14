/**
 * Performance Optimizer
 * Enhances website performance and responsiveness
 */

(function() {
    'use strict';

    // ===== LAZY LOADING IMAGES =====
    function initLazyLoading() {
        const images = document.querySelectorAll('img[loading="lazy"]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.classList.add('loaded');
                        observer.unobserve(img);
                    }
                });
            }, {
                rootMargin: '50px 0px',
                threshold: 0.01
            });

            images.forEach(img => imageObserver.observe(img));
        } else {
            // Fallback for browsers without IntersectionObserver
            images.forEach(img => img.classList.add('loaded'));
        }
    }

    // ===== DEBOUNCE FUNCTION =====
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // ===== THROTTLE FUNCTION =====
    function throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    // ===== OPTIMIZE SCROLL PERFORMANCE =====
    function optimizeScrollPerformance() {
        let ticking = false;
        
        const handleScroll = () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    // Your scroll handling code here
                    ticking = false;
                });
                ticking = true;
            }
        };

        window.addEventListener('scroll', handleScroll, { passive: true });
    }

    // ===== RESPONSIVE IMAGES =====
    function handleResponsiveImages() {
        const images = document.querySelectorAll('img[data-src-mobile], img[data-src-tablet], img[data-src-desktop]');
        
        const updateImageSrc = () => {
            const width = window.innerWidth;
            
            images.forEach(img => {
                let newSrc;
                
                if (width < 768 && img.dataset.srcMobile) {
                    newSrc = img.dataset.srcMobile;
                } else if (width < 1200 && img.dataset.srcTablet) {
                    newSrc = img.dataset.srcTablet;
                } else if (img.dataset.srcDesktop) {
                    newSrc = img.dataset.srcDesktop;
                }
                
                if (newSrc && img.src !== newSrc) {
                    img.src = newSrc;
                }
            });
        };

        updateImageSrc();
        window.addEventListener('resize', debounce(updateImageSrc, 250));
    }

    // ===== VIEWPORT HEIGHT FIX FOR MOBILE =====
    function fixMobileViewportHeight() {
        const setVH = () => {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        };

        setVH();
        window.addEventListener('resize', debounce(setVH, 250));
        window.addEventListener('orientationchange', setVH);
    }

    // ===== TOUCH DEVICE DETECTION =====
    function detectTouchDevice() {
        const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
        
        if (isTouchDevice) {
            document.documentElement.classList.add('touch-device');
        } else {
            document.documentElement.classList.add('no-touch');
        }
    }

    // ===== NETWORK SPEED DETECTION =====
    function detectNetworkSpeed() {
        if ('connection' in navigator) {
            const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
            
            if (connection) {
                const effectiveType = connection.effectiveType;
                document.documentElement.setAttribute('data-connection', effectiveType);
                
                // Reduce animations on slow connections
                if (effectiveType === 'slow-2g' || effectiveType === '2g') {
                    document.documentElement.classList.add('reduce-motion');
                }
            }
        }
    }

    // ===== PRELOAD CRITICAL RESOURCES =====
    function preloadCriticalResources() {
        const criticalResources = [
            { href: '/static/css/styles.css', as: 'style' },
            { href: '/static/css/responsive-optimizations.css', as: 'style' }
        ];

        criticalResources.forEach(resource => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.as = resource.as;
            link.href = resource.href;
            document.head.appendChild(link);
        });
    }

    // ===== REDUCE LAYOUT SHIFT =====
    function reduceLayoutShift() {
        // Add aspect ratio boxes to prevent layout shift
        const images = document.querySelectorAll('img:not([width]):not([height])');
        
        images.forEach(img => {
            if (img.naturalWidth && img.naturalHeight) {
                const aspectRatio = (img.naturalHeight / img.naturalWidth) * 100;
                img.style.aspectRatio = `${img.naturalWidth} / ${img.naturalHeight}`;
            }
        });
    }

    // ===== OPTIMIZE FONT LOADING =====
    function optimizeFontLoading() {
        if ('fonts' in document) {
            // Load critical fonts first
            const criticalFonts = [
                new FontFace('Orbitron', 'url(/static/fonts/orbitron.woff2)', { weight: '400' }),
                new FontFace('Poppins', 'url(/static/fonts/poppins.woff2)', { weight: '400' })
            ];

            Promise.all(criticalFonts.map(font => font.load())).then(fonts => {
                fonts.forEach(font => document.fonts.add(font));
            }).catch(err => {
                console.warn('Font loading failed:', err);
            });
        }
    }

    // ===== SMOOTH SCROLL POLYFILL =====
    function initSmoothScroll() {
        const links = document.querySelectorAll('a[href^="#"]');
        
        links.forEach(link => {
            link.addEventListener('click', function(e) {
                const targetId = this.getAttribute('href');
                
                if (targetId === '#') return;
                
                const targetElement = document.querySelector(targetId);
                
                if (targetElement) {
                    e.preventDefault();
                    
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                    
                    // Update URL without jumping
                    if (history.pushState) {
                        history.pushState(null, null, targetId);
                    }
                }
            });
        });
    }

    // ===== OPTIMIZE ANIMATIONS =====
    function optimizeAnimations() {
        // Pause animations when tab is not visible
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                document.documentElement.classList.add('paused-animations');
            } else {
                document.documentElement.classList.remove('paused-animations');
            }
        });

        // Reduce animations on battery saver mode
        if ('getBattery' in navigator) {
            navigator.getBattery().then(battery => {
                const updateBatteryStatus = () => {
                    if (battery.level < 0.2 || battery.charging === false) {
                        document.documentElement.classList.add('reduce-motion');
                    } else {
                        document.documentElement.classList.remove('reduce-motion');
                    }
                };

                updateBatteryStatus();
                battery.addEventListener('levelchange', updateBatteryStatus);
                battery.addEventListener('chargingchange', updateBatteryStatus);
            });
        }
    }

    // ===== RESPONSIVE TABLES =====
    function makeTablesResponsive() {
        const tables = document.querySelectorAll('table:not(.responsive-table)');
        
        tables.forEach(table => {
            const wrapper = document.createElement('div');
            wrapper.className = 'table-responsive';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
            table.classList.add('responsive-table');
        });
    }

    // ===== OPTIMIZE THIRD-PARTY SCRIPTS =====
    function optimizeThirdPartyScripts() {
        // Defer non-critical scripts
        const scripts = document.querySelectorAll('script[data-defer]');
        
        scripts.forEach(script => {
            const newScript = document.createElement('script');
            newScript.src = script.dataset.src;
            newScript.defer = true;
            
            if (script.dataset.async) {
                newScript.async = true;
            }
            
            document.body.appendChild(newScript);
        });
    }

    // ===== CACHE MANAGEMENT =====
    function manageCaching() {
        // Service Worker registration for offline support
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/sw.js').then(registration => {
                    console.log('ServiceWorker registered:', registration);
                }).catch(err => {
                    console.log('ServiceWorker registration failed:', err);
                });
            });
        }
    }

    // ===== PERFORMANCE MONITORING =====
    function monitorPerformance() {
        if ('PerformanceObserver' in window) {
            // Monitor Largest Contentful Paint (LCP)
            const lcpObserver = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                const lastEntry = entries[entries.length - 1];
                console.log('LCP:', lastEntry.renderTime || lastEntry.loadTime);
            });
            lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });

            // Monitor First Input Delay (FID)
            const fidObserver = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                entries.forEach(entry => {
                    console.log('FID:', entry.processingStart - entry.startTime);
                });
            });
            fidObserver.observe({ entryTypes: ['first-input'] });

            // Monitor Cumulative Layout Shift (CLS)
            let clsScore = 0;
            const clsObserver = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (!entry.hadRecentInput) {
                        clsScore += entry.value;
                        console.log('CLS:', clsScore);
                    }
                }
            });
            clsObserver.observe({ entryTypes: ['layout-shift'] });
        }
    }

    // ===== INITIALIZE ALL OPTIMIZATIONS =====
    function init() {
        // Run immediately
        detectTouchDevice();
        detectNetworkSpeed();
        fixMobileViewportHeight();
        
        // Run on DOM ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                initLazyLoading();
                handleResponsiveImages();
                initSmoothScroll();
                makeTablesResponsive();
                optimizeScrollPerformance();
                optimizeAnimations();
                reduceLayoutShift();
            });
        } else {
            initLazyLoading();
            handleResponsiveImages();
            initSmoothScroll();
            makeTablesResponsive();
            optimizeScrollPerformance();
            optimizeAnimations();
            reduceLayoutShift();
        }

        // Run on load
        window.addEventListener('load', () => {
            monitorPerformance();
            optimizeThirdPartyScripts();
        });
    }

    // Start optimization
    init();

    // Export functions for external use
    window.PerformanceOptimizer = {
        debounce,
        throttle,
        initLazyLoading,
        handleResponsiveImages
    };

})();
