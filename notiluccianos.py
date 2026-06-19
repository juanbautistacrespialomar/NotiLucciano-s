# -*- coding: utf-8 -*-
"""
NotiLucciano's - el "diario" de joda de la oficina.
Manda por mail: NotiLucciano's (noticias truchas) + clima + futbol del Mundial
+ cancion al azar de Spotify. Se dispara A MANO desde GitHub Actions (Run workflow).
No usa IA ni feeds de noticias: es todo de joda.
"""

import os
import sys
import base64
import random
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import requests

# =====================================================================
# CONFIGURACION
# =====================================================================

# ----- NotiLucciano's (las noticias de joda; las editamos cada viernes) -----
# Cada item es (VOLANTA, TITULAR, BAJADA).
MOSTRAR_NOTILUCCIANOS = True
# Cada item es (VOLANTA, TITULAR, BAJADA, FOTO).
# FOTO es opcional: pone la URL de una imagen, o dejala como "" si no queres foto.
NOTILUCCIANOS = [
    ("\u00a1EXCLUSIVO!",
     "AC\u00c1 VAN LOS TITULARES DE LA SEMANA",
     "Reemplazar por las noticias reales. Cada una es (volanta, titular, bajada, foto).",
     ""),
]

# ----- Clima (Mar del Plata) -----
CLIMA_LAT = -38.0055
CLIMA_LON = -57.5426
CLIMA_CIUDAD = "Mar del Plata"

# ----- Futbol (Mundial, Promiedos) -----
# El script consulta TODAS las URLs y junta los partidos. Si avanza la ronda y
# deja de traer partidos, agregar la URL nueva (del Network de Promiedos).
MOSTRAR_FUTBOL = True
FUTBOL_HASTA = "2026-07-19"
PROMIEDOS_URLS = [
    "https://api.promiedos.com.ar/league/games/fjda/5930_25_1_1",  # Fecha 1
    "https://api.promiedos.com.ar/league/games/fjda/5930_25_1_2",  # Fecha 2
    "https://api.promiedos.com.ar/league/games/fjda/5930_25_1_3",  # Fecha 3 (trae hasta la final)
]

# Pais (url_name de Promiedos) -> codigo ISO-2, para la bandera.
_PAIS_ISO = {
    "mexico": "MX", "south-africa": "ZA", "south-korea": "KR", "czech-republic": "CZ",
    "canada": "CA", "bosnia-&-herzegovina": "BA", "usa": "US", "paraguay": "PY",
    "qatar": "QA", "switzerland": "CH", "brazil": "BR", "morocco": "MA", "haiti": "HT",
    "australia": "AU", "turkiye": "TR", "germany": "DE", "curacao": "CW",
    "netherlands": "NL", "japan": "JP", "ivory-coast": "CI", "ecuador": "EC",
    "sweden": "SE", "tunisia": "TN", "spain": "ES", "cape-verde": "CV", "belgium": "BE",
    "egypt": "EG", "saudi-arabia": "SA", "uruguay": "UY", "iran": "IR",
    "new-zealand": "NZ", "france": "FR", "senegal": "SN", "iraq": "IQ", "norway": "NO",
    "argentina": "AR", "algeria": "DZ", "austria": "AT", "jordan": "JO",
    "portugal": "PT", "dr-congo": "CD", "croatia": "HR", "ghana": "GH", "panama": "PA",
    "uzbekistan": "UZ", "colombia": "CO", "italy": "IT", "denmark": "DK", "poland": "PL",
    "nigeria": "NG", "cameroon": "CM",
}

