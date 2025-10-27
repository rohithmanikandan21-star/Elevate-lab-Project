#!/usr/bin/env python3
"""
Custom wordlist generator.
Example:
python wordlist_generator.py --names "alice,bob" --keywords "company,dev" --years 2018-2022 --max 1000 -o examples/custom.txt
"""
import argparse
import itertools
import random
import re

LEET_MAP = {
    'a': ['4','@'],
    'b': ['8','6'],
    'e': ['3'],
    'i': ['1','!'],
    'l': ['1','7'],
    'o': ['0'],
    's': ['5','$'],
    't': ['7']
}

def leet_variants(s):
    """Generate a few leetspeak variants - limited for simplicity."""
    s = s.lower()
    variants = {s}
    for i, ch in enumerate(s):
        if ch in LEET_MAP:
            for repl in LEET_MAP[ch]:
                variants.add(s[:i] + repl + s[i+1:])
    # also add a capitalized variant
    variants.update({s.capitalize(), s.upper()})
    return list(variants)

def combine_bases(bases, keywords, years, symbols, max_items):
    """Create permutations/combinations in a controlled manner."""
    out = set()
    # basic combos: base + keyword, keyword + base
    for base in bases:
        base_variants = leet_variants(base) + [base]
        for b in base_variants:
            for kw in keywords:
                out.add(b + kw)
                out.add(kw + b)
                out.add(b + str(random.choice(years)) if years else b)
    # append years
    for item in list(out):
        for y in years:
            out.add(item + str(y))
    # add symbols/suffixes
    for item in list(out):
        for s in symbols:
            out.add(item + s)
            out.add(s + item)
    # add also standalone keywords and bases
    out.update(bases)
    out.update(keywords)
    # limit size
    out_list = list(out)
    random.shuffle(out_list)
    return out_list[:max_items]

def parse_year_range(range_str):
    if not range_str:
        return []
    m = re.match(r'(\d{4})-(\d{4})', range_str)
    if m:
        start = int(m.group(1))
        end = int(m.group(2))
        return list(range(start, end+1))
    else:
        # single year
        return [int(range_str)]

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--names", default="", help="Comma separated names")
    ap.add_argument("--keywords", default="", help="Comma separated keywords")
    ap.add_argument("--years", default="1990-2025", help="Year range like 1990-2025 or single 2020")
    ap.add_argument("--symbols", default="!@#", help="Symbols to add as suffix/prefix (no spaces)")
    ap.add_argument("--max", type=int, default=1000, help="Max words to generate")
    ap.add_argument("-o", "--output", required=True, help="Output file path")
    args = ap.parse_args()

    bases = [n.strip() for n in args.names.split(",") if n.strip()]
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
    years = parse_year_range(args.years)
    symbols = list(args.symbols)

    wordlist = combine_bases(bases, keywords, years, symbols, args.max)

    with open(args.output, "w", encoding="utf-8") as f:
        for w in wordlist:
            f.write(w + "\n")
    print(f"Wrote {len(wordlist)} words to {args.output}")
