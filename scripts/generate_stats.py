#!/usr/bin/env python3
"""Builds the profile stat cards (assets/stats.svg, langs.svg, streak.svg, activity.svg)
from the real GitHub GraphQL API. Runs daily in .github/workflows/update-stats.yml.
Standard library only. Needs GH_TOKEN and USERNAME env vars."""
import json, os, urllib.request, datetime as dt
from xml.sax.saxutils import escape

USER = os.environ.get("USERNAME", "Shubh12970")
TOKEN = os.environ["GH_TOKEN"]
BG, ACC, BLUE, TXT, MUT = "#050816", "#00A3FF", "#0077FF", "#E6EDF3", "#8B949E"
FONT = "Segoe UI,Helvetica,Arial,sans-serif"

def gql(q, v=None):
    req = urllib.request.Request("https://api.github.com/graphql",
        data=json.dumps({"query": q, "variables": v or {}}).encode(),
        headers={"Authorization": "bearer " + TOKEN, "Content-Type": "application/json", "User-Agent": "profile-stats"})
    r = json.load(urllib.request.urlopen(req, timeout=60))
    if "errors" in r: raise SystemExit(r["errors"])
    return r["data"]

base = gql("""query($u:String!){user(login:$u){createdAt followers{totalCount}
 repositories(ownerAffiliations:OWNER,isFork:false,first:100){totalCount nodes{stargazerCount
  languages(first:10,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}}}}}}""", {"u": USER})["user"]
created = dt.datetime.fromisoformat(base["createdAt"].replace("Z", "+00:00"))
now = dt.datetime.now(dt.timezone.utc)

days, commits, prs, issues, reviews = {}, 0, 0, 0, 0
start = created
while start < now:
    end = min(start + dt.timedelta(days=364), now)
    c = gql("""query($u:String!,$f:DateTime!,$t:DateTime!){user(login:$u){contributionsCollection(from:$f,to:$t){
      totalCommitContributions totalIssueContributions totalPullRequestContributions totalPullRequestReviewContributions
      contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}""",
      {"u": USER, "f": start.isoformat(), "t": end.isoformat()})["user"]["contributionsCollection"]
    commits += c["totalCommitContributions"]; issues += c["totalIssueContributions"]
    prs += c["totalPullRequestContributions"]; reviews += c["totalPullRequestReviewContributions"]
    for w in c["contributionCalendar"]["weeks"]:
        for d in w["contributionDays"]: days[d["date"]] = d["contributionCount"]
    start = end + dt.timedelta(seconds=1)

days = {k: v for k, v in days.items() if k <= now.date().isoformat()}
today = dt.date.fromisoformat(max(days))  # latest day GitHub reports; dates are exactly as on the profile graph
total = sum(days.values())
ordered = sorted(days)
# streaks: a streak stays alive until a full day is missed
longest, run, lstart, lbest = 0, 0, None, None
prev = None
for d in ordered:
    if days[d] > 0:
        run = run + 1 if prev else 1
        if run == 1: lstart = d
        if run >= longest: longest, lbest = run, (lstart, d)
        prev = True
    else:
        run, prev = 0, None
cur, cstart = 0, None
d = today
if days.get(d.isoformat(), 0) == 0: d -= dt.timedelta(days=1)
while days.get(d.isoformat(), 0) > 0:
    cur += 1; cstart = d; d -= dt.timedelta(days=1)
first = ordered[0] if ordered else today.isoformat()

def fmt(s):
    x = dt.date.fromisoformat(s); return x.strftime("%b ") + str(x.day)
def rng(a, b): return "-" if not a else (fmt(a) if a == b else f"{fmt(a)} - {fmt(b)}")
def card(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">'
            f'<title>{escape(title)}</title><rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="8" fill="{BG}" stroke="{BLUE}" stroke-opacity=".35"/>{body}</svg>\n')
def t(x, y, s, size=13, fill=TXT, weight=400, anchor="start"):
    return f'<text x="{x}" y="{y}" fill="{fill}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(str(s))}</text>'

stamp = f"Updated {today.strftime('%b')} {today.day}, {today.year}"
os.makedirs("assets", exist_ok=True)

# --- streak card
cols = [(total, "Total Contributions", f"{fmt(first)} - Present"),
        (cur, "Current Streak", rng(cstart.isoformat() if cstart else None, today.isoformat()) if cur else "No active streak"),
        (longest, "Longest Streak", rng(*lbest) if lbest else "-")]