# ----- Frase de la semana -----
# Frases reales y celebres de figuras del espectaculo/deporte argentino.
# Cada corrida elige una al azar. Cada item es (FRASE, AUTOR). Sumá las que quieras.
MOSTRAR_FRASE = True
FRASES = [
    # --- Diego Maradona ---
    ("La pelota no se mancha", "Diego Maradona"),
    ("Me cortaron las piernas", "Diego Maradona"),
    ("Fue la mano de Dios", "Diego Maradona"),
    ("Se le escap\u00f3 la tortuga", "Diego Maradona"),
    ("Ganarle a River es como que tu mam\u00e1 te despierte con un beso", "Diego Maradona"),
    ("Te lo digo a vos, Segurola y Habana, and\u00e1 a buscarlo", "Diego Maradona"),
    ("Tengo menos piernas que una foto carnet", "Diego Maradona"),
    ("M\u00e1s falso que d\u00f3lar celeste", "Diego Maradona"),
    ("L\u00e1stima no se le tiene a nadie, maestro", "Diego Maradona"),
    ("Tengo dos sue\u00f1os: jugar un Mundial y salir campe\u00f3n", "Diego Maradona"),
    ("Si voy al banco es para sacar plata, fiera", "Diego Maradona"),
    # --- Moria Cas\u00e1n ---
    ("\u00bfQui\u00e9nes son?", "Moria Cas\u00e1n"),
    ("Si quer\u00e9s llorar, llor\u00e1", "Moria Cas\u00e1n"),
    ("Sos un helado de pollo, no exist\u00eds", "Moria Cas\u00e1n"),
    ("A llorar al campito", "Moria Cas\u00e1n"),
    ("\u00a1Se calla el decorado!", "Moria Cas\u00e1n"),
    # --- Mirtha Legrand ---
    ("Como te ven, te tratan", "Mirtha Legrand"),
    ("Les he dado mi vida", "Mirtha Legrand"),
    ("\u00a1Qu\u00e9 mesaza!", "Mirtha Legrand"),
    # --- Ricardo Fort ---
    ("\u00a1Mam\u00e1, cortaste toda la looz!", "Ricardo Fort"),
    ("Yo no manejo el rating, yo manejo un Rolls Royce", "Ricardo Fort"),
    ("Yendo o llendo, da igual: voy arriba de mi Rolls Royce", "Ricardo Fort"),
    ("\u00a1Mam\u00e1, metiste el cutucuchillo!", "Ricardo Fort"),
    # --- Susana Gim\u00e9nez ---
    ("Un dinosaurio\u2026 \u00bfvivo?", "Susana Gim\u00e9nez"),
    ("\u00a1Se acab\u00f3, de ahora en m\u00e1s voy a cumplir 69!", "Susana Gim\u00e9nez"),
    # --- Espect\u00e1culo / humor ---
    ("\u00bfQu\u00e9 pretende usted de m\u00ed?", "Isabel Sarli"),
    ("\u00a1Hay que caminar chicas, hay que caminar!", "Lita de Lazzari"),
    ("Che Pedro, mir\u00e1 qui\u00e9n vino. No va andar", "Juan Carlos Calabr\u00f3"),
    ("Vermouth con papas fritas y\u2026 good show", "Tato Bores"),
    ("Si te gusta el durazno, bancate la pelusa", "Florencia de la V"),
    ("\u00a1Vos fum\u00e1!", "Carl\u00edn Calvo"),
    ("Billetera mata gal\u00e1n", "Jacobo Winograd"),
    ("No me peguen, soy Giordano", "Roberto Giordano"),
    ("Muchacha, hacete el papanicolau", "Tita Merello"),
    ("Qu\u00e9 pa\u00eds generoso", "Jorge Rial"),
    ("Estoy comprometido con mi tierra, casado con los problemas y divorciado de sus riquezas", "Inodoro Pereyra (Fontanarrosa)"),
    ("Parece que quieren hacer bowling conmigo", "Vicky Xipolitakis"),
    ("\u00bfQui\u00e9n sos? \u00a1Ubicate, pendejo!", "Nacha Guevara"),
    # --- Deporte ---
    ("Me gusta tanto la noche que al d\u00eda le pondr\u00eda un toldo", "Bambino Veira"),
    ("Pusimos un micro en el arco y entr\u00f3 por la ventanilla", "Bambino Veira"),
    ("\u00a1Por lo menos as\u00ed lo veo yo!", "Guillermo Nimo"),
    ("En la altura la pelota no dobla", "Daniel Passarella"),
    ("\u00bfEst\u00e1 crazy, Macaya?", "Marcelo Araujo"),
    ("La experiencia es un peine que te regalan cuando te qued\u00e1s pelado", "Ringo Bonavena"),
    ("\u00bfCu\u00e1ntos pulmones tengo? Uno, como todo el mundo", "Mostaza Merlo"),
    # --- M\u00fasica ---
    ("Yo no me gan\u00e9 la loter\u00eda, la hice laburando", "Pablo Lescano"),
    # --- Pol\u00edtica (frases hist\u00f3ricas del folclore) ---
    ("S\u00edganme, no los voy a defraudar", "Carlos Menem"),
    ("La casa est\u00e1 en orden", "Ra\u00fal Alfons\u00edn"),
    ("Soy lo mejor que le puede pasar al pa\u00eds", "Fernando de la R\u00faa"),
    ("El que deposit\u00f3 d\u00f3lares recibir\u00e1 d\u00f3lares", "Eduardo Duhalde"),
    ("Hacia fin de siglo la deuda externa ser\u00e1 insignificante", "Domingo Cavallo"),
]

