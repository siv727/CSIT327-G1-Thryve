/* * Main Marketplace Logic
 * Requires window.MARKETPLACE_CONFIG and 'categories-data' JSON script to be loaded in the HTML
 */

document.addEventListener('DOMContentLoaded', function () {
// --- Toast Notification System ---
function showToast(message) {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    toastMessage.textContent = message;

    // Show toast
    toast.classList.remove('translate-y-full', 'opacity-0');
    toast.classList.add('translate-y-0', 'opacity-100');

    // Hide after 3 seconds
    setTimeout(() => {
        toast.classList.remove('translate-y-0', 'opacity-100');
        toast.classList.add('translate-y-full', 'opacity-0');
    }, 3000);
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize everything
    initLocationAutocomplete();

    // Auto-open modal if requested (e.g. on validation error)
    if (window.MARKETPLACE_CONFIG.showCreateModal) {
        const modal = document.getElementById('add-listing-modal');
        if (modal) {
            modal.classList.remove('hidden');
            modal.classList.add('flex');
            setTimeout(() => initLocationAutocomplete(), 300);
        }
    }

    // Initialize Category Selectors
    categorySelector.init();
    editCategorySelector.init();

    // Setup other event listeners
    setupRealTimeValidation();

    // Initialize Book Now Modal event listeners
    const closeModalBtn = document.getElementById('close-book-now-modal');
    const cancelModalBtn = document.getElementById('cancel-book-now-btn');
    const bookNowModal = document.getElementById('book-now-modal');
    const bookNowForm = document.getElementById('book-now-form');

    closeModalBtn?.addEventListener('click', closeBookNowModal);
    cancelModalBtn?.addEventListener('click', closeBookNowModal);
    bookNowModal?.addEventListener('click', (e) => {
        if (e.target === bookNowModal) closeBookNowModal();
    });

    // Handle AJAX submission for Book Now form
    bookNowForm?.addEventListener('submit', function(e) {
        e.preventDefault();

        const requestBookingBtn = document.getElementById('request-booking-btn');
        requestBookingBtn.disabled = true;
        requestBookingBtn.textContent = 'Sending...';

        // Get CSRF token
        const csrfToken = this.querySelector('[name=csrfmiddlewaretoken]').value;
        const formData = new URLSearchParams(new FormData(this));

        // Send AJAX request to the new booking app API endpoint
        fetch('/bookings/request/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(`Success! ${data.message}`);
                closeBookNowModal();
            } else {
                requestBookingBtn.textContent = 'Request Booking'; // Restore button state
                showToast(`Error: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Submission error:', error);
            requestBookingBtn.textContent = 'Request Booking'; // Restore button state
            showToast('An unknown error occurred during submission. Check your network or form data.');
        })
        .finally(() => {
            requestBookingBtn.disabled = false;
        });
    });
});

// --- Data Helper ---
function getCategoriesData() {
    try {
        const script = document.getElementById('categories-data');
        if (script) {
            return JSON.parse(script.textContent);
        }
    } catch (e) {
        console.error("Could not parse categories data", e);
    }
    return {};
}

// --- Location Autocomplete ---
function initLocationAutocomplete() {
    const locationInput = document.getElementById('id_location');

    if (!locationInput || locationInput.dataset.geocoderInitialized === 'true') {
        return;
    }

    locationInput.dataset.geocoderInitialized = 'true';
    const searchCache = new Map();

    const commonLocations = {
        'cebu': [{ display_name: 'Cebu City, Cebu, Philippines' }, { display_name: 'Mandaue City, Cebu, Philippines' }],
        'manila': [{ display_name: 'Manila, Metro Manila, Philippines' }, { display_name: 'Quezon City, Metro Manila, Philippines' }],
        'davao': [{ display_name: 'Davao City, Davao del Sur, Philippines' }]
    };

    let geocodeTimeout;
    let currentDropdown = null;
    let lastQuery = '';

    locationInput.addEventListener('input', function () {
        clearTimeout(geocodeTimeout);
        const query = this.value.trim();

        if (query === lastQuery || query.length < 2) {
            removeDropdown();
            return;
        }
        lastQuery = query;
        geocodeTimeout = setTimeout(() => {
            searchLocations(query, locationInput);
        }, 150);
    });

    document.addEventListener('click', function (e) {
        if (!locationInput.parentNode.contains(e.target)) {
            removeDropdown();
        }
    });

    function searchLocations(query, input) {
        const lowerQuery = query.toLowerCase();
        if (commonLocations[lowerQuery]) {
            showLocationSuggestions(commonLocations[lowerQuery], input);
            return;
        }
        if (searchCache.has(query)) {
            showLocationSuggestions(searchCache.get(query), input);
            return;
        }

        const searchUrl = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}+Philippines&countrycodes=ph&limit=4&addressdetails=1&dedupe=1`;

        fetch(searchUrl)
            .then(response => response.json())
            .then(data => {
                searchCache.set(query, data);
                showLocationSuggestions(data, input);
            })
            .catch(error => {
                console.error('Geocoding error:', error);
                removeDropdown();
            });
    }

    function showLocationSuggestions(suggestions, input) {
        removeDropdown();
        if (suggestions.length === 0) return;

        const dropdown = document.createElement('div');
        dropdown.className = 'suggestions-dropdown absolute top-full left-0 right-0 bg-white border border-slate-200 rounded-lg shadow-lg z-50 mt-1 max-h-48 overflow-y-auto';

        suggestions.forEach(suggestion => {
            const item = document.createElement('div');
            item.className = 'px-3 py-2 hover:bg-slate-100 cursor-pointer text-sm border-b border-slate-100 last:border-b-0 transition-colors';

            const parts = suggestion.display_name.split(',');
            const displayName = parts.length > 3 ? parts.slice(0, 3).join(', ').trim() : suggestion.display_name;

            item.textContent = displayName;
            item.addEventListener('click', () => {
                input.value = displayName;
                removeDropdown();
            });
            dropdown.appendChild(item);
        });

        input.parentNode.appendChild(dropdown);
        currentDropdown = dropdown;
    }

    function removeDropdown() {
        if (currentDropdown) {
            currentDropdown.remove();
            currentDropdown = null;
        }
    }
}

// --- Category Selectors ---

// Create Listing Category Selector
const categorySelector = {
    trigger: document.getElementById('category-selector-trigger'),
    selector: document.getElementById('category-selector'),
    displayText: document.getElementById('category-display-text'),
    hiddenInput: document.getElementById('id_category'),
    mainCategories: document.getElementById('main-categories'),
    subcategories: document.getElementById('subcategories'),
    activeCategory: null,
    selectedSubcategory: null,

    init() {
        if (!this.trigger) return;
        this.setupEventListeners();
        this.setDefaultCategory();
    },

    setupEventListeners() {
        this.trigger.addEventListener('click', () => this.toggleSelector());
        document.addEventListener('click', (e) => {
            if (!this.trigger.contains(e.target) && !this.selector.contains(e.target)) {
                this.closeSelector();
            }
        });
        this.mainCategories.addEventListener('click', (e) => {
            if (e.target.classList.contains('category-btn')) {
                this.selectCategory(e.target.dataset.category);
            }
        });
        this.subcategories.addEventListener('click', (e) => {
            if (e.target.classList.contains('subcategory-btn')) {
                this.selectSubcategory(e.target.dataset.value, e.target.textContent);
            }
        });
        this.selector.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.closeSelector();
        });
    },

    setDefaultCategory() {
        const firstCategory = this.mainCategories.querySelector('.category-btn');
        if (firstCategory) {
            this.selectCategory(firstCategory.dataset.category);
        }
    },

    selectCategory(category) {
        this.mainCategories.querySelectorAll('.category-btn').forEach(btn => {
            btn.classList.remove('bg-brand-sky', 'text-white');
            btn.classList.add('hover:bg-brand-sky/10');
        });
        const activeBtn = this.mainCategories.querySelector(`[data-category="${category}"]`);
        if (activeBtn) {
            activeBtn.classList.add('bg-brand-sky', 'text-white');
            activeBtn.classList.remove('hover:bg-brand-sky/10');
        }
        this.activeCategory = category;
        this.updateSubcategories(category);
    },

    updateSubcategories(category) {
        this.subcategories.innerHTML = '';
        const data = getCategoriesData();
        // The JSON data structure from Python is { category: { label: '...', subcategories: [...] } }
        const subs = (data[category] && data[category].subcategories) ? data[category].subcategories : [];

        subs.forEach(sub => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'w-full text-left px-3 py-2 text-sm hover:bg-brand-sky/10 rounded subcategory-btn';
            // Value format: category-subcategory (as expected by backend logic)
            btn.dataset.value = `${category}-${sub.value}`;
            btn.textContent = sub.label;
            this.subcategories.appendChild(btn);
        });
    },

    selectSubcategory(value, label) {
        this.subcategories.querySelectorAll('.subcategory-btn').forEach(btn => {
            btn.classList.remove('bg-brand-leaf', 'text-white');
            btn.classList.add('hover:bg-brand-sky/10');
        });
        const selectedBtn = this.subcategories.querySelector(`[data-value="${value}"]`);
        if (selectedBtn) {
            selectedBtn.classList.add('bg-brand-leaf', 'text-white');
            selectedBtn.classList.remove('hover:bg-brand-sky/10');
        }
        this.displayText.textContent = label;
        this.displayText.classList.remove('text-slate-400');
        this.displayText.classList.add('text-slate-900');
        this.hiddenInput.value = value;
        this.selectedSubcategory = value;

        if (typeof clearFieldError === 'function') clearFieldError('category');
        setTimeout(() => this.closeSelector(), 150);
    },

    toggleSelector() {
        if (this.selector.classList.contains('hidden')) {
            this.openSelector();
        } else {
            this.closeSelector();
        }
    },
    openSelector() {
        this.selector.classList.remove('hidden');
        this.selector.classList.add('flex');
        this.trigger.classList.add('ring-2', 'ring-brand-sky');
    },
    closeSelector() {
        this.selector.classList.add('hidden');
        this.selector.classList.remove('flex');
        this.trigger.classList.remove('ring-2', 'ring-brand-sky');
    }
};

// Edit Listing Category Selector (Similar logic but for the edit modal)
const editCategorySelector = {
    trigger: document.getElementById('edit-category-selector-trigger'),
    selector: document.getElementById('edit-category-selector'),
    displayText: document.getElementById('edit-category-display-text'),
    hiddenInput: document.getElementById('edit_id_category'),
    mainCategories: document.getElementById('edit-main-categories'),
    subcategories: document.getElementById('edit-subcategories'),
    activeCategory: null,
    selectedSubcategory: null,

    init() {
        if (this.trigger && this.selector) {
            this.setupEventListeners();
        }
    },

    setupEventListeners() {
        this.trigger.addEventListener('click', () => this.toggleSelector());
        document.addEventListener('click', (e) => {
            if (!this.trigger.contains(e.target) && !this.selector.contains(e.target)) {
                this.closeSelector();
            }
        });
        this.mainCategories.addEventListener('click', (e) => {
            if (e.target.classList.contains('category-btn')) {
                this.selectCategory(e.target.dataset.category);
            }
        });
        this.subcategories.addEventListener('click', (e) => {
            if (e.target.classList.contains('subcategory-btn')) {
                this.selectSubcategory(e.target.dataset.value, e.target.textContent);
            }
        });
    },

    selectCategory(category) {
        this.mainCategories.querySelectorAll('.category-btn').forEach(btn => {
            btn.classList.remove('bg-brand-sky', 'text-white');
            btn.classList.add('hover:bg-brand-sky/10');
        });
        const activeBtn = this.mainCategories.querySelector(`[data-category="${category}"]`);
        if (activeBtn) {
            activeBtn.classList.add('bg-brand-sky', 'text-white');
            activeBtn.classList.remove('hover:bg-brand-sky/10');
        }
        this.activeCategory = category;
        this.updateSubcategories(category);
    },

    updateSubcategories(category) {
        this.subcategories.innerHTML = '';
        const data = getCategoriesData();
        const subs = (data[category] && data[category].subcategories) ? data[category].subcategories : [];

        subs.forEach(sub => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'w-full text-left px-3 py-2 text-sm hover:bg-brand-sky/10 rounded subcategory-btn';
            btn.dataset.value = `${category}-${sub.value}`;
            btn.textContent = sub.label;
            this.subcategories.appendChild(btn);
        });
    },

    selectSubcategory(value, label) {
        this.subcategories.querySelectorAll('.subcategory-btn').forEach(btn => {
            btn.classList.remove('bg-brand-leaf', 'text-white');
            btn.classList.add('hover:bg-brand-sky/10');
        });
        const selectedBtn = this.subcategories.querySelector(`[data-value="${value}"]`);
        if (selectedBtn) {
            selectedBtn.classList.add('bg-brand-leaf', 'text-white');
            selectedBtn.classList.remove('hover:bg-brand-sky/10');
        }
        this.displayText.textContent = label;
        this.displayText.classList.remove('text-slate-500');
        this.displayText.classList.add('text-slate-900');
        this.hiddenInput.value = value;
        this.selectedSubcategory = value.split('-')[1];
        this.closeSelector();
    },

    toggleSelector() {
        if (this.selector.classList.contains('hidden')) {
            this.openSelector();
        } else {
            this.closeSelector();
        }
    },
    openSelector() {
        this.selector.classList.remove('hidden');
        this.selector.classList.add('flex');
        this.trigger.classList.add('ring-2', 'ring-brand-sky');
    },
    closeSelector() {
        this.selector.classList.add('hidden');
        this.selector.classList.remove('flex');
        this.trigger.classList.remove('ring-2', 'ring-brand-sky');
    },
    setCategory(category, subcategory) {
        this.activeCategory = category;
        this.selectedSubcategory = subcategory;
        this.selectCategory(category);
        if (subcategory) {
            const subcategoryValue = `${category}-${subcategory}`;
            const data = getCategoriesData();
            const subs = (data[category] && data[category].subcategories) ? data[category].subcategories : [];
            const sub = subs.find(s => s.value === subcategory);
            const label = sub ? sub.label : subcategory;
            this.selectSubcategory(subcategoryValue, label);
        }
    }
};

// --- Modals (Edit, Delete, Details) ---

let currentDeleteListingId = null;
let currentEditListingId = null;
let editExistingImagesCount = 0;
let editNewImages = [];

function openDeleteListingModal(listingId) {
    currentDeleteListingId = listingId;
    document.getElementById('delete-listing-modal').classList.remove('hidden');
    document.getElementById('delete-listing-modal').classList.add('flex');
}

function closeDeleteListingModal() {
    document.getElementById('delete-listing-modal').classList.add('hidden');
    document.getElementById('delete-listing-modal').classList.remove('flex');
    currentDeleteListingId = null;
}

// Add event listeners for delete modal
document.getElementById('close-delete-modal')?.addEventListener('click', closeDeleteListingModal);
document.getElementById('cancel-delete-btn')?.addEventListener('click', closeDeleteListingModal);
document.getElementById('confirm-delete-btn')?.addEventListener('click', function () {
    if (currentDeleteListingId) {
        // Submit a hidden form for deletion
        const form = document.createElement('form');
        form.method = 'POST';
        // Using the URL pattern defined in urls.py
        form.action = `/marketplace/delete/${currentDeleteListingId}/`;

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfToken) {
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrfmiddlewaretoken';
            csrfInput.value = csrfToken.value;
            form.appendChild(csrfInput);
        }
        document.body.appendChild(form);
        form.submit();
    }
});

