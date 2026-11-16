/* offline-progress.js — Progreso offline para la APK de Geografía.
 *
 * La app web original guarda el progreso en el servidor del artefacto
 * (acciones getProgress / markTopicRead / recordAttempt / resetProgress,
 * POST a ./actions con cuerpo {action, args, actionCallId} y respuesta
 * {data: ...}). Dentro de la APK no hay servidor, así que este script
 * intercepta esas llamadas con fetch y las resuelve en localStorage,
 * con la MISMA lógica que el servidor (mejor nota por fracción de
 * aciertos, intentos acumulados, fecha del último intento).
 *
 * Se carga como script clásico en <head>, ANTES del bundle, así que
 * cuando el SDK captura globalThis.fetch ya ve este envoltorio.
 * No toca el contenido ni el diseño de la app.
 */
(function () {
  var KEY = "geo-progress-v1";

  function load() {
    try {
      return JSON.parse(localStorage.getItem(KEY) || "{}");
    } catch (e) {
      return {};
    }
  }
  function save(map) {
    try {
      localStorage.setItem(KEY, JSON.stringify(map));
    } catch (e) {
      /* almacenamiento lleno o bloqueado: el progreso no se guarda */
    }
  }
  function toRows(map) {
    var out = [];
    for (var id in map) {
      if (!Object.prototype.hasOwnProperty.call(map, id)) continue;
      var r = map[id] || {};
      out.push({
        topic_id: id,
        read: !!r.read,
        attempts: r.attempts || 0,
        best_correct: r.best_correct || 0,
        best_total: r.best_total || 0,
        last_attempt_at: r.last_attempt_at || null,
      });
    }
    return out;
  }

  function handle(action, args) {
    var map = load();
    if (action === "getProgress") {
      return { progress: toRows(map) };
    }
    if (action === "markTopicRead") {
      var row = map[args.topic_id] || {};
      row.read = true;
      map[args.topic_id] = row;
      save(map);
      return { ok: true };
    }
    if (action === "recordAttempt") {
      var prev = map[args.topic_id] || {};
      var prevFraction =
        prev.best_total > 0 ? prev.best_correct / prev.best_total : -1;
      var newFraction = args.correct / args.total;
      var isBest = newFraction >= prevFraction;
      map[args.topic_id] = {
        read: !!prev.read,
        attempts: (prev.attempts || 0) + 1,
        best_correct: isBest ? args.correct : prev.best_correct || 0,
        best_total: isBest ? args.total : prev.best_total || 0,
        last_attempt_at: new Date().toISOString(),
      };
      save(map);
      return { ok: true };
    }
    if (action === "resetProgress") {
      try {
        localStorage.removeItem(KEY);
      } catch (e) {}
      return { ok: true };
    }
    return null; // acción desconocida: dejar que siga a la red
  }

  var origFetch = window.fetch.bind(window);
  window.fetch = function (input, init) {
    var url = typeof input === "string" ? input : (input && input.url) || "";
    var method =
      (init && init.method) || (input && input.method) || "GET";
    if (method.toUpperCase() === "POST" && /\/actions(\?|#|$)/.test(url)) {
      try {
        var body = JSON.parse((init && init.body) || "{}");
        var data = handle(body.action, body.args || {});
        if (data !== null) {
          return Promise.resolve(
            new Response(JSON.stringify({ data: data }), {
              status: 200,
              headers: { "Content-Type": "application/json" },
            })
          );
        }
      } catch (e) {
        /* si algo falla, seguir a la red como antes */
      }
    }
    return origFetch(input, init);
  };
})();
