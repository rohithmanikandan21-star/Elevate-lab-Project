import os
import json
import threading
import time
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from scanner.crawler import crawl
from scanner.tests import test_reflection
import requests
from datetime import datetime

app = Flask(__name__, template_folder="../templates")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Simple index page
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        target = request.form.get("target")
        if target:
            # start scan in background
            scan_id = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            threading.Thread(target=run_scan, args=(scan_id, target), daemon=True).start()
            return redirect(url_for("results", scan_id=scan_id))
    return render_template("index.html")

@app.route("/results/<scan_id>")
def results(scan_id):
    path = os.path.join(DATA_DIR, f"{scan_id}.json")
    if os.path.exists(path):
        with open(path) as f:
            report = json.load(f)
    else:
        report = {"status": "running", "scan_id": scan_id}
    return render_template("results.html", report=report)

def run_scan(scan_id, target):
    out = {
        "scan_id": scan_id,
        "target": target,
        "started_at": datetime.utcnow().isoformat(),
        "status": "running",
        "findings": [],
        "pages_crawled": [],
    }
    path = os.path.join(DATA_DIR, f"{scan_id}.json")
    # save initial
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    # Crawl
    try:
        found = crawl(target, max_pages=50, delay=0.5)
        out["pages_crawled"] = found["pages"]
        session = requests.Session()
        # check page-level headers for first page
        try:
            resp = session.get(target, timeout=10)
            if resp:
                hdr_issues = []
                if 'strict-transport-security' not in {k.lower() for k in resp.headers}:
                    hdr_issues.append("Missing HSTS")
                if hdr_issues:
                    out["findings"].append({"type": "headers", "severity": "medium", "evidence": hdr_issues})
        except Exception:
            pass

        for form in found["forms"]:
            ev = test_reflection(session, form)
            if ev:
                out["findings"].append({
                    "type": "reflected-xss-probable",
                    "severity": "high",
                    "target": form["action"],
                    "evidence": ev
                })
        out["status"] = "finished"
        out["finished_at"] = datetime.utcnow().isoformat()
    except Exception as e:
        out["status"] = "error"
        out["error"] = str(e)
    with open(path, "w") as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    app.run(debug=True, port=5000)