# ----- Cancion (Spotify) -----
# Cada corrida elige UN artista al azar de esta lista y de ahi un tema al azar
# de su catalogo real. Edita la lista con los artistas que quieras.
ARTISTAS = [
    "Ariana Grande", "Tan Bionica", "Airbag", "Tini",
    "One Direction", "Taylor Swift", "Justin Bieber", "Shakira",
]

# ----- Colores -----
COLOR_HEADER  = "#0b3d6b"
COLOR_SECCION = "#1565c0"
COLOR_TEXTO   = "#333333"
COLOR_FONDO   = "#eef3f8"
COLOR_CAJA    = "#e6f1fb"

# Codigos de clima (WMO) -> (emoji, descripcion).
WMO = {
    0: ("\u2600\uFE0F", "Despejado"), 1: ("\U0001F324\uFE0F", "Mayormente despejado"),
    2: ("\u26C5", "Parcialmente nublado"), 3: ("\u2601\uFE0F", "Nublado"),
    45: ("\U0001F32B\uFE0F", "Niebla"), 48: ("\U0001F32B\uFE0F", "Niebla"),
    51: ("\U0001F326\uFE0F", "Llovizna"), 53: ("\U0001F326\uFE0F", "Llovizna"), 55: ("\U0001F326\uFE0F", "Llovizna"),
    61: ("\U0001F327\uFE0F", "Lluvia"), 63: ("\U0001F327\uFE0F", "Lluvia"), 65: ("\U0001F327\uFE0F", "Lluvia fuerte"),
    71: ("\U0001F328\uFE0F", "Nieve"), 73: ("\U0001F328\uFE0F", "Nieve"), 75: ("\U0001F328\uFE0F", "Nieve"),
    80: ("\U0001F326\uFE0F", "Chaparrones"), 81: ("\U0001F326\uFE0F", "Chaparrones"), 82: ("\U0001F327\uFE0F", "Chaparrones fuertes"),
    95: ("\u26C8\uFE0F", "Tormenta"), 96: ("\u26C8\uFE0F", "Tormenta"), 99: ("\u26C8\uFE0F", "Tormenta"),
}

# =====================================================================
# SECRETOS (vienen de los GitHub Secrets)
# =====================================================================

GMAIL_USER         = os.environ.get("GMAIL_USER")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
MAIL_TO            = os.environ.get("MAIL_TO", GMAIL_USER)
SPOTIFY_CLIENT_ID     = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")


def faltan_secretos():
    return [n for n, v in [
        ("GMAIL_USER", GMAIL_USER), ("GMAIL_APP_PASSWORD", GMAIL_APP_PASSWORD),
    ] if not v]


# =====================================================================
# HELPERS
# =====================================================================

def _bandera(url_name):
    """Imagen de bandera (flagcdn.com). Imagen y no emoji porque Windows no
    renderiza los emojis de bandera (los muestra como las 2 letras)."""
    especiales = {"england": "gb-eng", "scotland": "gb-sct", "wales": "gb-wls"}
    cod = especiales.get(url_name) or _PAIS_ISO.get(url_name, "").lower()
    if not cod:
        return ""
    return (f'<img src="https://flagcdn.com/w40/{cod}.png" width="24" height="16" '
            f'style="vertical-align:middle; border-radius:2px; '
            f'object-fit:cover; border:1px solid #e0e0e0;" alt="">')


# =====================================================================
# DATOS
# =====================================================================

