from __future__ import annotations

import json
import math
from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
ASSETS = ROOT / "assets"
PROJECTS = ASSETS / "projects"
SOURCE = ASSETS / "source"

def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )

def wrap_text(text: str, max_chars: int = 56) -> list[str]:
    words = text.split()
    lines: list[str] = []
    line = ""
    for word in words:
        if not line:
            line = word
        elif len(line) + 1 + len(word) <= max_chars:
            line += " " + word
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines

def card_svg(title, subtitle="", bullets=None, width=940, accent="#22c55e", body_font=16, title_size=22):
    bullets = bullets or []
    lines = []
    for b in bullets:
        lines.extend(wrap_text(b, 86))
    h = max(170, 28 * 2 + 62 + len(lines) * 26)
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" viewBox="0 0 {width} {h}">',
        f'<rect x="1" y="1" rx="20" ry="20" width="{width-2}" height="{h-2}" fill="#0d1117" stroke="#30363d"/>',
        f'<rect x="1" y="1" rx="20" ry="20" width="6" height="{h-2}" fill="{accent}"/>',
        f'<text x="44" y="36" fill="#f0f6fc" font-size="{title_size}" font-family="monospace" font-weight="700">{esc(title)}</text>',
    ]
    if subtitle:
        svg.append(f'<text x="44" y="62" fill="#8b949e" font-size="14" font-family="monospace">{esc(subtitle)}</text>')
    y = 90
    for line in lines:
        svg.append(f'<text x="44" y="{y}" fill="#c9d1d9" font-size="{body_font}" font-family="monospace" xml:space="preserve">• {esc(line)}</text>')
        y += 26
    svg.append('</svg>')
    return "\n".join(svg)

def chip_card(title, items, width=940, accent="#58a6ff"):
    h = 120 + max(1, math.ceil(len(items) / 4)) * 34
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" viewBox="0 0 {width} {h}">',
        f'<rect x="1" y="1" rx="20" ry="20" width="{width-2}" height="{h-2}" fill="#0d1117" stroke="#30363d"/>',
        f'<rect x="1" y="1" rx="20" ry="20" width="6" height="{h-2}" fill="{accent}"/>',
        f'<text x="44" y="36" fill="#f0f6fc" font-size="22" font-family="monospace" font-weight="700">{esc(title)}</text>',
    ]
    x0, y0 = 44, 72
    x, y = x0, y0
    for item in items:
        w = 12 * len(item) + 28
        if x + w > width - 24:
            x = x0
            y += 34
        svg.append(f'<rect x="{x}" y="{y-18}" width="{w}" height="24" rx="12" fill="#161b22" stroke="#30363d"/>')
        svg.append(f'<text x="{x+14}" y="{y}" fill="#c9d1d9" font-size="14" font-family="monospace">{esc(item)}</text>')
        x += w + 10
    svg.append('</svg>')
    return "\n".join(svg)