// Edit Modal Functions
function openEditModal(listingId) {
    // This function is for the specific implementation in your home.html loop
    // If you used the generic one from edit_listing.html, this might need adjustment
    const modal = document.getElementById(`editModal${listingId}`);
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
    }
}

function closeEditModal(listingId) {
    const modal = document.getElementById(`editModal${listingId}`);
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }
}

// Edit Listing Modal (Fetching Data)
function openEditListingModal(listingId) {
    // Redirect to the edit page instead of a modal for simplicity with MVT structure
    window.location.href = `/marketplace/edit/${listingId}/`;
}

// --- Create Listing Functions ---

let createSelectedFiles = [];

function handleCreateImagePreview(input) {
    const previewContainer = document.getElementById('create-image-previews');
    const photoCounter = document.getElementById('create-image-counter');
    if (!previewContainer || !photoCounter) return;

    if (input.files && input.files.length > 0) {
        const currentCount = createSelectedFiles.length;
        const availableSlots = 5 - currentCount;

        if (availableSlots <= 0) {
            alert('Maximum 5 images allowed. You have reached the limit.');
            input.value = '';
            return;
        }

        const filesToAdd = Array.from(input.files).slice(0, availableSlots);
        filesToAdd.forEach(file => createSelectedFiles.push(file));

        previewContainer.innerHTML = '';
        createSelectedFiles.forEach(file => {
            const reader = new FileReader();
            reader.onload = function (e) {
                const previewDiv = document.createElement('div');
                previewDiv.className = 'relative group';
                previewDiv.innerHTML = `<img src="${e.target.result}" alt="Preview" class="w-20 h-20 object-cover rounded-lg border-2 border-brand-sky">`;
                previewContainer.appendChild(previewDiv);
            };
            reader.readAsDataURL(file);
        });

        photoCounter.textContent = `Photos: ${createSelectedFiles.length}/5`;
        input.value = '';
    }
}

