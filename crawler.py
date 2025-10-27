# scanner/crawler.py
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from collections import deque
import time

HEADERS = {"User-Agent": "ReD-Scanner/0.1"}

def get_page(session, url):
    try:
        r = session.get(url, headers=HEADERS, timeout=10)
        return r
    except Exception as e:
        return None

def extract_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a['href']
        if href.startswith("javascript:") or href.startswith("#"):
            continue
        full = urljoin(base_url, href)
        # only same-host links by default
        if urlparse(full).netloc == urlparse(base_url).netloc:
            links.add(full)
    return links

def extract_forms(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    forms = []
    for form in soup.find_all("form"):
        action = form.get('action') or ''
        method = form.get('method', 'get').lower()
        inputs = []
        for inp in form.find_all(["input", "textarea", "select"]):
            name = inp.get('name')
            itype = inp.get('type', 'text')
            if name:
                inputs.append({'name': name, 'type': itype})
        forms.append({'action': urljoin(base_url, action), 'method': method, 'inputs': inputs})
    return forms

def crawl(start_url, max_pages=100, delay=0.5):
    session = requests.Session()
    q = deque([start_url])
    visited = set()
    found = {'pages': [], 'forms': []}
    while q and len(visited) < max_pages:
        url = q.popleft()
        if url in visited:
            continue
        r = get_page(session, url)
        visited.add(url)
        if not r or r.status_code != 200:
            continue
        found['pages'].append(url)
        links = extract_links(r.text, url)
        for l in links:
            if l not in visited:
                q.append(l)
        found['forms'].extend(extract_forms(r.text, url))
        time.sleep(delay)
    session.close()
    return found
