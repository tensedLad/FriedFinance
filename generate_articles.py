"""
Generate 34 SEO-optimized HTML article pages from batch markdown files.
Only uses ARTICLE 1: STANDARD INFORMATIONAL from each topic.
"""
import os
import re
from pathlib import Path

# Configuration
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = "https://friedfinance.com"

# Category mappings
CATEGORIES = {
    "batch1-business-loans": "business-loans",
    "batch1-business-loans-part2": "business-loans",
    "batch2-business-tax": "business-tax",
    "batch3-self-employment": "self-employment",
    "batch4-credit-cards": "credit-cards",
    "batch5-personal-finance": "personal-finance",
    "batch6-banking-investments": "banking",
    "batch7-business-insurance": "insurance",
    "batch8-car-insurance": "car-insurance",
    "batch9-debt-specialist": "debt",
}

CATEGORY_DISPLAY = {
    "business-loans": "Business Loans",
    "business-tax": "Business Tax",
    "self-employment": "Self-Employment",
    "credit-cards": "Credit Cards",
    "personal-finance": "Personal Finance",
    "banking": "Banking & Investments",
    "insurance": "Business Insurance",
    "car-insurance": "Car Insurance",
    "debt": "Debt",
}

TAG_CLASSES = {
    "business-loans": "tag-business-loans",
    "business-tax": "tag-taxes",
    "self-employment": "tag-self-employment",
    "credit-cards": "tag-credit-cards",
    "personal-finance": "tag-personal-finance",
    "banking": "tag-banking",
    "insurance": "tag-insurance",
    "car-insurance": "tag-car-insurance",
    "debt": "tag-debt",
}


