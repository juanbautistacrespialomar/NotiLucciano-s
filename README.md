# Fotos de las ediciones

Una carpeta por edición, nombrada con el mismo `id` que usás en `ediciones.json`
y en `ediciones/<id>.json` (formato `AAAA-MM-DD`).

```
fotos/
  2026-06-26/
    AMOR_RUNNER.jpeg
    GUERRA_DECLARADA.jpeg
  2026-07-04/
    ...
```

## Cómo referenciarlas en el JSON de la edición

- Foto de **tapa**: campo `foto` dentro de `tapa`.
- Foto de una **secundaria**: campo `foto` dentro del objeto de esa secundaria.

Ruta relativa desde la raíz del repo, siempre empezando con `./`:

```json
"tapa": { "foto": "./fotos/2026-06-26/AMOR_RUNNER.jpeg", ... }
```

## Reglas para no pelearte con GitHub Pages ni con el mail

1. **Nombres sin espacios ni acentos.** Usá guion bajo: `AMOR_RUNNER.jpeg`, no `AMOR RUNNER.jpeg`. Los espacios en URLs hay que escaparlos (`%20`) y es un dolor.
2. **Case-sensitive.** GitHub corre en Linux: `Foto.jpg` ≠ `foto.jpg`.
3. **Nombre nuevo = foto nueva.** El service worker cachea las fotos cache-first.
   Si reemplazás una foto pero mantenés el nombre, algunos las van a seguir viendo
   viejas. Cambiá el nombre (`running-v2.jpeg`) o subí el `CACHE` en `sw.js`.
4. **Livianas.** Redimensioná a ~700px de ancho y calidad ~85. Una tapa no necesita 4 MB.

Si una ruta está mal escrita, la app no muestra el ícono roto: cae elegante al
placeholder rosa/duotono (gracias al `onerror` del `<img>`).
