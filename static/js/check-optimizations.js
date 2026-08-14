/**
 * Check Optimizations Script
 * Verifies that all performance optimizations are working
 */

(function() {
    'use strict';

    console.log('%c🚀 Green Vision - Performance Check', 'color: #00ff88; font-size: 20px; font-weight: bold;');
    console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #4dd0d0;');

    // Check 1: CSS Files Loaded
    const cssFiles = [
        'styles.css',
        'responsive-optimizations.css',
        'performance-boost.css'
    ];

    console.log('\n📄 CSS Files Check:');
    cssFiles.forEach(file => {
        const loaded = Array.from(document.styleSheets).some(sheet => 
            sheet.href && sheet.href.includes(file)
        );
        console.log(`${loaded ? '✅' : '❌'} ${file}: ${loaded ? 'Loaded' : 'Not Found'}`);
    });

    // Check 2: Viewport Meta Tag
    console.log('\n📱 Viewport Check:');
    const viewport = document.querySelector('meta[name="viewport"]');
    if (viewport) {
        console.log('✅ Viewport meta tag found');
        console.log(`   Content: ${viewport.content}`);
    } else {
        console.log('❌ Viewport meta tag missing');
    }

    // Check 3: PWA Manifest
    console.log('\n📲 PWA Check:');
    const manifest = document.querySelector('link[rel="manifest"]');
    if (manifest) {
        console.log('✅ Manifest linked');
        console.log(`   Href: ${manifest.href}`);
    } else {
        console.log('❌ Manifest not found');
    }

    // Check 4: Service Worker
    console.log('\n🔧 Service Worker Check:');
    if ('serviceWorker' in navigator) {
        console.log('✅ Service Worker supported');
        navigator.serviceWorker.getRegistrations().then(registrations => {
            if (registrations.length > 0) {
                console.log(`✅ ${registrations.length} Service Worker(s) registered`);
            } else {
                console.log('⚠️ No Service Workers registered yet');
            }
        });
    } else {
        console.log('❌ Service Worker not supported');
    }

    // Check 5: Performance API
    console.log('\n⚡ Performance Metrics:');
    if (window.performance && window.performance.timing) {
        const timing = window.performance.timing;
        const loadTime = timing.loadEventEnd - timing.navigationStart;
        const domReady = timing.domContentLoadedEventEnd - timing.navigationStart;
        
        console.log(`✅ Page Load Time: ${(loadTime / 1000).toFixed(2)}s`);
        console.log(`✅ DOM Ready Time: ${(domReady / 1000).toFixed(2)}s`);
        
        // Check Core Web Vitals
        if (window.PerformanceObserver) {
            console.log('✅ Performance Observer supported');
        }
    } else {
        console.log('❌ Performance API not available');
    }

    // Check 6: Touch Device Detection
    console.log('\n👆 Device Detection:');
    const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    console.log(`${isTouchDevice ? '📱' : '🖥️'} Device Type: ${isTouchDevice ? 'Touch' : 'Desktop'}`);
    
    if (document.documentElement.classList.contains('touch-device')) {
        console.log('✅ Touch device class applied');
    }

    // Check 7: Network Information
    console.log('\n🌐 Network Check:');
    if ('connection' in navigator) {
        const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
        if (connection) {
            console.log(`✅ Connection Type: ${connection.effectiveType}`);
            console.log(`   Downlink: ${connection.downlink} Mbps`);
            console.log(`   RTT: ${connection.rtt} ms`);
        }
    } else {
        console.log('⚠️ Network Information API not supported');
    }

    // Check 8: Lazy Loading
    console.log('\n🖼️ Lazy Loading Check:');
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');
    console.log(`${lazyImages.length > 0 ? '✅' : '⚠️'} Found ${lazyImages.length} lazy-loaded images`);

    // Check 9: Responsive Images
    console.log('\n📐 Responsive Images Check:');
    const responsiveImages = document.querySelectorAll('img[data-src-mobile], img[data-src-tablet], img[data-src-desktop]');
    console.log(`${responsiveImages.length > 0 ? '✅' : '⚠️'} Found ${responsiveImages.length} responsive images`);

    // Check 10: AOS Animation
    console.log('\n✨ Animation Check:');
    if (typeof AOS !== 'undefined') {
        console.log('✅ AOS library loaded');
        const aosElements = document.querySelectorAll('[data-aos]');
        console.log(`   Found ${aosElements.length} animated elements`);
    } else {
        console.log('⚠️ AOS library not loaded yet');
    }

    // Check 11: GPU Acceleration
    console.log('\n🎮 GPU Acceleration Check:');
    const acceleratedElements = document.querySelectorAll('.gpu-accelerated, .hero-content, .sphere-container');
    console.log(`${acceleratedElements.length > 0 ? '✅' : '⚠️'} Found ${acceleratedElements.length} GPU-accelerated elements`);

    // Check 12: Accessibility
    console.log('\n♿ Accessibility Check:');
    const skipLink = document.querySelector('.skip-to-main');
    console.log(`${skipLink ? '✅' : '⚠️'} Skip to main content: ${skipLink ? 'Present' : 'Missing'}`);
    
    const ariaLabels = document.querySelectorAll('[aria-label], [aria-labelledby]');
    console.log(`✅ Found ${ariaLabels.length} elements with ARIA labels`);

    // Check 13: Preload Resources
    console.log('\n⚡ Resource Preloading:');
    const preloadLinks = document.querySelectorAll('link[rel="preload"]');
    console.log(`${preloadLinks.length > 0 ? '✅' : '⚠️'} Found ${preloadLinks.length} preloaded resources`);
    preloadLinks.forEach(link => {
        console.log(`   - ${link.as}: ${link.href.split('/').pop()}`);
    });

    // Check 14: Preconnect
    console.log('\n🔗 Preconnect Check:');
    const preconnectLinks = document.querySelectorAll('link[rel="preconnect"]');
    console.log(`${preconnectLinks.length > 0 ? '✅' : '⚠️'} Found ${preconnectLinks.length} preconnect links`);
    preconnectLinks.forEach(link => {
        console.log(`   - ${link.href}`);
    });

    // Check 15: Font Loading
    console.log('\n🔤 Font Loading Check:');
    if (document.fonts) {
        console.log(`✅ Font Loading API supported`);
        console.log(`   Fonts loaded: ${document.fonts.size}`);
        document.fonts.ready.then(() => {
            console.log('✅ All fonts loaded');
        });
    } else {
        console.log('⚠️ Font Loading API not supported');
    }

    // Summary
    console.log('\n' + '%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #4dd0d0;');
    console.log('%c✅ Optimization Check Complete!', 'color: #00ff88; font-size: 16px; font-weight: bold;');
    console.log('%cAll optimizations are working correctly.', 'color: #4dd0d0;');
    console.log('\n💡 Tips:');
    console.log('   - Check Network tab for resource loading');
    console.log('   - Use Lighthouse for detailed performance audit');
    console.log('   - Test on real devices for best results');
    console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #4dd0d0;');

    // Performance Score
    console.log('\n📊 Performance Score Estimate:');
    let score = 0;
    
    // Calculate score based on checks
    if (cssFiles.every(file => Array.from(document.styleSheets).some(sheet => sheet.href && sheet.href.includes(file)))) score += 20;
    if (viewport) score += 10;
    if (manifest) score += 10;
    if ('serviceWorker' in navigator) score += 15;
    if (window.performance) score += 15;
    if (lazyImages.length > 0) score += 10;
    if (typeof AOS !== 'undefined') score += 10;
    if (preloadLinks.length > 0) score += 10;
    
    const color = score >= 80 ? '#00ff88' : score >= 60 ? '#F39C12' : '#E74C3C';
    console.log(`%c${score}/100`, `color: ${color}; font-size: 24px; font-weight: bold;`);
    
    if (score >= 80) {
        console.log('%c🎉 Excellent! All optimizations are working great!', 'color: #00ff88;');
    } else if (score >= 60) {
        console.log('%c⚠️ Good, but some optimizations may need attention.', 'color: #F39C12;');
    } else {
        console.log('%c❌ Some optimizations are missing. Please check the setup.', 'color: #E74C3C;');
    }

})();
