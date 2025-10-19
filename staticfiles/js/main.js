// JOOG E-commerce JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeCartFunctionality();
    initializeCouponValidation();
    initializeAnimations();
    initializeImageLazyLoading();
    initializeDropdowns();
    initializePincodeHelpers();
    initializeSavedAddressToggle();
    initializeHeaderScrollEffect();
    initializeMobileMenu();
});

// Mobile Menu Functionality
function initializeMobileMenu() {
    window.toggleMobileMenu = function() {
        const mobileMenu = document.getElementById('mobile-menu');
        if (mobileMenu) {
            mobileMenu.classList.toggle('hidden');
        }
    };
    
    window.toggleMobileCategories = function() {
        const categoriesMenu = document.getElementById('mobile-categories-menu');
        const categoriesIcon = document.getElementById('mobile-categories-icon');
        
        if (categoriesMenu && categoriesIcon) {
            categoriesMenu.classList.toggle('hidden');
            categoriesIcon.classList.toggle('rotate-180');
        }
    };
}

// Cart Functionality
function initializeCartFunctionality() {
    const cartItems = document.querySelectorAll('.cart-item');
    
    cartItems.forEach(item => {
        const itemId = item.dataset.itemId;
        const quantityDisplay = item.querySelector('.quantity-display');
        const quantityBtns = item.querySelectorAll('.quantity-btn');
        const itemTotal = item.querySelector('.item-total');
        
        quantityBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const action = this.dataset.action;
                let currentQuantity = parseInt(quantityDisplay.textContent);
                
                if (action === 'increase') {
                    currentQuantity++;
                } else if (action === 'decrease' && currentQuantity > 1) {
                    currentQuantity--;
                } else if (action === 'decrease' && currentQuantity === 1) {
                    // Remove item
                    if (confirm('Remove this item from cart?')) {
                        currentQuantity = 0;
                    } else {
                        return;
                    }
                }
                
                updateCartItem(itemId, currentQuantity, quantityDisplay, itemTotal);
            });
        });
    });
}