function syncCreateFilesToInput() {
    const fileInput = document.getElementById('id_images');
    if (!fileInput) return;
    const dataTransfer = new DataTransfer();
    createSelectedFiles.forEach(file => dataTransfer.items.add(file));
    fileInput.files = dataTransfer.files;
}

// --- General Modal Logic (Add Listing) ---

const addListingModal = document.getElementById('add-listing-modal');
const addListingBtn = document.getElementById('add-listing-btn');
const closeAddModalBtn = document.getElementById('close-modal');
const cancelAddBtn = document.getElementById('cancel-btn');
const listingForm = document.getElementById('listing-form');

if (addListingBtn) {
    addListingBtn.addEventListener('click', () => {
        addListingModal.classList.remove('hidden');
        addListingModal.classList.add('flex');
        setTimeout(() => initLocationAutocomplete(), 300);
    });
}

const closeAddListingModal = () => {
    addListingModal.classList.add('hidden');
    addListingModal.classList.remove('flex');
    listingForm.reset();
    // Reset specific elements
    document.querySelectorAll('.error-message').forEach(e => e.remove());
    createSelectedFiles = [];
    const previews = document.getElementById('create-image-previews');
    if (previews) previews.innerHTML = '';
    const counter = document.getElementById('create-image-counter');
    if (counter) counter.textContent = 'Photos: 0/5';

    // Reset category selector
    const catInput = document.getElementById('id_category');
    if (catInput) catInput.value = '';
    const catDisplay = document.getElementById('category-display-text');
    if (catDisplay) {
        catDisplay.textContent = 'Choose Category';
        catDisplay.classList.add('text-slate-400');
    }
};

