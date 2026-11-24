import os
import re
import urllib.request
import json

def get_language_proportions(username):
    url = f"https://api.github.com/users/{username}/repos?per_page=100"
    req = urllib.request.Request(url, headers={"User-Agent": "Python"})
    try:
        with urllib.request.urlopen(req) as resp:
            repos = json.loads(resp.read().decode())
    except Exception as e:
        print(f"Failed to fetch repos: {e}")
        repos = []

    lang_counts = {}
    for r in repos:
        lang = r.get("language")
        if lang:
            lang_counts[lang] = lang_counts.get(lang, 0) + 1

    total = sum(lang_counts.values()) or 1
    return {k: v / total for k, v in lang_counts.items()}

def customize_aquarium(svg_path, username):
    if not os.path.exists(svg_path):
        print(f"File not found: {svg_path}")
        return

    with open(svg_path, "r", encoding="utf-8") as f:
        svg = f.read()

    proportions = get_language_proportions(username)
    print("Language distribution:", proportions)

    # Base scale multiplier: minimum 0.95, maximum 1.45 based on actual language share
    # Variety assignments:
    # Python (majority) -> Kohaku & Yamabuki (white & gold)
    # JavaScript -> Asagi (blue / grey)
    # TypeScript -> Karasugoi (black / deep sumi)
    # C / C++ -> Chagoi (tea / bronze)
    # Web / Other -> Platinum (silver / light)

    py_share = proportions.get("Python", 0.45)
    js_share = proportions.get("JavaScript", 0.15)
    ts_share = proportions.get("TypeScript", 0.12)
    c_share  = proportions.get("C", 0.08) + proportions.get("C++", 0.02)
    other_share = 1.0 - (py_share + js_share + ts_share + c_share)

    # Scale mapping function:
    def calc_scale(share, rank_bonus=0.0):
        # Range from ~0.95 to 1.40
        return round(0.95 + (share * 0.8) + rank_bonus, 2)

    py_scale = calc_scale(py_share, 0.05)
    js_scale = calc_scale(js_share)
    ts_scale = calc_scale(ts_share)
    c_scale  = calc_scale(c_share)
    other_scale = max(0.95, calc_scale(other_share))

    print(f"Calculated Scales: Python={py_scale}, JS={js_scale}, TS={ts_scale}, C={c_scale}, Other={other_scale}")

    # Map fish IDs to calculated language scales
    mappings = {
        "fish-white-1": py_scale,
        "fish-gold-1": py_scale,
        "fish-white-2": py_scale,
        "fish-gold-2": py_scale,
        "fish-asagi-1": js_scale,
        "fish-asagi-2": js_scale,
        "fish-black-1": ts_scale,
        "fish-black-2": ts_scale,
        "fish-tea-1": c_scale,
        "fish-tea-2": c_scale,
        "fish-platinum-1": other_scale,
        "fish-platinum-2": other_scale,
    }

    for fish_id, scale in mappings.items():
        pattern = rf'(id="{fish_id}"[\s\S]*?)transform="scale\([0-9.]+\)"'
        replacement = rf'\1transform="scale({scale:.3f})"'
        svg = re.sub(pattern, replacement, svg)

    # Fallback in case any remaining scale(0.530) exists
    svg = svg.replace('transform="scale(0.530)"', 'transform="scale(1.15)"')

    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print("Successfully updated aquarium with language-proportional scaling!")

if __name__ == "__main__":
    import sys
    svg_file = sys.argv[1] if len(sys.argv) > 1 else "dist/aquarium.svg"
    user = sys.argv[2] if len(sys.argv) > 2 else "Humble-Librarian"
    customize_aquarium(svg_file, user)
