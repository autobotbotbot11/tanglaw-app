// app.js - shared frontend API helpers and small utilities
// CHANGE API_BASE if your backend is at a different host/port
const API_BASE = "http://localhost:5000/api"; // <-- adjust if needed

// helper to do fetch + json + error handling
async function apiFetch(path, opts = {}) {
  const url = (path.startsWith('http') ? path : `${API_BASE}${path.startsWith('/')? path : '/' + path}`);
  const res = await fetch(url, opts);
  const json = await res.json().catch(()=> ({}));
  return { ok: res.ok, status: res.status, data: json };
}

// small helper to format timestamp (basic)
function fmtTime(ts) {
  // ts from backend is "YYYY-MM-DD HH:MM:SS" — return it raw for now
  return ts;
}

// export for other scripts (if needed)
window.apiFetch = apiFetch;
window.fmtTime = fmtTime;
window.API_BASE = API_BASE;