def slugify(text):
    """Convert title to URL-friendly slug."""
    # Remove year and UK mentions for cleaner URLs
    text = re.sub(r'\s+UK\s+2026:?', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+2026:?', '', text)
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[-\s]+', '-', text).strip('-')
    return text[:60]  # Limit length


def markdown_to_html(content):
    """Convert markdown content to HTML."""
    lines = content.split('\n')
    html_lines = []
    in_list = False
    in_table = False
    table_header_done = False
    
    for line in lines:
        stripped = line.strip()
        
        # Skip empty lines
        if not stripped:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            if in_table:
                html_lines.append('</tbody></table></div>')
                in_table = False
                table_header_done = False
            html_lines.append('')
            continue
        
        # Tables
        if stripped.startswith('|') and '|' in stripped[1:]:
            cells = [c.strip() for c in stripped.split('|')[1:-1]]
            if all(set(c) <= {'-', ':'} for c in cells):
                continue  # Skip separator row
            if not in_table:
                html_lines.append('<div class="table-wrapper"><table>')
                html_lines.append('<thead><tr>')
                for cell in cells:
                    html_lines.append(f'<th>{cell}</th>')
                html_lines.append('</tr></thead><tbody>')
                in_table = True
                table_header_done = True
            else:
                html_lines.append('<tr>')
                for cell in cells:
                    cell = convert_inline(cell)
                    html_lines.append(f'<td>{cell}</td>')
                html_lines.append('</tr>')
            continue
        
        # Close table if we have content that's not a table
        if in_table and not stripped.startswith('|'):
            html_lines.append('</tbody></table></div>')
            in_table = False
            table_header_done = False
        
        # Headers
        if stripped.startswith('## '):
            heading_text = stripped[3:]
            heading_id = slugify(heading_text)
            html_lines.append(f'<h2 id="{heading_id}">{heading_text}</h2>')
            continue
        if stripped.startswith('### '):
            heading_text = stripped[4:]
            heading_id = slugify(heading_text)
            html_lines.append(f'<h3 id="{heading_id}">{heading_text}</h3>')
            continue
        
        # Unordered lists
        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            item_text = convert_inline(stripped[2:])
            html_lines.append(f'<li>{item_text}</li>')
            continue
        
        # Numbered lists
        if re.match(r'^\d+\.\s', stripped):
            if not in_list:
                html_lines.append('<ul>')  # Using ul for styled lists
                in_list = True
            item_text = convert_inline(re.sub(r'^\d+\.\s', '', stripped))
            html_lines.append(f'<li>{item_text}</li>')
            continue
        
        # Close list if we have content that's not a list item
        if in_list:
            html_lines.append('</ul>')
            in_list = False
        
        # Paragraphs
        para_text = convert_inline(stripped)
        html_lines.append(f'<p>{para_text}</p>')
    
    # Close any open lists
    if in_list:
        html_lines.append('</ul>')
    if in_table:
        html_lines.append('</tbody></table></div>')
    
    return '\n          '.join(html_lines)


def convert_inline(text):
    """Convert inline markdown (bold, links, etc.)."""
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text


def extract_articles(filepath):
    """Extract ARTICLE 1 (Standard) articles from a batch file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by URL headers
    url_sections = re.split(r'\n## URL:', content)
    articles = []
    
    for section in url_sections[1:]:  # Skip first empty split
        # Find ARTICLE 1 section
        match = re.search(
            r'### ARTICLE 1: STANDARD INFORMATIONAL\s*\n\n'
            r'\*\*Title:\*\*\s*(.+?)\n\n'
            r'\*\*Meta Description:\*\*\s*(.+?)\n\n'
            r'---\n\n(.+?)(?=\n\n---\n\n### ARTICLE 2:|$)',
            section,
            re.DOTALL
        )
        
        if match:
            title = match.group(1).strip()
            meta_desc = match.group(2).strip()
            body = match.group(3).strip()
            articles.append({
                'title': title,
                'meta_description': meta_desc,
                'content': body
            })
    
    return articles


def generate_html(article, category, filename):
    """Generate HTML file for an article."""
    title = article['title']
    meta_desc = article['meta_description']
    content_html = markdown_to_html(article['content'])
    
    category_display = CATEGORY_DISPLAY.get(category, category.title())
    tag_class = TAG_CLASSES.get(category, "tag-default")
    canonical = f"{DOMAIN}/{category}/{filename}"
    css_path = "../css/main.css"
    js_path = "../js/main.js"
    
    # Estimate read time (200 words per minute)
    word_count = len(article['content'].split())
    read_time = max(1, round(word_count / 200))
    
    # Create short deck/excerpt from first paragraph
    first_para = article['content'].split('\n\n')[0][:200]
    deck = first_para + "..." if len(first_para) == 200 else first_para
    
    html = f'''<!DOCTYPE html>
<html lang="en-GB">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{meta_desc}">
  <meta property="og:title" content="{title} | FriedFinance">
  <meta property="og:description" content="{meta_desc}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="https://friedfinance.com/images/og-image.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="https://friedfinance.com/images/og-image.png">
  <link rel="canonical" href="{canonical}">
  <title>{title} | FriedFinance</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,700&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{css_path}">
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": "{title}",
    "datePublished": "2026-02-17",
    "dateModified": "2026-02-17",
    "author": {{ "@type": "Organization", "name": "FriedFinance", "url": "{DOMAIN}" }},
    "publisher": {{ "@type": "Organization", "name": "FriedFinance", "url": "{DOMAIN}" }},
    "description": "{meta_desc}",
    "mainEntityOfPage": {{ "@type": "WebPage", "@id": "{canonical}" }}
  }}
  </script>
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{ "@type": "ListItem", "position": 1, "name": "Home", "item": "{DOMAIN}/" }},
      {{ "@type": "ListItem", "position": 2, "name": "{category_display}", "item": "{DOMAIN}/{category}/" }},
      {{ "@type": "ListItem", "position": 3, "name": "{title[:50]}" }}
    ]
  }}
  </script>
</head>
<body>
  <a href="#main-content" class="skip-link">Skip to main content</a>
  
  <!-- Market Ticker -->
  <div class="ticker-wrap">
    <div class="ticker-inner container">
      <span class="ticker-label">LIVE</span>
      <div class="ticker-track">
        <div class="ticker-item">
          <span class="ticker-name">FTSE 100</span>
          <span class="ticker-value">8,234.18</span>
          <span class="ticker-change up">↑ 0.72%</span>
        </div>
        <div class="ticker-item">
          <span class="ticker-name">FTSE 250</span>
          <span class="ticker-value">21,142.39</span>
          <span class="ticker-change up">↑ 0.94%</span>
        </div>
        <div class="ticker-item">
          <span class="ticker-name">GBP/USD</span>
          <span class="ticker-value">1.2742</span>
          <span class="ticker-change down">↓ 0.21%</span>
        </div>
        <div class="ticker-item">
          <span class="ticker-name">Bank Rate</span>
          <span class="ticker-value">4.50%</span>
          <span class="ticker-change">-</span>
        </div>
        <div class="ticker-item">
          <span class="ticker-name">Gold</span>
          <span class="ticker-value">£1,698.40</span>
          <span class="ticker-change up">↑ 0.34%</span>
        </div>
        <div class="ticker-item">
          <span class="ticker-name">Corporation Tax</span>
          <span class="ticker-value">25%</span>
          <span class="ticker-change">-</span>
        </div>
        <div class="ticker-item">
          <span class="ticker-name">UK SME Count</span>
          <span class="ticker-value">5.5m</span>
          <span class="ticker-change up">↑ 2.1%</span>
        </div>
        <!-- Duplicate for seamless loop -->
        <div class="ticker-item">
          <span class="ticker-name">FTSE 100</span>
          <span class="ticker-value">8,234.18</span>
          <span class="ticker-change up">↑ 0.72%</span>
        </div>
        <div class="ticker-item">
          <span class="ticker-name">FTSE 250</span>
          <span class="ticker-value">21,142.39</span>
          <span class="ticker-change up">↑ 0.94%</span>
        </div>
        <div class="ticker-item">
          <span class="ticker-name">GBP/USD</span>
          <span class="ticker-value">1.2742</span>
          <span class="ticker-change down">↓ 0.21%</span>
        </div>
        <div class="ticker-item">
          <span class="ticker-name">Bank Rate</span>
          <span class="ticker-value">4.50%</span>
          <span class="ticker-change">-</span>
        </div>
        <div class="ticker-item">
          <span class="ticker-name">Gold</span>
          <span class="ticker-value">£1,698.40</span>
          <span class="ticker-change up">↑ 0.34%</span>
        </div>
        <div class="ticker-item">
          <span class="ticker-name">Corporation Tax</span>
          <span class="ticker-value">25%</span>
          <span class="ticker-change">-</span>
        </div>
        <div class="ticker-item">
          <span class="ticker-name">UK SME Count</span>
          <span class="ticker-value">5.5m</span>
          <span class="ticker-change up">↑ 2.1%</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Masthead -->
  <header class="masthead">
    <div class="container masthead-inner">
      <div class="masthead-left">
        Tuesday, February 17, 2026 · Vol. I, No. 1
      </div>
      <div class="masthead-center">
        <a href="../index.html" class="logo">
          <span class="logo-fried">Fried</span><span class="logo-finance">Finance</span>
        </a>
        <div class="logo-tagline">Your Money. Made Simple.</div>
      </div>
      <div class="masthead-right">
        <a href="../index.html#newsletter" class="btn btn-primary btn-sm">Subscribe Free</a>
      </div>
    </div>
  </header>

  <!-- Navigation -->
  <nav class="nav-wrap" role="navigation" aria-label="Main navigation">
    <div class="container nav-inner">
      <ul class="nav-links">
        <li><a href="../index.html">Home</a></li>
        <li><a href="../blog.html">All Articles</a></li>
        <li><a href="../blog.html?cat=business-loans"{' class="active"' if category == 'business-loans' else ''}>Business Loans</a></li>
        <li><a href="../blog.html?cat=business-tax"{' class="active"' if category == 'business-tax' else ''}>Business Tax</a></li>
        <li><a href="../blog.html?cat=credit-cards"{' class="active"' if category == 'credit-cards' else ''}>Credit Cards</a></li>
        <li><a href="../blog.html?cat=insurance"{' class="active"' if category == 'insurance' else ''}>Insurance</a></li>
        <li><a href="../blog.html?cat=banking"{' class="active"' if category == 'banking' else ''}>Banking</a></li>
        <li><a href="../blog.html?cat=personal-finance"{' class="active"' if category == 'personal-finance' else ''}>Personal Finance</a></li>
        <li><a href="../blog.html?cat=debt"{' class="active"' if category == 'debt' else ''}>Debt</a></li>
        <li><a href="../about.html">About</a></li>
      </ul>
      <div class="nav-actions">
        <button class="nav-search-btn" aria-label="Search">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"></circle>
            <path d="M21 21l-4.35-4.35"></path>
          </svg>
        </button>
        <button class="hamburger" aria-label="Menu" aria-expanded="false">
          <div class="hamburger-lines">
            <span class="hamburger-line"></span>
            <span class="hamburger-line"></span>
            <span class="hamburger-line"></span>
          </div>
        </button>
      </div>
    </div>
  </nav>

  <!-- Mobile Menu Overlay -->
  <div class="mobile-menu-overlay" aria-hidden="true"></div>
  
  <!-- Mobile Menu -->
  <div class="mobile-menu" role="dialog" aria-label="Mobile navigation">
    <div class="mobile-menu-header">
      <span class="mobile-menu-logo">
        <span class="logo-fried">Fried</span><span class="logo-finance">Finance</span>
      </span>
      <button class="mobile-menu-close" aria-label="Close menu">×</button>
    </div>
    <ul class="mobile-menu-links">
      <li><a href="../index.html">Home</a></li>
      <li><a href="../blog.html">All Articles</a></li>
      <li><a href="../blog.html?cat=business-loans">Business Loans</a></li>
      <li><a href="../blog.html?cat=business-tax">Business Tax</a></li>
      <li><a href="../blog.html?cat=self-employment">Self-Employment</a></li>
      <li><a href="../blog.html?cat=credit-cards">Credit Cards</a></li>
      <li><a href="../blog.html?cat=personal-finance">Personal Finance</a></li>
      <li><a href="../blog.html?cat=banking">Banking & Investments</a></li>
      <li><a href="../blog.html?cat=insurance">Business Insurance</a></li>
      <li><a href="../blog.html?cat=car-insurance">Car Insurance</a></li>
      <li><a href="../blog.html?cat=debt">Debt</a></li>
      <li><a href="../about.html">About</a></li>
      <li><a href="../resources.html">Resources</a></li>
    </ul>
    <div class="mobile-menu-cta">
      <a href="../index.html#newsletter" class="btn btn-gold" style="width: 100%;">Subscribe Free</a>
    </div>
  </div>

  <!-- Search Overlay -->
  <div class="search-overlay" role="dialog" aria-label="Search">
    <div class="search-card">
      <input type="search" placeholder="Search articles..." aria-label="Search articles">
      <button class="search-close">ESC</button>
    </div>
  </div>

  <!-- Main Content -->
  <main id="main-content">
    <div class="container">
      <!-- Breadcrumb -->
      <nav class="breadcrumb" aria-label="Breadcrumb">
        <a href="../index.html">Home</a> → <a href="../blog.html?cat={category}">{category_display}</a> → <span>{title[:50]}...</span>
      </nav>

      <!-- Post Header -->
      <header class="post-header fade-up">
        <span class="tag {tag_class}">{category_display}</span>
        <h1>{title}</h1>
        <p class="post-deck">{deck}</p>
        <p class="post-byline">By FriedFinance · Published February 17, 2026 · {read_time} min read</p>
        <div class="post-share-mini">
          <button data-share="twitter">Twitter/X</button>
          <span>·</span>
          <button data-share="linkedin">LinkedIn</button>
          <span>·</span>
          <button data-share="copy">Copy Link</button>
        </div>
      </header>

      <!-- 3-Column Post Layout -->
      <div class="post-layout">
        <!-- Left Sidebar: TOC -->
        <aside class="toc-sidebar">
          <p class="toc-title">TABLE OF CONTENTS</p>
          <ul class="toc-list">
            <!-- JS will populate this -->
          </ul>
        </aside>

        <!-- Center: Article Content -->
        <article class="post-content fade-up">
          {content_html}

          <!-- Inline Email Capture -->
          <div class="inline-capture inline-capture-dark">
            <div class="inline-capture-icon">FREE</div>
            <h4>Get Weekly Finance Tips</h4>
            <p>Join thousands getting clear, honest money advice every week.</p>
            <form class="email-form">
              <input type="email" placeholder="Enter your email" required style="background: #2a2825; border-color: #2a2825; color: #faf8f4;">
              <button type="submit" class="btn btn-gold">Subscribe Free</button>
            </form>
          </div>

          <p>Questions? Drop us a note at <a href="mailto:hello@friedfinance.com">hello@friedfinance.com</a>. We read every email.</p>
        </article>

        <!-- Right Sidebar -->
        <aside class="post-sidebar">
          <!-- Reading Progress -->
          <div class="reading-progress">
            <div class="reading-progress-bar"></div>
          </div>

          <!-- Share Widget -->
          <div class="share-widget">
            <p class="share-title">SHARE THIS</p>
            <div class="share-buttons">
              <button class="share-btn" data-share="twitter">
                <span>𝕏</span> Share on X/Twitter
              </button>
              <button class="share-btn" data-share="linkedin">
                <span>in</span> Share on LinkedIn
              </button>
              <button class="share-btn" data-share="copy">
                <span>+</span> Copy Link
              </button>
              <button class="share-btn" data-share="email">
                <span>✉</span> Share via Email
              </button>
            </div>
          </div>

          <!-- Author Card -->
          <div class="author-card">
            <div class="author-avatar author-logo"><span class="logo-fried">Fried</span><span class="logo-finance">Finance</span></div>
            <div class="author-info">
              <p class="author-name">FriedFinance Editorial Team</p>
              <p class="author-bio">Trusted financial guidance since 2014.</p>
              <a href="../about.html" class="author-link">About us →</a>
            </div>
          </div>
        </aside>
      </div>
    </div>

    <!-- Comments Section -->
    <div class="container">
      <div class="comments-section fade-up">
        <h3>Have a question about this article?</h3>
        <p>Drop us a note at <a href="mailto:hello@friedfinance.com">hello@friedfinance.com</a>. We read every email.</p>
      </div>
    </div>
  </main>

  <!-- Footer -->
  <footer class="footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-brand">
          <a href="../index.html" class="logo">
            <span class="logo-fried">Fried</span><span class="logo-finance">Finance</span>
          </a>
          <p>FriedFinance covers loans, tax, insurance, credit cards, investing, and debt - with honest, clear guidance anyone can use.</p>
          <div class="footer-social">
            <a href="javascript:void(0)" aria-label="Twitter/X" title="Coming soon">𝕏</a>
            <a href="javascript:void(0)" aria-label="LinkedIn" title="Coming soon">in</a>
            <a href="mailto:hello@friedfinance.com" aria-label="Email">✉</a>
          </div>
        </div>
        <div class="footer-col">
          <h4>Topics</h4>
          <ul>
            <li><a href="../blog.html?cat=business-loans">Business Loans</a></li>
            <li><a href="../blog.html?cat=business-tax">Business Tax</a></li>
            <li><a href="../blog.html?cat=credit-cards">Credit Cards</a></li>
            <li><a href="../blog.html?cat=insurance">Insurance</a></li>
            <li><a href="../blog.html?cat=banking">Banking</a></li>
            <li><a href="../blog.html?cat=debt">Debt</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h4>Site</h4>
          <ul>
            <li><a href="../index.html">Home</a></li>
            <li><a href="../blog.html">All Articles</a></li>
            <li><a href="../about.html">About</a></li>
            <li><a href="../resources.html">Free Resources</a></li>
            <li><a href="mailto:hello@friedfinance.com">Contact</a></li>
          </ul>
        </div>
        <div class="footer-newsletter">
          <h4>Newsletter</h4>
          <p>Get weekly money tips, free.</p>
          <form class="email-form">
            <input type="email" placeholder="Enter your email" required>
            <button type="submit" class="btn btn-gold">Subscribe</button>
          </form>
          <p class="email-note" style="margin-top: 0.5rem;">No spam. Unsubscribe anytime.</p>
        </div>
      </div>
      <div class="footer-bottom">
        <p class="footer-copyright">© 2026 FriedFinance. All rights reserved.</p>
        <p class="footer-disclaimer">FriedFinance is for informational purposes only and does not constitute financial advice. Always consult a qualified financial professional before making decisions.</p>
        <div class="footer-legal">
          <a href="../privacy.html">Privacy Policy</a>
          <a href="../privacy.html">Terms of Use</a>
          <a href="../privacy.html">Disclaimer</a>
        </div>
      </div>
    </div>
  </footer>

  <!-- Cookie Consent Banner -->
  <div class="cookie-consent" role="dialog" aria-label="Cookie consent">
    <p>We use cookies for analytics and advertising. "Accept All" enables personalised ads. "Necessary Only" shows non-personalised ads. <a href="../privacy.html#cookies">Cookie Policy</a></p>
    <div class="cookie-consent-buttons">
      <button class="btn-accept">Accept All</button>
      <button class="btn-necessary">Necessary Only</button>
    </div>
  </div>

  <script type="module">
    import {{ inject }} from 'https://esm.sh/@vercel/analytics';
    inject();
  </script>
  <script src="{js_path}"></script>
</body>
</html>'''
    
    return html


def main():
    """Main function to generate all articles."""
    batch_files = [
        "batch1-business-loans.md",
        "batch1-business-loans-part2.md",
        "batch2-business-tax.md",
        "batch3-self-employment.md",
        "batch4-credit-cards.md",
        "batch5-personal-finance.md",
        "batch6-banking-investments.md",
        "batch7-business-insurance.md",
        "batch8-car-insurance.md",
        "batch9-debt-specialist.md",
    ]
    
    all_articles = []
    
    for batch_file in batch_files:
        filepath = BASE_DIR / batch_file
        if not filepath.exists():
            print(f"⚠️  File not found: {batch_file}")
            continue
        
        batch_name = batch_file.replace('.md', '')
        category = CATEGORIES.get(batch_name, 'general')
        
        articles = extract_articles(filepath)
        print(f"📄 {batch_file}: Found {len(articles)} standard articles")
        
        for article in articles:
            article['category'] = category
            article['batch'] = batch_name
            all_articles.append(article)
    
    print(f"\n📊 Total articles to generate: {len(all_articles)}")
    
    # Create category folders and generate HTML
    created_files = []
    for article in all_articles:
        category = article['category']
        category_dir = BASE_DIR / category
        category_dir.mkdir(exist_ok=True)
        
        filename = slugify(article['title']) + '.html'
        filepath = category_dir / filename
        
        html = generate_html(article, category, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        created_files.append({
            'category': category,
            'filename': filename,
            'title': article['title'],
            'path': f"{category}/{filename}"
        })
        print(f"✅ Created: {category}/{filename}")
    
    print(f"\n🎉 Successfully created {len(created_files)} HTML files!")
    
    # Generate summary
    print("\n📁 Files by category:")
    categories_count = {}
    for f in created_files:
        cat = f['category']
        categories_count[cat] = categories_count.get(cat, 0) + 1
    
    for cat, count in sorted(categories_count.items()):
        print(f"   {cat}/: {count} files")
    
    return created_files


if __name__ == "__main__":
    main()
