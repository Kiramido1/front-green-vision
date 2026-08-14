/**
 * Performance Monitoring and Optimization
 * Green Vision Website
 */

(function() {
    'use strict';

    // Performance observer for monitoring
    if ('PerformanceObserver' in window) {
        // Monitor Long Tasks
        try {
            const longTaskObserver = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (entry.duration > 50) {
                        console.warn('Long task detected:', entry.duration + 'ms');
                    }
                }
            });
            longTaskObserver.observe({ entryTypes: ['longtask'] });
        } catch (e) {
            // Long task API not supported
        }

        // Monitor Layout Shifts
        try {
            const clsObserver = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (!entry.hadRecentInput && entry.value > 0.1) {
                        console.warn('Layout shift detected:', entry.value);
                    }
                }
            });
            clsObserver.observe({ entryTypes: ['layout-shift'] });
        } catch (e) {
            // Layout shift API not supported
        }
    }

    // Debounce function for scroll events
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

    // Throttle function for resize events
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

    // Optimize scroll events
    const optimizedScroll = debounce(() => {
        // Your scroll logic here
    }, 100);

    // Optimize resize events
    const optimizedResize = throttle(() => {
        // Your resize logic here
    }, 200);

    // Use passive event listeners for better scroll performance
    if ('passive' in window) {
        window.addEventListener('scroll', optimizedScroll, { passive: true });
        window.addEventListener('resize', optimizedResize, { passive: true });
    } else {
        window.addEventListener('scroll', optimizedScroll);
        window.addEventListener('resize', optimizedResize);
    }

    // Intersection Observer for lazy loading
    if ('IntersectionObserver' in window) {
        const lazyLoadObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    
                    // Load video when in viewport
                    if (element.tagName === 'VIDEO' && !element.src) {
                        const source = element.querySelector('source');
                        if (source && source.dataset.src) {
                            source.src = source.dataset.src;
                            element.load();
                        }
                    }
                    
                    lazyLoadObserver.unobserve(element);
                }
            });
        }, {
            rootMargin: '50px'
        });

        // Observe lazy load elements
        document.querySelectorAll('[loading="lazy"]').forEach(el => {
            lazyLoadObserver.observe(el);
        });
    }

    // Request Animation Frame optimization
    let ticking = false;
    function requestTick(callback) {
        if (!ticking) {
            requestAnimationFrame(() => {
                callback();
                ticking = false;
            });
            ticking = true;
        }
    }

    // Optimize animations
    function optimizeAnimations() {
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        
        if (prefersReducedMotion) {
            // Disable animations for users who prefer reduced motion
            document.documentElement.style.setProperty('--animation-duration', '0.01ms');
        }
    }

    // Check connection speed and adjust quality
    if ('connection' in navigator) {
        const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
        
        if (connection) {
            const effectiveType = connection.effectiveType;
            
            // Reduce animation complexity on slow connections
            if (effectiveType === 'slow-2g' || effectiveType === '2g') {
                document.body.classList.add('low-bandwidth');
                console.info('Low bandwidth detected, reducing animation complexity');
            }
        }
    }

    // Memory management
    function cleanupUnusedResources() {
        // Remove event listeners from elements no longer in viewport
        // This helps prevent memory leaks
    }

    // Initialize optimizations
    document.addEventListener('DOMContentLoaded', () => {
        optimizeAnimations();
        
        // Log performance metrics
        if (window.performance && window.performance.timing) {
            window.addEventListener('load', () => {
                setTimeout(() => {
                    const perfData = window.performance.timing;
                    const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
                    const connectTime = perfData.responseEnd - perfData.requestStart;
                    const renderTime = perfData.domComplete - perfData.domLoading;
                    
                    console.info('Performance Metrics:');
                    console.info('Page Load Time:', pageLoadTime + 'ms');
                    console.info('Connect Time:', connectTime + 'ms');
                    console.info('Render Time:', renderTime + 'ms');
                }, 0);
            });
        }
    });

    // Cleanup on page unload
    window.addEventListener('beforeunload', cleanupUnusedResources);

})();
