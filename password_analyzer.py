#!/usr/bin/env python3
"""
Password strength analyzer using zxcvbn with a fallback entropy estimator.
Usage:
    python password_analyzer.py --password "P@ssw0rd123"
"""
import argparse
from math import log2
try:
    from zxcvbn import zxcvbn
    ZXC_AVAILABLE = True
except Exception:
    ZXC_AVAILABLE = False

def entropy_estimate(pw: str) -> float:
    """Simple entropy estimate based on character sets used."""
    pool = 0
    if any(c.islower() for c in pw): pool += 26
    if any(c.isupper() for c in pw): pool += 26
    if any(c.isdigit() for c in pw): pool += 10
    if any(not c.isalnum() for c in pw): pool += 32  # rough symbol count
    if pool == 0:
        return 0.0
    return len(pw) * log2(pool)

def analyze_password(pw: str):
    result = {}
    if ZXC_AVAILABLE:
        z = zxcvbn(pw)
        result['score'] = z.get('score')  # 0-4
        result['crack_time_display'] = z.get('crack_times_display', {})
        result['feedback'] = z.get('feedback', {})
        result['calc_entropy'] = entropy_estimate(pw)
        result['warning'] = z.get('feedback', {}).get('warning', '')
    else:
        result['score'] = None
        result['calc_entropy'] = entropy_estimate(pw)
        result['warning'] = 'zxcvbn not installed; showing entropy estimate only.'
    return result

def pretty_print(res):
    print("=== Password Analysis ===")
    if res['score'] is not None:
        print(f"zxcvbn score (0-4): {res['score']}")
    print(f"Estimated entropy (bits): {res['calc_entropy']:.2f}")
    if 'crack_time_display' in res and res['crack_time_display']:
        print("Crack time estimates:")
        for k,v in res['crack_time_display'].items():
            print(f"  {k}: {v}")
    if res.get('warning'):
        print("Warning:", res['warning'])
    if res.get('feedback'):
        print("Feedback:")
        for field in ('suggestions','warning'):
            if res['feedback'].get(field):
                print(f"  {field}: {res['feedback'][field]}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--password", "-p", required=True, help="Password to analyze")
    args = ap.parse_args()
    out = analyze_password(args.password)
    pretty_print(out)
