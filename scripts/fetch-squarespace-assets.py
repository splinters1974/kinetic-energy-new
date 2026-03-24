#!/usr/bin/env python3
import os, re, sys, time, urllib.request, urllib.error
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
ASSETS_CSS = REPO_ROOT / "assets" / "css"
ASSETS_JS  = REPO_ROOT / "assets" / "js"
ASSETS_IMG = REPO_ROOT / "assets" / "images"

for d in [ASSETS_CSS, ASSETS_JS, ASSETS_IMG]:
    d.mkdir(parents=True, exist_ok=True)

def extract_urls_from_html(pattern, files):
    found = set()
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        found.update(re.findall(pattern, text))
    return found

html_files = list(REPO_ROOT.glob("*.html")) + list((REPO_ROOT / "insight").glob("*.html"))

css_urls = extract_urls_from_html(r'href="(https://(?:static1|assets)\.squarespace\.com/[^"]+\.css[^"]*)"', html_files)
site_bundle_urls = extract_urls_from_html(r'src="(https://static1\.squarespace\.com/[^"]+site-bundle[^"]*\.js[^"]*)"', html_files)
favicon_urls = extract_urls_from_html(r'href="(https://images\.squarespace-cdn\.com/[^"]+favicon\.ico[^"]*)"', html_files)

all_img_urls = set()
for f in html_files:
    text = f.read_text(encoding="utf-8", errors="ignore")
    for m in re.finditer(r'https://images\.squarespace-cdn\.com/content/v1/[^\s"\'&<>]+', text):
        url = m.group(0).rstrip('",\'')
        base = re.sub(r'\?.*$', '', url)
        if re.search(r'\.(jpg|jpeg|png|gif|webp|svg|ico)$', base, re.I):
            all_img_urls.add(base)

def download(url, dest_path, retries=3):
    if dest_path.exists() and dest_path.stat().st_size > 0:
        print(f"  [skip] {dest_path.name}")
        return True
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            dest_path.write_bytes(data)
            print(f"  [ok]   {dest_path.name} ({len(data):,} bytes)")
            return True
        except urllib.error.HTTPError as e:
            print(f"  [err]  {url} → HTTP {e.code}", file=sys.stderr)
            return False
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"  [err]  {url} → {e}", file=sys.stderr)
                return False
    return False

def url_to_local_path(url):
    base_url = re.sub(r'\?.*$', '', url)
    parts = base_url.rstrip('/').split('/')
    filename = parts[-1]
    hash_seg = parts[-2] if len(parts) >= 2 else ''
    clean_name = re.sub(r'[^a-zA-Z0-9._-]', '-', filename)
    local_name = f"{hash_seg}--{clean_name}" if hash_seg else clean_name
    return ASSETS_IMG / local_name

url_map = {}

print("\n=== Downloading CSS ===")
for url in sorted(css_urls):
    filename = url.split('/')[-1].split('?')[0] or 'squarespace.css'
    dest = ASSETS_CSS / ('site.css' if 'site.css' in url else 'static.css' if 'static.css' in url else filename)
    if download(url, dest):
        url_map[url] = f"/assets/css/{dest.name}"

user_css_urls = extract_urls_from_html(r'href="(https://assets\.squarespace\.com/[^"]+user-account-core[^"]+\.css[^"]*)"', html_files)
for url in sorted(user_css_urls):
    dest = ASSETS_CSS / 'user-account-core.css'
    if download(url, dest):
        url_map[url] = "/assets/css/user-account-core.css"

print("\n=== Downloading JS ===")
for url in sorted(site_bundle_urls):
    dest = ASSETS_JS / 'site-bundle.js'
    if download(url, dest):
        url_map[url] = "/assets/js/site-bundle.js"

print("\n=== Downloading favicons ===")
for i, url in enumerate(sorted(favicon_urls)[:2]):
    name = ['favicon-light.ico', 'favicon-dark.ico'][i]
    dest = ASSETS_IMG / name
    base = re.sub(r'\?.*$', '', url)
    if download(url, dest):
        url_map[base] = f"/assets/images/{name}"

print(f"\n=== Downloading {len(all_img_urls)} images ===")
for url in sorted(all_img_urls):
    if 'favicon' in url.lower():
        continue
    dest = url_to_local_path(url)
    if download(url + "?format=1500w", dest):
        url_map[url] = f"/assets/images/{dest.name}"

print("\n=== Updating HTML files ===")

def replace_in_html(text, url_map):
    for sq_url, local_path in sorted(url_map.items(), key=lambda x: -len(x[0])):
        text = text.replace(sq_url, local_path)
        text = re.sub(re.escape(sq_url) + r'\?[^\s"\'&<>]*', local_path, text)
    return text

updated = 0
for f in html_files:
    original = f.read_text(encoding="utf-8", errors="ignore")
    updated_text = replace_in_html(original, url_map)
    if updated_text != original:
        f.write_text(updated_text, encoding="utf-8")
        updated += 1
        print(f"  [ok]   {f.relative_to(REPO_ROOT)}")

print(f"\nDone. Updated {updated} HTML files.")
