# Geografía Preuniversitario — APK Android

Empaquetado con Capacitor de la app web de Geografía para preuniversitario
(10.º Geografía General y 11.º Geografía Regional). La app funciona
offline: el contenido y los ejercicios van dentro de la APK y el progreso
se guarda en localStorage del teléfono.

- **appId:** `cu.roi.geopre`
- **Nombre:** Geografía Preuniversitario
- **Versión:** 1.0.0 (versionCode 1, versionName 1.0)
- **Límite de peso:** menos de 50 MB (la parte web pesa ~360 KB, sin
  imágenes pesadas ni música; los PDF completos de los libros NO van
  dentro de la APK).

## Cómo se compila

La compilación local con Gradle NO funciona en esta VM (el daemon de
Gradle no logra comunicarse con el cliente; causa raíz no hallada).
La vía que funciona es **GitHub Actions**, igual que Ecos del Olimpo.
El workflow (`.github/workflows/build-apk.yml`) se dispara **solo a
mano** (Run workflow): no hay build automático en cada push, para no
compilar una versión vieja del contenido web.

1. En GitHub: repo `Roiber16/geografia-preuniversitario`, pestaña
   **Actions > Compilar APK Geografía > Run workflow**.
2. La APK aparece en **Artifacts > geografia-preuniversitario-debug**
   (se guarda 30 días).
3. Se descarga y se instala directamente en el teléfono. Es una APK
   **debug** (no es versión de tienda).

## Secreto necesario: el keystore debug (una sola vez)

El keystore debug **NO está en el repo** a propósito. Es solo de
depuración, con las claves por defecto (`android` / `android`), y si
estuviera en un repo público cualquiera podría firmar una APK debug con
la misma clave y actualizar por encima de la app instalada en el
teléfono. Por eso el workflow lo restaura desde un secreto:

- **Nombre del secreto:** `GEOGRAFIA_DEBUG_KEYSTORE_B64`
- **Dónde:** repo en GitHub > Settings > Secrets and variables > Actions
- **Valor:** el archivo local `keystore/geografia-debug.keystore` en
  base64, sin saltos de línea. Desde la carpeta del proyecto:
  `base64 -w0 keystore/geografia-debug.keystore`
  (el valor que imprime ese comando es el secreto; no se pega en
  ningún chat ni archivo).
- **Huella del keystore (para comprobar que es el mismo):**
  SHA-256 `67:98:0D:60:CB:15:21:C1:5E:8F:55:CB:1F:74:54:A7:08:DD:06:AF:32:02:4A:1C:CA:CF:BA:A7:CA:74:65:08`

Con ese secreto, `scripts/fix-debug-signing.js` (que corre DESPUÉS de
`cap sync`, porque el sync reescribe `build.gradle`) fija la firma
debug a ese keystore, y **todas las builds salen con la misma clave**:
las actualizaciones se instalan encima sin desinstalar la anterior.

## Cómo actualizar el contenido web y reconstruir

Cuando la app web cambie (nueva versión viva del artefacto), la APK
vieja queda obsoleta. Pasos, en esta misma carpeta:

```sh
./scripts/actualizar-www.sh   # copia el dist nuevo a www/ y reinyecta offline-progress.js
npx cap sync android          # copia www/ a android/app/src/main/assets/public/
node scripts/fix-debug-signing.js   # DESPUÉS del sync, o se pierde el parche
git add -A && git commit -m "Contenido nuevo: <qué cambió>"
git push origin main
```

Y luego en GitHub: Actions > Compilar APK Geografía > Run workflow.

El progreso offline lo resuelve `www/offline-progress.js`: envuelve
`window.fetch` antes de que cargue el bundle y responde a las 4
acciones del servidor (`getProgress`, `markTopicRead`, `recordAttempt`,
`resetProgress`) con localStorage (`geo-progress-v1`). Al copiar un
`dist` nuevo hay que volver a inyectar el `<script>` en el `<head>`
de `www/index.html` (eso lo hace `actualizar-www.sh`).

## Qué NO hacer

- No compilar una APK final con un `www/` viejo: comprobar antes que
  el dist trae el último contenido (temas, galería, buscador, mapa
  interactivo).
- No subir el keystore al repo ni pegarlo en ningún chat o archivo.
- No usar este keystore para una versión de tienda: es solo debug.
