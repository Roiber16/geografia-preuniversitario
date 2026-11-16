#!/bin/bash
# actualizar-www.sh — Copia el dist nuevo del artefacto web a www/
# y reinyecta offline-progress.js (progreso offline con localStorage).
#
# Uso: ./scripts/actualizar-www.sh
# Se ejecuta en la raíz del proyecto (~/workspace/geografia-apk/).
#
# NO reutiliza el www/ viejo: lo vacía y lo vuelve a copiar entero.
# Después de este script hay que hacer:
#   npx cap sync android
#   node scripts/fix-debug-signing.js   # DESPUÉS del sync
#   git add -A && git commit -m "Contenido nuevo: ..." && git push origin main
# Y luego disparar el workflow a mano en GitHub Actions.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="$HOME/workspace/ts-spaces/app-de-geografia-para-preuniversitario/client/dist"
WWW="$ROOT/www"

if [ ! -d "$DIST" ]; then
  echo "ERROR: no existe el dist del artefacto en $DIST"
  echo "Reconstruye primero el cliente del artefacto (bun run build:client)."
  exit 1
fi

if [ ! -f "$ROOT/www/offline-progress.js" ]; then
  echo "ERROR: falta www/offline-progress.js en el proyecto. No sigo."
  exit 1
fi

echo "Copiando dist nuevo a www/ ..."
cp "$ROOT/www/offline-progress.js" /tmp/offline-progress.js.bak
rm -rf "$WWW"
mkdir -p "$WWW"
cp -r "$DIST"/. "$WWW"/
cp /tmp/offline-progress.js.bak "$WWW/offline-progress.js"

# Reinyectar el <script> en el <head> del nuevo index.html, si falta.
if ! grep -q "offline-progress.js" "$WWW/index.html"; then
  echo "Inyectando offline-progress.js en index.html ..."
  sed -i 's#<head>#<head>\n    <script src="./offline-progress.js"></script>#' "$WWW/index.html"
fi

echo "Verificación:"
grep -c "offline-progress.js" "$WWW/index.html" | xargs echo "  offline-progress.js en index.html (veces):"
grep -o "g10-[a-z-]*\|g11-[a-z-]*" "$WWW"/assets/*.js 2>/dev/null | sort -u | wc -l | xargs echo "  ids de tema en el bundle:"
grep -o "Equal Earth" "$WWW"/assets/*.js 2>/dev/null | wc -l | xargs echo "  menciones a Equal Earth:"
echo "Listo. Ahora: npx cap sync android && node scripts/fix-debug-signing.js"
