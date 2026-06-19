# NotiLucciano's

El "diario" de joda de la oficina. Manda por mail, **a mano** cuando vos quieras:

1. **NotiLucciano's** — las noticias truchas (las editamos cada vez).
2. **Clima** de Mar del Plata.
3. **Fútbol** — resultados del Mundial del día anterior.
4. **Canción** — un tema al azar de Spotify (artista distinto cada vez).

No usa IA ni feeds de noticias. Corre en **GitHub Actions**, disparado a mano
desde el botón "Run workflow".

---

## Estructura del repo

```
notiluccianos/
├── notiluccianos.py            <- el script
├── requirements.txt            <- una sola libreria (requests)
├── README.md                   <- esto
└── .github/
    └── workflows/
        └── notiluccianos.yml    <- el workflow (disparo manual)
```

El `.yml` TIENE que estar en `.github/workflows/`.

---

## Puesta en marcha (cuenta y Gmail nuevos)

### 1. Crear el repo
En la cuenta nueva de GitHub, creá un repo (privado está bien) y subí los 4
archivos respetando la estructura de carpetas.

### 2. Contraseña de aplicación de Gmail (cuenta nueva)
1. Activá la verificación en 2 pasos en la cuenta de Google nueva.
2. Andá a https://myaccount.google.com/apppasswords
3. Creá una contraseña de aplicación. Te da 16 caracteres: copialos.

### 3. App de Spotify
Podés reusar las credenciales de Spotify del otro proyecto, o crear una app
nueva en https://developer.spotify.com/dashboard y copiar el Client ID y el
Client Secret.

### 4. Cargar los Secrets
En el repo: **Settings → Secrets and variables → Actions → New repository secret**.
Creá estos:

| Nombre                    | Valor                                          |
|---------------------------|------------------------------------------------|
| `GMAIL_USER`              | la casilla nueva, ej: `notiluccianos@gmail.com`|
| `GMAIL_APP_PASSWORD`      | los 16 caracteres del paso 2                   |
| `MAIL_TO`                 | destinatarios separados por coma, sin espacios |
| `SPOTIFY_CLIENT_ID`       | Client ID de la app de Spotify                 |
| `SPOTIFY_CLIENT_SECRET`   | Client Secret de la app de Spotify             |

No necesita Gemini (este mail no usa IA).

### 5. Ejecutarlo
Cada vez que quieras mandarlo: pestaña **Actions** → "NotiLucciano's" →
botón **Run workflow** → Run. En un par de minutos llega el mail.

---

## Cómo editar las noticias

En `notiluccianos.py`, arriba, está la lista `NOTILUCCIANOS`. Cada noticia es
una tripleta `(VOLANTA, TITULAR, BAJADA)`:

```python
NOTILUCCIANOS = [
    ("¡EXCLUSIVO!", "TITULAR EN MAYÚSCULAS", "La bajada con el detalle."),
    ("ESCÁNDALO",   "OTRO TITULAR",          "Otra bajada."),
]
```

Agregás o sacás tripletas. Para apagar toda la sección: `MOSTRAR_NOTILUCCIANOS = False`.

## Otros ajustes
- **Artistas de la canción:** editá la lista `ARTISTAS`. Cada corrida elige uno al azar.
- **Fútbol:** se apaga solo el 19/07. Para apagarlo antes: `MOSTRAR_FUTBOL = False`.
- **Destinatarios:** se editan en el Secret `MAIL_TO` (lista separada por coma).
