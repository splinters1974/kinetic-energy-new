#!/usr/bin/env python3
"""
Remove all external Squarespace CDN scripts from HTML files.
Fix OG/canonical URLs to use absolute paths.
This eliminates the Norton malware false-positive caused by loading
scripts from squarespace.com on a non-Squarespace domain.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
BASE_URL = "https://www.kinetic-energy.co.uk"

# OG image: use a local image (update this path if a better one is uploaded)
LOCAL_OG_IMAGE = "/assets/images/004356f6-0d9f-43e3-8f36-66888b3666fb--IMG_5908.JPG"
LOCAL_OG_IMAGE_ABS = f"{BASE_URL}{LOCAL_OG_IMAGE}"

def clean_html(text: str) -> str:
    # 1. Remove Squarespace preconnect hint
    text = re.sub(r'\s*<link\s+rel="preconnect"\s+href="https://images\.squarespace-cdn\.com"\s*>', '', text)

    # 2. Remove polyfiller scripts that are appended to the Google Fonts line
    #    Pattern: <script ... src="https://assets.squarespace.com/@sqs/polyfiller/..."></script>
    text = re.sub(
        r'<script[^>]*src="https://assets\.squarespace\.com/@sqs/polyfiller/[^"]*"[^>]*></script>',
        '', text
    )

    # 3. Remove the SQUARESPACE_ROLLUPS init script
    text = re.sub(r'<script[^>]*>SQUARESPACE_ROLLUPS\s*=\s*\{\};\s*</script>', '', text)

    # 4. Remove inline SQUARESPACE_ROLLUPS registration scripts
    #    Pattern: <script>(function(rollups, name) { ... })(SQUARESPACE_ROLLUPS, '...');</script>
    text = re.sub(
        r'<script>\(function\(rollups,\s*name\).*?\)\(SQUARESPACE_ROLLUPS,\s*\'[^\']*\'\);\s*</script>',
        '', text, flags=re.DOTALL
    )

    # 5. Remove all external script tags pointing to assets.squarespace.com
    text = re.sub(
        r'<script[^>]*src="https://assets\.squarespace\.com/[^"]*"[^>]*>\s*</script>',
        '', text
    )

    # 6. Remove the huge Static.SQUARESPACE_CONTEXT inline script block
    text = re.sub(
        r'<script[^>]*data-name="static-context"[^>]*>.*?</script>',
        '', text, flags=re.DOTALL
    )
    # Also catch it without data-name but containing SQUARESPACE_CONTEXT
    text = re.sub(
        r'<script[^>]*>\s*Static\s*=\s*window\.Static.*?</script>',
        '', text, flags=re.DOTALL
    )

    # 7. Remove definitions.sqspcdn.com script tags (image effects)
    text = re.sub(
        r'<script[^>]*src="https://definitions\.sqspcdn\.com/[^"]*"[^>]*>\s*</script>',
        '', text
    )
    # Also the protocol-relative variants
    text = re.sub(
        r'<script[^>]*src="//definitions\.sqspcdn\.com/[^"]*"[^>]*>\s*</script>',
        '', text
    )
    # Remove definitions.sqspcdn.com CSS link tags
    text = re.sub(
        r'<link[^>]*href="https://definitions\.sqspcdn\.com/[^"]*"[^>]*/?>',
        '', text
    )
    text = re.sub(
        r'<link[^>]*href="//definitions\.sqspcdn\.com/[^"]*"[^>]*/?>',
        '', text
    )

    # 7b. Remove Static.COOKIE_BANNER_CAPABLE script (Squarespace cookie tracking)
    text = re.sub(
        r'<script>\s*Static\.COOKIE_BANNER_CAPABLE\s*=\s*true;\s*</script>',
        '', text
    )

    # 8. Remove the user-account-core CSS (Squarespace login styling, useless here)
    text = re.sub(
        r'<link[^>]*href="/assets/css/user-account-core\.css"[^>]*/?>',
        '', text
    )
    text = re.sub(
        r'<link[^>]*href="/assets/css/user-account-core-[^"]*\.css"[^>]*/?>',
        '', text
    )

    # 8b. Fix JSON-LD structured data: replace Squarespace CDN logo URL with local path
    # The logo image hash 846d0f36-a6f0-4864-9131-5c2cf092159a is stored locally
    LOCAL_LOGO = f"{BASE_URL}/assets/images/846d0f36-a6f0-4864-9131-5c2cf092159a--Kinetic-Energy-Logo-no-tag--White-Back.png"
    text = re.sub(
        r'//images\.squarespace-cdn\.com/content/v1/[^"\'\\]+/846d0f36-a6f0-4864-9131-5c2cf092159a/[^"\'\\]*',
        LOCAL_LOGO,
        text
    )
    # Fix any other static1.squarespace.com in JSON-LD (LocalBusiness image etc.)
    text = re.sub(
        r'"image":"https://static1\.squarespace\.com/[^"]*"',
        f'"image":"{LOCAL_OG_IMAGE_ABS}"',
        text
    )

    # 8c. Remove the Squarespace comment tag
    text = text.replace('<!-- End of Squarespace Headers -->', '')

    # 9. Fix OG/social image URLs (still pointing to static1.squarespace.com)
    #    Replace the Squarespace-hosted OG image with the local copy
    text = re.sub(
        r'https://static1\.squarespace\.com/static/[^"]*?/IMG_5880\.jpeg\?format=\d+w',
        LOCAL_OG_IMAGE_ABS,
        text
    )
    # Catch any remaining static1.squarespace.com image references in meta tags
    text = re.sub(
        r'(content|href)="https://static1\.squarespace\.com/[^"]*"',
        lambda m: m.group(0).replace(
            m.group(0),
            f'{m.group(1)}="{LOCAL_OG_IMAGE_ABS}"'
        ) if 'og:image' in text[:text.find(m.group(0))+200] or 'twitter:image' in text[:text.find(m.group(0))+200] or 'thumbnailUrl' in text[:text.find(m.group(0))+200] or 'image_src' in text[:text.find(m.group(0))+200] else m.group(0),
        text
    )

    # 10. Fix og:url to use absolute URL (currently relative like "index.html")
    text = re.sub(
        r'(<meta\s+property="og:url"\s+content=")([^/"][^"]*\.html|[^/"][^"]*\.xml|index\.html)(")',
        lambda m: f'{m.group(1)}{BASE_URL}/{m.group(2).lstrip("/")}{m.group(3)}',
        text
    )
    # Handle og:url that is just "index.html" -> homepage
    text = re.sub(
        r'(<meta\s+property="og:url"\s+content=")index\.html(")',
        f'\\1{BASE_URL}/\\2',
        text
    )

    # 11. Fix canonical link to use absolute URL
    text = re.sub(
        r'(<link\s+rel="canonical"\s+href=")(?!https?://)([^"]+)(")',
        lambda m: f'{m.group(1)}{BASE_URL}/{m.group(2).lstrip("/")}{m.group(3)}',
        text
    )

    return text


def fix_jsonld_urls(text: str, filename: str) -> str:
    """Fix relative URLs in JSON-LD structured data blocks."""
    stem = Path(filename).name
    if stem == 'index.html':
        page_url = f"{BASE_URL}/"
    else:
        page_path = stem.replace('.html', '')
        page_url = f"{BASE_URL}/{page_path}"

    def fix_jsonld_block(m):
        block = m.group(0)
        # Fix "url":"relative" -> absolute
        block = re.sub(
            r'"url"\s*:\s*"(?!https?://)([^"]*)"',
            f'"url":"{page_url}"',
            block
        )
        return block

    text = re.sub(
        r'<script\s+type="application/ld\+json">.*?</script>',
        fix_jsonld_block,
        text,
        flags=re.DOTALL
    )
    return text


def fix_og_image_meta(text: str, filename: str) -> str:
    """
    More targeted fix for static1.squarespace.com image meta tags.
    Replaces og:image, twitter:image, thumbnailUrl, image_src meta content.
    """
    # og:image
    text = re.sub(
        r'(<meta\s+property="og:image"\s+content=")https://static1\.squarespace\.com/[^"]*(")',
        f'\\1{LOCAL_OG_IMAGE_ABS}\\2',
        text
    )
    # twitter:image
    text = re.sub(
        r'(<meta\s+name="twitter:image"\s+content=")https://static1\.squarespace\.com/[^"]*(")',
        f'\\1{LOCAL_OG_IMAGE_ABS}\\2',
        text
    )
    # itemprop thumbnailUrl
    text = re.sub(
        r'(<meta\s+itemprop="thumbnailUrl"\s+content=")https://static1\.squarespace\.com/[^"]*(")',
        f'\\1{LOCAL_OG_IMAGE_ABS}\\2',
        text
    )
    # itemprop image
    text = re.sub(
        r'(<meta\s+itemprop="image"\s+content=")https://static1\.squarespace\.com/[^"]*(")',
        f'\\1{LOCAL_OG_IMAGE_ABS}\\2',
        text
    )
    # link image_src
    text = re.sub(
        r'(<link\s+rel="image_src"\s+href=")https://static1\.squarespace\.com/[^"]*(")',
        f'\\1{LOCAL_OG_IMAGE_ABS}\\2',
        text
    )
    return text


def fix_canonical_and_og_url(text: str, filename: str) -> str:
    """Fix canonical and og:url to use absolute URLs."""
    # Determine the page URL
    stem = Path(filename).name
    if stem == 'index.html':
        page_url = f"{BASE_URL}/"
    else:
        # Remove .html extension for clean URL
        page_path = stem.replace('.html', '')
        page_url = f"{BASE_URL}/{page_path}"

    # Fix canonical
    text = re.sub(
        r'<link\s+rel="canonical"\s+href="[^"]*"',
        f'<link rel="canonical" href="{page_url}"',
        text
    )
    # Fix og:url
    text = re.sub(
        r'<meta\s+property="og:url"\s+content="[^"]*"',
        f'<meta property="og:url" content="{page_url}"',
        text
    )
    # Fix itemprop url (schema.org)
    text = re.sub(
        r'<meta\s+itemprop="url"\s+content="[^"]*"',
        f'<meta itemprop="url" content="{page_url}"',
        text
    )

    return text


def process_files():
    html_files = list(REPO_ROOT.glob("*.html")) + list((REPO_ROOT / "insight").glob("*.html"))
    updated = 0
    errors = []

    for f in sorted(html_files):
        try:
            original = f.read_text(encoding="utf-8", errors="ignore")
            text = clean_html(original)
            text = fix_og_image_meta(text, f.name)
            text = fix_canonical_and_og_url(text, f.name)
            text = fix_jsonld_urls(text, f.name)

            if text != original:
                f.write_text(text, encoding="utf-8")
                updated += 1
                print(f"  [ok]   {f.relative_to(REPO_ROOT)}")
            else:
                print(f"  [skip] {f.relative_to(REPO_ROOT)} (no changes)")
        except Exception as e:
            errors.append((f, str(e)))
            print(f"  [err]  {f.relative_to(REPO_ROOT)}: {e}", file=sys.stderr)

    print(f"\nDone. Updated {updated}/{len(html_files)} HTML files.")
    if errors:
        print(f"Errors in {len(errors)} files:", file=sys.stderr)
        for f, err in errors:
            print(f"  {f}: {err}", file=sys.stderr)


if __name__ == "__main__":
    print(f"Processing HTML files in {REPO_ROOT}")
    process_files()