if (closeAddModalBtn) closeAddModalBtn.addEventListener('click', closeAddListingModal);
if (cancelAddBtn) cancelAddBtn.addEventListener('click', closeAddListingModal);
if (addListingModal) {
    addListingModal.addEventListener('click', (e) => {
        if (e.target === addListingModal) closeAddListingModal();
    });
}

if (listingForm) {
    listingForm.addEventListener('submit', () => syncCreateFilesToInput());
}

// --- Dynamic Form Fields ---

const listingTypeRadios = document.querySelectorAll('input[name="listing_type"]');
const dynamicFieldLabel = document.getElementById('dynamic-field-label');
const priceContainer = document.getElementById('price-container');
const swapContainer = document.getElementById('swap-container');
const budgetContainer = document.getElementById('budget-container');

function updateDynamicField(selectedType) {
    if (!priceContainer) return;

    // Clear errors
    document.querySelectorAll('.error-message').forEach(el => {
        if (el.closest('#dynamic-field-container')) el.remove();
    });

    priceContainer.classList.add('hidden');
    swapContainer.classList.add('hidden');
    budgetContainer.classList.add('hidden');

    if (selectedType === 'sale') {
        priceContainer.classList.remove('hidden');
        dynamicFieldLabel.textContent = 'Price *';
        dynamicFieldLabel.setAttribute('for', 'id_price');
    } else if (selectedType === 'swap') {
        swapContainer.classList.remove('hidden');
        dynamicFieldLabel.textContent = 'Looking to Swap For *';
        dynamicFieldLabel.setAttribute('for', 'id_swap_for');
    } else if (selectedType === 'buy') {
        budgetContainer.classList.remove('hidden');
        dynamicFieldLabel.textContent = 'Budget *';
        dynamicFieldLabel.setAttribute('for', 'id_budget');
    }
}

