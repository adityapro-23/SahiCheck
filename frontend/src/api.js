/**
 * api.js – Three API helpers + the NDJSON stream reader.
 *
 * All network code lives here so the rest of the UI never touches fetch() directly.
 */

/** GET /api/checks → [{id, name, tier, source, max_points}, …] */
export async function fetchChecks() {
  const res = await fetch("/api/checks");
  if (!res.ok) throw new Error(`/api/checks failed: ${res.status}`);
  return res.json();
}

/** GET /api/demo/{name} → {text} */
export async function fetchDemo(name) {
  const res = await fetch(`/api/demo/${name}`);
  if (!res.ok) throw new Error(`Demo fetch failed: ${res.status}`);
  return res.json(); // {text}
}

/**
 * POST /api/check – streams NDJSON events.
 *
 * @param {FormData} formData  – already built by the caller
 * @param {(event: object) => void} onEvent – called for every parsed JSON line
 * @returns {Promise<void>}    – resolves when the stream closes
 *
 * The function splits the ReadableStream on newlines, parses each line as JSON,
 * and calls `onEvent`.  An `error` event propagates as a thrown Error so callers
 * can catch it in one place.
 *
 * NOTE: We use fetch + ReadableStream instead of EventSource because EventSource
 * cannot send multipart POST bodies.
 */
export async function streamCheck(formData, onEvent) {
  const res = await fetch("/api/check", { method: "POST", body: formData });

  // HTTP-level errors (422 validation, 500, etc.) arrive as JSON, not as a stream.
  if (!res.ok) {
    let detail = `Server error ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch (_) { /* ignore parse failures */ }
    throw new Error(detail);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let sawFinal = false;

  function handleLine(line) {
    const trimmed = line.trim();
    if (!trimmed) return;
    let event;
    try {
      event = JSON.parse(trimmed);
    } catch (_) {
      throw new Error("The server returned an invalid analysis event.");
    }
    onEvent(event);
    if (event.type === "final") sawFinal = true;
    if (event.type === "error") {
      throw new Error(event.message || "Pipeline error");
    }
  }

  // Read chunks from the response body, split on newlines, parse each JSON line.
  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      buffer += decoder.decode();
      handleLine(buffer);
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    // Keep the last (possibly partial) fragment in the buffer.
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      handleLine(line);
    }
  }
  if (!sawFinal) {
    throw new Error("The analysis stream ended before returning a result.");
  }
}
