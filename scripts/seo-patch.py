#!/usr/bin/env python3
"""
SEO optimisation patch for kinetic-energy.co.uk
Fixes: titles, meta descriptions, og:tags, twitter tags, H1s, JSON-LD.
"""
import re, sys, json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
BASE_URL  = "https://www.kinetic-energy.co.uk"
BRAND     = "Kinetic Energy Consulting"

# ---------------------------------------------------------------------------
# Per-page SEO data
# ---------------------------------------------------------------------------
PAGES = {
    "index.html": {
        "title": f"Commercial Strategy & Sales Consulting for Energy Businesses | {BRAND}",
        "description": "Kinetic Energy Consulting helps energy and technology businesses sharpen their sales strategy, build powerful go-to-market plans and drive real commercial results. We turn complex opportunities into clear growth.",
        "og_title": f"Commercial Strategy & Sales Consulting | {BRAND}",
    },
    "why-kinetic-energy.html": {
        "title": f"Why Kinetic Energy Consulting? | {BRAND}",
        "description": "Driven by experience, powered by results. We've led energy teams, shaped major deals and navigated real commercial challenges. Discover why businesses trust Kinetic Energy Consulting to drive growth.",
        "h1": "Driven by Experience. Powered by Results.",
    },
    "services-we-deliver.html": {
        "title": f"Commercial Consulting Services for the Energy Sector | {BRAND}",
        "description": "From go-to-market strategy to bid support, sales coaching and market entry — explore the full range of commercial consulting services Kinetic Energy Consulting delivers to energy businesses.",
        "h1": "Commercial Consulting Services",
    },
    "who-we-work-with.html": {
        "title": f"Who We Work With | {BRAND}",
        "description": "We work with energy solution providers, consultancies, engineering firms, investors and new market entrants. Find out if Kinetic Energy Consulting is the right partner for your business.",
    },
    "our-story.html": {
        "title": f"Our Story | {BRAND}",
        "description": "The story behind Kinetic Energy Consulting — built on more than 30 years of frontline commercial experience in the energy sector, helping businesses turn strategy into real, measurable growth.",
    },
    "experience.html": {
        "title": f"Our Experience | {BRAND}",
        "description": "Decades of hands-on commercial leadership across the energy sector. Explore the track record, clients and results that make Kinetic Energy Consulting a trusted partner for energy businesses.",
    },
    "contact.html": {
        "title": f"Contact Us | {BRAND}",
        "description": "Get in touch with Kinetic Energy Consulting. Whether you have a specific challenge or just want to explore how we can help, we'd love to hear from you.",
    },
    "pricing.html": {
        "title": f"Pricing & Engagement Options | {BRAND}",
        "description": "Flexible engagement models to suit your business. From project-based work to fractional leadership, find out how Kinetic Energy Consulting structures its commercial consulting services.",
    },
    "return-on-investment.html": {
        "title": f"Return on Investment | {BRAND}",
        "description": "See how Kinetic Energy Consulting delivers clear, measurable ROI. Six proven ways our commercial consulting creates tangible returns for energy businesses from day one of engagement.",
        "h1": "The Six Ways We Generate Clear and Immediate ROI",
    },
    "testimonials.html": {
        "title": f"Client Testimonials | {BRAND}",
        "description": "Hear from the energy businesses we've helped. Client testimonials covering go-to-market strategy, sales performance, bid success and commercial growth delivered by Kinetic Energy Consulting.",
    },
    "insight.html": {
        "title": f"Insight & Articles | {BRAND}",
        "description": "Thought leadership and practical insight from Kinetic Energy Consulting. Articles covering energy market strategy, sales performance, commercial growth and the future of the energy sector.",
        "h1": "Insight & Articles",
    },
    "sales-assets.html": {
        "title": f"Sales Assets & Resources | {BRAND}",
        "description": "Practical sales tools, frameworks and resources for energy businesses. Developed by Kinetic Energy Consulting to support stronger commercial performance and sharper go-to-market execution.",
    },

    # Service pages — all were "About 1 — Kinetic Strategy Consulting"
    "bid-and-pursuit-strategy.html": {
        "title": f"Bid & Pursuit Strategy | {BRAND}",
        "description": "Win more complex energy deals. We help organisations sharpen bid qualification, pursuit planning and proposal quality — so every bid is more focused, competitive and likely to convert.",
        "h1": "Bid & Pursuit Strategy",
    },
    "commercial-strategy-deal-structuring.html": {
        "title": f"Commercial Strategy & Deal Structuring | {BRAND}",
        "description": "Build commercial models that work in the real world. From pricing frameworks to PPAs and funded delivery models, we help energy businesses structure deals that are profitable and scalable.",
        "h1": "Commercial Strategy & Deal Structuring",
    },
    "go-to-market-strategy.html": {
        "title": f"Go-to-Market Strategy | {BRAND}",
        "description": "Get clarity on how to win in the markets that matter most. We help energy businesses define target customers, sharpen their positioning and build go-to-market momentum that lasts.",
        "h1": "Go-to-Market Strategy",
    },
    "interim-and-fractional-commercial-leadership.html": {
        "title": f"Interim & Fractional Commercial Leadership | {BRAND}",
        "description": "Senior commercial capability when you need it. Our fractional sales and strategy leaders provide hands-on expertise to shape direction and drive results — without the full-time overhead.",
        "h1": "Interim & Fractional Commercial Leadership",
    },
    "market-entry-and-expansion-support.html": {
        "title": f"Market Entry & Expansion Support | {BRAND}",
        "description": "Expanding into new energy sectors or regions? We provide evidence-led market entry support helping businesses and investors identify the right opportunities and enter new markets with confidence.",
        "h1": "Market Entry & Expansion Support",
    },
    "marketing-and-demand-alignment.html": {
        "title": f"Marketing & Demand Alignment | {BRAND}",
        "description": "Bridge the gap between sales and marketing. We align energy business teams around shared targets, clear messaging and qualified pipelines — turning activity into revenue, not just leads.",
        "h1": "Marketing & Demand Alignment",
    },
    "marketing-proposition-development.html": {
        "title": f"Marketing & Proposition Development | {BRAND}",
        "description": "Turn technical expertise into propositions that win customers. We build marketing strategies combining sharp messaging, sector positioning and digital tools that generate real demand in energy markets.",
        "h1": "Marketing & Proposition Development",
    },
    "non-executive-representation.html": {
        "title": f"Non-Executive Board Representation | {BRAND}",
        "description": "Independent commercial thinking for stronger boards. We provide non-executive representation that brings external challenge, market clarity and strategic insight to energy businesses.",
        "h1": "Non-Executive Board Representation",
    },
    "partnership-and-channel-strategy.html": {
        "title": f"Partnership & Channel Strategy | {BRAND}",
        "description": "Scale faster through the right partnerships. We identify, structure and activate partner and channel relationships that open new energy markets without the cost of building from scratch.",
        "h1": "Partnership & Channel Strategy",
    },
    "recruiting-the-right-people.html": {
        "title": f"Recruiting the Right Commercial People | {BRAND}",
        "description": "Build teams that deliver. With 30+ years of experience hiring and leading commercial teams, we help energy businesses recruit individuals who strengthen performance and drive long-term growth.",
        "h1": "Recruiting the Right People",
    },
    "sales-performance-and-coaching.html": {
        "title": f"Sales Performance & Coaching | {BRAND}",
        "description": "Unlock your team's commercial potential. We help energy businesses build sales strategies that improve conversion, increase pipeline velocity and create the structure needed to win consistently.",
        "h1": "Sales Performance & Coaching",
    },
    "sales-process-pipeline-optimisation.html": {
        "title": f"Sales Process & Pipeline Optimisation | {BRAND}",
        "description": "Build a sales function on repeatable process, not individual heroics. We help energy businesses design clear sales systems that bring structure, consistency and control to their pipeline.",
        "h1": "Sales Process & Pipeline Optimisation",
    },
    "value-proposition-development.html": {
        "title": f"Value Proposition Development | {BRAND}",
        "description": "Translate what you do into outcomes customers buy. We help energy businesses build value propositions around cost reduction, risk and resilience — not just features — to win more consistently.",
        "h1": "Value Proposition Development",
    },
    "why-not-just-use-ai.html": {
        "title": f"Why Not Just Use AI? | {BRAND}",
        "description": "AI helps, but experience delivers. When shaping energy sales strategy or building commercial models, real-world knowledge makes the difference. Here's why human expertise still matters.",
        "h1": "AI Helps – Experience Delivers",
    },

    # "Who we work with" sub-pages
    "corporate-leadership-teams-in-transition.html": {
        "title": f"Corporate Leadership Teams in Transition | {BRAND}",
        "description": "Supporting corporate leadership teams navigating commercial transition. We provide strategic clarity and hands-on support to help energy businesses realign, restructure and accelerate performance.",
    },
    "energy-and-decarbonisation-solution-providers.html": {
        "title": f"Energy & Decarbonisation Solution Providers | {BRAND}",
        "description": "We help energy and decarbonisation solution providers sharpen their commercial strategy, build compelling propositions and accelerate growth in a rapidly evolving market.",
    },
    "energy-consultancies.html": {
        "title": f"Energy Consultancies | {BRAND}",
        "description": "Commercial growth support for energy consultancies. We help consultancy businesses develop sharper propositions, stronger pipelines and more effective routes to market.",
    },
    "engineering-fm-providers.html": {
        "title": f"Engineering & FM Providers | {BRAND}",
        "description": "Helping engineering and FM providers win more energy contracts. We support commercial strategy, bid success and market positioning for businesses in the building services sector.",
    },
    "investors-funds-private-equity.html": {
        "title": f"Investors, Funds & Private Equity | {BRAND}",
        "description": "Commercial due diligence and growth support for investors and private equity. We help funds assess energy market opportunities and accelerate commercial performance in portfolio businesses.",
    },
    "new-market-entrants.html": {
        "title": f"New Market Entrants | {BRAND}",
        "description": "Entering the UK energy market? We provide commercial strategy, go-to-market planning and positioning support to help new entrants launch effectively and build momentum from day one.",
    },
}