listingTypeRadios.forEach(radio => {
    radio.addEventListener('change', (e) => updateDynamicField(e.target.value));
});

// --- Image Gallery Logic ---

let currentGalleryImages = [];
let currentImageIndex = 0;
let currentZoom = 1;
let currentTranslateX = 0;
let currentTranslateY = 0;
let isDragging = false;
let startX, startY, startTranslateX, startTranslateY;

function openImageGallery(listingId) {
    currentGalleryImages = [];
    const listingCard = document.querySelector(`[data-listing-id="${listingId}"]`);

    if (listingCard) {
        const imagesData = listingCard.dataset.images;
        if (imagesData) {
            const imageUrls = imagesData.split(',');
            currentGalleryImages = imageUrls.map(url => ({
                url: url.trim(),
                alt: 'Listing image'
            }));
        }
    }

    if (currentGalleryImages.length === 0) {
        currentGalleryImages = [{
            url: window.MARKETPLACE_CONFIG.placeholderImage,
            alt: 'No image available'
        }];
    }

    currentImageIndex = 0;
    updateGalleryDisplay();
    document.getElementById('image-gallery-modal').classList.remove('hidden');
    document.getElementById('image-gallery-modal').classList.add('flex');
    document.body.style.overflow = 'hidden';
}

function updateGalleryDisplay() {
    const mainImage = document.getElementById('gallery-main-image');
    const counter = document.getElementById('image-counter');
    const thumbnailStrip = document.getElementById('thumbnail-strip');

    currentZoom = 1;
    currentTranslateX = 0;
    currentTranslateY = 0;
    mainImage.style.transform = `scale(${currentZoom}) translate(${currentTranslateX}px, ${currentTranslateY}px)`;

    mainImage.src = currentGalleryImages[currentImageIndex].url;
    mainImage.alt = currentGalleryImages[currentImageIndex].alt;
    counter.textContent = `${currentImageIndex + 1} / ${currentGalleryImages.length}`;

    // Thumbnails
    thumbnailStrip.innerHTML = '';
    currentGalleryImages.forEach((image, index) => {
        const thumb = document.createElement('img');
        thumb.src = image.url;
        thumb.className = `w-16 h-16 object-cover rounded cursor-pointer border-2 ${index === currentImageIndex ? 'border-brand-sky' : 'border-transparent'}`;
        thumb.onclick = () => {
            currentImageIndex = index;
            updateGalleryDisplay();
        };
        thumbnailStrip.appendChild(thumb);
    });
}

