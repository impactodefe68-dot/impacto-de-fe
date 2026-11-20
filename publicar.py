#!/usr/bin/env python3
"""Agente diario 'De regreso a casa' — publica en Instagram, TikTok y X.

Cada publicación es un carrusel de 2 imágenes:
  1) el problema (con flecha 'dale a la otra →')
  2) la respuesta (con el versículo)

Lee publicaciones.json, elige la siguiente según estado.json,
la publica en cada red (si tiene sus secretos configurados) y avanza el índice.
"""
import json
import os
import subprocess
import sys
import time

import requests

BASE = os.path.dirname(os.path.abspath(__file__))
OWNER = os.environ.get("REPO_OWNER", "impactodefe68-dot")
REPO = os.environ.get("REPO_NAME", "impacto-de-fe")
BRANCH = "main"


def cargar_json(nombre, defecto):
    try:
        with open(os.path.join(BASE, nombre), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return defecto


def guardar_json(nombre, datos):
    with open(os.path.join(BASE, nombre), "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


def url_cruda(ruta):
    return f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}/{ruta}"


# ---------------- Instagram (Meta Graph API, carrusel) ----------------
def publicar_instagram(rutas_img, caption):
    ig_id = os.environ["IG_USER_ID"]
    token = os.environ["IG_ACCESS_TOKEN"]
    children = []
    for ruta in rutas_img:
        r = requests.post(
            f"https://graph.facebook.com/v21.0/{ig_id}/media",
            data={"image_url": url_cruda(ruta), "media_type": "IMAGE", "access_token": token},
            timeout=90,
        )
        r.raise_for_status()
        children.append(r.json()["id"])
        time.sleep(3)
    r = requests.post(
        f"https://graph.facebook.com/v21.0/{ig_id}/media",
        data={
            "media_type": "CAROUSEL",
            "children": ",".join(children),
            "caption": caption,
            "access_token": token,
        },
        timeout=90,
    )
    r.raise_for_status()
    cid = r.json()["id"]
    r2 = requests.post(
        f"https://graph.facebook.com/v21.0/{ig_id}/media_publish",
        data={"creation_id": cid, "access_token": token},
        timeout=90,
    )
    r2.raise_for_status()
    return r2.json().get("id", "ok")


# ---------------- X (Twitter, 2 imágenes) ----------------
def publicar_x(rutas_img, texto):
    from requests_oauthlib import OAuth1Session

    oauth = OAuth1Session(
        os.environ["X_API_KEY"],
        os.environ["X_API_SECRET"],
        os.environ["X_ACCESS_TOKEN"],
        os.environ["X_ACCESS_SECRET"],
    )
    media_ids = []
    for ruta in rutas_img:
        with open(os.path.join(BASE, ruta), "rb") as f:
            r = oauth.post(
                "https://upload.twitter.com/1.1/media/upload.json",
                files={"media": f},
                timeout=120,
            )
        r.raise_for_status()
        media_ids.append(r.json()["media_id_string"])
    r2 = oauth.post(
        "https://api.twitter.com/2/tweets",
        json={"text": texto[:280], "media": {"media_ids": media_ids}},
        timeout=60,
    )
    r2.raise_for_status()
    return r2.json()["data"]["id"]


# ---------------- TikTok (Content Posting API, video de las 2 imágenes) ----------------
def publicar_tiktok(rutas_img, titulo):
    token = os.environ["TIKTOK_ACCESS_TOKEN"]
    mp4 = "/tmp/de-regreso-casa.mp4"
    entradas = []
    for ruta in rutas_img:
        entradas += ["-loop", "1", "-i", os.path.join(BASE, ruta)]
    n = len(rutas_img)
    dur = 5 / n
    filtros = []
    for i in range(n):
        filtros.append(
            f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            f"trim=duration={dur},setpts=PTS-STARTPTS[v{i}]"
        )
    filtros.append("".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[v]")
    subprocess.run(
        ["ffmpeg", "-y", *entradas, "-filter_complex", ";".join(filtros),
         "-map", "[v]", "-r", "30", "-c:v", "libx264", "-pix_fmt", "yuv420p", mp4],
        check=True,
        capture_output=True,
    )
    size = os.path.getsize(mp4)
    chunk = 5 * 1024 * 1024 if size >= 5 * 1024 * 1024 else size
    total = (size + chunk - 1) // chunk
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=UTF-8",
    }
    r = requests.post(
        "https://open.tiktokapis.com/v2/post/publish/video/init/",
        headers=headers,
        json={
            "post_info": {
                "title": titulo[:150],
                "privacy_level": os.environ.get("TIKTOK_PRIVACY", "PUBLIC_TO_EVERYONE"),
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": size,
                "chunk_size": chunk,
                "total_chunk_count": total,
            },
        },
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()["data"]
    upload_url = data["upload_url"]
    publish_id = data.get("publish_id")
    with open(mp4, "rb") as f:
        for i in range(total):
            start = i * chunk
            end = min(start + chunk, size) - 1
            f.seek(start)
            piece = f.read(end - start + 1)
            rr = requests.put(
                upload_url,
                data=piece,
                headers={
                    "Content-Range": f"bytes {start}-{end}/{size}",
                    "Content-Length": str(len(piece)),
                },
                timeout=300,
            )
            rr.raise_for_status()
    for _ in range(6):
        time.sleep(10)
        rs = requests.post(
            "https://open.tiktokapis.com/v2/post/publish/status/fetch/",
            headers=headers,
            json={"publish_id": publish_id},
            timeout=60,
        )
        if rs.ok:
            st = rs.json().get("data", {}).get("status")
            if st == "PUBLISH_COMPLETE":
                return publish_id
            if st == "FAILED":
                raise RuntimeError("TikTok reportó FAILED")
    return publish_id or "subido"


def main():
    pubs = cargar_json("publicaciones.json", [])
    if not pubs:
        print("No hay publicaciones en publicaciones.json")
        sys.exit(1)
    estado = cargar_json("estado.json", {"indice": 0})
    i = estado.get("indice", 0) % len(pubs)
    p = pubs[i]
    print(f"Publicando #{i + 1}: {p['titulo']}")
    ok = []
    if os.environ.get("IG_USER_ID") and os.environ.get("IG_ACCESS_TOKEN"):
        try:
            publicar_instagram(p["imagenes"], p["caption"])
            ok.append("Instagram")
            print("✔ Instagram")
        except Exception as e:
            print(f"✘ Instagram: {e}")
    if os.environ.get("X_API_KEY"):
        try:
            publicar_x(p["imagenes"], p.get("x") or p["caption"])
            ok.append("X")
            print("✔ X")
        except Exception as e:
            print(f"✘ X: {e}")
    if os.environ.get("TIKTOK_ACCESS_TOKEN"):
        try:
            publicar_tiktok(p["imagenes_tiktok"], p["caption"])
            ok.append("TikTok")
            print("✔ TikTok")
        except Exception as e:
            print(f"✘ TikTok: {e}")
    if not ok:
        print("No se publicó en ninguna red; no se avanzará la publicación.")
        sys.exit(1)
    estado["indice"] = i + 1
    guardar_json("estado.json", estado)
    print(f"Listo. Publicadas: {', '.join(ok) or 'ninguna'}")


if __name__ == "__main__":
    main()