async function updateCartItem(itemId, quantity, quantityDisplay, itemTotal) {
    try {
        const response = await fetch(`/orders/update-cart-item/${itemId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ quantity: quantity })
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (data.removed) {
                // Remove the entire item row
                const cartItem = quantityDisplay.closest('.cart-item');
                cartItem.style.animation = 'slideOut 0.3s ease-out';
                setTimeout(() => cartItem.remove(), 300);
            } else {
                quantityDisplay.textContent = quantity;
                itemTotal.textContent = `₹${data.item_total}`;
            }
            
            // Update cart totals
            updateCartTotals(data.cart_total);
        }
    } catch (error) {
        console.error('Error updating cart:', error);
        showNotification('Error updating cart', 'error');
    }
}

// Coupon Validation
function initializeCouponValidation() {
    const applyCouponBtn = document.getElementById('apply-coupon');
    const couponInput = document.getElementById('coupon-input');
    
    if (applyCouponBtn && couponInput) {
        applyCouponBtn.addEventListener('click', async function() {
            const code = couponInput.value.trim();
            
            if (!code) {
                showCouponMessage('Please enter a coupon code', 'error');
                return;
            }
            
            this.disabled = true;
            this.innerHTML = '<div class="loading mr-2"></div> Validating...';
            
            try {
                const response = await fetch('/coupons/validate-coupon/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: JSON.stringify({ code: code })
                });
                
                const data = await response.json();
                
                if (data.valid) {
                    showCouponMessage(data.message, 'success');
                    applyCouponDiscount(data.discount_type, data.discount_value, data.discount_amount);
                    
                    // Set the validated coupon in the hidden field for form submission
                    const validatedCouponField = document.getElementById('validated-coupon');
                    if (validatedCouponField) {
                        validatedCouponField.value = code;
                    }
                    
                    // Store coupon data for checkout
                    sessionStorage.setItem('appliedCoupon', JSON.stringify({
                        code: code,
                        discount_type: data.discount_type,
                        discount_value: data.discount_value,
                        discount_amount: data.discount_amount
                    }));
                } else {
                    showCouponMessage(data.message, 'error');
                    
                    // Clear the validated coupon field
                    const validatedCouponField = document.getElementById('validated-coupon');
                    if (validatedCouponField) {
                        validatedCouponField.value = '';
                    }
                    
                    // Clear any previously applied coupon
                    sessionStorage.removeItem('appliedCoupon');
                    clearCouponDiscount();
                }
            } catch (error) {
                console.error('Error validating coupon:', error);
                showCouponMessage('Error validating coupon', 'error');
            } finally {
                this.disabled = false;
                this.innerHTML = 'Apply';
            }
        });
        
        // Check for previously applied coupon on page load
        const appliedCoupon = sessionStorage.getItem('appliedCoupon');
        if (appliedCoupon) {
            try {
                const couponData = JSON.parse(appliedCoupon);
                couponInput.value = couponData.code;
                applyCouponDiscount(couponData.discount_type, couponData.discount_value, couponData.discount_amount);
                showCouponMessage('Coupon applied', 'success');
            } catch (e) {
                sessionStorage.removeItem('appliedCoupon');
            }
        }
    }
}

function showCouponMessage(message, type) {
    const couponMessage = document.getElementById('coupon-message');
    if (couponMessage) {
        couponMessage.className = type === 'success' ? 'text-green-600 text-sm' : 'text-red-600 text-sm';
        couponMessage.textContent = message;
    }
}

function applyCouponDiscount(discountType, discountValue, discountAmount) {
    const subtotalElement = document.getElementById('subtotal');
    const discountRow = document.getElementById('discount-row');
    const discountAmountElement = document.getElementById('discount-amount');
    const finalTotal = document.getElementById('final-total');
    
    if (subtotalElement && discountRow && discountAmountElement && finalTotal) {
        const subtotal = parseFloat(subtotalElement.textContent.replace('₹', ''));
        
        // Use the discount amount calculated by the server
        const discount = discountAmount || 0;
        
        discountAmountElement.textContent = `-₹${discount.toFixed(2)}`;
        finalTotal.textContent = `₹${(subtotal - discount).toFixed(2)}`;
        discountRow.style.display = 'flex';
    }
}

function clearCouponDiscount() {
    const discountRow = document.getElementById('discount-row');
    const subtotalElement = document.getElementById('subtotal');
    const finalTotal = document.getElementById('final-total');
    
    if (discountRow && subtotalElement && finalTotal) {
        discountRow.style.display = 'none';
        const subtotal = parseFloat(subtotalElement.textContent.replace('₹', ''));
        finalTotal.textContent = `₹${subtotal.toFixed(2)}`;
    }
}

// Animations
function initializeAnimations() {
    // Add fade-in animation to elements when they come into view
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements that should animate
    document.querySelectorAll('.product-card, .category-card, .admin-card').forEach(el => {
        observer.observe(el);
    });
}

// Image Lazy Loading
function initializeImageLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('loading');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Utility Functions
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function updateCartTotals(cartTotal) {
    const cartSubtotal = document.querySelector('.cart-subtotal');
    const cartTotalElement = document.querySelector('.cart-total');
    
    if (cartSubtotal) cartSubtotal.textContent = `₹${cartTotal}`;
    if (cartTotalElement) cartTotalElement.textContent = `₹${cartTotal}`;
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} fixed top-4 right-4 z-50 max-w-sm animate-slide-in`;
    notification.innerHTML = `
        <div class="flex justify-between items-center">
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-gray-500 hover:text-gray-700">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'fadeOut 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}

// Add to cart with AJAX
function addToCartAjax(productId) {
    const btn = event.target;
    const originalText = btn.innerHTML;
    
    btn.disabled = true;
    btn.innerHTML = '<div class="loading mr-2"></div> Adding...';
    
    fetch(`/orders/add-to-cart/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest',
        },
        body: new FormData()
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            // Update cart counter
            const cartCounter = document.querySelector('.cart-counter');
            if (cartCounter) {
                cartCounter.textContent = data.cart_total;
            }
        } else {
            showNotification('Error adding to cart', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error adding to cart', 'error');
    })
    .finally(() => {
        btn.disabled = false;
        btn.innerHTML = originalText;
    });
}

// Search functionality
function initializeSearch() {
    const searchInput = document.querySelector('input[name="q"]');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                if (this.value.length > 2) {
                    // Perform search
                    window.location.href = `${window.location.pathname}?q=${encodeURIComponent(this.value)}`;
                }
            }, 500);
        });
    }
}

// Mobile menu toggle
function toggleMobileMenu() {
    const mobileMenu = document.getElementById('mobile-menu');
    if (mobileMenu) {
        mobileMenu.classList.toggle('hidden');
    }
}

// Mobile categories toggle
function toggleMobileCategories() {
    const mobileCategoriesMenu = document.getElementById('mobile-categories-menu');
    const mobileCategoriesIcon = document.getElementById('mobile-categories-icon');
    
    if (mobileCategoriesMenu && mobileCategoriesIcon) {
        mobileCategoriesMenu.classList.toggle('hidden');
        mobileCategoriesIcon.classList.toggle('rotate-180');
    }
}

// Smooth scroll to sections
function smoothScrollTo(target) {
    const element = document.querySelector(target);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Initialize search on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeSearch();
});