def obtener_clima():
    try:
        url = ("https://api.open-meteo.com/v1/forecast"
               f"?latitude={CLIMA_LAT}&longitude={CLIMA_LON}"
               "&current=temperature_2m,weather_code"
               "&daily=temperature_2m_max,temperature_2m_min"
               "&timezone=America/Argentina/Buenos_Aires")
        r = requests.get(url, timeout=12)
        if r.ok:
            d = r.json()
            actual = d.get("current", {})
            diaria = d.get("daily", {})
            maxs = diaria.get("temperature_2m_max") or [None]
            mins = diaria.get("temperature_2m_min") or [None]
            return {"temp": actual.get("temperature_2m"), "codigo": actual.get("weather_code"),
                    "max": maxs[0], "min": mins[0]}
    except Exception as e:
        print(f"[AVISO] No pude traer el clima: {e}")
    return None


def _spotify_token():
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        return None
    try:
        auth = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
        r = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth}",
                     "Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "client_credentials"}, timeout=12)
        if r.ok:
            return r.json().get("access_token")
        print(f"[AVISO] Spotify token devolvio {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"[AVISO] No pude obtener token de Spotify: {e}")
    return None


def _spotify_get(url, token, params=None):
    try:
        r = requests.get(url, headers={"Authorization": f"Bearer {token}"}, params=params, timeout=12)
        if r.ok:
            return r.json()
        print(f"[AVISO] Spotify GET {url.split('/')[-1]} devolvio {r.status_code}: {r.text[:150]}")
        return None
    except Exception as e:
        print(f"[AVISO] Spotify GET fallo ({url}): {e}")
        return None


def obtener_cancion():
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        print("[AVISO] Faltan credenciales de Spotify. No muestro cancion.")
        return None

    artista = random.choice(ARTISTAS)  # uno distinto cada corrida
    rng = random.Random()

    token = _spotify_token()
    if not token:
        print("[AVISO] Spotify no devolvio token (revisar credenciales). No muestro cancion.")
        return None

    try:
        bus = _spotify_get("https://api.spotify.com/v1/search", token,
                           {"q": artista, "type": "artist", "limit": 1, "market": "AR"})
        items = (bus or {}).get("artists", {}).get("items", [])
        if not items:
            print(f"[AVISO] No encontre al artista '{artista}' en Spotify.")
            return None
        artista_id = items[0]["id"]
        artista_nombre = items[0].get("name", artista)

        albs = _spotify_get(f"https://api.spotify.com/v1/artists/{artista_id}/albums", token,
                            {"market": "AR", "include_groups": "album", "limit": 10})
        albumes = (albs or {}).get("items", [])
        if not albumes:
            print(f"[AVISO] '{artista_nombre}' no devolvio albumes.")
            return None
        album = rng.choice(albumes)
        imgs = album.get("images", [])
        portada = imgs[0]["url"] if imgs else ""

        trks = _spotify_get(f"https://api.spotify.com/v1/albums/{album['id']}/tracks", token,
                            {"market": "AR", "limit": 10})
        tracks = (trks or {}).get("items", [])
        if not tracks:
            print(f"[AVISO] El album elegido de '{artista_nombre}' no devolvio temas.")
            return None
        t = rng.choice(tracks)

        print(f"[INFO] Cancion: '{t.get('name')}' - {artista_nombre}")
        return {
            "titulo": t.get("name", ""),
            "artista": artista_nombre,
            "link": t.get("external_urls", {}).get("spotify", ""),
            "portada": portada,
        }
    except Exception as e:
        print(f"[AVISO] No pude obtener la cancion de Spotify: {e}")
        return None


def obtener_futbol():
    hoy = datetime.now(timezone(timedelta(hours=-3)))
    if not MOSTRAR_FUTBOL or hoy.strftime("%Y-%m-%d") > FUTBOL_HASTA:
        return []

    games = []
    vistos = set()
    for url in PROMIEDOS_URLS:
        if not url or url.startswith("PEGAR"):
            continue
        try:
            r = requests.get(url, timeout=12)
            if not r.ok:
                print(f"[AVISO] Promiedos devolvio HTTP {r.status_code} en una URL.")
                continue
            for g in r.json().get("games", []):
                clave = g.get("id") or (g.get("url_name", "") + g.get("start_time", ""))
                if clave in vistos:
                    continue
                vistos.add(clave)
                games.append(g)
        except Exception as e:
            print(f"[AVISO] No pude traer el futbol de una URL: {e}")
            continue

    ahora = hoy.replace(tzinfo=None)
    desde = (ahora - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

    partidos = []
    for g in games:
        try:
            cuando = datetime.strptime(g.get("start_time", ""), "%d-%m-%Y %H:%M")
        except ValueError:
            continue
        if not (desde <= cuando <= ahora):
            continue
        teams = g.get("teams", [])
        scores = g.get("scores", [])
        if len(teams) < 2 or len(scores) < 2:
            continue
        partidos.append({
            "local": teams[0].get("name", ""),
            "visitante": teams[1].get("name", ""),
            "bandera_local": _bandera(teams[0].get("url_name", "")),
            "bandera_visitante": _bandera(teams[1].get("url_name", "")),
            "gl": int(scores[0]), "gv": int(scores[1]),
            "fin": g.get("status", {}).get("enum") == 3,
            "estado": g.get("status", {}).get("short_name", ""),
        })
    print(f"[INFO] Futbol: {len(partidos)} partidos en la ventana.")
    return partidos


# =====================================================================
# ARMADO DEL HTML
# =====================================================================

def _caja_notiluccianos():
    if not MOSTRAR_NOTILUCCIANOS or not NOTILUCCIANOS:
        return ""
    ROJO = "#d50000"
    AMARILLO = "#ffd600"
    NEGRO = "#0a0a0a"

    notas = ""
    for nota in NOTILUCCIANOS:
        volanta, titular, bajada = nota[0], nota[1], nota[2]
        foto = nota[3] if len(nota) > 3 else ""
        img_html = ""
        if foto:
            img_html = (f'<img src="{foto}" width="100%" '
                        f'style="display:block; max-height:240px; object-fit:cover; '
                        f'margin-top:10px; border-radius:4px;" alt="">')
        notas += (
            f'<div style="background:#ffffff; border-bottom:3px solid {NEGRO}; padding:13px 16px;">'
            f'<span style="display:inline-block; background:{ROJO}; color:#ffffff; font-size:11px; '
            f'font-weight:bold; padding:2px 8px; border-radius:3px; text-transform:uppercase; '
            f'letter-spacing:0.5px;">{volanta}</span>'
            f'<div style="color:{NEGRO}; font-size:20px; font-weight:900; line-height:1.15; '
            f'margin-top:7px; text-transform:uppercase;">{titular}</div>'
            f'<div style="color:#444444; font-size:13px; line-height:1.45; margin-top:5px; '
            f'font-style:italic;">{bajada}</div>'
            f'{img_html}</div>'
        )

    return (
        f'<div style="margin-bottom:26px; border:4px solid {NEGRO}; border-radius:6px; overflow:hidden;">'
        f'<div style="background:{ROJO}; padding:12px 16px; text-align:center;">'
        f'<div style="color:{AMARILLO}; font-size:30px; font-weight:900; letter-spacing:1px; '
        f'text-shadow:2px 2px 0 {NEGRO};">NOTILUCCIANO\u2019S</div>'
        f'<div style="color:#ffffff; font-size:11px; font-weight:bold; letter-spacing:3px; '
        f'text-transform:uppercase; margin-top:2px;">La verdad que nadie se anima a contar</div>'
        f'</div>'
        f'<div style="background:{AMARILLO}; color:{NEGRO}; font-size:12px; font-weight:900; '
        f'text-align:center; padding:5px; letter-spacing:2px; text-transform:uppercase;">'
        f'\u25cf En vivo \u00b7 Edici\u00f3n especial \u00b7 No apto para cr\u00e9dulos \u25cf</div>'
        f'{notas}'
        f'</div>'
    )


def _caja_clima(clima):
    if not clima or clima.get("temp") is None:
        return ""
    emoji, desc = WMO.get(clima.get("codigo"), ("\U0001F324\uFE0F", ""))
    temp = round(clima["temp"])
    mn = round(clima["min"]) if clima.get("min") is not None else None
    mx = round(clima["max"]) if clima.get("max") is not None else None
    rango = f" &nbsp;&middot;&nbsp; m\u00edn {mn}\u00b0 / m\u00e1x {mx}\u00b0" if mn is not None and mx is not None else ""
    return (f'<div style="background:{COLOR_CAJA}; border-radius:8px; padding:11px 16px; '
            f'margin-bottom:24px; color:{COLOR_HEADER}; font-size:14px;">'
            f'<span style="font-size:17px; vertical-align:middle;">{emoji}</span>&nbsp; '
            f'<span style="font-weight:bold;">{CLIMA_CIUDAD}</span> &nbsp; {temp}\u00b0 '
            f'<span style="color:#5a7a99;">{desc}{rango}</span></div>')


def _caja_futbol(partidos):
    if not partidos:
        return ""
    filas = ""
    for p in partidos:
        marcador = f"{p['gl']} - {p['gv']}" if p["fin"] else f"{p['gl']} - {p['gv']} ({p['estado']})"
        filas += (
            f'<tr>'
            f'<td style="padding:7px 6px; text-align:right; font-size:14px; color:{COLOR_TEXTO}; width:42%;">'
            f'{p["local"]} &nbsp; {p["bandera_local"]}</td>'
            f'<td style="padding:7px 4px; text-align:center; font-size:15px; font-weight:bold; color:{COLOR_HEADER}; width:16%;">{marcador}</td>'
            f'<td style="padding:7px 6px; text-align:left; font-size:14px; color:{COLOR_TEXTO}; width:42%;">'
            f'{p["bandera_visitante"]} &nbsp; {p["visitante"]}</td>'
            f'</tr>'
        )
    return (
        f'<div style="margin-bottom:26px;">'
        f'<div style="background:{COLOR_SECCION}; color:#ffffff; font-size:15px; font-weight:bold; '
        f'padding:9px 14px; border-radius:6px;">\u26BD&nbsp; F\u00fatbol &middot; Mundial</div>'
        f'<table width="100%" cellpadding="0" cellspacing="0" style="margin-top:10px;">{filas}</table>'
        f'</div>'
    )


def _caja_frase(frase):
    if not frase:
        return ""
    texto, autor = frase
    return (
        f'<div style="margin-bottom:26px;">'
        f'<div style="background:{COLOR_SECCION}; color:#ffffff; font-size:15px; font-weight:bold; '
        f'padding:9px 14px; border-radius:6px;">\U0001F4AC&nbsp; Frase de la semana</div>'
        f'<div style="background:{COLOR_CAJA}; border-left:5px solid {COLOR_SECCION}; '
        f'border-radius:4px; padding:18px 22px; margin-top:10px;">'
        f'<div style="font-size:19px; font-style:italic; color:{COLOR_HEADER}; line-height:1.4;">'
        f'\u201c{texto}\u201d</div>'
        f'<div style="font-size:13px; font-weight:bold; color:#5a7a99; margin-top:11px;">'
        f'\u2014 {autor}</div>'
        f'</div></div>'
    )


def _caja_cancion(cancion):
    if not cancion:
        return ""
    titulo = cancion.get("titulo", "")
    artista = cancion.get("artista", "")
    link = cancion.get("link", "")
    portada = cancion.get("portada", "")
    VERDE = "#1DB954"
    NEGRO = "#121212"

    celda_img = ""
    if portada:
        celda_img = (f'<td style="width:88px; vertical-align:middle; padding-right:16px;">'
                     f'<img src="{portada}" width="88" height="88" style="border-radius:6px; display:block;" alt=""></td>')
    boton = ""
    if link:
        boton = (f'<a href="{link}" style="display:inline-block; background:{VERDE}; color:#000000; '
                 f'font-size:13px; font-weight:bold; text-decoration:none; padding:9px 22px; '
                 f'border-radius:500px; margin-top:11px;">\u25B6&nbsp; Escuchar ahora</a>')
    marca = (f'<div style="margin-bottom:13px;">'
             f'<span style="display:inline-block; width:13px; height:13px; background:{VERDE}; '
             f'border-radius:50%; vertical-align:middle;"></span>'
             f'<span style="color:{VERDE}; font-size:13px; font-weight:bold; letter-spacing:0.3px; vertical-align:middle;">&nbsp; Spotify</span>'
             f'<span style="color:#b3b3b3; font-size:11px; text-transform:uppercase; letter-spacing:1px; vertical-align:middle;">'
             f'&nbsp;&middot;&nbsp; Canci&oacute;n de la semana</span></div>')
    return (f'<div style="background:{NEGRO}; border-radius:10px; padding:18px 20px; margin-bottom:10px;">'
            f'{marca}'
            f'<table cellpadding="0" cellspacing="0" style="width:100%;"><tr>{celda_img}'
            f'<td style="vertical-align:middle;">'
            f'<div style="color:#ffffff; font-size:17px; font-weight:bold;">{titulo}</div>'
            f'<div style="color:#b3b3b3; font-size:14px; margin-top:3px;">{artista}</div>'
            f'{boton}</td></tr></table></div>')


def _fecha_en_espanol():
    """Fecha en castellano, sin depender del idioma del servidor (GitHub esta en ingles)."""
    dias = ["Lunes", "Martes", "Mi\u00e9rcoles", "Jueves", "Viernes", "S\u00e1bado", "Domingo"]
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
             "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    ahora = datetime.now(timezone(timedelta(hours=-3)))
    return f"{dias[ahora.weekday()]} {ahora.day} de {meses[ahora.month - 1]} de {ahora.year}"


def armar_html(clima, partidos, frase, cancion):
    fecha_hoy = _fecha_en_espanol()
    es_viernes = datetime.now(timezone(timedelta(hours=-3))).weekday() == 4
    # Bombo solo los viernes; el resto de los dias, un saludo normal.
    if es_viernes:
        bombo = ('<div style="font-size:15px; font-weight:bold; color:#ffd600; margin-top:8px;">'
                 '\U0001F37A\U0001F1E6\U0001F1F7 \u00a1VIERNES QUE TE QUIERO VIERNES! \U0001F1E6\U0001F1F7\U0001F37A</div>')
    else:
        bombo = ''
    return f"""<!DOCTYPE html>
<html><body style="margin:0; padding:0; background:{COLOR_FONDO};">
  <div style="max-width:640px; margin:0 auto; background:#ffffff; font-family:Arial,Helvetica,sans-serif;">
    <div style="background:{COLOR_HEADER}; color:#ffffff; padding:20px 28px;">
      <div style="font-size:22px; font-weight:bold;">NotiLucciano\u2019s</div>
      <div style="font-size:13px; color:#bcd4ec; margin-top:3px;">{fecha_hoy}</div>
      {bombo}
    </div>
    <div style="padding:24px 28px 6px;">
      {_caja_notiluccianos()}
      {_caja_clima(clima)}
      {_caja_futbol(partidos)}
      {_caja_frase(frase)}
      {_caja_cancion(cancion)}
    </div>
    <div style="padding:14px 28px 24px; color:#9aa7b4; font-size:11px;">
      NotiLucciano\u2019s &mdash; toda la informaci\u00f3n que no necesit\u00e1s, y un poco m\u00e1s.
    </div>
  </div>
</body></html>"""


def enviar_mail(cuerpo_html):
    fecha_hoy = datetime.now(timezone(timedelta(hours=-3))).strftime("%d/%m/%Y")
    mensaje = MIMEMultipart("alternative")
    mensaje["Subject"] = f"NotiLucciano's - {fecha_hoy}"
    mensaje["From"] = GMAIL_USER
    mensaje["To"] = MAIL_TO
    mensaje.attach(MIMEText(cuerpo_html, "html", "utf-8"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
        servidor.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        servidor.sendmail(GMAIL_USER, MAIL_TO.split(","), mensaje.as_string())
    print(f"[OK] Mail enviado a {MAIL_TO}.")


# =====================================================================
# MAIN
# =====================================================================

def main():
    print("[INFO] ====== NotiLucciano's ======")
    faltantes = faltan_secretos()
    if faltantes:
        print(f"[ERROR] Faltan estas variables de entorno: {', '.join(faltantes)}")
        sys.exit(1)
    clima = obtener_clima()
    partidos = obtener_futbol()
    cancion = obtener_cancion()
    frase = random.choice(FRASES) if (MOSTRAR_FRASE and FRASES) else None
    html = armar_html(clima, partidos, frase, cancion)
    enviar_mail(html)


if __name__ == "__main__":
    main()
