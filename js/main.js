/**
 * FriedFinance - Main JavaScript
 * Vanilla JS, no dependencies
 */

(function() {
  'use strict';

  // ===========================================
  // DOM Ready
  // ===========================================
  document.addEventListener('DOMContentLoaded', init);

  function init() {
    initNavigation();
    initMobileMenu();
    initSearchOverlay();
    initScrollAnimations();
    initCategoryFilter();
    initLiveSearch();
    initTableOfContents();
    initReadingProgress();
    initShareButtons();
    initEmailForms();
    initURLParams();
    initTickerTouch();
  }

  // ===========================================
  // Navigation
  // ===========================================
  function initNavigation() {
    const navWrap = document.querySelector('.nav-wrap');
    if (!navWrap) return;

    let lastScroll = 0;
    
    window.addEventListener('scroll', () => {
      const currentScroll = window.pageYOffset;
      
      // Add shadow when scrolled
      if (currentScroll > 10) {
        navWrap.classList.add('scrolled');
      } else {
        navWrap.classList.remove('scrolled');
      }
      
      lastScroll = currentScroll;
    });
  }

  // ===========================================
  // Mobile Menu
  // ===========================================
  function initMobileMenu() {
    const hamburger = document.querySelector('.hamburger');
    const mobileMenu = document.querySelector('.mobile-menu');
    const mobileOverlay = document.querySelector('.mobile-menu-overlay');
    const mobileClose = document.querySelector('.mobile-menu-close');

    if (!hamburger || !mobileMenu) return;

    function openMenu() {
      hamburger.classList.add('active');
      mobileMenu.classList.add('active');
      if (mobileOverlay) mobileOverlay.classList.add('active');
      document.body.style.overflow = 'hidden';
    }

    function closeMenu() {
      hamburger.classList.remove('active');
      mobileMenu.classList.remove('active');
      if (mobileOverlay) mobileOverlay.classList.remove('active');
      document.body.style.overflow = '';
    }

    hamburger.addEventListener('click', () => {
      if (mobileMenu.classList.contains('active')) {
        closeMenu();
      } else {
        openMenu();
      }
    });

    if (mobileClose) {
      mobileClose.addEventListener('click', closeMenu);
    }

    if (mobileOverlay) {
      mobileOverlay.addEventListener('click', closeMenu);
    }

    // ESC key to close
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && mobileMenu.classList.contains('active')) {
        closeMenu();
      }
    });
  }

  // ===========================================
  // Search Overlay
  // ===========================================
  function initSearchOverlay() {
    const searchBtn = document.querySelector('.nav-search-btn');
    const searchOverlay = document.querySelector('.search-overlay');
    const searchInput = document.querySelector('.search-overlay input');
    const searchClose = document.querySelector('.search-close');

    if (!searchBtn || !searchOverlay) return;

    function openSearch() {
      searchOverlay.classList.add('active');
      document.body.style.overflow = 'hidden';
      setTimeout(() => {
        if (searchInput) searchInput.focus();
      }, 100);
    }

    function closeSearch() {
      searchOverlay.classList.remove('active');
      document.body.style.overflow = '';
      if (searchInput) searchInput.value = '';
    }

    searchBtn.addEventListener('click', openSearch);

    if (searchClose) {
      searchClose.addEventListener('click', closeSearch);
    }

    // Close on overlay click
    searchOverlay.addEventListener('click', (e) => {
      if (e.target === searchOverlay) {
        closeSearch();
      }
    });

    // ESC key to close
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && searchOverlay.classList.contains('active')) {
        closeSearch();
      }
    });

    // Redirect on Enter
    if (searchInput) {
      searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          const query = searchInput.value.trim();
          if (query) {
            window.location.href = `blog.html?q=${encodeURIComponent(query)}`;
          }
        }
      });
    }
  }

  // ===========================================
  // Scroll Animations (fade-up)
  // ===========================================
  function initScrollAnimations() {
    const fadeElements = document.querySelectorAll('.fade-up');
    
    if (!fadeElements.length) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.1,
      rootMargin: '0px 0px -40px 0px'
    });

    fadeElements.forEach(el => observer.observe(el));
  }

  // ===========================================
  // Category Filtering
  // ===========================================
  function initCategoryFilter() {
    const categoryTabs = document.querySelectorAll('.category-tab');
    const filterableItems = document.querySelectorAll('[data-category]');
    const articleCount = document.querySelector('.blog-header-count');
    const noResults = document.querySelector('.no-results');
    
    if (!categoryTabs.length || !filterableItems.length) return;

    categoryTabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const category = tab.dataset.category;
        
        // Update active tab
        categoryTabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        
        // Filter items
        filterPosts(category);
      });
    });

    function filterPosts(category) {
      let visibleCount = 0;
      const searchQuery = getSearchQuery();
      
      filterableItems.forEach(item => {
        const itemCategory = item.dataset.category;
        const matchesCategory = category === 'all' || itemCategory === category;
        const matchesSearch = matchesSearchQuery(item, searchQuery);
        
        if (matchesCategory && matchesSearch) {
          item.style.display = '';
          visibleCount++;
        } else {
          item.style.display = 'none';
        }
      });
      
      updateArticleCount(visibleCount);
      updateNoResults(visibleCount);
    }

    function getSearchQuery() {
      const searchInput = document.querySelector('#live-search');
      return searchInput ? searchInput.value.toLowerCase().trim() : '';
    }

    function matchesSearchQuery(item, query) {
      if (!query) return true;
      const title = (item.dataset.title || '').toLowerCase();
      const excerpt = (item.dataset.excerpt || '').toLowerCase();
      return title.includes(query) || excerpt.includes(query);
    }

    function updateArticleCount(count) {
      if (articleCount) {
        articleCount.textContent = `Showing ${count} article${count !== 1 ? 's' : ''}`;
      }
    }

    function updateNoResults(count) {
      if (noResults) {
        if (count === 0) {
          noResults.classList.add('visible');
        } else {
          noResults.classList.remove('visible');
        }
      }
    }

    // Make filterPosts available globally for live search
    window.filterPosts = filterPosts;
    window.getActiveCategory = () => {
      const activeTab = document.querySelector('.category-tab.active');
      return activeTab ? activeTab.dataset.category : 'all';
    };
  }

  // ===========================================
  // Live Search (blog.html)
  // ===========================================
  function initLiveSearch() {
    const searchInput = document.querySelector('#live-search');
    
    if (!searchInput) return;

    searchInput.addEventListener('input', () => {
      const category = window.getActiveCategory ? window.getActiveCategory() : 'all';
      if (window.filterPosts) {
        window.filterPosts(category);
      }
    });
  }

  // ===========================================
  // Table of Contents (post.html)
  // ===========================================
  function initTableOfContents() {
    const tocList = document.querySelector('.toc-list');
    const postContent = document.querySelector('.post-content');
    
    if (!tocList || !postContent) return;

    const headings = postContent.querySelectorAll('h2, h3');
    
    if (!headings.length) return;

    // Generate TOC
    headings.forEach((heading, index) => {
      const id = heading.id || `section-${index}`;
      heading.id = id;
      
      const li = document.createElement('li');
      const a = document.createElement('a');
      a.href = `#${id}`;
      a.textContent = heading.textContent;
      a.className = heading.tagName === 'H3' ? 'toc-h3' : '';
      
      a.addEventListener('click', (e) => {
        e.preventDefault();
        const target = document.getElementById(id);
        if (target) {
          const offset = 80; // Nav height + padding
          const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - offset;
          window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
          });
        }
      });
      
      li.appendChild(a);
      tocList.appendChild(li);
    });

    // Highlight active section
    const tocLinks = tocList.querySelectorAll('a');
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          tocLinks.forEach(link => link.classList.remove('active'));
          const activeLink = tocList.querySelector(`a[href="#${entry.target.id}"]`);
          if (activeLink) {
            activeLink.classList.add('active');
          }
        }
      });
    }, {
      rootMargin: '-80px 0px -70% 0px'
    });

    headings.forEach(heading => observer.observe(heading));
  }

  // ===========================================
  // Reading Progress (post.html)
  // ===========================================
  function initReadingProgress() {
    const progressBar = document.querySelector('.reading-progress-bar');
    const postContent = document.querySelector('.post-content');
    
    if (!progressBar || !postContent) return;

    window.addEventListener('scroll', () => {
      const contentRect = postContent.getBoundingClientRect();
      const contentTop = contentRect.top + window.pageYOffset;
      const contentHeight = contentRect.height;
      const windowHeight = window.innerHeight;
      const scrollY = window.pageYOffset;
      
      // Calculate progress
      const start = contentTop - windowHeight;
      const end = contentTop + contentHeight - windowHeight;
      const current = scrollY - start;
      const total = end - start;
      
      let progress = (current / total) * 100;
      progress = Math.max(0, Math.min(100, progress));
      
      progressBar.style.width = `${progress}%`;
    });
  }

  // ===========================================
  // Share Buttons (post.html)
  // ===========================================
  function initShareButtons() {
    // Twitter share
    document.querySelectorAll('[data-share="twitter"]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const url = window.location.href;
        const title = document.querySelector('h1')?.textContent || 'Check this out';
        const text = encodeURIComponent(`${title} ${url}`);
        window.open(`https://twitter.com/intent/tweet?text=${text}`, '_blank', 'width=550,height=420');
      });
    });

    // LinkedIn share
    document.querySelectorAll('[data-share="linkedin"]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const url = encodeURIComponent(window.location.href);
        window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${url}`, '_blank', 'width=550,height=420');
      });
    });

    // Copy link
    document.querySelectorAll('[data-share="copy"]').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.preventDefault();
        try {
          await navigator.clipboard.writeText(window.location.href);
          const originalText = btn.textContent;
          btn.textContent = '✓ Copied!';
          btn.classList.add('copied');
          setTimeout(() => {
            btn.textContent = originalText;
            btn.classList.remove('copied');
          }, 2000);
        } catch (err) {
          console.error('Failed to copy:', err);
        }
      });
    });

    // Email share
    document.querySelectorAll('[data-share="email"]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const url = window.location.href;
        const title = document.querySelector('h1')?.textContent || 'Check this out';
        const subject = encodeURIComponent(title);
        const body = encodeURIComponent(`I thought you might find this interesting: ${url}`);
        window.location.href = `mailto:?subject=${subject}&body=${body}`;
      });
    });
  }

  // ===========================================
  // Email Form Handler
  // ===========================================
  function initEmailForms() {
    const forms = document.querySelectorAll('.email-form');
    
    forms.forEach(form => {
      form.addEventListener('submit', (e) => handleSubscribe(e, form));
    });
  }

  function handleSubscribe(event, form) {
    event.preventDefault();
    
    const emailInput = form.querySelector('input[type="email"]');
    const submitBtn = form.querySelector('button[type="submit"]');
    
    if (!emailInput || !submitBtn) return;
    
    const email = emailInput.value.trim();
    
    // Validate email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      emailInput.style.borderColor = 'var(--red)';
      emailInput.focus();
      return;
    }
    
    // Reset border color
    emailInput.style.borderColor = '';
    
    // Show loading state
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Subscribing…';
    submitBtn.disabled = true;
    
    // Simulate API call (replace with real MailerLite endpoint)
    // Real implementation would look like:
    // fetch('[MAILERLITE_ENDPOINT]', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({ email })
    // })
    // .then(response => response.json())
    // .then(data => { ... })
    
    setTimeout(() => {
      // Success state
      submitBtn.textContent = "✓ You're in!";
      submitBtn.style.backgroundColor = 'var(--green)';
      submitBtn.style.borderColor = 'var(--green)';
      emailInput.value = '';
      
      // Reset after 3 seconds
      setTimeout(() => {
        submitBtn.textContent = originalText;
        submitBtn.style.backgroundColor = '';
        submitBtn.style.borderColor = '';
        submitBtn.disabled = false;
      }, 3000);
    }, 1000);
  }

  // Make handleSubscribe available globally
  window.handleSubscribe = handleSubscribe;

  // ===========================================
  // URL Parameter Handling (blog.html)
  // ===========================================
  function initURLParams() {
    const urlParams = new URLSearchParams(window.location.search);
    
    // Handle category param
    const catParam = urlParams.get('cat');
    if (catParam) {
      const categoryTab = document.querySelector(`.category-tab[data-category="${catParam}"]`);
      if (categoryTab) {
        categoryTab.click();
      }
    }
    
    // Handle search query param
    const queryParam = urlParams.get('q');
    if (queryParam) {
      const searchInput = document.querySelector('#live-search');
      if (searchInput) {
        searchInput.value = queryParam;
        // Trigger filter
        const event = new Event('input', { bubbles: true });
        searchInput.dispatchEvent(event);
      }
    }
  }

  // ===========================================
  // Ticker Touch Support
  // ===========================================
  function initTickerTouch() {
    const tickerTrack = document.querySelector('.ticker-track');
    
    if (!tickerTrack) return;

    // Pause on touch for mobile devices
    tickerTrack.addEventListener('touchstart', () => {
      tickerTrack.style.animationPlayState = 'paused';
    });

    tickerTrack.addEventListener('touchend', () => {
      tickerTrack.style.animationPlayState = 'running';
    });
  }

  // ===========================================
  // Cookie Consent Banner (GDPR + AdSense Compliant)
  // ===========================================
  
  // Initialize Google Consent Mode defaults (before any Google scripts load)
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  
  // Check existing consent on page load
  const existingConsent = localStorage.getItem('ff_cookie_consent');
  if (existingConsent === 'all') {
    gtag('consent', 'default', {
      'ad_storage': 'granted',
      'ad_user_data': 'granted',
      'ad_personalization': 'granted',
      'analytics_storage': 'granted'
    });
  } else if (existingConsent === 'necessary') {
    gtag('consent', 'default', {
      'ad_storage': 'denied',
      'ad_user_data': 'denied',
      'ad_personalization': 'denied',
      'analytics_storage': 'granted'
    });
  } else {
    // No consent yet - default to denied (GDPR compliant)
    gtag('consent', 'default', {
      'ad_storage': 'denied',
      'ad_user_data': 'denied',
      'ad_personalization': 'denied',
      'analytics_storage': 'denied',
      'wait_for_update': 500
    });
  }

  function initCookieConsent() {
    const banner = document.querySelector('.cookie-consent');
    if (!banner) return;

    // Check if consent already given
    const consent = localStorage.getItem('ff_cookie_consent');
    if (consent) return;

    // Show banner after short delay
    setTimeout(() => {
      banner.classList.add('active');
    }, 1000);

    // Accept all cookies (including personalized ads)
    const acceptBtn = banner.querySelector('.btn-accept');
    if (acceptBtn) {
      acceptBtn.addEventListener('click', () => {
        localStorage.setItem('ff_cookie_consent', 'all');
        banner.classList.remove('active');
        
        // Update Google Consent Mode - grant all
        gtag('consent', 'update', {
          'ad_storage': 'granted',
          'ad_user_data': 'granted',
          'ad_personalization': 'granted',
          'analytics_storage': 'granted'
        });
      });
    }

    // Necessary only (non-personalized ads, basic analytics)
    const necessaryBtn = banner.querySelector('.btn-necessary');
    if (necessaryBtn) {
      necessaryBtn.addEventListener('click', () => {
        localStorage.setItem('ff_cookie_consent', 'necessary');
        banner.classList.remove('active');
        
        // Update Google Consent Mode - deny personalization
        gtag('consent', 'update', {
          'ad_storage': 'denied',
          'ad_user_data': 'denied',
          'ad_personalization': 'denied',
          'analytics_storage': 'granted'
        });
      });
    }
  }

  // Initialize cookie consent
  initCookieConsent();

})();
