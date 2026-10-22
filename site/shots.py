#!/usr/bin/env python3
"""Development aid, not part of the build: screenshots of the built site and the
Open Graph image static/og.png. Needs `playwright` for Python and a Chromium
(set CHROME to its path if playwright has none of its own).

    python3 site/shots.py DIR [PAGE ...]   # PNGs of PAGE (default: / and /spec) at 1280 and 390 px, light and dark
    python3 site/shots.py --og             # rewrite site/static/og.png (1200 x 630)
"""
import os
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

SITE = Path(__file__).resolve().parent
PORT = 8765
sys.path.insert(0, str(SITE))


def og_html() -> str:
    import build
    logo = build.LOGO.format(s=120)
    return f"""<!doctype html><meta charset="utf-8"><style>{(SITE / 'style.css').read_text()}
    body {{ width: 1200px; height: 630px; display: flex; flex-direction: column; justify-content: center; padding: 0 90px; background: var(--bg); }}
    .b {{ display: flex; align-items: center; gap: 28px; font-size: 96px; font-weight: 700; letter-spacing: -.03em; }}
    p {{ font-size: 44px; line-height: 1.22; letter-spacing: -.02em; margin: 40px 0 0; max-width: 21em; font-weight: 600; }}
    small {{ font-size: 28px; color: var(--muted); margin-top: 44px; }}</style>
    <div class="b">{logo}<span>unifold</span></div>
    <p>An architecture map that is kept in the folders, checked against the code, and never drawn by hand.</p>
    <small>unifold.md &nbsp; draft open standard</small>"""


def main() -> None:
    args = sys.argv[1:]
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get("CHROME"), args=["--no-sandbox"])
        if args and args[0] == "--og":
            pg = browser.new_page(viewport={"width": 1200, "height": 630})
            pg.set_content(og_html())
            (SITE / "static").mkdir(exist_ok=True)
            pg.screenshot(path=str(SITE / "static" / "og.png"))
            print("wrote site/static/og.png")
            return
        out = Path(args[0]) if args else Path("shots")
        pages = args[1:] or ["/", "/spec"]
        out.mkdir(parents=True, exist_ok=True)
        server = subprocess.Popen([sys.executable, str(SITE / "build.py"), "--serve", str(PORT)],
                                  stdout=subprocess.DEVNULL)
        time.sleep(4)
        try:
            for path in pages:
                name = path.strip("/").replace("/", "-") or "index"
                for width in (1280, 390):
                    for scheme in ("light", "dark"):
                        ctx = browser.new_context(viewport={"width": width, "height": 800}, color_scheme=scheme,
                                                  device_scale_factor=1)
                        pg = ctx.new_page()
                        pg.goto(f"http://localhost:{PORT}{path}")
                        overflow = pg.evaluate("document.documentElement.scrollWidth - window.innerWidth")
                        f = out / f"{name}-{width}-{scheme}.png"
                        pg.screenshot(path=str(f), full_page=True)
                        print(f"{f}  horizontal overflow: {overflow}px")
                        ctx.close()
        finally:
            server.terminate()


if __name__ == "__main__":
    main()
