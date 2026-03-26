#!/usr/bin/env python3
"""
Gera carrossel no formato "thread-style" КЯАТА. — PNG 1080x1080.
Cada slide parece um post de texto com imagem opcional embaixo.
Lê JSON do stdin, salva PNGs em output/YYYY-MM-DD/.
"""
import json, sys, urllib.request, urllib.parse
from pathlib import Path
from datetime import datetime

# ── CONFIG ──────────────────────────────────────────────────────────
PALETA = {
    "bg":      "#111111",
    "surface": "#1A1A1A",
    "accent":  "#C9A227",
    "text":    "#F2F2F0",
    "muted":   "#8A8A8A",
    "border":  "#2A2A2A",
}

_env_path = Path(__file__).parent.parent / ".env"
_creds = {}
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            _creds[k.strip()] = v.strip()
PEXELS_KEY = _creds.get("PEXELS_KEY", "pf4uzCsl8nG2BjyUWw7cVUsplqnT9JcA7yQreUz3wOH0YZbOqm6w5Eni")


# ── IMAGEM ───────────────────────────────────────────────────────────
def baixar_imagem(query: str, destino: Path):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        q = urllib.parse.quote(query)
        req = urllib.request.Request(
            f"https://api.pexels.com/v1/search?query={q}&per_page=5&orientation=landscape",
            headers={**headers, "Authorization": PEXELS_KEY}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            fotos = json.loads(r.read()).get("photos", [])
        if fotos:
            img_url = fotos[0]["src"]["large2x"]
            req2 = urllib.request.Request(img_url, headers=headers)
            with urllib.request.urlopen(req2, timeout=15) as r2:
                destino.write_bytes(r2.read())
            return True
    except Exception as e:
        print(f"  ⚠ Pexels: {e}", file=sys.stderr)
    # Fallback Picsum (landscape)
    try:
        seed = abs(hash(query)) % 1000
        req = urllib.request.Request(
            f"https://picsum.photos/seed/{seed}/1080/480",
            headers=headers
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            destino.write_bytes(r.read())
        return True
    except:
        return False


# ── GERA HTML ────────────────────────────────────────────────────────
def gerar_html_thread(slide: dict, total: int, img_path: Path) -> str:
    num      = slide["numero"]
    texto    = slide.get("texto", "")
    imagem   = slide.get("imagem", True)   # se False, slide só-texto
    tag      = slide.get("tag", "")        # tag colorida opcional (ex: "BREAKING")
    is_cta   = slide.get("is_cta", False)

    bg      = PALETA["bg"]
    accent  = PALETA["accent"]
    text    = PALETA["text"]
    muted   = PALETA["muted"]
    surface = PALETA["surface"]
    border  = PALETA["border"]

    tem_imagem = imagem and img_path.exists()
    img_url    = f"file://{img_path.absolute()}" if tem_imagem else ""

    # Bloco de imagem no HTML
    img_html = ""
    if tem_imagem:
        img_html = f"""
        <div class="img-block">
          <img src="{img_url}" alt="">
        </div>"""

    # Tag opcional
    tag_html = ""
    if tag:
        tag_html = f'<div class="tag-label">{tag}</div>'

    # CTA pill no último slide
    cta_html = ""
    if is_cta:
        cta_html = f'<div class="cta-pill">SALVA ✦ COMPARTILHA ✦ SEGUE</div>'

    # Número do slide
    num_html = f'<div class="slide-num">{num:02d} / {total:02d}</div>'

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap');
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  width:1080px; height:1080px; overflow:hidden;
  font-family:'DM Sans',sans-serif;
  background:{bg};
  display:flex; flex-direction:column;
  position:relative;
}}

/* Barra de acento lateral */
.side-bar {{
  position:absolute; left:0; top:0; bottom:0;
  width:5px; background:{accent};
}}

