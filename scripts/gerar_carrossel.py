#!/usr/bin/env python3
"""
Gera carrossel КЯАТА. em PNG 1080x1080.
Lê JSON do stdin com lista de slides, salva PNGs em output/YYYY-MM-DD/.
"""
import json, sys, os, urllib.request, urllib.parse
from pathlib import Path
from datetime import datetime

# ── CONFIG ─────────────────────────────────────────────────────────
PALETA = {
    "bg":      "#111111",
    "surface": "#1A1A1A",
    "accent":  "#C9A227",
    "text":    "#F2F2F0",
    "muted":   "#8A8A8A",
    "overlay": "linear-gradient(160deg, rgba(10,10,10,0.72) 0%, rgba(17,17,17,0.92) 100%)"
}

# Lê Pexels key do .env do content-team
_env_path = Path(__file__).parent.parent / ".env"
_creds = {}
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            _creds[k.strip()] = v.strip()
PEXELS_KEY = _creds.get("PEXELS_KEY", "pf4uzCsl8nG2BjyUWw7cVUsplqnT9JcA7yQreUz3wOH0YZbOqm6w5Eni")


# ── IMAGEM DE FUNDO ─────────────────────────────────────────────────
def baixar_imagem(query: str, destino: Path):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        q = urllib.parse.quote(query)
        req = urllib.request.Request(
            f"https://api.pexels.com/v1/search?query={q}&per_page=5&orientation=square",
            headers={**headers, "Authorization": PEXELS_KEY}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            fotos = json.loads(r.read()).get("photos", [])
        if fotos:
            img_url = fotos[0]["src"]["large2x"]
            req2 = urllib.request.Request(img_url, headers=headers)
            with urllib.request.urlopen(req2, timeout=15) as r2:
                destino.write_bytes(r2.read())
            return
    except Exception as e:
        print(f"  ⚠ Pexels: {e}, usando Picsum", file=sys.stderr)
    seed = abs(hash(query)) % 1000
    req = urllib.request.Request(f"https://picsum.photos/seed/{seed}/1080/1080", headers=headers)
    with urllib.request.urlopen(req, timeout=15) as r:
        destino.write_bytes(r.read())


# ── GERA HTML ───────────────────────────────────────────────────────
def gerar_html(slide: dict, total: int, img_path: Path) -> str:
    num      = slide["numero"]
    titulo   = slide.get("titulo", "")
    texto    = slide.get("texto", "")
    emoji    = slide.get("emoji", "")
    subtema  = slide.get("subtema", "КЯАТА.")
    is_capa  = (num == 1)
    is_cta   = (num == total)
    img_url  = f"file://{img_path.absolute()}" if img_path.exists() else ""

    bg      = PALETA["bg"]
    accent  = PALETA["accent"]
    text    = PALETA["text"]
    muted   = PALETA["muted"]
    overlay = PALETA["overlay"]

    if is_capa:
        corpo = f"""
        <div class="slide-inner capa">
          <div class="num-badge">01 / {total:02d}</div>
          <div class="emoji-big">{emoji}</div>
          <h1 class="titulo-capa">{titulo}</h1>
          <div class="subtema-tag">{subtema}</div>
          <div class="bar-accent"></div>
        </div>"""
    elif is_cta:
        corpo = f"""
        <div class="slide-inner cta">
          <div class="num-badge">{num:02d} / {total:02d}</div>
          <div class="emoji-big">{emoji}</div>
          <h2 class="titulo-cta">{titulo}</h2>
          <p class="texto-cta">{texto}</p>
          <div class="cta-pill">SALVA ✦ COMPARTILHA ✦ SEGUE</div>
          <div class="logo-rodape">КЯАТА.</div>
        </div>"""
    else:
        corpo = f"""
        <div class="slide-inner conteudo">
          <div class="num-badge">{num:02d} / {total:02d}</div>
          <div class="tag-topo">{emoji} {subtema}</div>
          <h2 class="titulo-slide">{titulo}</h2>
          <div class="divider-line"></div>
          <p class="texto-slide">{texto}</p>
        </div>"""

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&display=swap');
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ width:1080px; height:1080px; overflow:hidden; font-family:'DM Sans',sans-serif; background:{bg}; position:relative; }}
.bg-img {{ position:absolute; inset:0; background:url('{img_url}') center/cover no-repeat; filter:saturate(0.9) brightness(0.8); }}
.overlay {{ position:absolute; inset:0; background:{overlay}; }}
.grain {{ position:absolute; inset:0; background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E"); opacity:0.3; pointer-events:none; }}
.side-bar {{ position:absolute; left:0; top:0; bottom:0; width:6px; background:{accent}; }}
.logo-fixo {{ position:absolute; bottom:36px; left:32px; font-family:'Bebas Neue',sans-serif; font-size:20px; color:rgba(242,242,240,0.4); letter-spacing:3px; }}
.slide-inner {{ position:absolute; inset:0; padding:70px 68px 70px 84px; display:flex; flex-direction:column; justify-content:center; color:{text}; }}
.num-badge {{ position:absolute; top:40px; right:48px; font-family:'Bebas Neue',sans-serif; font-size:15px; letter-spacing:3px; color:{muted}; }}
/* CAPA */
.capa {{ justify-content:flex-end; padding-bottom:96px; }}
.emoji-big {{ font-size:60px; margin-bottom:20px; }}
.titulo-capa {{ font-family:'Bebas Neue',sans-serif; font-size:90px; line-height:0.95; color:#fff; text-shadow:0 4px 24px rgba(0,0,0,0.6); margin-bottom:18px; max-width:820px; }}
.subtema-tag {{ font-size:13px; letter-spacing:5px; color:{accent}; font-weight:600; margin-bottom:22px; text-transform:uppercase; }}
.bar-accent {{ width:72px; height:4px; background:{accent}; border-radius:2px; }}
/* CONTEÚDO */
.tag-topo {{ font-size:12px; letter-spacing:4px; color:{accent}; font-weight:600; text-transform:uppercase; margin-bottom:24px; }}
.titulo-slide {{ font-family:'Bebas Neue',sans-serif; font-size:68px; line-height:1.0; color:#fff; text-shadow:0 2px 20px rgba(0,0,0,0.7); margin-bottom:22px; max-width:840px; }}
.divider-line {{ width:52px; height:3px; background:{accent}; border-radius:2px; margin-bottom:26px; }}
.texto-slide {{ font-size:25px; line-height:1.65; color:rgba(242,242,240,0.93); max-width:840px; font-weight:400; text-shadow:0 2px 12px rgba(0,0,0,0.7); }}
/* CTA */
.cta {{ align-items:center; text-align:center; padding:80px; }}
.titulo-cta {{ font-family:'Bebas Neue',sans-serif; font-size:78px; color:#fff; line-height:1.0; margin-bottom:22px; text-shadow:0 4px 24px rgba(0,0,0,0.5); }}
.texto-cta {{ font-size:25px; color:rgba(242,242,240,0.82); max-width:720px; line-height:1.6; margin-bottom:38px; font-weight:300; }}
.cta-pill {{ background:{accent}; color:#111; font-family:'Bebas Neue',sans-serif; font-size:21px; letter-spacing:4px; padding:16px 44px; border-radius:100px; margin-bottom:32px; }}
.logo-rodape {{ font-family:'Bebas Neue',sans-serif; font-size:22px; color:rgba(242,242,240,0.35); letter-spacing:4px; }}
</style>
</head>
<body>
<div class="bg-img"></div>
<div class="overlay"></div>
<div class="grain"></div>
<div class="side-bar"></div>
{corpo}
<div class="logo-fixo">КЯАТА.</div>
</body>
</html>"""


# ── RENDER PNG ──────────────────────────────────────────────────────
def html_para_png(html_path: str, png_path: str):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1080})
        page.goto(f"file://{html_path}")
        page.wait_for_timeout(2500)  # aguarda fontes do Google Fonts
        page.screenshot(path=png_path, full_page=False)
        browser.close()


# ── MAIN ────────────────────────────────────────────────────────────
def main():
    payload = json.loads(sys.stdin.read())
    # payload: {"titulo": str, "slides": [...], "subtema": str, "hashtags": [...]}
    slides  = payload["slides"]
    total   = len(slides)
    subtema = payload.get("subtema", "КЯАТА.")

    hoje    = datetime.now().strftime("%Y-%m-%d")
    slug    = payload.get("slug", "carrossel")
    pasta   = Path(f"/Users/victormandarino/projetos/krata/content-team/output/{hoje}/{slug}")
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "html").mkdir(exist_ok=True)

    arquivos_png = []

    for slide in slides:
        num = slide["numero"]
        slide["subtema"] = subtema
        print(f"  [{num:02d}/{total}] {slide.get('titulo', '')}", file=sys.stderr)

        img_path = pasta / f"img_{num:02d}.jpg"
        try:
            baixar_imagem(slide.get("query_imagem", "dark abstract minimal"), img_path)
        except Exception as e:
            print(f"    ⚠ imagem: {e}", file=sys.stderr)

        html_content = gerar_html(slide, total, img_path)
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
