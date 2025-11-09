/**
 * Main JavaScript for Shree Vinayaga E-Commerce
 * Handles mobile menu, form validation, and UI interactions
 */

// Mobile Menu Toggle
function toggleMobileMenu() {
    const menu = document.getElementById('navbarMenu');
    menu.classList.toggle('active');
}

// Close mobile menu when clicking outside
document.addEventListener('click', function(event) {
    const menu = document.getElementById('navbarMenu');
    const toggle = document.querySelector('.navbar-toggle');
    
    if (menu && toggle && menu.classList.contains('active')) {
        if (!menu.contains(event.target) && !toggle.contains(event.target)) {
            menu.classList.remove('active');
        }
    }
});

// Form Validation Helpers
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    const re = /^[\d\s\+\-\(\)]+$/;
    return re.test(phone) && phone.replace(/\D/g, '').length >= 10;
}

// Add fade-in animation to cards on scroll
function addFadeInAnimation() {
    const cards = document.querySelectorAll('.card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    cards.forEach(card => {
        observer.observe(card);
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Add fade-in animations
    addFadeInAnimation();
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
    
    // Image lazy loading fallback
    const images = document.querySelectorAll('img[loading="lazy"]');
    if ('loading' in HTMLImageElement.prototype) {
        // Browser supports lazy loading
        images.forEach(img => {
            img.src = img.dataset.src || img.src;
        });
    } else {
        // Fallback for browsers that don't support lazy loading
        const lazyImageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src || img.src;
                    lazyImageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(img => lazyImageObserver.observe(img));
    }
});

// Enable hover-to-rotate for <model-viewer> elements and thumbnail switching
function setupModelViewers() {
    // Toggle auto-rotate on hover so users can see rotation while hovering
    const models = document.querySelectorAll('.product-model, model-viewer');
    models.forEach(m => {
        m.addEventListener('mouseenter', () => {
            try { m.setAttribute('auto-rotate', ''); } catch (e) {}
        });
        m.addEventListener('mouseleave', () => {
            try { m.removeAttribute('auto-rotate'); } catch (e) {}
        });
    });
}

// Change the main model viewer's src (used by thumbnails)
function changeModel(src, thumbEl) {
    const mainModel = document.getElementById('mainModel');
    if (!mainModel) return;
    // Update src
    mainModel.src = src;

    // update active thumbnail classes
    document.querySelectorAll('.thumbnail, .model-thumb').forEach(t => t.classList.remove('active'));
    if (thumbEl) thumbEl.classList.add('active');
}

// Initialize model viewers after DOM ready
document.addEventListener('DOMContentLoaded', function() {
    setupModelViewers();
});

// Smooth scroll to top
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Add scroll-to-top button
window.addEventListener('scroll', function() {
    const scrollBtn = document.getElementById('scrollToTop');
    if (scrollBtn) {
        if (window.pageYOffset > 300) {
            scrollBtn.style.display = 'block';
        } else {
            scrollBtn.style.display = 'none';
        }
    }
});

// Quantity input validation
document.querySelectorAll('input[type="number"]').forEach(input => {
    input.addEventListener('input', function() {
        const min = parseInt(this.min) || 1;
        const max = parseInt(this.max) || Infinity;
        let value = parseInt(this.value);
        
        if (isNaN(value) || value < min) {
            this.value = min;
        } else if (value > max) {
            this.value = max;
        }
    });
});

// Confirm before deleting
function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this item?');
}

// Price formatting
function formatPrice(amount) {
    return '₹' + parseFloat(amount).toFixed(2);
}

// Console message for developers
console.log('%cShree Vinayaga E-Commerce', 'color: #007BFF; font-size: 20px; font-weight: bold;');
console.log('%cBuilt with Flask, PostgreSQL, and modern web technologies', 'color: #6C757D; font-size: 12px;');
