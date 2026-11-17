/**
 * fix-debug-signing.js — Firma debug explícita en build.gradle.
 *
 * Por qué existe: copiar el keystore fijo a ~/.android/debug.keystore no
 * basta — Gradle puede resolver su propio debug.keystore por otro camino
 * y cada build saldría con una clave efímera distinta, obligando a Roi a
 * desinstalar la APK anterior para instalar la nueva.
 *
 * Solución robusta: configurar la firma debug EXPLÍCITAMENTE en
 * android/app/build.gradle, apuntando al keystore del repo
 * (keystore/geografia-debug.keystore). Así Gradle usa siempre la misma
 * clave y las actualizaciones instalan encima sin desinstalar.
 *
 * Se ejecuta DESPUÉS de `npx cap sync android`, porque cap sync reescribe
 * android/app/build.gradle y borraría el parche si se aplicara antes.
 * Es idempotente.
 *
 * Uso: node scripts/fix-debug-signing.js
 */
const fs = require("fs");
const path = require("path");

const gradlePath = path.join(__dirname, "..", "android", "app", "build.gradle");

if (!fs.existsSync(gradlePath)) {
  console.error("No existe build.gradle en " + gradlePath);
  process.exit(1);
}

let gradle = fs.readFileSync(gradlePath, "utf8");

if (!gradle.includes("geografia-debug.keystore")) {
  const anchor = "    buildTypes {";
  if (!gradle.includes(anchor)) {
    console.error('AVISO: no se encontró "buildTypes {" en build.gradle. Revisa a mano.');
    process.exit(1);
  }

  const signingBlock = `    signingConfigs {
        debug {
            storeFile file("../../keystore/geografia-debug.keystore")
            storePassword "android"
            keyAlias "androiddebugkey"
            keyPassword "android"
        }
    }
`;
  gradle = gradle.replace(anchor, signingBlock + anchor);
}

// La sección debug de buildTypes debe usar esa firma. La plantilla de
// Capacitor 8.6 no trae bloque `debug` (solo `release`): sin él, Gradle
// firmaría el debug con su keystore automático y cada build saldría con
// otra clave. Lo creamos explícitamente si falta.
if (!/buildTypes\s*\{[^}]*\bdebug\s*\{/.test(gradle)) {
  gradle = gradle.replace(
    /(\n    buildTypes \{)/,
    "$1\n        debug {\n            signingConfig signingConfigs.debug\n        }"
  );
} else if (!/debug\s*\{\s*\n\s*signingConfig signingConfigs\.debug/.test(gradle)) {
  gradle = gradle.replace(
    /(\n    buildTypes \{\n        debug \{)/,
    "$1\n            signingConfig signingConfigs.debug"
  );
}

// La versión también la fija este script: cap sync reescribe build.gradle
// y con él versionCode/versionName, así que se reponen aquí en cada build.
// v2 = GeoPre (menú + icono Atlas). Subir ambos números en cada entrega.
gradle = gradle.replace(/versionCode \d+/, "versionCode 2");
gradle = gradle.replace(/versionName "[^"]*"/, 'versionName "1.0.1"');

fs.writeFileSync(gradlePath, gradle);
console.log("build.gradle: firma debug fijada a keystore/geografia-debug.keystore");