/* Rodapé com logo */
.footer {{
  position:absolute; bottom:0; left:0; right:0;
  height:64px;
  border-top:1px solid {border};
  display:flex; align-items:center;
  padding:0 56px;
  gap:12px;
}}
.footer-logo {{
  font-family:'DM Sans',sans-serif;
  font-weight:700; font-size:16px;
  color:{accent}; letter-spacing:2px;
}}
.footer-handle {{
  font-size:14px; color:{muted};
}}
.slide-num {{
  margin-left:auto;
  font-size:13px; color:{muted}; letter-spacing:2px;
}}

/* Área de conteúdo */
.content {{
  flex:1;
  padding:64px 72px 80px 72px;
  display:flex; flex-direction:column;
  justify-content:center;
  gap:32px;
  padding-bottom:100px; /* espaço pro footer */
}}

.tag-label {{
  display:inline-block;
  background:{accent};
  color:#111;
  font-size:12px; font-weight:700;
  letter-spacing:2px;
  padding:6px 14px;
  border-radius:4px;
  align-self:flex-start;
  text-transform:uppercase;
}}

.texto {{
  font-size:38px;
  font-weight:500;
  line-height:1.45;
  color:{text};
  max-width:900px;
}}
.texto strong {{
  color:{accent};
  font-weight:700;
}}

/* Imagem */
.img-block {{
  border-radius:12px;
  overflow:hidden;
  max-height:320px;
  border:1px solid {border};
}}
.img-block img {{
  width:100%; height:320px;
  object-fit:cover;
  display:block;
  filter:brightness(0.9) saturate(0.85);
}}

/* CTA */
.cta-pill {{
  display:inline-block;
  background:{accent};
  color:#111;
  font-weight:700;
  font-size:18px;
  letter-spacing:3px;
  padding:14px 40px;
  border-radius:100px;
  align-self:flex-start;
}}

/* Slide só-texto: fonte maior */
.texto-only .texto {{
  font-size:44px;
  line-height:1.4;
}}
</style>
</head>
<body>
<div class="side-bar"></div>

<div class="content {'texto-only' if not tem_imagem and not is_cta else ''}">
  {tag_html}
  <div class="texto">{texto}</div>
  {img_html}
  {cta_html}
</div>

<div class="footer">
  <div class="footer-logo">КЯАТА.</div>
  <div class="footer-handle">@krata.ag</div>
  {num_html}
</div>
</body>
</html>"""


# ── RENDER PNG ───────────────────────────────────────────────────────
def html_para_png(html_path: str, png_path: str):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1080})
        page.goto(f"file://{html_path}")
        page.wait_for_timeout(2500)
        page.screenshot(path=png_path, full_page=False)
        browser.close()


# ── MAIN ─────────────────────────────────────────────────────────────
def main():
    payload = json.loads(sys.stdin.read())
    slides  = payload["slides"]
    total   = len(slides)

    hoje  = datetime.now().strftime("%Y-%m-%d")
    slug  = payload.get("slug", "thread")
    pasta = Path(__file__).parent.parent / "output" / hoje / slug
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "html").mkdir(exist_ok=True)

    arquivos_png = []

    for slide in slides:
        num    = slide["numero"]
        imagem = slide.get("imagem", True)
        print(f"  [{num:02d}/{total}] slide {num}", file=sys.stderr)

        img_path = pasta / f"img_{num:02d}.jpg"
        if imagem and slide.get("query_imagem"):
            baixar_imagem(slide["query_imagem"], img_path)

        html_content = gerar_html_thread(slide, total, img_path)
        html_path    = pasta / "html" / f"slide_{num:02d}.html"
        html_path.write_text(html_content, encoding="utf-8")

        png_path = pasta / f"slide_{num:02d}.png"
        try:
            html_para_png(str(html_path.absolute()), str(png_path))
            arquivos_png.append(str(png_path))
            print(f"    ✓ slide_{num:02d}.png", file=sys.stderr)
        except Exception as e:
            print(f"    ⚠ png: {e}", file=sys.stderr)

    result = {
        "pasta": str(pasta),
        "slides": len(arquivos_png),
        "arquivos": arquivos_png,
        "titulo": payload.get("titulo", "")
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
