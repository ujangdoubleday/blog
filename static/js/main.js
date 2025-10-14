// Blog JavaScript functionality
// Set dark theme immediately before DOM loads to prevent flash
if (!localStorage.getItem('theme')) {
    document.documentElement.setAttribute('data-theme', 'dark');
}

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const siteNavigation = document.querySelector('.site-navigation');
    
    if (mobileMenuToggle && siteNavigation) {
        mobileMenuToggle.addEventListener('click', function() {
            siteNavigation.classList.toggle('active');
            mobileMenuToggle.classList.toggle('active');
        });
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add reading progress bar for posts
    const postContent = document.querySelector('.post-content, .page-content');
    if (postContent) {
        const progressBar = document.createElement('div');
        progressBar.className = 'reading-progress';
        progressBar.innerHTML = '<div class="reading-progress-bar"></div>';
        document.body.appendChild(progressBar);
        
        const progressBarFill = progressBar.querySelector('.reading-progress-bar');
        
        window.addEventListener('scroll', function() {
            const windowHeight = window.innerHeight;
            const documentHeight = document.documentElement.scrollHeight - windowHeight;
            const scrolled = window.scrollY;
            const progress = scrolled / documentHeight;
            
            progressBarFill.style.width = Math.min(progress * 100, 100) + '%';
        });
    }
    
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
    const searchInput = document.querySelector('#search-input');
    const searchResults = document.querySelector('#search-results');
    
    if (searchInput && searchResults) {
        let searchData = [];
        
        // Load search data
        fetch('/search.json')
            .then(response => response.json())
            .then(data => {
                searchData = data;
            })
            .catch(err => console.error('Search data not found:', err));
        
        searchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase().trim();
            
            if (query.length < 2) {
                searchResults.innerHTML = '';
                searchResults.style.display = 'none';
                return;
            }
            
            const results = searchData.filter(item => 
                item.title.toLowerCase().includes(query) ||
                item.content.toLowerCase().includes(query) ||
                item.tags.some(tag => tag.toLowerCase().includes(query))
            ).slice(0, 5);
            
            if (results.length > 0) {
                searchResults.innerHTML = results.map(result => `
                    <div class="search-result">
                        <h4><a href="${result.url}">${result.title}</a></h4>
                        <p>${result.excerpt}</p>
                        <small>${result.date}</small>
                    </div>
                `).join('');
                searchResults.style.display = 'block';
            } else {
                searchResults.innerHTML = '<div class="search-result">No results found</div>';
                searchResults.style.display = 'block';
            }
        });
        
        // Hide search results when clicking outside
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.style.display = 'none';
            }
        });
    }
    
    // Theme toggle
    const themeToggle = document.querySelector('#theme-toggle');
    if (themeToggle) {
        const sunIcon = themeToggle.querySelector('.sun-icon');
        const moonIcon = themeToggle.querySelector('.moon-icon');
        
        // Set default theme to dark if no preference saved
        const savedTheme = localStorage.getItem('theme');
        const currentTheme = savedTheme || 'dark';
        
        // Force dark mode as default
        document.documentElement.setAttribute('data-theme', currentTheme);
        updateThemeIcons(currentTheme);
        
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcons(newTheme);
        });
        
        function updateThemeIcons(theme) {
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

// Add CSS for reading progress and copy button
const style = document.createElement('style');
style.textContent = `
    .reading-progress {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        z-index: 1000;
        background: #e2e8f0;
    }
    
    .reading-progress-bar {
        height: 100%;
        background: #2563eb;
        transition: width 0.1s ease;
    }
    
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
    
    @media (max-width: 768px) {
        .site-navigation.active {
            display: flex;
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: var(--background);
            flex-direction: column;
            padding: 1rem;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
            border: 1px solid var(--border-color);
            border-top: none;
            border-radius: 0 0 8px 8px;
            z-index: 1000;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
        }
        
        .mobile-menu-toggle.active span:nth-child(1) {
            transform: rotate(45deg) translate(5px, 5px);
        }
        
        .mobile-menu-toggle.active span:nth-child(2) {
            opacity: 0;
        }
        
        .mobile-menu-toggle.active span:nth-child(3) {
            transform: rotate(-45deg) translate(7px, -6px);
        }
    }
`;
document.head.appendChild(style);
