/*
AI Quiz Platform - Advanced 3D JavaScript
Interactive 3D effects, animations, and user interactions
*/

class Advanced3DEffects {
    constructor() {
        this.init();
        this.setupEventListeners();
        this.createFloatingElements();
        this.init3DCursor();
        this.setupParallaxEffects();
        this.initParticleEffects();
    }

    init() {
        console.log('🚀 Advanced 3D Effects Initialized');
        
        // Set up CSS custom properties for dynamic 3D effects
        this.updateCSSVariables();
        
        // Initialize 3D transforms
        this.init3DTransforms();
        
        // Set up intersection observer for scroll animations
        this.setupIntersectionObserver();
        
        // Initialize audio for 3D effects
        this.initAudioEffects();
    }

    updateCSSVariables() {
        const root = document.documentElement;
        
        // Dynamic 3D variables based on viewport
        const updateVariables = () => {
            const width = window.innerWidth;
            const height = window.innerHeight;
            const depth = Math.min(width, height);
            
            root.style.setProperty('--viewport-width', `${width}px`);
            root.style.setProperty('--viewport-height', `${height}px`);
            root.style.setProperty('--viewport-depth', `${depth}px`);
            root.style.setProperty('--perspective', `${depth * 2}px`);
        };
        
        updateVariables();
        window.addEventListener('resize', updateVariables);
    }

    init3DTransforms() {
        // Add 3D transform classes to elements
        const elements3D = document.querySelectorAll('.card-3d, .form-3d, .btn-3d, .stat-card-3d');
        
        elements3D.forEach(element => {
            element.style.transformStyle = 'preserve-3d';
            element.style.transform = 'translateZ(0px)';
            
            // Add hover 3D effects
            this.add3DHoverEffect(element);
        });
    }

    add3DHoverEffect(element) {
        let isHovering = false;
        let currentX = 0;
        let currentY = 0;
        let targetX = 0;
        let targetY = 0;

        const handleMouseMove = (e) => {
            if (!isHovering) return;
            
            const rect = element.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;
            
            const deltaX = (e.clientX - centerX) / (rect.width / 2);
            const deltaY = (e.clientY - centerY) / (rect.height / 2);
            
            targetX = deltaX * 15;
            targetY = deltaY * -15;
        };

        const handleMouseEnter = () => {
            isHovering = true;
            element.style.transition = 'transform 0.1s ease-out';
        };

        const handleMouseLeave = () => {
            isHovering = false;
            targetX = 0;
            targetY = 0;
            element.style.transition = 'transform 0.3s ease-out';
        };

        const animate = () => {
            currentX += (targetX - currentX) * 0.1;
            currentY += (targetY - currentY) * 0.1;
            
            element.style.transform = `
                translateZ(${20 + Math.abs(currentX) + Math.abs(currentY)}px)
                rotateX(${currentY}deg)
                rotateY(${currentX}deg)
                scale(${1 + Math.abs(currentX) * 0.005})
            `;
            
            requestAnimationFrame(animate);
        };

        element.addEventListener('mousemove', handleMouseMove);
        element.addEventListener('mouseenter', handleMouseEnter);
        element.addEventListener('mouseleave', handleMouseLeave);
        
        animate();
    }

    createFloatingElements() {
        const container = document.createElement('div');
        container.className = 'floating-3d';
        document.body.appendChild(container);

        // Create 3D floating shapes
        for (let i = 0; i < 4; i++) {
            const shape = document.createElement('div');
            shape.className = `shape-3d shape-3d-${i + 1}`;
            container.appendChild(shape);
        }
    }

