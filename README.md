# NotiLucciano's 📰🍦

El "diario" de joda de la oficina, ahora como **app instalable** (PWA) en vez de mail.
Sale una **edición nueva cada viernes** y todas quedan guardadas en **el kiosco**.

No usa IA, ni feeds, ni servidores, ni base de datos. Son archivos estáticos en
GitHub Pages. Cero presupuesto, cero mantenimiento.

---

## Cómo funciona (el modelo)

- Cada edición es **un archivo JSON** en `ediciones/` (ej: `ediciones/2026-06-26.json`).
  Esa es tu "publicación" guardada de ese viernes.
- `ediciones.json` (en la raíz) es **el índice del kiosco**: la lista de todas las
  ediciones, la más nueva primero.
- `index.html` es **el lector**: muestra la última edición grande y abajo el kiosco
  con las anteriores. Lee todo de esos JSON.
- Si un día no hay archivos (o abrís el `index.html` suelto en tu compu), el lector
  cae con elegancia a una **edición demo** embebida. Cuando están los archivos, usa
  los reales solo.

---

## El ritual del viernes (nuevo y cortito)

1. Me pasás a mí (Claudio) **las noticias de la semana**, como te salgan: los chimentos,
   el horóscopo, la encuesta, el índice LUCC, la canción, etc. Crudo está perfecto.
2. Yo te devuelvo **dos archivos listos**:
   - `ediciones/AAAA-MM-DD.json` → la edición de ese viernes.
   - `ediciones.json` → el índice actualizado (con la nueva agregada al principio).
3. Vos subís esos dos archivos al repo + las **fotos** de la semana a `fotos/`.
4. Listo. Queda online y la PWA se actualiza sola.

> Para armarte el índice actualizado yo puedo **leer el `ediciones.json` que ya está
> publicado** en tu GitHub Pages, así no tenés que pasármelo a mano. Vos avisame la URL.

---

## Estructura del repo

```
/
├── index.html                 <- el lector (no se toca semana a semana)
├── manifest.webmanifest       <- config de la PWA (instalable)
├── sw.js                      <- service worker (offline)
├── ediciones.json             <- ÍNDICE del kiosco  [cambia cada viernes]
├── ediciones/
│   ├── 2026-06-26.json        <- una edición  [se agrega una por viernes]
│   └── ...
├── fotos/
│   └── (las fotos de cada edición)
├── icons/                     <- íconos de la app
└── README.md
```

---

## Fotos

- Subís la foto al repo (ej: `fotos/2026-07-03/running.jpg`).
- En el JSON, la referenciás con la ruta relativa: `"foto": "fotos/2026-07-03/running.jpg"`.
- Sirve tanto en la tapa (`tapa.foto`) como en las secundarias (`secundarias[].foto`).
- Si una nota **no** tiene foto, el lector le pone un placeholder duotono lindo. Nada se rompe.
- ⚠️ **Ojo, cuidado con las mayúsculas y espacios** en los nombres: GitHub Pages corre en
  Linux y distingue `Running.JPG` de `running.jpg`. Mejor todo en minúscula y sin espacios.

## Canción

- En `cancion.spotifyUrl` pegás el link de un tema/álbum/playlist de Spotify.
  El lector muestra el **reproductor embebido** (sin claves ni secretos).
- Si lo dejás vacío (`""`), muestra un botón "Escuchar en Spotify" que busca el tema. No falla igual.

---

## Publicar / deploy (una sola vez)

1. Subí todos estos archivos al repo respetando las carpetas.
2. **Settings → Pages → Build and deployment**: Source = *Deploy from a branch*,
   Branch = `main` (carpeta `/root`). Guardar.
3. En un par de minutos queda en:
   `https://juanbautistacrespialomar.github.io/NotiLucciano-s/`

Para publicar una edición nueva después: subís/actualizás `ediciones/AAAA-MM-DD.json`
y `ediciones.json`. Nada más.

---

## Instalar la app en el celu

- **Android (Chrome):** menú ⋮ → "Agregar a la pantalla de inicio" / "Instalar app".
- **iPhone (Safari):** botón Compartir → "Agregar a inicio".
- Se abre a pantalla completa, con ícono propio, y las ediciones ya vistas se leen
  **sin señal**.

---

## Notas técnicas

- **Actualizaciones:** el service worker sirve las ediciones network-first (trae lo
  último si hay señal). Si alguna vez cambiás el `index.html` y querés forzar que a
  todos se les limpie el cache viejo, en `sw.js` subí una versión: `notilucc-v1` → `v2`.
- **Privacidad:** GitHub Pages es público. Por eso las notas usan apodos/iniciales
  (M, MT, Tikititah, Clari, Blas...). Seguí con esa costumbre y listo.
- **Lo viejo:** `notiluccianos.py`, `requirements.txt` y el workflow de Actions ya no se
  usan. Podés borrarlos o moverlos a una carpeta `viejo/` si querés guardar el recuerdo.
