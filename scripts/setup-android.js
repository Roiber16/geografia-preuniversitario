/**
 * setup-android.js — Prepara la plataforma Android antes de compilar.
 *
 * Si la carpeta android/ no existe, la crea con `npx cap add android`.
 * Copia los iconos desde assets/res/ y aplica la firma debug fija
 * (fix-debug-signing.js). NO fuerza orientación horizontal ni pantalla
 * completa: esta app se usa en vertical, como un libro.
 *
 * Después de este script, el flujo es:
 *   npx cap sync android
 *   node scripts/fix-debug-signing.js   (otra vez, porque cap sync
 *                                        reescribe build.gradle)
 *   cd android && ./gradlew assembleDebug
 *
 * Uso: node scripts/setup-android.js
 */
const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

const root = path.join(__dirname, "..");
const androidDir = path.join(root, "android");
const resSrc = path.join(root, "assets", "res");
const resDst = path.join(androidDir, "app", "src", "main", "res");

function copyDir(src, dst) {
  fs.mkdirSync(dst, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const s = path.join(src, entry.name);
    const d = path.join(dst, entry.name);
    if (entry.isDirectory()) copyDir(s, d);
    else fs.copyFileSync(s, d);
  }
}

if (!fs.existsSync(androidDir)) {
  console.log("No existe android/. Creando la plataforma con Capacitor...");
  execSync("npx cap add android", { cwd: root, stdio: "inherit" });
} else {
  console.log("La carpeta android/ ya existe. No se regenera.");
}

console.log("Copiando iconos desde assets/res/ ...");
copyDir(resSrc, resDst);
console.log("Iconos copiados.");

require("./fix-debug-signing.js");
console.log("setup-android.js terminado.");
