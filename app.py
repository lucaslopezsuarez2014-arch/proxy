"""
Proxy Instance Manager - Flask Backend
Run: pip install flask selenium && python app.py
Then open: http://localhost:5000
"""

from flask import Flask, jsonify, request, send_from_directory
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import threading
import time
import os
import uuid

app = Flask(__name__, static_folder="static")

# ── In-memory instance store ──────────────────────────────────────────────────
instances = {}   # id -> { id, proxy, url, status, driver, created_at }
lock = threading.Lock()

# Use webdriver-manager to automatically get the correct chromedriver
def get_chromedriver_path():
    """Get the path to chromedriver, installing it if necessary."""
    try:
        return ChromeDriverManager().install()
    except Exception as e:
        # Fallback to system chromedriver
        return os.environ.get("CHROMEDRIVER_PATH", "chromedriver")

# ── Helpers ───────────────────────────────────────────────────────────────────

def launch_browser(inst_id: str):
    with lock:
        inst = instances.get(inst_id)
        if not inst:
            return
        inst["status"] = "launching"

    proxy = inst["proxy"]
    url   = inst["url"]

    options = Options()
    options.add_argument(f"--proxy-server=http://{proxy}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--user-data-dir=/tmp/chrome_{inst_id}")
    options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    try:
        # Use the correct chromedriver path
        chromedriver_path = "/Users/tinolopezantuna/.wdm/drivers/chromedriver/mac64/145.0.7632.117/chromedriver-mac-arm64/chromedriver"
        service = Service(executable_path=chromedriver_path)
        driver  = webdriver.Chrome(service=service, options=options)
        driver.get(url)

        with lock:
            instances[inst_id]["driver"] = driver
            instances[inst_id]["status"] = "online"
    except Exception as e:
        with lock:
            instances[inst_id]["status"] = f"error: {e}"
            instances[inst_id]["driver"] = None


def stop_browser(inst_id: str):
    with lock:
        inst = instances.get(inst_id)
        if not inst:
            return
        driver = inst.get("driver")
        inst["status"] = "stopped"
        inst["driver"] = None

    if driver:
        try:
            driver.quit()
        except Exception:
            pass


# ── API routes ────────────────────────────────────────────────────────────────

@app.route("/api/instances", methods=["GET"])
def get_instances():
    with lock:
        safe = [
            {k: v for k, v in inst.items() if k != "driver"}
            for inst in instances.values()
        ]
    return jsonify(safe)


@app.route("/api/instances", methods=["POST"])
def create_instance():
    data  = request.json or {}
    proxy = data.get("proxy", "").strip()
    url   = data.get("url", "https://example.com").strip()

    if not proxy:
        return jsonify({"error": "proxy required"}), 400

    inst_id = str(uuid.uuid4())[:8]
    inst_num = len(instances)

    with lock:
        instances[inst_id] = {
            "id":         inst_id,
            "num":        inst_num,
            "proxy":      proxy,
            "url":        url,
            "status":     "pending",
            "driver":     None,
            "created_at": time.time(),
        }

    threading.Thread(target=launch_browser, args=(inst_id,), daemon=True).start()
    return jsonify({k: v for k, v in instances[inst_id].items() if k != "driver"}), 201


@app.route("/api/instances/<inst_id>/restart", methods=["POST"])
def restart_instance(inst_id):
    with lock:
        if inst_id not in instances:
            return jsonify({"error": "not found"}), 404
        instances[inst_id]["status"] = "restarting"

    threading.Thread(target=_restart, args=(inst_id,), daemon=True).start()
    return jsonify({"status": "restarting"})


def _restart(inst_id):
    stop_browser(inst_id)
    time.sleep(1)
    launch_browser(inst_id)


@app.route("/api/instances/<inst_id>", methods=["DELETE"])
def delete_instance(inst_id):
    stop_browser(inst_id)
    with lock:
        instances.pop(inst_id, None)
    return jsonify({"deleted": inst_id})


# ── Serve the frontend ────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    print("🚀  Proxy Instance Manager running at http://localhost:5001")
    app.run(debug=False, port=5001)
