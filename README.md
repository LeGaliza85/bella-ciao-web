# Bella Ciao · Web

Web del restaurante **Bella Ciao** (Av. d'Enclar, 84 · Andorra la Vella).
Carta completa en cuatro idiomas (CA / ES / FR / EN) y dos canales
(restaurante y delivery), construida a partir de la carta maestra en Excel.

- **Web**: `index.html` (home) y `carta.html` (carta completa)
- **Diseño**: `untitled.pen` (canvas de pen.dev) — referencia visual
- **Datos**: `data/carta-maestra-v1.xlsx` → `assets/menu-data.js`

---

## Estructura

```
index.html            Home: hero, datos, avance de carta, la casa, platos, bodega, reseñas, visita
carta.html            Carta completa: cabecera, índice de categorías y secciones
assets/
  site.css            Sistema de diseño (tokens, componentes, breakpoints)
  app.js              Runtime: idioma, canal, render de carta, índice pegajoso
  i18n.js             Diccionario ES → CA/FR/EN de la interfaz + etiquetas cortas
  menu-data.js        GENERADO: 107 platos (restaurante) / 65 (delivery), 4 idiomas
  logo.png            Emblema (esquinas transparentes)
images/               Fotografía del hero, la casa, platos y bodega
map-warm.png          Mapa estilizado de la ubicación
data/
  carta-maestra-v1.xlsx   Carta maestra corporativa (fuente de verdad)
tools/
  extract_menu.py     Excel → assets/menu-data.js
  verify_menu.py      Compara el Excel con lo publicado
  menu_fixes.py       Correcciones de nombres por idioma
untitled.pen          Documento de diseño (pen.dev)
```

---

## Cómo funciona

**Carta.** `assets/menu-data.js` contiene los bloques (`pizze`, `pasta`, `postres`…),
sus grupos y los platos, cada uno con nombre y descripción en los cuatro idiomas,
precio y disponibilidad por canal. La web filtra por canal y pinta con
`assets/app.js`; no hay contenido de carta escrito a mano en el HTML.

**Idioma y canal.** Se guardan en `localStorage` y en la URL
(`?lang=ca&canal=delivery`), así que se mantienen al navegar y se pueden compartir.

**Textos fijos.** `assets/i18n.js` traduce la interfaz. La clave es el texto en
español que aparece en el HTML; si añades un texto nuevo, añade su entrada en los
tres idiomas.

**Índice de categorías.** Barra pegajosa bajo la cabecera, con la sección activa
resaltada (scroll + `IntersectionObserver` + sondeo de respaldo). En móvil es un
carrusel horizontal que centra la categoría activa. Las secciones usan anclas
estables (`#pizze`, `#pasta`, `#postres`…) independientes del idioma.

**Nombres de producto.** Se muestran siempre en mayúsculas por CSS
(`text-transform`), también en el panel de la home y en las tarjetas destacadas.

---

## Actualizar la carta

1. Edita `data/carta-maestra-v1.xlsx` (hoja `MAESTRA`).
   Columnas relevantes: `Categoria`, `Nombre_*`, `Descripcion_*`,
   `Precio_restaurante_EUR`, `Precio_delivery_EUR` y los flags
   `Restaurante`, `Web`, `Delivery_TakeAway`.
2. Regenera los datos:

   ```bash
   python tools/extract_menu.py
   ```

3. Comprueba que no falta nada:

   ```bash
   python tools/verify_menu.py
   ```

   Debe terminar sin diferencias (las 4 filas `BC-SUG-*` están desactivadas en el
   Excel a propósito).

4. Si el cambio afecta a un texto fijo (título de sección, aviso…), actualízalo en
   `assets/i18n.js`.

Para usar otro Excel: `python tools/extract_menu.py ruta/al/fichero.xlsx`.

**Correcciones de nombres.** El Excel mezcla idiomas en algunas filas. Los arreglos
viven en `tools/menu_fixes.py` y se aplican en cada regeneración (por ejemplo
`MARGARITA → MARGHERITA`, `PROSCIUTO → PROSCIUTTO`, `AIGUA S. PELLEGRINO → AGUA…`).
Si se corrigen en el Excel, se pueden quitar de ese fichero.

---

## Desarrollo

No hay build: son ficheros estáticos. Para verlos en local:

```bash
python -m http.server 8777
# http://localhost:8777/index.html
```

Abre siempre desde un servidor (no `file://`) para que el almacenamiento y las
rutas se comporten igual que en producción.

**Publicación.** Cualquier hosting estático sirve (Netlify, Vercel, GitHub Pages,
S3…). El repositorio es privado; si se quiere GitHub Pages hará falta cuenta Pro o
publicar desde otro proveedor.

---

## Pendientes / decisiones abiertas

- **Precios de delivery**: en el Excel todos los incrementos son 0, así que se
  muestran los mismos precios que en restaurante. Revisar si debe haber recargo.
- **Cannoli** (8,20) y **Babá al ron** (8,50) estaban en la carta anterior y no
  existen en la maestra: no se muestran.
- **Sugerencias desactivadas**: Crema di Peperoni & Salami, Pizza de l'Any,
  Focaccia con Mortadela de Trufa y Tortellini Salmón & Gorgonzola (filas
  `BC-SUG-*`, con `Web = False`).
- **Vinos**: la maestra no incluye carta de vinos; la sección Bodega es informativa.
- **Entrecot**: se muestra 8,50 con la nota «precio por 100 g · mínimo 300 g»
  heredada de la carta anterior; confirmar.
