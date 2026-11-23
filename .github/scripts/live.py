import base64
import datetime as dt
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import gen
from gen import ACC, ACC2, DIM, LINE, MONO, MUTED, PANEL, SANS, TEXT, esc

USER = "mirola777"
UA = {"User-Agent": "mirola777-profile"}
CATS = [
    ("necesidad", "needs", "#e53935"),
    ("acopio", "collection", "#2e7d32"),
    ("albergue", "shelters", "#1565c0"),
    ("animales", "animals", "#6a1b9a"),
    ("dinero", "money", "#00838f"),
    ("sangre", "blood", "#c62828"),
    ("mercado", "groceries", "#ef6c00"),
    ("otros", "other", "#455a64"),
]


def get(url, headers=None, data=None, timeout=20):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})}, data=data)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
        return r.status, body


def get_json(url, headers=None, data=None):
    status, body = get(url, headers, data)
    return status, (json.loads(body) if body else None)


def gh_headers():
    tok = os.environ.get("GITHUB_TOKEN")
    h = {"Accept": "application/vnd.github+json"}
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h


def data_uri(url, mime="image/png"):
    try:
        _, body = get(url)
        return f"data:{mime};base64,{base64.b64encode(body).decode()}"
    except Exception:
        return None


def clip(s, n):
    s = " ".join(s.split())
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def wrap(s, n, lines):
    words, out, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) > n:
            out.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    if cur:
        out.append(cur)
    if len(out) > lines:
        out = out[:lines]
        out[-1] = clip(out[-1] + " …", n)
    return out


def fetch_unidos():
    try:
        _, d = get_json("https://unidos-por-colombia.vercel.app/api/points")
        pts = d.get("points") or []
    except Exception:
        return None
    counts = {}
    for p in pts:
        counts[p.get("category")] = counts.get(p.get("category"), 0) + 1
    verified = sum(1 for p in pts if p.get("verified"))
    return {"total": len(pts), "capped": len(pts) >= 1000, "counts": counts, "verified": verified}


def fetch_activity():
    try:
        _, evs = get_json(f"https://api.github.com/users/{USER}/events/public?per_page=50", gh_headers())
    except Exception:
        return None
    evs = [e for e in (evs or []) if e["repo"]["name"] != f"{USER}/{USER}"]
    for e in evs:
        repo, t, p = e["repo"]["name"], e["type"], e.get("payload") or {}
        when = e["created_at"][:10]
        if t == "PullRequestEvent" and p.get("action") in ("opened", "closed", "merged"):
            pr = p.get("pull_request") or {}
            num = pr.get("number") or p.get("number")
            title, merged = pr.get("title"), pr.get("merged")
            if num and not title:
                try:
                    _, full = get_json(f"https://api.github.com/repos/{repo}/pulls/{num}", gh_headers())
                    title, merged = full.get("title"), full.get("merged")
                except Exception:
                    title = f"#{num}"
            if merged:
                verb = "merged a pull request"
            elif p.get("action") == "closed":
                verb = "closed a pull request"
            else:
                verb = "opened a pull request"
            return {"verb": verb, "title": title or "", "repo": repo, "when": when}
        if t == "ReleaseEvent":
            return {"verb": "published a release", "title": (p.get("release") or {}).get("name") or "", "repo": repo, "when": when}
    for e in evs:
        if e["type"] == "PushEvent":
            p = e.get("payload") or {}
            commits = p.get("commits") or []
            msg = commits[-1]["message"].splitlines()[0] if commits else ""
            branch = (p.get("ref") or "").replace("refs/heads/", "")
            return {"verb": "pushed code", "title": msg or (f"to {branch}" if branch else ""), "repo": e["repo"]["name"], "when": e["created_at"][:10]}
    return None


def fetch_spotify():
    cid, sec, ref = (os.environ.get(k) for k in ("SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET", "SPOTIFY_REFRESH_TOKEN"))
    if not (cid and sec and ref):
        return None
    try:
        auth = base64.b64encode(f"{cid}:{sec}".encode()).decode()
        _, tok = get_json(
            "https://accounts.spotify.com/api/token",
            {"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"},
            urllib.parse.urlencode({"grant_type": "refresh_token", "refresh_token": ref}).encode(),
        )
        h = {"Authorization": f"Bearer {tok['access_token']}"}
        status, cur = get_json("https://api.spotify.com/v1/me/player/currently-playing", h)
        playing = status == 200 and cur and cur.get("is_playing") and cur.get("item")
        if playing:
            item = cur["item"]
        else:
            _, rec = get_json("https://api.spotify.com/v1/me/player/recently-played?limit=1", h)
            item = rec["items"][0]["track"]
        imgs = item.get("album", {}).get("images") or []
        art = data_uri(imgs[-2]["url"] if len(imgs) > 1 else imgs[0]["url"], "image/jpeg") if imgs else None
        return {
            "playing": bool(playing),
            "track": item["name"],
            "artist": ", ".join(a["name"] for a in item.get("artists", [])),
            "art": art,
        }
    except Exception as e:
        print("spotify:", e, file=sys.stderr)
        return None


