import os, sys, json, time, asyncio, subprocess
from pathlib import Path
import urllib.request
import base64
from importlib import import_module

sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.conf import settings
from django.contrib.auth.models import User
SessionStore = import_module(settings.SESSION_ENGINE).SessionStore

user = User.objects.filter(is_superuser=True).first()
session = SessionStore()
session['_auth_user_id'] = str(user.pk)
session['_auth_user_backend'] = 'django.contrib.auth.backends.ModelBackend'
session['_auth_user_hash'] = user.get_session_auth_hash()
session.save()
session_key = session.session_key
print(f"Superuser session created: {session_key}")

out_dir = Path(r"C:\Users\omtiw\.gemini\antigravity\brain\ad970ea7-1c12-437d-8cb9-37536c085a10")
scratch_profile = out_dir / "scratch" / "chrome_prof_headless_pdf"
port = 9452
chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

cmd = [
    chrome_exe,
    f"--remote-debugging-port={port}",
    "--remote-allow-origins=*",
    f"--user-data-dir={scratch_profile}",
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    "--window-size=1200,1600",
    "about:blank"
]

proc = subprocess.Popen(cmd)
time.sleep(2.5)

try:
    tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{port}/json").read())
    page_tab = next(t for t in tabs if t.get("type") == "page")
    ws_url = page_tab["webSocketDebuggerUrl"]

    import websockets

    async def run():
        async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
            msg_id = 0
            async def send(method, params=None):
                nonlocal msg_id
                msg_id += 1
                req = {"id": msg_id, "method": method}
                if params: req["params"] = params
                await ws.send(json.dumps(req))
                while True:
                    raw = await ws.recv()
                    data = json.loads(raw)
                    if data.get("id") == msg_id: return data.get("result", {})

            await send("Network.enable")
            await send("Page.enable")
            await send("DOM.enable")

            # Set session cookie
            await send("Network.setCookie", {
                "name": "sessionid",
                "value": session_key,
                "domain": "127.0.0.1",
                "path": "/",
                "httpOnly": True
            })

            # Emulate desktop at standard 1200x1600
            await send("Emulation.setDeviceMetricsOverride", {
                "width": 1200,
                "height": 1600,
                "deviceScaleFactor": 1,
                "mobile": False
            })

            targets = [
                ("pdf_bill3_en_comp.png", "http://127.0.0.1:8000/bills/3/pdf/?lang=en&sign=0"),
                ("pdf_bill3_hi_comp.png", "http://127.0.0.1:8000/bills/3/pdf/?lang=hi&sign=0"),
                ("pdf_bill3_en_sign.png", "http://127.0.0.1:8000/bills/3/pdf/?lang=en&sign=1"),
                ("pdf_bill2_en_unpaid.png", "http://127.0.0.1:8000/bills/2/pdf/?lang=en&sign=0"),
            ]

            for fname, url in targets:
                print(f"Navigating to {url}...")
                await send("Page.navigate", {"url": url})
                await asyncio.sleep(2.0)
                shot = await send("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": True})
                (out_dir / fname).write_bytes(base64.b64decode(shot["data"]))
                print(f"Saved {fname} ({len(shot['data'])} bytes)")

    asyncio.run(run())
finally:
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except:
        proc.kill()
    print("All captures completed.")
