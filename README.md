# Proxy Instance Manager

A web-based dashboard to launch and manage Chrome browser instances, each running through its own proxy.

---

## Requirements

- Python 3.8+
- Google Chrome installed
- ChromeDriver matching your Chrome version

---

## Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Install ChromeDriver

Download the ChromeDriver that matches your Chrome version from:
https://chromedriver.chromium.org/downloads

Then either:
- Place `chromedriver` (or `chromedriver.exe` on Windows) in the same folder as `app.py`
- **Or** set the environment variable:
  ```bash
  export CHROMEDRIVER_PATH=/path/to/chromedriver   # Mac/Linux
  set CHROMEDRIVER_PATH=C:\path\to\chromedriver.exe  # Windows
  ```

---

## Running

```bash
python app.py
```

Then open your browser at:
```
http://localhost:5000
```

---

## How to Use

### Adding an Instance
1. Enter a proxy in the **Proxy** field using the format `host:port`  
   Example: `145.223.44.209:5892`
2. Enter the **Target URL** you want to open  
   Example: `https://example.com`
3. Click **+ Add Instance**

A new Chrome window will open routed through that proxy. The card will show:
- 🟡 **pending / launching** — starting up
- 🟢 **online** — browser is open and running
- 🔴 **error** — something went wrong (check proxy or ChromeDriver)

### Restarting an Instance
Click **Restart** on any card to kill and relaunch that browser window through the same proxy.

### Removing an Instance
Click **✕** to close the browser and remove the instance from the dashboard.

---

## File Structure

```
proxy-instance-manager/
├── app.py              # Flask backend
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── static/
    └── index.html      # Web dashboard frontend
```

---

## Notes

- Each instance runs in its own isolated Chrome profile (no session conflicts)
- The dashboard auto-refreshes every 2.5 seconds
- Respect rate limits and waiting times when using proxies
- Instances are stored in memory — they will be lost if you restart the server