function closeImageGallery() {
    document.getElementById('image-gallery-modal').classList.add('hidden');
    document.getElementById('image-gallery-modal').classList.remove('flex');
    document.body.style.overflow = '';
}

// Gallery Event Listeners
document.getElementById('close-gallery')?.addEventListener('click', closeImageGallery);
document.getElementById('prev-image')?.addEventListener('click', () => {
    if (currentImageIndex > 0) { currentImageIndex--; updateGalleryDisplay(); }
});
document.getElementById('next-image')?.addEventListener('click', () => {
    if (currentImageIndex < currentGalleryImages.length - 1) { currentImageIndex++; updateGalleryDisplay(); }
});

// --- Listing Details Modal ---
function openListingDetailsModal(listingId) {
    const listingCard = document.querySelector(`[data-listing-id="${listingId}"]`);
    if (!listingCard) return;

    // 1. Populate Text Content
    document.getElementById('details-title').textContent = listingCard.dataset.title;
    document.getElementById('details-description').innerHTML = listingCard.dataset.description;

    // 2. Populate Seller Info
    document.getElementById('details-seller').innerHTML = `
        <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
        </svg>
        <strong>${listingCard.dataset.yourName}</strong> | ${listingCard.dataset.company}
    `;

    // 3. Populate Badges & Price
    const type = listingCard.dataset.listingType;
    let badgeHtml = '';
    let priceHtml = '';

    if (type === 'sale') {
        badgeHtml = `
            <span class="inline-flex items-center gap-1 text-[11px] tracking-wide font-bold text-white bg-slate-800 px-2.5 py-1 rounded-full">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
                </svg>
                SALE
            </span>`;
        priceHtml = listingCard.dataset.price;
    } else if (type === 'swap') {
        badgeHtml = `
            <span class="inline-flex items-center gap-1 text-[11px] tracking-wide font-bold text-white bg-emerald-600 px-2.5 py-1 rounded-full">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"></path>
                </svg>
                SWAP
            </span>`;
        priceHtml = `Looking for: <span class="text-brand-leaf">${listingCard.dataset.swapFor}</span>`;
    } else {
        badgeHtml = `
            <span class="inline-flex items-center gap-1 text-[11px] tracking-wide font-bold text-white bg-slate-700 px-2.5 py-1 rounded-full">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path>
                </svg>
                BUY
            </span>`;
        priceHtml = `Budget: <span class="text-brand-leaf">${listingCard.dataset.budget}</span>`;
    }

    document.getElementById('details-badges').innerHTML = badgeHtml;
    document.getElementById('details-price').innerHTML = priceHtml;

    // 4. Populate Location and Date (Added)
    const location = listingCard.dataset.location;
    const date = listingCard.dataset.date;
    const metaContainer = document.getElementById('details-meta');

    if (metaContainer) {
        metaContainer.innerHTML = `
            <span class="flex items-center gap-1">
                <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
                ${location}
            </span>
            <span class="flex items-center gap-1">
                <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7H3v12a2 2 0 002 2z"></path>
                </svg>
                ${date}
            </span>
        `;
    }

    // 5. Populate Image
    const images = listingCard.dataset.images;
    const imgEl = document.getElementById('details-main-image');
    // Ensure MARKETPLACE_CONFIG is defined, fallback if not
    const placeholder = (window.MARKETPLACE_CONFIG && window.MARKETPLACE_CONFIG.placeholderImage) ? window.MARKETPLACE_CONFIG.placeholderImage : '/static/thryve_app/images/listing-placeholder.png';

    if (imgEl) {
        imgEl.src = (images && images.trim() !== '') ? images.split(',')[0].trim() : placeholder;
    }

    // 6. Show Modal
    const modal = document.getElementById('listing-details-modal');
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    document.body.style.overflow = 'hidden';

    // 7. Setup Gallery Button
    const galleryBtn = document.getElementById('view-gallery-btn');
    if (galleryBtn) {
        galleryBtn.onclick = () => {
            closeListingDetailsModal();
            openImageGallery(listingId);
        };
    }
}