def tile(x, y, w, h):
    return f'<rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" rx="16" fill="#ffffff" fill-opacity="0.02" stroke="{LINE}"/>'


def label(x, y, s, color=DIM):
    return f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="11" fill="{color}" letter-spacing="1.5">{esc(s)}</text>'


def unidos_tile(x, y, w, h, u):
    out = [tile(x, y, w, h), label(x + 22, y + 36, "UNIDOS POR COLOMBIA")]
    if not u:
        out.append(f'<text x="{x + 22}" y="{y + 110}" font-family="{SANS}" font-size="16" fill="{MUTED}">data unavailable right now</text>')
        return "".join(out)
    num = f"{u['total']:,}" + ("+" if u["capped"] else "")
    out.append(f'<text x="{x + 20}" y="{y + 104}" font-family="{SANS}" font-size="52" font-weight="800" fill="url(#acc)" letter-spacing="-2">{num}</text>')
    out.append(f'<text x="{x + 22}" y="{y + 130}" font-family="{SANS}" font-size="14" fill="{MUTED}">aid points live on the map</text>')
    bx, by, bw = x + 22, y + 156, w - 44
    total = sum(u["counts"].values()) or 1
    cx = bx
    segs = []
    for i, (k, _, col) in enumerate(CATS):
        n = u["counts"].get(k, 0)
        if not n:
            continue
        sw = max(2, bw * n / total)
        segs.append(f'<rect class="seg" style="animation-delay:{0.3 + i * 0.12:.2f}s" x="{cx:.1f}" y="{by}" width="{sw:.1f}" height="10" fill="{col}"/>')
        cx += sw
    out.append(f'<clipPath id="bar"><rect x="{bx}" y="{by}" width="{bw}" height="10" rx="5"/></clipPath><g clip-path="url(#bar)"><rect x="{bx}" y="{by}" width="{bw}" height="10" fill="{LINE}"/>{"".join(segs)}</g>')
    top = sorted(((u["counts"].get(k, 0), name, col) for k, name, col in CATS), reverse=True)[:3]
    ly = by + 36
    for i, (n, name, col) in enumerate(top):
        yy = ly + i * 22
        out.append(f'<circle cx="{bx + 4}" cy="{yy - 4}" r="4" fill="{col}"/><text x="{bx + 16}" y="{yy}" font-family="{MONO}" font-size="12" fill="{MUTED}">{esc(name)}</text><text x="{x + w - 22}" y="{yy}" text-anchor="end" font-family="{MONO}" font-size="12" fill="{TEXT}">{n:,}</text>')
    return "".join(out)


def activity_tile(x, y, w, h, a):
    out = [tile(x, y, w, h), label(x + 22, y + 36, "LATEST ON GITHUB")]
    if not a:
        out.append(f'<text x="{x + 22}" y="{y + 110}" font-family="{SANS}" font-size="16" fill="{MUTED}">quiet week, cooking something</text>')
        return "".join(out)
    out.append(f'<text x="{x + 22}" y="{y + 78}" font-family="{SANS}" font-size="15" fill="{ACC2}">{esc(a["verb"])}</text>')
    cpl = max(18, int((w - 44) / 9.6))
    for i, ln in enumerate(wrap(a["title"], cpl, 3)):
        out.append(f'<text x="{x + 22}" y="{y + 112 + i * 26}" font-family="{SANS}" font-size="18" font-weight="650" fill="{TEXT}" letter-spacing="-0.3">{esc(ln)}</text>')
    out.append(f'<text x="{x + 22}" y="{y + h - 50}" font-family="{MONO}" font-size="12" fill="{MUTED}">{esc(clip(a["repo"], int((w - 44) / 7.4)))}</text>')
    out.append(f'<text x="{x + 22}" y="{y + h - 26}" font-family="{MONO}" font-size="12" fill="{DIM}">{esc(a["when"])}</text>')
    return "".join(out)


