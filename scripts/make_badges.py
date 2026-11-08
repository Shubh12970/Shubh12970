#!/usr/bin/env python3
"""Builds the static skill badges in assets/badges (self-hosted, no third-party image service)."""
import re, sys, os
ICON_DIR = sys.argv[1]
OUT = "assets/badges"
BG, FG, ACC = "#050816", "#E6EDF3", "#00A3FF"
BADGES = [  # (file, label, icon)
 ("c","C","c"),("cpp","C++","cplusplus"),("java","Java","openjdk"),("python","Python","python"),
 ("javascript","JavaScript","javascript"),("typescript","TypeScript","typescript"),
 ("html5","HTML5","html5"),("css3","CSS3","css3"),("react","React.js","react"),
 ("nodejs","Node.js","nodedotjs"),("express","Express.js","express"),("springboot","Spring Boot","springboot"),
 ("postgresql","PostgreSQL","postgresql"),("mongodb","MongoDB","mongodb"),
 ("git","Git","git"),("github","GitHub","github"),("vscode","Visual Studio Code","visualstudiocode"),
]
def icon_path(name):
    s = open(os.path.join(ICON_DIR, name + ".svg")).read()
    return " ".join(re.findall(r'<path d="([^"]+)"', s))
def badge(label, icon, big=False):
    h = 40 if big else 30
    fs = 13 if big else 12
    tw = round(len(label) * (fs * 0.56) + (len(label) > 0) * 2)
    pad, isz, gap = (18, 18, 9) if big else (12, 15, 8)
    w = pad + isz + gap + tw + pad
    sc = isz / 24
    ty = h / 2 + fs * 0.35
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{label}">'
        f'<title>{label}</title><rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="6" fill="{BG}" stroke="#0077FF" stroke-opacity=".45"/>'
        f'<g transform="translate({pad},{(h-isz)/2}) scale({sc})"><path fill="{ACC}" d="{icon_path(icon)}"/></g>'
        f'<text x="{pad+isz+gap}" y="{ty}" fill="{FG}" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="{fs}" font-weight="600" textLength="{tw}" lengthAdjust="spacingAndGlyphs">{label}</text></svg>\n')
os.makedirs(OUT, exist_ok=True)
for f,l,i in BADGES:
    open(f"{OUT}/{f}.svg","w").write(badge(l,i))
for f,l,i in [("link-github","GitHub","github"),("link-linkedin","LinkedIn","linkedin"),
              ("cta-github","Explore My GitHub","github"),("cta-linkedin","Connect on LinkedIn","linkedin")]:
    open(f"{OUT}/{f}.svg","w").write(badge(l,i,big=True))
for f,l in [("status-dev","In development")]:
    pass
print("ok")

# blue "Explore Repository" button
lab = "Explore Repository"; h = 30; isz = 15; tw = round(len(lab)*7.4+2); w = 12+isz+8+tw+12
open(f"{OUT}/explore-repo.svg","w").write(
 f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{lab}"><title>{lab}</title>'
 f'<rect width="{w}" height="{h}" rx="6" fill="#0077FF"/><g transform="translate(12,{(h-isz)/2}) scale({isz/24})"><path fill="#FFFFFF" d="{icon_path("github")}"/></g>'
 f'<text x="{12+isz+8}" y="{h/2+4.2}" fill="#FFFFFF" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="12" font-weight="600" textLength="{tw}" lengthAdjust="spacingAndGlyphs">{lab}</text></svg>\n')

# header / footer banners (same gradient 050816 -> 0A192F -> 0077FF)
os.makedirs("assets", exist_ok=True)
FONT = "Segoe UI,Helvetica,Arial,sans-serif"
open("assets/header.svg","w").write(
 f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="180" viewBox="0 0 900 180" role="img" aria-label="Shubhra Jyothsna - Full-Stack Development | Artificial Intelligence">'
 '<defs><linearGradient id="g" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="#050816"/><stop offset=".5" stop-color="#0A192F"/><stop offset="1" stop-color="#0077FF"/></linearGradient></defs>'
 '<rect width="900" height="180" fill="url(#g)"/>'
 f'<text x="450" y="88" text-anchor="middle" fill="#FFFFFF" font-family="{FONT}" font-size="38" font-weight="700" letter-spacing="1">SHUBHRA JYOTHSNA</text>'
 f'<text x="450" y="122" text-anchor="middle" fill="#FFFFFF" font-family="{FONT}" font-size="13" letter-spacing="1.5">FULL-STACK DEVELOPMENT | ARTIFICIAL INTELLIGENCE</text></svg>\n')
open("assets/footer.svg","w").write(
 '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="65" viewBox="0 0 900 65" role="img" aria-label=""><defs><linearGradient id="g" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="#0077FF"/><stop offset="1" stop-color="#050816"/></linearGradient></defs><rect width="900" height="65" fill="url(#g)"/></svg>\n')