# Blog articles that only need twitter:title fixed
TWITTER_TITLE_FIXES = {
    "insight/the-salesperson-the-algorithm-and-the-energy-bill.html": {
        "twitter_title": f"The Salesperson, the Algorithm, and the Energy Bill | {BRAND}",
        "twitter_description": "After 30 years in sales leadership and working in the energy sector, AI is the most disruptive shift I've seen. Here's how it's reshaping B2B energy sales — and what still requires human expertise.",
    },
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def update_or_add_meta(text: str, name_or_prop: str, attr: str, content: str) -> str:
    """Update existing meta tag or add it after <title> if missing."""
    pattern = rf'<meta\s+{attr}="{re.escape(name_or_prop)}"[^>]*/?>'
    replacement = f'<meta {attr}="{name_or_prop}" content="{content}"/>'
    if re.search(pattern, text):
        return re.sub(pattern, replacement, text)
    # Insert after </title>
    return re.sub(r'(</title>)', rf'\1\n{replacement}', text, count=1)


def set_title(text: str, new_title: str) -> str:
    return re.sub(r'<title>[^<]*</title>', f'<title>{new_title}</title>', text)


def inject_h1(text: str, h1_text: str) -> str:
    """Inject a visually-hidden H1 immediately after <body ...>"""
    # Only inject if no <h1 already exists in the visible content blocks
    if re.search(r'<h1(?!\s+class="blog-title")', text):
        # Check if it's already a proper h1 with real content
        h1_match = re.search(r'<h1[^>]*>(.+?)</h1>', text, re.DOTALL)
        if h1_match:
            return text  # already has a content h1, don't add another
    tag = f'<h1 class="seo-h1">{h1_text}</h1>'
    return re.sub(r'(<body[^>]*>)', rf'\1\n{tag}', text, count=1)


def fix_jsonld_homepage(text: str) -> str:
    """Expand JSON-LD on homepage with proper WebSite and LocalBusiness data."""
    website_schema = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "url": f"{BASE_URL}/",
        "name": BRAND,
        "description": "Commercial strategy, sales consulting and go-to-market support for energy and technology businesses.",
        "image": f"{BASE_URL}/assets/images/846d0f36-a6f0-4864-9131-5c2cf092159a--Kinetic-Energy-Logo-no-tag--White-Back.png",
    }
    local_business_schema = {
        "@context": "https://schema.org",
        "@type": "ProfessionalService",
        "name": BRAND,
        "url": f"{BASE_URL}/",
        "image": f"{BASE_URL}/assets/images/846d0f36-a6f0-4864-9131-5c2cf092159a--Kinetic-Energy-Logo-no-tag--White-Back.png",
        "description": "Commercial strategy, sales consulting and go-to-market support for energy and technology businesses in the UK.",
        "telephone": "+44 787 201 5769",
        "email": "martynsheridan@gmail.com",
        "address": {
            "@type": "PostalAddress",
            "addressCountry": "GB"
        },
        "areaServed": "GB",
        "priceRange": "££",
    }
    new_jsonld = (
        f'<script type="application/ld+json">{json.dumps(website_schema, ensure_ascii=False)}</script>'
        f'<script type="application/ld+json">{json.dumps(local_business_schema, ensure_ascii=False)}</script>'
    )
    # Replace existing JSON-LD blocks in head
    text = re.sub(
        r'(<script\s+type="application/ld\+json">.*?</script>)+',
        new_jsonld,
        text,
        count=1,
        flags=re.DOTALL
    )
    return text


# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------

def process_page(filepath: Path, data: dict) -> str:
    text = filepath.read_text(encoding="utf-8", errors="ignore")
    original = text

    title    = data.get("title")
    desc     = data.get("description")
    og_title = data.get("og_title", title)
    h1       = data.get("h1")

    if title:
        text = set_title(text, title)
        # og:title
        text = update_or_add_meta(text, "og:title", "property", og_title or title)
        # twitter:title
        text = update_or_add_meta(text, "twitter:title", "name", og_title or title)

    if desc:
        text = update_or_add_meta(text, "description", "name", desc)
        text = update_or_add_meta(text, "og:description", "property", desc)
        text = update_or_add_meta(text, "twitter:description", "name", desc)

    if h1:
        text = inject_h1(text, h1)

    return text if text != original else original


def process_twitter_fix(filepath: Path, data: dict) -> str:
    text = filepath.read_text(encoding="utf-8", errors="ignore")
    original = text
    if "twitter_title" in data:
        text = update_or_add_meta(text, "twitter:title", "name", data["twitter_title"])
    if "twitter_description" in data:
        text = update_or_add_meta(text, "twitter:description", "name", data["twitter_description"])
    return text if text != original else original


def run():
    updated = 0
    errors  = []

    # Main page fixes
    for filename, data in PAGES.items():
        filepath = REPO_ROOT / filename
        if not filepath.exists():
            print(f"  [miss] {filename}", file=sys.stderr)
            continue
        try:
            new_text = process_page(filepath, data)
            if filename == "index.html":
                new_text = fix_jsonld_homepage(new_text)
            original = filepath.read_text(encoding="utf-8", errors="ignore")
            if new_text != original:
                filepath.write_text(new_text, encoding="utf-8")
                updated += 1
                print(f"  [ok]   {filename}")
            else:
                print(f"  [skip] {filename}")
        except Exception as e:
            errors.append((filename, str(e)))
            print(f"  [err]  {filename}: {e}", file=sys.stderr)

    # Twitter-only fixes
    for filename, data in TWITTER_TITLE_FIXES.items():
        filepath = REPO_ROOT / filename
        if not filepath.exists():
            print(f"  [miss] {filename}", file=sys.stderr)
            continue
        try:
            new_text = process_twitter_fix(filepath, data)
            original = filepath.read_text(encoding="utf-8", errors="ignore")
            if new_text != original:
                filepath.write_text(new_text, encoding="utf-8")
                updated += 1
                print(f"  [ok]   {filename}")
            else:
                print(f"  [skip] {filename}")
        except Exception as e:
            errors.append((filename, str(e)))
            print(f"  [err]  {filename}: {e}", file=sys.stderr)

    print(f"\nDone. Updated {updated} files.")
    if errors:
        for f, e in errors:
            print(f"  ERROR {f}: {e}", file=sys.stderr)


if __name__ == "__main__":
    run()