// Dropdown functionality
function initializeDropdowns() {
    // Handle all dropdowns
    const dropdowns = document.querySelectorAll('.dropdown');
    
    dropdowns.forEach(dropdown => {
        const dropdownButton = dropdown.querySelector('button');
        const dropdownMenu = dropdown.querySelector('.dropdown-menu');
        
        if (dropdownButton && dropdownMenu) {
            // Toggle dropdown on click
            dropdownButton.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                // Close other dropdowns first
                dropdowns.forEach(otherDropdown => {
                    if (otherDropdown !== dropdown) {
                        const otherMenu = otherDropdown.querySelector('.dropdown-menu');
                        if (otherMenu) {
                            otherMenu.classList.add('hidden');
                        }
                    }
                });
                
                // Toggle current dropdown
                dropdownMenu.classList.toggle('hidden');
            });
            
            // Handle hover for desktop
            dropdown.addEventListener('mouseenter', function() {
                dropdownMenu.classList.remove('hidden');
            });
            
            dropdown.addEventListener('mouseleave', function() {
                dropdownMenu.classList.add('hidden');
            });
        }
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        dropdowns.forEach(dropdown => {
            if (!dropdown.contains(e.target)) {
                const dropdownMenu = dropdown.querySelector('.dropdown-menu');
                if (dropdownMenu) {
                    dropdownMenu.classList.add('hidden');
                }
            }
        });
    });
    
    // Close dropdowns on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            dropdowns.forEach(dropdown => {
                const dropdownMenu = dropdown.querySelector('.dropdown-menu');
                if (dropdownMenu) {
                    dropdownMenu.classList.add('hidden');
                }
            });
        }
    });
}

// PIN code helper: constrain to 6 digits and suggest city for known PINs
function initializePincodeHelpers(){
    const pinSelectors = ['#id_postal_code', '#id_shipping_postal_code'];
    const citySelectors = ['#id_city', '#id_shipping_city'];
    const countrySelectors = ['#id_country', '#id_shipping_country'];
    const stateSelectors = ['#id_state', '#id_shipping_state'];
    const hints = { '560001':'Bengaluru', '560027':'Bengaluru', '560002':'Bengaluru' };
    pinSelectors.forEach((sel, idx)=>{
        const pin = document.querySelector(sel);
        const city = document.querySelector(citySelectors[idx]);
        const country = document.querySelector(countrySelectors[idx]);
        const state = document.querySelector(stateSelectors[idx]);
        if(pin){
            pin.setAttribute('maxlength','6');
            pin.addEventListener('input', function(){ this.value = this.value.replace(/[^0-9]/g,'').slice(0,6); });
            pin.addEventListener('blur', async function(){
                const v = this.value;
                const parent = this.closest('div');
                const setErr = (msg)=>{
                    if(parent){ let err = parent.querySelector('.form-error'); if(!err){ err = document.createElement('div'); err.className='form-error'; parent.appendChild(err);} err.textContent=msg; }
                };
                const clearErr = ()=>{ const e = parent && parent.querySelector('.form-error'); if(e && e.textContent.includes('PIN')) e.remove(); };
                if(v && !/^\d{6}$/.test(v)){ setErr('Enter a valid 6-digit PIN code.'); return; } else { clearErr(); }

                // Try API for India PIN -> fetch PO details
                try{
                    const res = await fetch(`https://api.postalpincode.in/pincode/${v}`);
                    const data = await res.json();
                    if(Array.isArray(data) && data[0] && data[0].Status === 'Success'){
                        const po = data[0].PostOffice && data[0].PostOffice[0];
                        if(city && po && po.District){ city.value = po.District; }
                        if(state && po && po.State){ state.value = po.State; }
                        if(country){ country.value = (po && po.Country) ? po.Country : 'India'; }
                    } else if(city && hints[v]){
                        city.value = hints[v];
                        if(country){ country.value = 'India'; }
                    }
                } catch(err){
                    if(city && hints[v]){ city.value = hints[v]; }
                    if(country){ country.value = 'India'; }
                }
            });
        }
    });
}

// Toggle form fields based on "Use saved address"
function initializeSavedAddressToggle(){
    const useSaved = document.getElementById('use_saved');
    const form = document.getElementById('checkout-form');
    if(!useSaved || !form) return;
    const inputs = ['id_shipping_address','id_shipping_city','id_shipping_state','id_shipping_postal_code','id_shipping_country']
        .map(id => document.getElementById(id)).filter(Boolean);

    const setDisabled = (disabled)=>{
        inputs.forEach(el=>{ el.readOnly = disabled; el.classList.toggle('bg-gray-100', disabled); });
    };

    useSaved.addEventListener('change', ()=>{
        setDisabled(useSaved.checked);
    });

    // Initialize state on load
    setDisabled(useSaved.checked);
}

// Header scroll effect to merge header with content
function initializeHeaderScrollEffect(){
    const header = document.querySelector('.nav-header');
    if(!header) return;
    const onScroll = ()=>{
        if(window.scrollY > 10){
            header.classList.add('scrolled');
            header.classList.remove('is-top');
        } else {
            header.classList.remove('scrolled');
            header.classList.add('is-top');
        }
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
}