def photo_to_ascii(img_path, width=90):
    img = Image.open(img_path).convert("RGB")
    w, h = img.size
    height = max(1, int(width * (h / w) * 0.48))
    img = img.resize((width, height), Image.Resampling.LANCZOS)
    gray = ImageOps.grayscale(img)
    gray = ImageEnhance.Contrast(gray).enhance(1.8)
    gray = ImageEnhance.Sharpness(gray).enhance(1.25)
    gray = gray.filter(ImageFilter.SMOOTH_MORE)
    ramp = "@%#*+=-:. `"
    pix = list(gray.getdata())
    chars = [ramp[p * len(ramp) // 256] for p in pix]
    return ["".join(chars[i:i+width]) for i in range(0, len(chars), width)]

def portrait_svg(lines, width=940):
    max_cols = max(len(l) for l in lines)
    font = 12
    line_h = 16
    h = 44 + len(lines) * line_h + 20
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" viewBox="0 0 {width} {h}">',
        f'<defs><clipPath id="c"><rect x="18" y="18" width="{width-36}" height="{h-36}" rx="18"/></clipPath></defs>',
        f'<rect x="1" y="1" rx="22" ry="22" width="{width-2}" height="{h-2}" fill="#0d1117" stroke="#30363d"/>',
        '<g clip-path="url(#c)">',
    ]
    for i, line in enumerate(lines):
        y = 38 + i * line_h
        svg.append(f'<text x="24" y="{y}" fill="#c9d1d9" font-size="{font}" font-family="monospace" xml:space="preserve">{esc(line)}</text>')
        svg.append(
            f'<rect x="24" y="{y-font+2}" width="{max_cols * (font*0.60)}" height="{font+2}" fill="#0d1117">'
            f'<animate attributeName="width" from="{max_cols * (font*0.60)}" to="0" dur="0.55s" begin="{i*0.075:.2f}s" fill="freeze" />'
            f'</rect>'
        )
    svg.append('</g></svg>')
    return "\n".join(svg)

def main():
    lines = photo_to_ascii(SOURCE / "portrait.jpg", width=90)
    (ASSETS / "portrait.txt").write_text("\n".join(lines), encoding="utf-8")
    (ASSETS / "portrait.svg").write_text(portrait_svg(lines), encoding="utf-8")

    summary = [
        f"{CFG['headline']} · {CFG['subheadline']}",
        f"{CFG['tagline']}",
        f"Education: {CFG['education']['school']} · {CFG['education']['graduation']}",
        "Open to: SDE Internships and New Grad roles",
    ]
    stats = CFG["stats"]
    summary_svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="940" height="260" viewBox="0 0 940 260">',
        '<rect x="1" y="1" rx="20" ry="20" width="938" height="258" fill="#0d1117" stroke="#30363d"/>',
        f'<text x="28" y="42" fill="#f0f6fc" font-size="24" font-family="monospace" font-weight="700">{esc(CFG["name"])}</text>',
        f'<text x="28" y="68" fill="#8b949e" font-size="16" font-family="monospace">{esc(summary[0])}</text>',
        f'<text x="28" y="92" fill="#c9d1d9" font-size="15" font-family="monospace">{esc(summary[1])}</text>',
    ]
    for idx, (k, v) in enumerate(stats):
        xx = 24 + idx * (212 + 14)
        summary_svg.append(f'<rect x="{xx}" y="122" width="212" height="88" rx="14" fill="#161b22" stroke="#30363d"/>')
        summary_svg.append(f'<text x="{xx+16}" y="150" fill="#8b949e" font-size="14" font-family="monospace">{esc(k)}</text>')
        summary_svg.append(f'<text x="{xx+16}" y="178" fill="#f0f6fc" font-size="22" font-family="monospace" font-weight="700">{esc(v)}</text>')
    summary_svg.append('</svg>')
    (ASSETS / "summary.svg").write_text("\n".join(summary_svg), encoding="utf-8")

    exp = [
        "Shipd AI (DataCurve YC-24) · Outlier AI — Software Developer, Contract (May 2025 - Apr 2026)",
        *["  " + b for b in CFG["experience"][0]["bullets"]],
        "",
        "Rablo.in — Frontend Developer, Intern (Nov 2024 - Feb 2025)",
        *["  " + b for b in CFG["experience"][1]["bullets"]],
    ]
    (ASSETS / "experience.svg").write_text(card_svg("Experience", "Selected work history", exp, width=940, accent="#58a6ff"), encoding="utf-8")

    proj_map = {
        "RizzInterviews": ("rizzinterviews", "#22c55e"),
        "RootCause AI": ("rootcause-ai", "#a371f7"),
        "Relay": ("relay", "#f78166"),
        "Zenith": ("zenith", "#58a6ff"),
    }
    for p in CFG["projects"]:
        slug, accent = proj_map[p["name"]]
        bullets = [
            f"Tier: {p['tier']} · {p['period']}",
            f"Tech: {p['tech']}",
            "",
            *["  " + b for b in p["bullets"]],
            "",
            f"Repo: {p['repo']}",
        ]
        (PROJECTS / f"{slug}.svg").write_text(card_svg(p["name"], p["alias"], bullets, width=460, accent=accent), encoding="utf-8")

    skill_map = {
        "Languages": ("languages", "#22c55e"),
        "Frontend": ("frontend", "#58a6ff"),
        "Backend": ("backend", "#a371f7"),
        "AI": ("ai", "#f78166"),
        "Cloud & DevOps": ("cloud", "#f2cc60"),
        "Practices": ("practices", "#8b949e"),
    }
    for title, items in CFG["skills"].items():
        slug, accent = skill_map[title]
        (ASSETS / f"skills-{slug}.svg").write_text(chip_card(title, items, width=940, accent=accent), encoding="utf-8")

    (ASSETS / "achievements.svg").write_text(card_svg("Achievements", "Selected signals", CFG["achievements"], width=940, accent="#f78166"), encoding="utf-8")
    (ASSETS / "contact.svg").write_text(card_svg("Contact", "Reach me here", [
        f"Email: {CFG['contact']['email']}",
        f"LinkedIn: https://www.linkedin.com/in/{CFG['contact']['linkedin']}",
        f"GitHub: https://github.com/{CFG['contact']['github']}",
    ], width=940, accent="#22c55e"), encoding="utf-8")

    readme = f"""# {CFG['name']}

<div align="center">
  <img src="assets/portrait.svg" width="940" alt="ASCII portrait of Mohammed Sadique" />
</div>

<div align="center">
  <img src="assets/summary.svg" width="940" alt="Profile summary" />
</div>

## About

{CFG['summary']}

I prefer building:
- full-stack product and application software
- AI-assisted tools and workflows
- backend systems with clean interfaces
- small cloud-aware deployments over unnecessary infrastructure

## Experience

<div align="center">
  <img src="assets/experience.svg" width="940" alt="Experience" />
</div>

## Featured Projects

### Tier 1

<div align="center">
  <img src="assets/projects/rizzinterviews.svg" width="460" alt="RizzInterviews" />
  <img src="assets/projects/rootcause-ai.svg" width="460" alt="RootCause AI" />
</div>

<div align="center">
  <img src="assets/projects/relay.svg" width="460" alt="Relay" />
  <img src="assets/projects/zenith.svg" width="460" alt="Zenith" />
</div>

### Links

- **RizzInterviews**: {CFG['projects'][0]['repo']}
- **RootCause AI**: {CFG['projects'][1]['repo']}
- **Relay**: {CFG['projects'][2]['repo']}
- **Zenith**: https://github.com/sadique-mohammed/zenith-frontend · https://github.com/sadique-mohammed/zenith-backend · https://github.com/sadique-mohammed/zenith-extension

## Skills

<div align="center">
  <img src="assets/skills-languages.svg" width="940" alt="Languages" />
</div>

<div align="center">
  <img src="assets/skills-frontend.svg" width="940" alt="Frontend" />
</div>

<div align="center">
  <img src="assets/skills-backend.svg" width="940" alt="Backend" />
</div>

<div align="center">
  <img src="assets/skills-ai.svg" width="940" alt="AI" />
</div>

<div align="center">
  <img src="assets/skills-cloud.svg" width="940" alt="Cloud and DevOps" />
</div>

<div align="center">
  <img src="assets/skills-practices.svg" width="940" alt="Practices" />
</div>

## Achievements

<div align="center">
  <img src="assets/achievements.svg" width="940" alt="Achievements" />
</div>

## Currently Focused On

- SWE / Full-stack product and application development
- AI-powered developer tools and backend systems
- Cloud fundamentals: Docker, Linux, GitHub Actions, AWS basics, Kubernetes basics

## Contact

<div align="center">
  <img src="assets/contact.svg" width="940" alt="Contact" />
</div>

- Email: {CFG['contact']['email']}
- LinkedIn: https://www.linkedin.com/in/{CFG['contact']['linkedin']}
- GitHub: https://github.com/{CFG['contact']['github']}

---

Repository generated from a config-driven profile engine so the README, assets, and workflow stay in sync.
"""
    (ROOT / "README.md").write_text(readme, encoding="utf-8")

if __name__ == "__main__":
    main()