def spotify_tile(x, y, w, h, s):
    out = [tile(x, y, w, h)]
    out.append(label(x + 22, y + 36, "NOW PLAYING" if s["playing"] else "LAST PLAYED", ACC2 if s["playing"] else DIM))
    ax, ay, asz = x + 22, y + 56, 96
    if s.get("art"):
        out.append(f'<clipPath id="art"><rect x="{ax}" y="{ay}" width="{asz}" height="{asz}" rx="10"/></clipPath><image clip-path="url(#art)" x="{ax}" y="{ay}" width="{asz}" height="{asz}" href="{s["art"]}"/>')
    else:
        out.append(f'<rect x="{ax}" y="{ay}" width="{asz}" height="{asz}" rx="10" fill="{LINE}"/>')
    if s["playing"]:
        bars = []
        for i in range(4):
            bars.append(f'<rect class="eq" style="animation-delay:{i * 0.18:.2f}s" x="{ax + asz + 18 + i * 7}" y="{ay + 4}" width="4" height="22" rx="2" fill="{ACC2}"/>')
        out.append("".join(bars))
    tx = x + 22
    cpl = max(16, int((w - 44) / 9.8))
    for i, ln in enumerate(wrap(s["track"], cpl, 2)):
        out.append(f'<text x="{tx}" y="{ay + asz + 34 + i * 24}" font-family="{SANS}" font-size="18" font-weight="650" fill="{TEXT}" letter-spacing="-0.3">{esc(ln)}</text>')
    out.append(f'<text x="{tx}" y="{y + h - 26}" font-family="{MONO}" font-size="12" fill="{MUTED}">{esc(clip(s["artist"], int((w - 44) / 7.4)))}</text>')
    return "".join(out)


def live_svg(u, a, s):
    W, H = 1000, 340
    pad, gap, ty, th = 24, 16, 64, 252
    tiles = [("u", u), ("a", a)] + ([("s", s)] if s else [])
    n = len(tiles)
    tw = (W - 2 * pad - gap * (n - 1)) / n
    body = []
    for i, (k, v) in enumerate(tiles):
        x = pad + i * (tw + gap)
        fn = {"u": unidos_tile, "a": activity_tile, "s": spotify_tile}[k]
        body.append(f'<g class="t" style="animation-delay:{0.1 + i * 0.15:.2f}s">{fn(x, ty, tw, th, v)}</g>')
    today = dt.datetime.now(dt.timezone.utc).strftime("%b %-d, %Y").lower()
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Live panel: Unidos por Colombia aid points, latest GitHub activity{', music' if s else ''}">
<style>
@keyframes pulse {{ 0%,100% {{ opacity: 1 }} 50% {{ opacity: .3 }} }}
@keyframes up {{ from {{ opacity: 0; transform: translateY(10px) }} to {{ opacity: 1; transform: translateY(0) }} }}
@keyframes grow {{ from {{ opacity: 0 }} to {{ opacity: 1 }} }}
@keyframes eq {{ 0%,100% {{ transform: scaleY(.3) }} 50% {{ transform: scaleY(1) }} }}
.live {{ animation: pulse 1.6s ease-in-out infinite }}
.t {{ animation: up .7s ease-out both }}
.seg {{ animation: grow .5s ease-out both }}
.eq {{ transform-box: fill-box; transform-origin: bottom; animation: eq .9s ease-in-out infinite }}
</style>
<defs>{gen.defs_common()}</defs>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="22" fill="{PANEL}" stroke="{LINE}"/>
<circle class="live" cx="{pad + 6}" cy="34" r="5" fill="#ef4444"/>
<text x="{pad + 20}" y="39" font-family="{MONO}" font-size="12" fill="{TEXT}" letter-spacing="2">LIVE</text>
<text x="{W - pad}" y="39" text-anchor="end" font-family="{MONO}" font-size="12" fill="{DIM}">auto-updated every 30 min · synced {today}</text>
{"".join(body)}
</svg>
"""


def cmd_live(out):
    out = Path(out)
    u = fetch_unidos()
    a = fetch_activity()
    s = fetch_spotify()
    (out / "live.svg").write_text(live_svg(u, a, s))
    if u:
        stat = f"{u['total']:,}" + ("+" if u["capped"] else "")
        (out / "featured.svg").write_text(gen.featured(stat, "AID POINTS LIVE"))
    elif not (out / "featured.svg").exists():
        (out / "featured.svg").write_text(gen.featured())
    print(json.dumps({"unidos": u and u["total"], "activity": a, "spotify": s and {k: v for k, v in s.items() if k != "art"}}))


LOGIN_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")


def guestbook_svg(entries, total):
    W = 1000
    per_row, size, gx, gy = 12, 56, 80, 92
    shown = entries[:24]
    rows = max(1, (len(shown) + per_row - 1) // per_row)
    H = 96 + rows * gy + 20
    items = []
    x0 = (W - (min(len(shown), per_row) - 1) * gx) / 2 if shown else W / 2
    for i, e in enumerate(shown):
        r, c = divmod(i, per_row)
        cx = x0 + c * gx
        cy = 108 + r * gy
        av = e.get("avatar")
        ring = f'<circle cx="{cx}" cy="{cy}" r="{size / 2 + 3}" fill="none" stroke="url(#acc)" stroke-width="2.5"/>' if i == 0 else ""
        img = f'<image clip-path="url(#c{i})" x="{cx - size / 2}" y="{cy - size / 2}" width="{size}" height="{size}" href="{av}"/>' if av else f'<circle cx="{cx}" cy="{cy}" r="{size / 2}" fill="{LINE}"/>'
        items.append(
            f'<clipPath id="c{i}"><circle cx="{cx}" cy="{cy}" r="{size / 2}"/></clipPath>'
            f'<g class="a" style="animation-delay:{0.2 + i * 0.06:.2f}s">{ring}{img}'
            f'<text x="{cx}" y="{cy + size / 2 + 20}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{TEXT if i == 0 else MUTED}">{esc(clip(e["login"], 11))}</text></g>'
        )
    if not shown:
        items.append(f'<text x="{W / 2}" y="120" text-anchor="middle" font-family="{SANS}" font-size="18" fill="{MUTED}">no signatures yet. be the first one ↓</text>')
    count = f"{total} signature" + ("" if total == 1 else "s")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Guestbook: {esc(count)}">
<style>
@keyframes pop {{ 0% {{ opacity: 0; transform: scale(.6) }} 70% {{ opacity: 1; transform: scale(1.06) }} 100% {{ opacity: 1; transform: scale(1) }} }}
.a {{ transform-box: fill-box; transform-origin: center; animation: pop .55s ease-out both }}
</style>
<defs>{gen.defs_common()}</defs>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="22" fill="{PANEL}" stroke="{LINE}"/>
<text x="24" y="40" font-family="{MONO}" font-size="12" fill="{DIM}" letter-spacing="2">GUESTBOOK</text>
<text x="{W - 24}" y="40" text-anchor="end" font-family="{MONO}" font-size="12" fill="{MUTED}">{esc(count)}</text>
{"".join(items)}
</svg>
"""