function closeListingDetailsModal() {
    document.getElementById('listing-details-modal').classList.add('hidden');
    document.getElementById('listing-details-modal').classList.remove('flex');
    document.body.style.overflow = '';
}

document.getElementById('close-details-modal')?.addEventListener('click', closeListingDetailsModal);

// --- Validation Logic ---

function setupRealTimeValidation() {
    if (!listingForm) return;
    const inputs = listingForm.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        if (input.id !== 'id_category') {
            input.addEventListener('input', (e) => {
                clearFieldError(e.target.id.replace('id_', ''));
            });
        }
    });
}

function clearFieldError(fieldName) {
    // Logic to find container and remove .error-message
    // (Simplifying for brevity - assumes standard Django form structure)
    const field = document.getElementById(`id_${fieldName}`);
    if (field) {
        field.classList.remove('border-red-500');
        const container = field.closest('div');
        if (container) {
            const err = container.querySelector('.error-message');
            if (err) err.remove();
        }
    }
}

// Function to handle price input formatting (commas)
function handlePriceInput(event) {
    const input = event.target;
    // Remove all non-digit and non-decimal characters
    let value = input.value.replace(/[^\d.]/g, '');

    // Allow only one decimal point
    const parts = value.split('.');
    if (parts.length > 2) {
        value = parts[0] + '.' + parts.slice(1).join('');
    }

    // Split into integer and decimal parts
    const [integerPart, decimalPart] = value.split('.');

    // Add commas to integer part
    const formattedInteger = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, ',');

    // Reconstruct the value with decimal part if it exists
    input.value = decimalPart !== undefined ? formattedInteger + '.' + decimalPart : formattedInteger;
}

