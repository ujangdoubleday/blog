// Blog JavaScript functionality
// Set dark theme immediately before DOM loads to prevent flash
if (!localStorage.getItem('theme')) {
    document.documentElement.setAttribute('data-theme', 'dark');
}

document.addEventListener('DOMContentLoaded', function() {
    // Search modal functionality
    const searchToggle = document.querySelector('#search-toggle');
    const searchModal = document.querySelector('#search-modal');
    const searchModalOverlay = document.querySelector('#search-modal-overlay');
    const searchInput = document.querySelector('#search-input');
    const searchResults = document.querySelector('#search-results');

    if (searchToggle && searchModal) {
        searchToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            searchModal.style.display = 'flex';
            searchInput.focus();
        });
    }

    // Close modal when clicking overlay
    if (searchModalOverlay) {
        searchModalOverlay.addEventListener('click', function() {
            searchModal.style.display = 'none';
            searchInput.value = '';
            searchResults.innerHTML = '';
        });
    }

    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && searchModal && searchModal.style.display === 'flex') {
            searchModal.style.display = 'none';
            searchInput.value = '';
            searchResults.innerHTML = '';
        }
    });

    // Mobile menu toggle
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const siteNavigation = document.querySelector('.site-navigation');

    if (mobileMenuToggle && siteNavigation) {
        mobileMenuToggle.addEventListener('click', function() {
            siteNavigation.classList.toggle('active');
            mobileMenuToggle.classList.toggle('active');
        });
    }


    // Reading progress bar removed to support browser reader mode

    // Copy code blocks functionality
    document.querySelectorAll('pre code').forEach(codeBlock => {
        const button = document.createElement('button');
        button.className = 'copy-code-button';
        button.textContent = 'Copy';
        button.setAttribute('aria-label', 'Copy code to clipboard');

        const pre = codeBlock.parentElement;
        pre.style.position = 'relative';
        pre.appendChild(button);

        button.addEventListener('click', async function() {
            try {
                await navigator.clipboard.writeText(codeBlock.textContent);
                button.textContent = 'Copied!';
                button.classList.add('copied');

                setTimeout(() => {
                    button.textContent = 'Copy';
                    button.classList.remove('copied');
                }, 2000);
            } catch (err) {
                console.error('Failed to copy code: ', err);
                button.textContent = 'Failed';
                setTimeout(() => {
                    button.textContent = 'Copy';
                }, 2000);
            }
        });
    });

    // Image lazy loading
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));

    // Search functionality (if search input exists)
    if (searchInput && searchResults) {
        let searchData = [];
        let searchTimeout;
        let currentHighlight = -1;

        // Load search data
        fetch('/search.json')
            .then(response => response.json())
            .then(data => {
                searchData = data;
            })
            .catch(err => console.error('Search data not found:', err));

        // Debounced search function
        function performSearch() {
            const query = searchInput.value.toLowerCase().trim();

            if (query.length < 2) {
                searchResults.innerHTML = '';
                searchResults.style.display = 'none';
                currentHighlight = -1;
                return;
            }

            const results = searchData.filter(item =>
                item.title.toLowerCase().includes(query) ||
                item.content.toLowerCase().includes(query)
            ).slice(0, 8);

            if (results.length > 0) {
                searchResults.innerHTML = results.map((result, index) => `
                    <div class="search-result" data-index="${index}">
                        <span class="search-result-type">${result.type}</span>
                        <a href="${result.url}" class="search-result-link">${result.title}</a>
                        ${result.date ? `<small>${result.date}</small>` : ''}
                    </div>
                `).join('');
                searchResults.style.display = 'block';
                currentHighlight = -1;
            } else {
                searchResults.innerHTML = '<div class="search-result search-no-results">No results found</div>';
                searchResults.style.display = 'block';
                currentHighlight = -1;
            }
        }

        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(performSearch, 150);
        });

        // Keyboard navigation
        searchInput.addEventListener('keydown', function(e) {
            const resultItems = searchResults.querySelectorAll('.search-result:not(.search-no-results)');

            if (e.key === 'ArrowDown') {
                e.preventDefault();
                currentHighlight = Math.min(currentHighlight + 1, resultItems.length - 1);
                updateHighlight(resultItems);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                currentHighlight = Math.max(currentHighlight - 1, -1);
                updateHighlight(resultItems);
            } else if (e.key === 'Enter' && currentHighlight >= 0) {
                e.preventDefault();
                const link = resultItems[currentHighlight].querySelector('.search-result-link');
                if (link) link.click();
            } else if (e.key === 'Escape') {
                searchResults.style.display = 'none';
                currentHighlight = -1;
            }
        });

        function updateHighlight(items) {
            items.forEach((item, index) => {
                if (index === currentHighlight) {
                    item.style.background = 'var(--hover-background)';
                    item.scrollIntoView({ block: 'nearest' });
                } else {
                    item.style.background = '';
                }
            });
        }

        // Hide search results when clicking outside
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.style.display = 'none';
            }
        });
    }

    // Close search input wrapper when clicking outside
    document.addEventListener('click', function(e) {
        if (searchInputWrapper && searchToggle && !searchToggle.contains(e.target) && !searchInputWrapper.contains(e.target)) {
            searchInputWrapper.style.display = 'none';
        }
    });

    // Theme toggle - support both buttons (global and homepage)
    const themeToggles = document.querySelectorAll('#theme-toggle, #theme-toggle-home');

    // Set default theme to dark if no preference saved
    const savedTheme = localStorage.getItem('theme');
    const currentTheme = savedTheme || 'dark';
    document.documentElement.setAttribute('data-theme', currentTheme);

    // Initialize all theme toggle buttons
    themeToggles.forEach(themeToggle => {
        const sunIcon = themeToggle.querySelector('.sun-icon');
        const moonIcon = themeToggle.querySelector('.moon-icon');

        updateThemeIcons(sunIcon, moonIcon, currentTheme);

        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';

            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);

            // Update all toggle buttons
            themeToggles.forEach(toggle => {
                const sun = toggle.querySelector('.sun-icon');
                const moon = toggle.querySelector('.moon-icon');
                updateThemeIcons(sun, moon, newTheme);
            });
        });
    });

    function updateThemeIcons(sunIcon, moonIcon, theme) {
        if (sunIcon && moonIcon) {
            if (theme === 'dark') {
                sunIcon.style.display = 'block';
                moonIcon.style.display = 'none';
            } else {
                sunIcon.style.display = 'none';
                moonIcon.style.display = 'block';
            }
        }
    }
});

// Add CSS for copy button
const style = document.createElement('style');
style.textContent = `
    .copy-code-button {
        position: absolute;
        top: 0.5rem;
        right: 0.5rem;
        background: #374151;
        color: white;
        border: none;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
        cursor: pointer;
        opacity: 0;
        transition: opacity 0.2s ease;
    }

    pre:hover .copy-code-button {
        opacity: 1;
    }

    .copy-code-button:hover {
        background: #4b5563;
    }

    .copy-code-button.copied {
        background: #059669;
    }

`;
document.head.appendChild(style);