def sign_svg():
    W, H = 300, 56
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Sign the guestbook">
<style>
@keyframes glow {{ 0%,100% {{ opacity: .35 }} 50% {{ opacity: .9 }} }}
@keyframes nudge {{ 0%,100% {{ transform: translateX(0) }} 50% {{ transform: translateX(4px) }} }}
.g {{ animation: glow 2.4s ease-in-out infinite }}
.n {{ animation: nudge 1.2s ease-in-out infinite }}
</style>
<defs>{gen.defs_common()}</defs>
<rect class="g" x="1" y="1" width="{W - 2}" height="{H - 2}" rx="{H / 2 - 1}" fill="none" stroke="url(#acc)" stroke-width="2"/>
<rect x="4" y="4" width="{W - 8}" height="{H - 8}" rx="{H / 2 - 4}" fill="{PANEL}"/>
<text x="{W / 2 - 10}" y="{H / 2 + 5}" text-anchor="middle" font-family="{MONO}" font-size="15" fill="{TEXT}">sign the guestbook</text>
<text class="n" x="{W / 2 + 92}" y="{H / 2 + 5}" font-family="{MONO}" font-size="15" fill="{ACC}">→</text>
</svg>
"""


def render_guestbook(out):
    out = Path(out)
    db = out / "guestbook.json"
    entries = json.loads(db.read_text()) if db.exists() else []
    for e in entries[:24]:
        e["avatar"] = data_uri(f"https://avatars.githubusercontent.com/u/{e['id']}?s=112")
    (out / "guestbook.svg").write_text(guestbook_svg(entries, len(entries)))


def cmd_guestbook(out):
    out = Path(out)
    ev = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    issue = ev.get("issue") or {}
    user = issue.get("user") or {}
    login, uid = user.get("login", ""), user.get("id")
    result = "skip"
    if "sign" in (issue.get("title") or "").lower() and LOGIN_RE.match(login) and isinstance(uid, int) and user.get("type") == "User":
        db = out / "guestbook.json"
        entries = json.loads(db.read_text()) if db.exists() else []
        if any(e["id"] == uid for e in entries):
            result = "dup"
        else:
            entries.insert(0, {"login": login, "id": uid, "signed_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")})
            db.write_text(json.dumps(entries, indent=1) + "\n")
            render_guestbook(out)
            result = "new"
    gho = os.environ.get("GITHUB_OUTPUT")
    if gho:
        with open(gho, "a") as f:
            f.write(f"result={result}\nlogin={login}\n")
    print(result, login)


if __name__ == "__main__":
    cmd, out = sys.argv[1], sys.argv[2]
    Path(out).mkdir(parents=True, exist_ok=True)
    if cmd == "live":
        cmd_live(out)
    elif cmd == "guestbook":
        cmd_guestbook(out)
    elif cmd == "guestbook-render":
        render_guestbook(out)
    elif cmd == "sign":
        (Path(out) / "sign.svg").write_text(sign_svg())
    elif cmd == "static":
        gen.render_static(out)
