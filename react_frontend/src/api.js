const BASE = "/api";

async function call(method, path, { params, body } = {}) {
  const qs = params ? "?" + new URLSearchParams(params) : "";
  let res;
  try {
    res = await fetch(`${BASE}${path}${qs}`, {
      method,
      headers: body ? { "Content-Type": "application/json" } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new Error("Can't reach the ReadSeed backend. Is FastAPI running on port 8000?");
  }
  if (!res.ok) {
    let detail = "";
    try { detail = (await res.json()).detail; } catch { /* ignore */ }
    throw new Error(`Server error ${res.status}${detail ? `: ${detail}` : ""}`);
  }
  return res.json();
}


export const api = {
  lookup: (word) => call("POST", "/words/lookup", { body: { word } }),
  confirm: (word, meanings) => call("POST", "/words/confirm", { body: { word, meanings } }),
  related: (word) => call("GET", "/words/related", { params: { word } }),
  addRelated: (words) => call("POST", "/words/related/add", { body: { words } }),
  question: () => call("GET", "/quiz/question"),
  answer: (word_id, answer) => call("POST", "/quiz/answer", { body: { word_id, answer } }),
  vocab: () => call("GET", "/words"),
};