const priceIn = document.getElementById('id_price');
const budgetIn = document.getElementById('id_budget');
if(priceIn) priceIn.addEventListener('input', handlePriceInput);
if(budgetIn) budgetIn.addEventListener('input', handlePriceInput);

// --- Book Now Modal Logic ---
// Note: Elements are accessed lazily to ensure they exist when modal is opened


function openBookNowModal(listingId) {
    const listingCard = document.querySelector(`[data-listing-id="${listingId}"]`);
    if (!listingCard) return;

    // Check if user is trying to book their own listing
    const listingUserId = parseInt(listingCard.dataset.userId);
    const currentUserId = window.MARKETPLACE_CONFIG.currentUserId;

    if (listingUserId === currentUserId) {
        showToast("You can't set a booking for yourself!");
        return;
    }

    const type = listingCard.dataset.listingType;
    const title = listingCard.dataset.title;

    // Get modal elements (lazy loading to ensure they exist)
    const bookNowModal = document.getElementById('book-now-modal');
    const modalTitle = document.getElementById('modal-title-text');
    const messageTextarea = document.getElementById('message');
    const messageHelperText = document.getElementById('message-helper-text');
    const listingIdInput = document.getElementById('booking-listing-id');
    const listingTypeInput = document.getElementById('booking-listing-type');

    // 1. Set hidden form values
    listingIdInput.value = listingId;
    listingTypeInput.value = type;

    // 2. Set dynamic text based on listing type
    modalTitle.textContent = `Arrange Transaction/Exchange for: ${title}`;
    messageTextarea.value = ''; // Clear previous message
    messageTextarea.placeholder = 'Describe your item or service';
    messageHelperText.textContent = '';

    // Define helper text based on the limited timeframe/meeting clarification
    let helperText = '';

    if (type === 'sale' || type === 'buy') {
        messageTextarea.placeholder = 'e.g., "I want to buy this item and can meet for pickup on Nov 16th."';
        helperText = 'Propose a date and time to meet for pickup/delivery. The dates selected are for the meeting window and are NOT the listing\'s expiration date.';
    } else if (type === 'swap') {
        messageTextarea.placeholder = 'e.g., "I am offering a XYZ tool and can meet for the exchange on Nov 17th."';
        helperText = 'Clearly describe the item you are offering for swap, and confirm your preferred exchange date. The dates selected are for the meeting window and are NOT the listing\'s expiration date.';
    }

    messageHelperText.textContent = helperText;

    // 3. Reset dates (optional, but good practice)
    document.getElementById('start-date').value = '';
    document.getElementById('end-date').value = '';

    // 4. Show modal
    bookNowModal.classList.remove('hidden');
    bookNowModal.classList.add('flex');
    document.body.style.overflow = 'hidden';
}

function closeBookNowModal() {
    const bookNowModal = document.getElementById('book-now-modal');
    const bookNowForm = document.getElementById('book-now-form');
    const requestBookingBtn = document.getElementById('request-booking-btn');

    bookNowModal.classList.add('hidden');
    bookNowModal.classList.remove('flex');
    document.body.style.overflow = '';
    bookNowForm.reset();
    requestBookingBtn.disabled = false;
    requestBookingBtn.textContent = 'Request Booking';
}