b = ""
for i, (n, lab, sub) in enumerate(cols):
    cx = 85 + i * 165
    b += t(cx, 78, n, 34, "#FFFFFF", 700, "middle") + t(cx, 108, lab, 13, ACC if i == 1 else TXT, 600, "middle") + t(cx, 128, sub, 11, MUT, 400, "middle")
    if i: b += f'<line x1="{cx-82}" y1="52" x2="{cx-82}" y2="132" stroke="{BLUE}" stroke-opacity=".3"/>'
b += t(247, 28, "Contribution Streak", 14, ACC, 700, "middle") + t(247, 160, stamp, 10, MUT, 400, "middle")
open("assets/streak.svg", "w").write(card(495, 175, b, f"GitHub contribution streak: current {cur} days, longest {longest} days, {total} total contributions"))

# --- stats card
stars = sum(r["stargazerCount"] for r in base["repositories"]["nodes"])
rows = [("Total contributions", total), ("Commits", commits), ("Pull requests", prs), ("Issues", issues),
        ("Repositories", base["repositories"]["totalCount"]), ("Stars earned", stars)]
b = t(25, 32, f"{USER}'s GitHub Statistics", 15, ACC, 700)
for i, (k, v) in enumerate(rows):
    y = 62 + i * 18
    b += f'<circle cx="31" cy="{y-4}" r="3" fill="{ACC}"/>' + t(44, y, k, 12.5) + t(450, y, v, 12.5, "#FFFFFF", 700, "end")
open("assets/stats.svg", "w").write(card(495, 175, b, "GitHub statistics"))

# --- languages card
lang = {}
for r in base["repositories"]["nodes"]:
    for e in r["languages"]["edges"]: lang[e["node"]["name"]] = lang.get(e["node"]["name"], 0) + e["size"]
top = sorted(lang.items(), key=lambda x: -x[1])[:6]; tot = sum(v for _, v in lang.items()) or 1
shades = ["#3D2BC8", "#00E5FF", "#0061F2", "#6E9FFF", "#A9D9FF", "#DCEEFF"]  # approved distinct-blues palette (rank order)
b = t(25, 32, "Most Used Languages", 15, ACC, 700)
x = 25; bw = 445
b += f'<clipPath id="c"><rect x="25" y="46" width="{bw}" height="8" rx="4"/></clipPath><g clip-path="url(#c)">'
for (n, v), col in zip(top, shades):
    w = bw * v / sum(vv for _, vv in top); b += f'<rect x="{x:.1f}" y="46" width="{w:.1f}" height="8" fill="{col}"/>'; x += w
b += "</g>"
for i, ((n, v), col) in enumerate(zip(top, shades)):
    cx = 25 + (i % 2) * 225; y = 82 + (i // 2) * 24
    b += f'<circle cx="{cx+5}" cy="{y-4}" r="5" fill="{col}"/>' + t(cx + 16, y, n, 12.5) + t(cx + 200, y, f"{100*v/tot:.1f}%", 12, MUT, 400, "end")
open("assets/langs.svg", "w").write(card(495, 175, b, "Most used programming languages"))

# --- activity graph (last 31 days)
last = [(today - dt.timedelta(days=i)) for i in range(30, -1, -1)]
vals = [days.get(d.isoformat(), 0) for d in last]
W, H, L, R, T, B = 900, 260, 46, 24, 52, 40
mx = max(max(vals), 4); px = lambda i: L + i * (W - L - R) / 30; py = lambda v: T + (H - T - B) * (1 - v / mx)
pts = [(px(i), py(v)) for i, v in enumerate(vals)]
line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
b = t(W/2, 30, "Contribution Activity", 16, ACC, 700, "middle")
for k in range(0, mx + 1, max(1, mx // 4)):
    y = py(k); b += f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" stroke="{BLUE}" stroke-opacity=".18"/>' + t(L-8, y+4, k, 10, MUT, 400, "end")
b += f'<polygon points="{L},{py(0):.1f} {line} {W-R},{py(0):.1f}" fill="{BLUE}" fill-opacity=".35"/><polyline points="{line}" fill="none" stroke="{BLUE}" stroke-width="2.5" stroke-linejoin="round"/>'
for x, y in pts: b += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#FFFFFF"/>'
for i in range(0, 31, 5): b += t(px(i), H-16, f"{last[i].day} {last[i].strftime('%b')}", 10, MUT, 400, "middle")
b += t(W-R, 30, "last 31 days", 10, MUT, 400, "end")
open("assets/activity.svg", "w").write(card(W, H, b, "GitHub contribution activity, last 31 days"))
print(json.dumps({"total": total, "current": cur, "longest": longest, "commits": commits, "prs": prs, "issues": issues, "top": top}))
