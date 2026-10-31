// انیمیشن‌های بخش چرا پیکسوریا و CTA با Anime.js

document.addEventListener('DOMContentLoaded', function() {
    // انیمیشن بخش چرا پیکسوریا
    const whyItems = document.querySelectorAll('.why-item');

    // تابع انیمیشن هر آیتم
    function animateWhyItem(item, index) {
        // انیمیشن اولیه - ظهور
        anime({
            targets: item,
            opacity: [0, 1],
            translateY: [50, 0],
            duration: 800,
            easing: 'easeOutExpo',
            delay: index * 150
        });

        // انیمیشن هنگام hover
        item.addEventListener('mouseenter', function() {
            anime({
                targets: this.querySelector('.ascii-text'),
                scale: [1, 1.1],
                duration: 400,
                easing: 'easeOutElastic(1, .8)'
            });

            anime({
                targets: this.querySelector('h3'),
                color: '#e8c47a',
                duration: 300,
                easing: 'easeOutQuad'
            });
        });

        item.addEventListener('mouseleave', function() {
            anime({
                targets: this.querySelector('.ascii-text'),
                scale: [1.1, 1],
                duration: 400,
                easing: 'easeOutElastic(1, .8)'
            });

            anime({
                targets: this.querySelector('h3'),
                color: '#f5f3ee',
                duration: 300,
                easing: 'easeOutQuad'
            });
        });
    }

    // اجرای انیمیشن‌ها
    whyItems.forEach((item, index) => {
        animateWhyItem(item, index);
    });

    // انیمیشن بخش CTA
    const ctaSection = document.querySelector('.cta-section');
    const ctaTitle = document.querySelector('.cta-title');
    const ctaText = document.querySelector('.cta-text');
    const contactItems = document.querySelectorAll('.contact-item');
    const buttons = document.querySelectorAll('.cta-btn');

    // انیمیشن عنوان CTA
    anime({
        targets: ctaTitle,
        opacity: [0, 1],
        translateY: [-30, 0],
        scale: [0.9, 1],
        duration: 1000,
        easing: 'easeOutExpo'
    });

    // انیمیشن متن CTA
    anime({
        targets: ctaText,
        opacity: [0, 1],
        translateY: [30, 0],
        duration: 1000,
        delay: 200,
        easing: 'easeOutExpo'
    });

    // انیمیشن آیتم‌های تماس
    contactItems.forEach((item, index) => {
        anime({
            targets: item,
            opacity: [0, 1],
            translateX: [index % 2 === 0 ? -50 : 50, 0],
            duration: 800,
            delay: 400 + (index * 150),
            easing: 'easeOutExpo'
        });
    });

    // انیمیشن دکمه‌ها
    buttons.forEach((btn, index) => {
        anime({
            targets: btn,
            opacity: [0, 1],
            scale: [0.8, 1],
            duration: 600,
            delay: 700 + (index * 200),
            easing: 'easeOutBack'
        });

        // انیمیشن هنگام کلیک
        btn.addEventListener('click', function(e) {
            // ایجاد موج
            const ripple = document.createElement('div');
            ripple.style.position = 'absolute';
            ripple.style.width = '20px';
            ripple.style.height = '20px';
            ripple.style.background = 'rgba(255, 255, 255, 0.5)';
            ripple.style.borderRadius = '50%';
            ripple.style.transform = 'translate(-50%, -50%)';
            ripple.style.pointerEvents = 'none';
            ripple.style.animation = 'ripple 0.6s ease-out';

            const rect = this.getBoundingClientRect();
            ripple.style.left = (e.clientX - rect.left) + 'px';
            ripple.style.top = (e.clientY - rect.top) + 'px';

            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);

            setTimeout(() => ripple.remove(), 600);
        });
    });

    // انیمیشن کدهای شناور
    const floatingCodes = document.querySelectorAll('.floating-code');

    floatingCodes.forEach((code, index) => {
        anime({
            targets: code,
            opacity: [0, 1, 0],
            translateY: [0, -30, 0],
            rotate: [0, 5, 0],
            duration: 6000,
            delay: index * 2000,
            easing: 'easeInOutSine',
            loop: true
        });
    });

    // Intersection Observer برای انیمیشن هنگام اسکرول
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                if (entry.target.classList.contains('why-pixoria-section')) {
                    whyItems.forEach((item, index) => {
                        setTimeout(() => {
                            item.style.transform = 'translateY(0)';
                        }, index * 100);
                    });
                }
            }
        });
    }, observerOptions);

    // مشاهده بخش‌ها
    if (ctaSection) observer.observe(ctaSection);
    if (document.querySelector('.why-pixoria-section')) {
        document.querySelector('.why-pixoria-section').forEach(section => {
            observer.observe(section);
        });
    }
});

// افزودن CSS برای انیمیشن ripple
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            width: 200px;
            height: 200px;
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);