/**
 * Green Vision - Main Application JavaScript
 * Production-ready, accessible, and performant
 */

'use strict';

// ===== GLOBAL STATE =====
const AppState = {
    isInitialized: false,
    animationFrameId: null,
    particleSystem: null,
    intersectionObserver: null,
    resizeObserver: null,
    prefersReducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    isVisible: true
};

// ===== PERFORMANCE UTILITIES =====
const Utils = {
    // Throttle function for performance
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    // Debounce function for performance
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Check if element is in viewport
    isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    },

    // Safe animation frame request
    requestAnimationFrame(callback) {
        if (!AppState.prefersReducedMotion && AppState.isVisible) {
            return window.requestAnimationFrame(callback);
        }
        return null;
    }
};

// ===== INITIALIZATION =====
class GreenVisionApp {
    constructor() {
        this.init();
    }

    async init() {
        if (AppState.isInitialized) return;

        try {
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.initializeComponents());
            } else {
                this.initializeComponents();
            }

            // Set up visibility change listener for performance
            document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
            
            // Set up reduced motion listener
            window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', this.handleMotionPreferenceChange.bind(this));

            AppState.isInitialized = true;
        } catch (error) {
            console.error('Failed to initialize Green Vision app:', error);
        }
    }

    initializeComponents() {
        // Initialize loading screen first
        this.initLoadingScreen();
        
        // Initialize all other components
        this.initNavigation();
        this.initScrollAnimations();
        this.initCounterAnimations();
        this.initInteractiveElements();
        this.initParticleSystem();
        this.initSmoothScrolling();
        this.initKeyboardNavigation();
        
        console.log('Green Vision app initialized successfully');
    }

    // ===== PROFESSIONAL NAVIGATION =====
    initNavigation() {
        const navbar = document.querySelector('.futuristic-nav');
        const navToggler = document.querySelector('.futuristic-toggler');
        const navCollapse = document.querySelector('.navbar-collapse');
        const navLinks = document.querySelectorAll('.futuristic-link');
        const progressBar = document.querySelector('.nav-progress-bar');

        if (!navbar) return;

        // Enhanced scroll effect with progress bar
        const handleScroll = Utils.throttle(() => {
            const scrolled = window.scrollY;
            const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
            const scrollProgress = (scrolled / maxScroll) * 100;
            
            // Update navbar appearance
            if (scrolled > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
            
            // Update progress bar
            if (progressBar) {
                progressBar.style.width = `${Math.min(scrollProgress, 100)}%`;
            }
            
            // Update active link based on scroll position
            this.updateActiveNavLink();
        }, 16);

        window.addEventListener('scroll', handleScroll, { passive: true });

        // Enhanced navigation link handling
        navLinks.forEach(link => {
            // Add hover effects
            link.addEventListener('mouseenter', () => {
                if (!AppState.prefersReducedMotion) {
                    this.addNavLinkHoverEffect(link);
                }
            });

            link.addEventListener('click', (e) => {
                // Skip external links
                if (link.hasAttribute('data-external')) {
                    return;
                }
                
                const targetId = link.getAttribute('href');
                
                // Only prevent default for anchor links (starting with #)
                if (targetId && targetId.startsWith('#')) {
                    e.preventDefault();
                    const targetSection = document.querySelector(targetId);
                    
                    if (targetSection) {
                        // Close mobile menu if open
                        if (navCollapse && navCollapse.classList.contains('show')) {
                            const bsCollapse = new bootstrap.Collapse(navCollapse);
                            bsCollapse.hide();
                        }

                        // Smooth scroll with offset for fixed navbar
                        const offsetTop = targetSection.offsetTop - (navbar.offsetHeight + 20);
                        window.scrollTo({
                        top: offsetTop,
                        behavior: 'smooth'
                    });

                    // Add click ripple effect
                    this.createNavRippleEffect(link, e);
                    
                    // Update active state immediately
                    this.setActiveNavLink(link);
                }
            });

            // Keyboard support
            link.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    link.click();
                }
            });
        });

        // Enhanced mobile toggler with animation
        if (navToggler) {
            navToggler.addEventListener('click', (e) => {
                const isExpanded = navToggler.getAttribute('aria-expanded') === 'true';
                navToggler.setAttribute('aria-expanded', !isExpanded);
                
                // Add click effect
                this.createNavRippleEffect(navToggler, e);
                
                // Animate hamburger lines
                this.animateTogglerLines(navToggler, !isExpanded);
            });
        }
        
        // Initialize active link on load
        this.updateActiveNavLink();
    }

    updateActiveNavLink() {
        const sections = document.querySelectorAll('section[id]');
        const navLinks = document.querySelectorAll('.futuristic-link');
        
        let current = '';
        const viewportHeight = window.innerHeight;
        const scrollPosition = window.scrollY + viewportHeight / 3;
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            
            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            const href = link.getAttribute('href');
            if (href === `#${current}` || (current === '' && href === '#home')) {
                link.classList.add('active');
            }
        });
    }
    
    setActiveNavLink(activeLink) {
        const navLinks = document.querySelectorAll('.futuristic-link');
        navLinks.forEach(link => link.classList.remove('active'));
        activeLink.classList.add('active');
    }
    
    // Add navigation hover effects
    addNavLinkHoverEffect(link) {
        if (AppState.prefersReducedMotion) return;
        
        const linkBg = link.querySelector('.link-bg');
        if (linkBg && !link.classList.contains('active')) {
            linkBg.style.transform = 'scale(0.8)';
            linkBg.style.opacity = '0.5';
            
            setTimeout(() => {
                linkBg.style.transform = '';
                linkBg.style.opacity = '';
            }, 200);
        }
    }
    
    // Create navigation ripple effect
    createNavRippleEffect(element, event) {
        if (AppState.prefersReducedMotion) return;
        
        const rect = element.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        const ripple = document.createElement('span');
        ripple.style.cssText = `
            position: absolute;
            border-radius: 50%;
            background: rgba(0, 204, 204, 0.4);
            transform: scale(0);
            animation: navRipple 0.6s linear;
            width: 50px;
            height: 50px;
            left: ${x - 25}px;
            top: ${y - 25}px;
            pointer-events: none;
            z-index: 10;
        `;
        
        // Add animation if not exists
        if (!document.getElementById('nav-ripple-animation')) {
            const style = document.createElement('style');
            style.id = 'nav-ripple-animation';
            style.textContent = `
                @keyframes navRipple {
                    to {
                        transform: scale(2.5);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
        
        element.style.position = 'relative';
        element.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }
    
    // Animate mobile toggler lines
    animateTogglerLines(toggler, isOpen) {
        if (AppState.prefersReducedMotion) return;
        
        const lines = toggler.querySelectorAll('.toggler-line');
        if (lines.length !== 3) return;
        
        if (isOpen) {
            // Transform to X
            lines[0].style.transform = 'rotate(45deg) translate(6px, 6px)';
            lines[1].style.opacity = '0';
            lines[2].style.transform = 'rotate(-45deg) translate(6px, -6px)';
        } else {
            // Reset to hamburger
            lines[0].style.transform = '';
            lines[1].style.opacity = '';
            lines[2].style.transform = '';
        }
    }

    // ===== SCROLL ANIMATIONS =====
    initScrollAnimations() {
        if (AppState.prefersReducedMotion) return;

        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        AppState.intersectionObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animationPlayState = 'running';
                    entry.target.classList.add('animate');
                }
            });
        }, observerOptions);

        // Observe fade-in elements
        const fadeElements = document.querySelectorAll('.fade-in-up');
        fadeElements.forEach(el => {
            AppState.intersectionObserver.observe(el);
        });

        // Observe feature cards
        const featureCards = document.querySelectorAll('.feature-card');
        featureCards.forEach(el => {
            AppState.intersectionObserver.observe(el);
        });
    }

    // ===== COUNTER ANIMATIONS =====
    initCounterAnimations() {
        const counters = document.querySelectorAll('.stat-number');
        if (!counters.length) return;

        const observerOptions = {
            threshold: 0.5,
            rootMargin: '0px 0px -100px 0px'
        };

        const counterObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animateCounter(entry.target);
                    counterObserver.unobserve(entry.target);
                }
            });
        }, observerOptions);

        counters.forEach(counter => {
            counterObserver.observe(counter);
        });
    }

    animateCounter(element) {
        const target = parseInt(element.getAttribute('data-target'));
        const duration = 2000;
        const step = target / (duration / 16);
        let current = 0;

        const updateCounter = () => {
            current += step;
            if (current >= target) {
                current = target;
                element.textContent = Math.floor(current).toLocaleString();
                return;
            }
            
            element.textContent = Math.floor(current).toLocaleString();
            
            if (!AppState.prefersReducedMotion) {
                element.style.textShadow = `0 0 ${20 + Math.random() * 10}px var(--neon-green)`;
            }
            
            Utils.requestAnimationFrame(updateCounter);
        };

        updateCounter();
    }

    // ===== INTERACTIVE ELEMENTS =====
    initInteractiveElements() {
        this.initButtons();
        this.initFeatureCards();
        this.initSphere();
    }

    initButtons() {
        const buttons = document.querySelectorAll('.futuristic-btn');
        
        buttons.forEach(button => {
            // Mouse events
            button.addEventListener('mouseenter', (e) => {
                if (!AppState.prefersReducedMotion) {
                    e.target.style.transform = 'translateY(-3px) scale(1.02)';
                }
                this.addRippleEffect(e.target);
            });
            
            button.addEventListener('mouseleave', (e) => {
                if (!AppState.prefersReducedMotion) {
                    e.target.style.transform = 'translateY(0) scale(1)';
                }
            });
            
            // Click events
            button.addEventListener('click', (e) => {
                this.createClickEffect(e, e.target);
                
                // Handle button actions
                const buttonText = e.target.textContent.trim();
                if (buttonText.includes('Join Us')) {
                    this.handleJoinAction();
                } else if (buttonText.includes('Learn More')) {
                    this.handleLearnMoreAction();
                }
            });

            // Keyboard events
            button.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    button.click();
                }
            });
        });
    }

    initFeatureCards() {
        const featureCards = document.querySelectorAll('.feature-card');
        
        featureCards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                if (!AppState.prefersReducedMotion) {
                    this.style.background = 'rgba(0, 255, 255, 0.1)';
                    this.style.transform = 'translateY(-15px)';
                }
            });
            
            card.addEventListener('mouseleave', function() {
                if (!AppState.prefersReducedMotion) {
                    this.style.background = 'rgba(42, 42, 42, 0.5)';
                    this.style.transform = 'translateY(0)';
                }
            });
        });
    }

    initSphere() {
        const sphere = document.querySelector('.holographic-sphere');
        if (!sphere) return;

        let isDragging = false;
        let startX, startY;
        let currentRotationX = 0;
        let currentRotationY = 0;

        // Mouse events
        sphere.addEventListener('mousedown', (e) => {
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            sphere.style.cursor = 'grabbing';
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging || AppState.prefersReducedMotion) return;
            
            const deltaX = e.clientX - startX;
            const deltaY = e.clientY - startY;
            
            currentRotationY += deltaX * 0.5;
            currentRotationX -= deltaY * 0.5;
            
            sphere.style.transform = `rotateX(${currentRotationX}deg) rotateY(${currentRotationY}deg)`;
            
            startX = e.clientX;
            startY = e.clientY;
        });

        document.addEventListener('mouseup', () => {
            isDragging = false;
            sphere.style.cursor = 'grab';
        });

        // Touch events for mobile
        sphere.addEventListener('touchstart', (e) => {
            if (e.touches.length === 1) {
                isDragging = true;
                startX = e.touches[0].clientX;
                startY = e.touches[0].clientY;
            }
        }, { passive: true });

        sphere.addEventListener('touchmove', (e) => {
            if (!isDragging || AppState.prefersReducedMotion || e.touches.length !== 1) return;
            
            const deltaX = e.touches[0].clientX - startX;
            const deltaY = e.touches[0].clientY - startY;
            
            currentRotationY += deltaX * 0.5;
            currentRotationX -= deltaY * 0.5;
            
            sphere.style.transform = `rotateX(${currentRotationX}deg) rotateY(${currentRotationY}deg)`;
            
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        }, { passive: true });

        sphere.addEventListener('touchend', () => {
            isDragging = false;
        });

        // Keyboard interaction
        sphere.addEventListener('keydown', (e) => {
            if (AppState.prefersReducedMotion) return;
            
            const step = 10;
            switch(e.key) {
                case 'ArrowLeft':
                    currentRotationY -= step;
                    break;
                case 'ArrowRight':
                    currentRotationY += step;
                    break;
                case 'ArrowUp':
                    currentRotationX -= step;
                    break;
                case 'ArrowDown':
                    currentRotationX += step;
                    break;
                default:
                    return;
            }
            
            e.preventDefault();
            sphere.style.transform = `rotateX(${currentRotationX}deg) rotateY(${currentRotationY}deg)`;
        });
    }

    // ===== PARTICLE SYSTEM =====
    initParticleSystem() {
        if (AppState.prefersReducedMotion) return;

        const particleContainer = document.querySelector('.floating-particles');
        if (!particleContainer) return;

        const particles = [];
        const particleCount = Math.min(50, Math.floor(window.innerWidth / 20)); // Responsive particle count

        // Create particles
        for (let i = 0; i < particleCount; i++) {
            const particle = this.createParticle();
            particles.push(particle);
            particleContainer.appendChild(particle.element);
        }

        AppState.particleSystem = particles;

        // Animate particles
        const animateParticles = () => {
            if (AppState.prefersReducedMotion || !AppState.isVisible) {
                AppState.animationFrameId = Utils.requestAnimationFrame(animateParticles);
                return;
            }

            particles.forEach(particle => {
                this.updateParticle(particle);
            });
            
            AppState.animationFrameId = Utils.requestAnimationFrame(animateParticles);
        };

        animateParticles();
    }

    createParticle() {
        const element = document.createElement('div');
        element.className = 'particle';
        
        const size = Math.random() * 4 + 2;
        const colors = ['0, 255, 255', '0, 255, 136', '0, 230, 255'];
        const color = colors[Math.floor(Math.random() * colors.length)];
        
        Object.assign(element.style, {
            position: 'absolute',
            width: size + 'px',
            height: size + 'px',
            background: `rgba(${color}, ${Math.random() * 0.8 + 0.2})`,
            borderRadius: '50%',
            boxShadow: `0 0 ${Math.random() * 20 + 10}px rgba(${color}, 0.5)`,
            pointerEvents: 'none',
            zIndex: '1'
        });
        
        return {
            element: element,
            x: Math.random() * window.innerWidth,
            y: Math.random() * window.innerHeight,
            vx: (Math.random() - 0.5) * 0.5,
            vy: (Math.random() - 0.5) * 0.5,
            life: Math.random() * 100 + 100,
            maxLife: Math.random() * 100 + 100
        };
    }

    updateParticle(particle) {
        particle.x += particle.vx;
        particle.y += particle.vy;
        particle.life--;
        
        // Boundary checking
        if (particle.x < 0 || particle.x > window.innerWidth) particle.vx *= -1;
        if (particle.y < 0 || particle.y > window.innerHeight) particle.vy *= -1;
        
        // Reset particle if life is over
        if (particle.life <= 0) {
            particle.x = Math.random() * window.innerWidth;
            particle.y = Math.random() * window.innerHeight;
            particle.life = particle.maxLife;
        }
        
        // Update position
        particle.element.style.left = particle.x + 'px';
        particle.element.style.top = particle.y + 'px';
        
        // Update opacity based on life
        const opacity = particle.life / particle.maxLife;
        particle.element.style.opacity = opacity;
    }

    // ===== SMOOTH SCROLLING =====
    initSmoothScrolling() {
        const scrollIndicator = document.querySelector('.scroll-indicator .scroll-arrow');
        if (scrollIndicator) {
            scrollIndicator.addEventListener('click', () => {
                const featuresSection = document.querySelector('#features');
                if (featuresSection) {
                    featuresSection.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        }
    }

    // ===== KEYBOARD NAVIGATION =====
    initKeyboardNavigation() {
        // Trap focus in mobile menu when open
        const navToggler = document.querySelector('.navbar-toggler');
        const navCollapse = document.querySelector('.navbar-collapse');
        
        if (navToggler && navCollapse) {
            navCollapse.addEventListener('shown.bs.collapse', () => {
                const firstLink = navCollapse.querySelector('.futuristic-link');
                if (firstLink) firstLink.focus();
            });
        }

        // Global keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Escape key closes mobile menu
            if (e.key === 'Escape' && navCollapse && navCollapse.classList.contains('show')) {
                const bsCollapse = new bootstrap.Collapse(navCollapse);
                bsCollapse.hide();
                navToggler.focus();
            }
        });
    }

    // ===== UTILITY METHODS =====
    addRippleEffect(button) {
        if (AppState.prefersReducedMotion) return;

        const ripple = document.createElement('span');
        ripple.className = 'ripple-effect';
        
        Object.assign(ripple.style, {
            position: 'absolute',
            top: '50%',
            left: '50%',
            width: '0',
            height: '0',
            borderRadius: '50%',
            background: 'rgba(255, 255, 255, 0.3)',
            transform: 'translate(-50%, -50%)',
            animation: 'ripple 0.6s ease-out',
            pointerEvents: 'none'
        });
        
        button.appendChild(ripple);
        
        setTimeout(() => {
            if (ripple.parentNode) {
                ripple.remove();
            }
        }, 600);
    }

    createClickEffect(event, element) {
        if (AppState.prefersReducedMotion) return;

        const rect = element.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        const effect = document.createElement('div');
        effect.className = 'click-effect';
        
        Object.assign(effect.style, {
            position: 'absolute',
            left: x + 'px',
            top: y + 'px',
            width: '0',
            height: '0',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(0, 255, 255, 0.8) 0%, transparent 70%)',
            transform: 'translate(-50%, -50%)',
            animation: 'clickExpand 0.5s ease-out',
            pointerEvents: 'none',
            zIndex: '1000'
        });
        
        element.appendChild(effect);
        
        setTimeout(() => {
            if (effect.parentNode) {
                effect.remove();
            }
        }, 500);
    }

    // ===== ACTION HANDLERS =====
    handleJoinAction() {
        // Placeholder for join action
        console.log('Join action triggered');
        // Could open a modal, redirect to signup, etc.
    }

    handleLearnMoreAction() {
        // Scroll to features section
        const featuresSection = document.querySelector('#features');
        if (featuresSection) {
            featuresSection.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }

    // ===== EVENT HANDLERS =====
    handleVisibilityChange() {
        AppState.isVisible = !document.hidden;
        
        if (!AppState.isVisible && AppState.animationFrameId) {
            cancelAnimationFrame(AppState.animationFrameId);
            AppState.animationFrameId = null;
        }
    }

    handleMotionPreferenceChange(e) {
        AppState.prefersReducedMotion = e.matches;
        
        if (AppState.prefersReducedMotion) {
            // Stop all animations
            if (AppState.animationFrameId) {
                cancelAnimationFrame(AppState.animationFrameId);
                AppState.animationFrameId = null;
            }
            
            // Hide particle system
            const particleContainer = document.querySelector('.floating-particles');
            if (particleContainer) {
                particleContainer.style.display = 'none';
            }
        }
    }

    // ===== LOADING SCREEN =====
    initLoadingScreen() {
        const loadingScreen = document.getElementById('loading-screen');
        if (!loadingScreen) return;

        const progressBar = loadingScreen.querySelector('.loading-progress');
        const loadingText = loadingScreen.querySelector('.loading-text');
        const loadingPercentage = loadingScreen.querySelector('.loading-percentage');

        if (!progressBar || !loadingText || !loadingPercentage) return;

        let progress = 0;
        const loadingMessages = [
            'Initializing Future Technology...',
            'Loading Holographic Interface...',
            'Connecting to Satellite Network...',
            'Calibrating AI Systems...',
            'Optimizing Agricultural Data...',
            'Preparing Green Vision...',
            'Ready for Launch!'
        ];

        const updateProgress = () => {
            // Simulate realistic loading progress
            const increment = Math.random() * 15 + 5;
            progress = Math.min(progress + increment, 100);
            
            // Update progress bar
            progressBar.style.width = progress + '%';
            
            // Update percentage
            loadingPercentage.textContent = Math.floor(progress) + '%';
            
            // Update loading message based on progress
            const messageIndex = Math.min(
                Math.floor((progress / 100) * loadingMessages.length),
                loadingMessages.length - 1
            );
            loadingText.textContent = loadingMessages[messageIndex];
            
            if (progress >= 100) {
                // Loading complete
                setTimeout(() => {
                    this.hideLoadingScreen(loadingScreen);
                }, 500);
            } else {
                // Continue loading
                setTimeout(updateProgress, Math.random() * 200 + 100);
            }
        };

        // Start loading simulation
        setTimeout(updateProgress, 300);
    }

    hideLoadingScreen(loadingScreen) {
        if (AppState.prefersReducedMotion) {
            // Immediate hide for reduced motion users
            loadingScreen.style.display = 'none';
        } else {
            // Smooth fade out
            loadingScreen.classList.add('fade-out');
            
            setTimeout(() => {
                loadingScreen.style.display = 'none';
                // Trigger any post-load animations
                this.triggerPostLoadAnimations();
            }, 500);
        }
    }

    triggerPostLoadAnimations() {
        // Trigger hero section animations after loading
        const heroElements = document.querySelectorAll('.fade-in-up');
        heroElements.forEach((element, index) => {
            setTimeout(() => {
                element.style.animationPlayState = 'running';
            }, index * 100);
        });
    }

    // ===== CLEANUP =====
    destroy() {
        // Clean up event listeners and animations
        if (AppState.animationFrameId) {
            cancelAnimationFrame(AppState.animationFrameId);
        }
        
        if (AppState.intersectionObserver) {
            AppState.intersectionObserver.disconnect();
        }
        
        if (AppState.resizeObserver) {
            AppState.resizeObserver.disconnect();
        }
        
        AppState.isInitialized = false;
    }
}

// ===== ADDITIONAL ANIMATIONS =====
const additionalStyles = `
@keyframes ripple {
    0% {
        width: 0;
        height: 0;
        opacity: 1;
    }
    100% {
        width: 100px;
        height: 100px;
        opacity: 0;
    }
}

@keyframes clickExpand {
    0% {
        width: 0;
        height: 0;
        opacity: 1;
    }
    100% {
        width: 50px;
        height: 50px;
        opacity: 0;
    }
}

.particle {
    transition: opacity 0.3s ease;
    will-change: transform, opacity;
}

.feature-card {
    transform-style: preserve-3d;
    will-change: transform;
}

.holographic-sphere {
    will-change: transform;
}
`;

// Inject additional styles
if (!document.querySelector('#additional-styles')) {
    const styleSheet = document.createElement('style');
    styleSheet.id = 'additional-styles';
    styleSheet.textContent = additionalStyles;
    document.head.appendChild(styleSheet);
}

// ===== INITIALIZE APPLICATION =====
let app;

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        app = new GreenVisionApp();
    });
} else {
    app = new GreenVisionApp();
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (app) {
        app.destroy();
    }
});

// Export for potential external use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GreenVisionApp;
}
