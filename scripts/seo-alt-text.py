#!/usr/bin/env python3
"""
Add descriptive alt text to images with empty alt="" attributes.
Derives alt text from filename and page context.
"""
import re, sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

# Map filename patterns → descriptive alt text
# Key = substring to match in src attribute (case-insensitive)
ALT_MAP = [
    # Kinetic Energy branding
    ("Kinetic-Energy-Logo",         "Kinetic Energy Consulting logo"),
    ("Kinetic-Energy-Tag",          "Kinetic Energy Consulting logo"),
    ("KineticEnergy",               "Kinetic Energy Consulting logo"),

    # Client / partner logos
    ("Logo_E.ON",                   "E.ON logo"),
    ("Centrica",                    "Centrica Business Solutions logo"),
    ("eEnergy",                     "eEnergy logo"),
    ("Regus",                       "Regus logo"),
    ("ylem",                        "Ylem logo"),
    ("Aa-logo",                     "Client logo"),
    ("linkedin-logo",               "LinkedIn logo"),

    # People / team photos
    ("IMG_5880",                    "Kinetic Energy Consulting team"),
    ("IMG_5903",                    "Kinetic Energy Consulting team"),
    ("IMG_5908",                    "Kinetic Energy Consulting team"),
    ("IMG_5910",                    "Kinetic Energy Consulting team"),
    ("IMG_5912",                    "Kinetic Energy Consulting team"),
    ("IMG_5916",                    "Kinetic Energy Consulting team"),
    ("IMG_5930",                    "Kinetic Energy Consulting team"),
    ("DFE20159",                    "Energy sector professional"),
    ("Trade-151",                   "Energy industry team"),
    ("Nov-7",                       "Kinetic Energy Consulting team"),

    # Unsplash stock images — describe by likely use in energy sector context
    ("unsplash-image-rRWiVQzLm7k",  "Modern city energy infrastructure at night"),
    ("unsplash-image-s8HyIEe7lF0",  "Energy sector landscape"),
    ("unsplash-image-qCi_MzVODoU",  "Commercial strategy and business growth"),
    ("unsplash-image-9yCYGgPe5Kg",  "Energy industry operations"),
    ("unsplash-image-5fNmWej4tAA",  "Energy market analysis and strategy"),
    ("unsplash-image-MYbhN8KaaEc",  "Energy sector professionals in discussion"),
    ("unsplash-image-eS72kLFS6s0",  "Energy infrastructure and technology"),
    ("unsplash-image-x-ghf9LjrVg",  "Commercial consulting and business performance"),
    ("unsplash-image-Gw_sFen8VhU",  "Energy sector growth and opportunity"),
    ("unsplash-image-2pPw5Glro5I",  "Sales strategy and pipeline development"),
    ("unsplash-image-_6HzPU9Hyfg",  "Energy market landscape"),
    ("unsplash-image-KdeqA3aTnBY",  "Data centre and digital energy infrastructure"),
    ("unsplash-image-XrIfY_4cK1w",  "Renewable energy and decarbonisation"),
    ("unsplash-image-npxXWgQ33ZQ",  "Energy consultancy and commercial strategy"),
    ("unsplash-image-Q1p7bh3SHj8",  "Energy sector business development"),
    ("unsplash-image-rRWiVQzLm7k",  "Energy market at night"),
    ("unsplash-image-s8HyIEe7lF0",  "Energy operations"),
    ("unsplash-image-ENMFKQWK",     "Energy and sustainability landscape"),
    ("unsplash-image",              "Energy sector background image"),

    # Generic fallbacks
    ("favicon",                     "Kinetic Energy Consulting favicon"),
    ("favicon-light",               "Kinetic Energy Consulting favicon"),
    ("favicon-dark",                "Kinetic Energy Consulting favicon"),
]


def get_alt_text(src: str) -> str:
    """Return descriptive alt text based on the image src."""
    for pattern, alt in ALT_MAP:
        if pattern.lower() in src.lower():
            return alt
    # Last resort: derive from filename
    fname = src.split("/")[-1].split("?")[0]
    # Strip UUID prefix (hash--name)
    if "--" in fname:
        fname = fname.split("--", 1)[1]
    # Remove extension, replace separators
    name = re.sub(r'\.(jpg|jpeg|png|gif|webp|svg|ico)$', '', fname, flags=re.I)
    name = re.sub(r'[-_]', ' ', name).strip()
    return f"{name} image" if name else "Image"


def fix_empty_alts(text: str) -> tuple[str, int]:
    """
    Squarespace img tags often have MULTIPLE alt attributes: a good one first,
    then alt="" at the end (browser keeps last duplicate, so empty wins).
    Strategy:
    - If tag has a non-empty alt AND a trailing empty alt: remove the empty one(s)
    - If tag has only alt="": replace with descriptive text from filename
    """
    count = 0

    def replacer(m: re.Match) -> str:
        nonlocal count
        tag = m.group(0)

        # Find all alt attribute values in the tag
        all_alts = re.findall(r'\balt\s*=\s*"([^"]*)"', tag)
        if not all_alts:
            all_alts = re.findall(r"\balt\s*=\s*'([^']*)'", tag)

        if not all_alts:
            return tag  # no alt at all — leave alone

        non_empty = [a for a in all_alts if a.strip()]
        has_empty  = any(a.strip() == "" for a in all_alts)

        if not has_empty:
            return tag  # no problem

        if non_empty:
            # Keep the first meaningful alt, remove all empty alt attributes
            best_alt = non_empty[0]
            # Remove ALL alt attributes
            new_tag = re.sub(r'\s*\balt\s*=\s*"[^"]*"', '', tag)
            new_tag = re.sub(r"\s*\balt\s*=\s*'[^']*'", '', new_tag)
            # Inject the best alt before the closing > or />
            if new_tag.endswith('/>'):
                new_tag = new_tag[:-2].rstrip() + f' alt="{best_alt}"/>'
            else:
                new_tag = new_tag[:-1].rstrip() + f' alt="{best_alt}">'
            count += 1
            return new_tag
        else:
            # All alts are empty — derive from src
            src_match = re.search(r'\bsrc\s*=\s*"([^"]+)"', tag)
            if not src_match:
                src_match = re.search(r'\bdata-src\s*=\s*"([^"]+)"', tag)
            if src_match:
                alt = get_alt_text(src_match.group(1))
                # Replace first empty alt, remove subsequent ones
                new_tag = re.sub(r'\balt\s*=\s*""', f'alt="{alt}"', tag, count=1)
                new_tag = re.sub(r'\s*\balt\s*=\s*""', '', new_tag)
                count += 1
                return new_tag
            return tag

    new_text = re.sub(r'<img\b[^>]*>', replacer, text)
    return new_text, count


def run():
    html_files = list(REPO_ROOT.glob("*.html")) + list((REPO_ROOT / "insight").glob("*.html"))
    total_fixed = 0

    for f in sorted(html_files):
        try:
            original = f.read_text(encoding="utf-8", errors="ignore")
            new_text, n = fix_empty_alts(original)
            if n > 0:
                f.write_text(new_text, encoding="utf-8")
                total_fixed += n
                print(f"  [ok]   {f.relative_to(REPO_ROOT)}  ({n} alt tags added)")
        except Exception as e:
            print(f"  [err]  {f}: {e}", file=sys.stderr)

    print(f"\nDone. Added/fixed {total_fixed} alt attributes.")


if __name__ == "__main__":
    run()
