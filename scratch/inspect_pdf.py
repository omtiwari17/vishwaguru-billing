import os
import sys
import time
import json
import urllib.request
import subprocess
from importlib import import_module

sys.path.insert(0, os.path.abspath('.'))

# Setup Django to generate session cookie
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.conf import settings

from django.contrib.auth.models import User
SessionStore = import_module(settings.SESSION_ENGINE).SessionStore

user = User.objects.filter(is_superuser=True).first()
if not user:
    user = User.objects.first()

session = SessionStore()
session['_auth_user_id'] = str(user.pk)
session['_auth_user_backend'] = 'django.contrib.auth.backends.ModelBackend'
session['_auth_user_hash'] = user.get_session_auth_hash()
session.save()
session_key = session.session_key
print(f"Authenticated as user {user.username}, session_key: {session_key}")

# Launch Headless Chrome on port 9225
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
user_data_dir = os.path.join(os.environ.get("TEMP", r"C:\temp"), "chrome_cdp_pdf_profile")

cmd = [
    chrome_path,
    "--headless=new",
    "--remote-debugging-port=9225",
    f"--user-data-dir={user_data_dir}",
    "--disable-gpu",
    "--no-sandbox",
    "--window-size=1200,1600"
]

proc = subprocess.Popen(cmd)
time.sleep(2)

from websockets.sync.client import connect

try:
    with urllib.request.urlopen("http://127.0.0.1:9225/json") as resp:
        targets = json.loads(resp.read().decode())
    ws_url = targets[0]["webSocketDebuggerUrl"]

    ws = connect(ws_url, close_timeout=15)

    msg_id = 0

    def cdp_send(method, params=None):
        global msg_id
        msg_id += 1
        payload = {"id": msg_id, "method": method}
        if params:
            payload["params"] = params
        ws.send(json.dumps(payload))
        while True:
            res = json.loads(ws.recv())
            if res.get("id") == msg_id:
                return res.get("result", {})

    cdp_send("Network.enable")
    cdp_send("Page.enable")

    # Set session cookie
    cdp_send("Network.setCookie", {
        "name": "sessionid",
        "value": session_key,
        "domain": "127.0.0.1",
        "path": "/",
        "httpOnly": True
    })

    artifact_dir = r"C:\Users\omtiw\.gemini\antigravity\brain\ad970ea7-1c12-437d-8cb9-37536c085a10"

    test_views = [
        ("pdf_bill3_en_comp.png", "http://127.0.0.1:8000/bills/3/pdf/?lang=en&sign=0"),
        ("pdf_bill3_hi_comp.png", "http://127.0.0.1:8000/bills/3/pdf/?lang=hi&sign=0"),
        ("pdf_bill3_en_sign.png", "http://127.0.0.1:8000/bills/3/pdf/?lang=en&sign=1"),
        ("pdf_bill2_en_unpaid.png", "http://127.0.0.1:8000/bills/2/pdf/?lang=en&sign=0"),
    ]

    for fname, url in test_views:
        print(f"Navigating to {url}...")
        cdp_send("Page.navigate", {"url": url})
        time.sleep(2)  # Wait for render and web fonts
        
        # Capture full page screenshot
        snap = cdp_send("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": True})
        img_data = snap.get("data")
        if img_data:
            import base64
            out_path = os.path.join(artifact_dir, fname)
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(img_data))
            print(f"Saved screenshot: {out_path}")

    ws.close()
finally:
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except:
        proc.kill()
    print("CDP finished successfully.")