    init3DCursor() {
        const cursor = document.createElement('div');
        cursor.className = 'cursor-3d';
        cursor.innerHTML = '<div class="cursor-dot"></div><div class="cursor-ring"></div>';
        document.body.appendChild(cursor);

        const style = document.createElement('style');
        style.textContent = `
            .cursor-3d {
                position: fixed;
                width: 20px;
                height: 20px;
                pointer-events: none;
                z-index: 9999;
                mix-blend-mode: difference;
                transition: transform 0.1s ease-out;
            }
            
            .cursor-dot {
                position: absolute;
                width: 4px;
                height: 4px;
                background: white;
                border-radius: 50%;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
            }
            
            .cursor-ring {
                position: absolute;
                width: 20px;
                height: 20px;
                border: 2px solid white;
                border-radius: 50%;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                transition: all 0.3s ease-out;
            }
            
            .cursor-3d.hover .cursor-ring {
                width: 30px;
                height: 30px;
                border-color: #667eea;
            }
            
            .cursor-3d.click .cursor-ring {
                width: 15px;
                height: 15px;
            }
        `;
        document.head.appendChild(style);

        let mouseX = 0, mouseY = 0;
        let cursorX = 0, cursorY = 0;

        document.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;
        });

        const animateCursor = () => {
            cursorX += (mouseX - cursorX) * 0.1;
            cursorY += (mouseY - cursorY) * 0.1;
            
            cursor.style.transform = `translate3d(${cursorX - 10}px, ${cursorY - 10}px, 0)`;
            
            requestAnimationFrame(animateCursor);
        };

        // Add hover effects
        document.querySelectorAll('a, button, .btn-3d, .card-3d').forEach(element => {
            element.addEventListener('mouseenter', () => cursor.classList.add('hover'));
            element.addEventListener('mouseleave', () => cursor.classList.remove('hover'));
            element.addEventListener('mousedown', () => cursor.classList.add('click'));
            element.addEventListener('mouseup', () => cursor.classList.remove('click'));
        });

        animateCursor();
    }

    setupParallaxEffects() {
        const parallaxElements = document.querySelectorAll('[data-parallax]');
        
        const handleScroll = () => {
            const scrollY = window.scrollY;
            
            parallaxElements.forEach(element => {
                const speed = element.dataset.parallax || 0.5;
                const yPos = -(scrollY * speed);
                const depth = element.dataset.depth || 10;
                
                element.style.transform = `
                    translate3d(0, ${yPos}px, ${depth}px)
                    rotateX(${yPos * 0.01}deg)
                `;
            });
        };

        window.addEventListener('scroll', handleScroll);
        handleScroll();
    }

    initParticleEffects() {
        // Create particle system for special effects
        this.createParticleSystem();
    }

    createParticleSystem() {
        const canvas = document.createElement('canvas');
        canvas.className = 'particle-canvas';
        canvas.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
        `;
        document.body.appendChild(canvas);

        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const particles = [];
        const particleCount = 50;

        class Particle {
            constructor() {
                this.reset();
            }

            reset() {
                this.x = Math.random() * canvas.width;
                this.y = Math.random() * canvas.height;
                this.z = Math.random() * 1000;
                this.size = Math.random() * 2 + 1;
                this.speedX = (Math.random() - 0.5) * 0.5;
                this.speedY = (Math.random() - 0.5) * 0.5;
                this.speedZ = Math.random() * 2 + 1;
                this.opacity = Math.random() * 0.5 + 0.2;
            }

            update() {
                this.x += this.speedX;
                this.y += this.speedY;
                this.z -= this.speedZ;

                if (this.z <= 0) {
                    this.reset();
                    this.z = 1000;
                }

                // Wrap around edges
                if (this.x < 0) this.x = canvas.width;
                if (this.x > canvas.width) this.x = 0;
                if (this.y < 0) this.y = canvas.height;
                if (this.y > canvas.height) this.y = 0;
            }

            draw() {
                const scale = 1000 / (1000 + this.z);
                const x2d = (this.x - canvas.width / 2) * scale + canvas.width / 2;
                const y2d = (this.y - canvas.height / 2) * scale + canvas.height / 2;
                const size = this.size * scale;

                ctx.globalAlpha = this.opacity * scale;
                ctx.fillStyle = '#ffffff';
                ctx.beginPath();
                ctx.arc(x2d, y2d, size, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        // Create particles
        for (let i = 0; i < particleCount; i++) {
            particles.push(new Particle());
        }

        const animate = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            particles.forEach(particle => {
                particle.update();
                particle.draw();
            });

            requestAnimationFrame(animate);
        };

        animate();

        // Handle resize
        window.addEventListener('resize', () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        });
    }

    setupIntersectionObserver() {
        const options = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in-3d');
                    this.animateElement3D(entry.target);
                }
            });
        }, options);

        // Observe elements for 3D animations
        document.querySelectorAll('.card-3d, .stat-card-3d, .quiz-container-3d').forEach(element => {
            observer.observe(element);
        });
    }

    animateElement3D(element) {
        element.style.opacity = '0';
        element.style.transform = 'translateZ(-100px) rotateY(90deg)';

        setTimeout(() => {
            element.style.transition = 'all 0.8s cubic-bezier(0.23, 1, 0.320, 1)';
            element.style.opacity = '1';
            element.style.transform = 'translateZ(0) rotateY(0deg)';
        }, 100);
    }

    initAudioEffects() {
        // Create audio context for 3D sound effects
        this.audioContext = null;
        
        // Initialize audio on first user interaction
        const initAudio = () => {
            if (!this.audioContext) {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            }
        };

        document.addEventListener('click', initAudio, { once: true });
        document.addEventListener('touchstart', initAudio, { once: true });
    }

    play3DSound(type) {
        if (!this.audioContext) return;

        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);

        switch (type) {
            case 'hover':
                oscillator.frequency.value = 800;
                gainNode.gain.value = 0.1;
                break;
            case 'click':
                oscillator.frequency.value = 1200;
                gainNode.gain.value = 0.2;
                break;
            case 'success':
                oscillator.frequency.value = 600;
                gainNode.gain.value = 0.3;
                break;
        }

        oscillator.start();
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.1);
        oscillator.stop(this.audioContext.currentTime + 0.1);
    }

    setupEventListeners() {
        // Add 3D sound effects to interactions
        document.querySelectorAll('.btn-3d, .card-3d').forEach(element => {
            element.addEventListener('mouseenter', () => this.play3DSound('hover'));
            element.addEventListener('click', () => this.play3DSound('click'));
        });

        // Add keyboard navigation for 3D effects
        this.setupKeyboardNavigation();
        
        // Add touch gestures for mobile 3D effects
        this.setupTouchGestures();
    }

    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            // 3D navigation with arrow keys
            if (e.key === 'ArrowUp' || e.key === 'ArrowDown' || 
                e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
                e.preventDefault();
                this.navigate3D(e.key);
            }
        });
    }

    navigate3D(direction) {
        const focusableElements = document.querySelectorAll('a, button, input, select, textarea');
        const currentIndex = Array.from(focusableElements).indexOf(document.activeElement);
        
        let nextIndex;
        switch (direction) {
            case 'ArrowUp':
                nextIndex = Math.max(0, currentIndex - 1);
                break;
            case 'ArrowDown':
                nextIndex = Math.min(focusableElements.length - 1, currentIndex + 1);
                break;
            default:
                return;
        }
        
        if (nextIndex !== currentIndex && focusableElements[nextIndex]) {
            focusableElements[nextIndex].focus();
            this.play3DSound('hover');
        }
    }

    setupTouchGestures() {
        let touchStartX = 0;
        let touchStartY = 0;

        document.addEventListener('touchstart', (e) => {
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
        });

        document.addEventListener('touchmove', (e) => {
            if (!touchStartX || !touchStartY) return;

            const touchEndX = e.touches[0].clientX;
            const touchEndY = e.touches[0].clientY;

            const deltaX = touchEndX - touchStartX;
            const deltaY = touchEndY - touchStartY;

            // Apply 3D tilt effect based on touch movement
            const element = e.target.closest('.card-3d, .form-3d');
            if (element) {
                const rotateY = deltaX * 0.1;
                const rotateX = deltaY * -0.1;
                
                element.style.transform = `
                    translateZ(20px)
                    rotateX(${rotateX}deg)
                    rotateY(${rotateY}deg)
                `;
            }
        });

        document.addEventListener('touchend', (e) => {
            const element = e.target.closest('.card-3d, .form-3d');
            if (element) {
                element.style.transform = 'translateZ(20px) rotateX(0deg) rotateY(0deg)';
            }
            
            touchStartX = 0;
            touchStartY = 0;
        });
    }

    // Public API for external use
    add3DEffect(selector, effect) {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
            switch (effect) {
                case 'float':
                    this.addFloatingEffect(element);
                    break;
                case 'rotate':
                    this.addRotatingEffect(element);
                    break;
                case 'pulse':
                    this.addPulsingEffect(element);
                    break;
                default:
                    this.add3DHoverEffect(element);
            }
        });
    }

    addFloatingEffect(element) {
        element.style.animation = 'float-3d 6s ease-in-out infinite';
    }

    addRotatingEffect(element) {
        element.style.animation = 'rotate-3d 10s linear infinite';
    }

    addPulsingEffect(element) {
        element.style.animation = 'pulse-3d 2s ease-in-out infinite';
    }

    // Performance optimization
    optimizePerformance() {
        // Reduce effects on low-end devices
        if (this.isLowEndDevice()) {
            document.body.classList.add('reduced-motion');
            this.disableHeavyEffects();
        }
    }

    isLowEndDevice() {
        // Simple check for low-end devices
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        
        if (!gl) return true;
        
        const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
        if (debugInfo) {
            const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
            return renderer.includes('Software') || renderer.includes('Microsoft');
        }
        
        return false;
    }

    disableHeavyEffects() {
        // Disable particle effects
        const particleCanvas = document.querySelector('.particle-canvas');
        if (particleCanvas) {
            particleCanvas.remove();
        }
        
        // Reduce floating elements
        const floatingElements = document.querySelectorAll('.shape-3d');
        floatingElements.forEach(element => element.remove());
    }
}

// 3D CSS Animations
const style3D = document.createElement('style');
style3D.textContent = `
    @keyframes float-3d {
        0%, 100% { transform: translate3d(0, 0, 0) rotateX(0deg) rotateY(0deg); }
        25% { transform: translate3d(30px, -30px, 50px) rotateX(90deg) rotateY(45deg); }
        50% { transform: translate3d(-20px, 20px, 100px) rotateX(180deg) rotateY(90deg); }
        75% { transform: translate3d(-30px, -20px, 50px) rotateX(270deg) rotateY(135deg); }
    }
    
    @keyframes rotate-3d {
        0% { transform: translate3d(0, 0, 0) rotateX(0deg) rotateY(0deg) rotateZ(0deg); }
        100% { transform: translate3d(0, 0, 0) rotateX(360deg) rotateY(360deg) rotateZ(360deg); }
    }
    
    @keyframes pulse-3d {
        0%, 100% { transform: translate3d(0, 0, 0) scale(1); }
        50% { transform: translate3d(0, 0, 20px) scale(1.1); }
    }
    
    .animate-in-3d {
        animation: slideIn3D 0.8s cubic-bezier(0.23, 1, 0.320, 1) forwards;
    }
    
    @keyframes slideIn3D {
        0% {
            opacity: 0;
            transform: translate3d(-100px, 0, -200px) rotateY(90deg);
        }
        100% {
            opacity: 1;
            transform: translate3d(0, 0, 0) rotateY(0deg);
        }
    }
    
    .reduced-motion * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
`;
document.head.appendChild(style3D);

// Initialize 3D effects when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.advanced3D = new Advanced3DEffects();
});

// Export for global access
window.Advanced3DEffects = Advanced3DEffects;
