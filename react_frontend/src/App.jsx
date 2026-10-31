import { useEffect, useState } from "react";
import { api } from "./api";

const STAGES = { New: ["🌰", "Seed"], Learning: ["🌱", "Sprout"], Review: ["🌿", "Growing"], Relearning: ["🍂", "Wilting"] };
const kind = (v) => (v === "EQUIVALENT" ? "good" : v?.startsWith("PARTIAL") ? "partial" : "miss");
const VERDICT = {
  good: ["Spot on", "That matches the meaning."],
  partial: ["Close", "Your answer is narrower than the full meaning."],
  miss: ["Not quite", "Here's what it means."],
};

function dueText(iso) {
  if (!iso) return "soon";
  const h = (new Date(iso) - Date.now()) / 36e5;
  if (h < 1) return "within the hour";
  if (h < 24) return `in about ${Math.round(h)} hours`;
  const d = Math.round(h / 24);
  return d === 1 ? "tomorrow" : `in ${d} days`;
}

function relatedWords(d) {
  const items = Array.isArray(d) ? d : d?.related || d?.related_words || d?.words || [];
  return items.map((x) => (typeof x === "string" ? x : x?.word)).filter(Boolean);
}

function Meanings({ items = [] }) {
  if (!items.length) return <p className="muted">No definitions came back for this word.</p>;
  const groups = items.reduce((a, m) => ((a[m.part_of_speech || "other"] ||= []).push(m), a), {});
  return Object.entries(groups).map(([pos, list]) => (
    <div key={pos} className="pos-group">
      <span className="pos">{pos}</span>
      <ol>
        {list.map((m, i) => (
          <li key={i}>
            {m.definition}
            {m.example && <em>“{m.example}”</em>}
          </li>
        ))}
      </ol>
    </div>
  ));
}

/* ------------------------------- Discover ------------------------------- */
function Discover({ notify }) {
  const [word, setWord] = useState("");
  const [res, setRes] = useState(null);
  const [busy, setBusy] = useState(false);
  const [hist, setHist] = useState([]);
  const [rel, setRel] = useState(null);
  const [pick, setPick] = useState([]);

  async function search(w) {
    w = w.trim();
    if (!w) return;
    setWord(w); setBusy(true); setRel(null); setPick([]);
    try {
      const d = await api.lookup(w);
      setRes(d);
      if (["found", "existing"].includes(d.status)) {
        const name = d.word || w;
        setHist((h) => [name, ...h.filter((x) => x.toLowerCase() !== name.toLowerCase())].slice(0, 6));
      }
    } catch (e) { setRes(null); notify(e.message, "error"); }
    finally { setBusy(false); }
  }
  const run = (fn, ok) => async () => {
    try { const r = await fn(); ok(r); } catch (e) { notify(e.message, "error"); }
  };
  const save = run(() => api.confirm(res.word, res.meanings || []), (r) => {
    notify(r?.message || "Saved to your vocabulary", "ok");
    setRes({ ...res, status: "existing" });
  });
  const findRelated = run(() => api.related(res.word), (d) => setRel(relatedWords(d)));
  const addPicked = run(() => api.addRelated(pick), (r) => {
    notify(r?.message || `Added ${pick.length} words`, "ok");
    setPick([]);
  });

  return (
    <section>
      <h1 className="hero">Grow your vocabulary,<br /><i>one word at a time.</i></h1>
      <form className="search" onSubmit={(e) => { e.preventDefault(); search(word); }}>
        <input value={word} onChange={(e) => setWord(e.target.value)} placeholder="Try “ephemeral”" autoFocus />
        <button className="btn" disabled={busy}>{busy ? "Looking…" : "Look up"}</button>
      </form>
      {hist.length > 0 && (
        <div className="chips"><span className="muted">Recent</span>
          {hist.map((h) => <button key={h} className="chip" onClick={() => search(h)}>{h}</button>)}
        </div>
      )}

      {res?.status === "not_found" && <div className="banner miss">We couldn't find that word. Check the spelling.</div>}
      {res?.status === "suggestion" && (
        <div className="banner partial">
          Did you mean <b>{res.suggested_word}</b>?{" "}
          <button className="chip" onClick={() => search(res.suggested_word)}>Look it up</button>
        </div>
      )}
      {res && ["found", "existing"].includes(res.status) && (
        <article className="card">
          <div className="row">
            <h2 className="headword">{res.word}</h2>
            {res.status === "existing"
              ? <span className="tag">In your vocabulary</span>
              : <button className="btn" onClick={save}>Save to vocabulary</button>}
          </div>
          <Meanings items={res.meanings} />
          <hr />
          <h3>Related words</h3>
          {rel === null && <button className="btn ghost" onClick={findRelated}>Find related words</button>}
          {rel?.length === 0 && <p className="muted">Nothing related found.</p>}
          {rel?.length > 0 && (
            <>
              <div className="chips">
                {rel.map((r) => (
                  <button key={r} className={"chip" + (pick.includes(r) ? " on" : "")}
                    onClick={() => setPick((p) => (p.includes(r) ? p.filter((x) => x !== r) : [...p, r]))}>{r}</button>
                ))}
              </div>
              <button className="btn" disabled={!pick.length} onClick={addPicked}>Add {pick.length || ""} selected</button>
            </>
          )}
        </article>
      )}
    </section>
  );
}

/* ------------------------------- Practice ------------------------------- */
function Practice({ notify }) {
  const [s, setS] = useState({ phase: "setup", total: 5, i: 0, score: 0, q: null, fb: null, results: [] });
  const [ans, setAns] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (p) => setS((x) => ({ ...x, ...p }));

  async function next(first) {
    setBusy(true);
    try {
      const q = await api.question();
      set({ q, fb: null, phase: "asking", ...(first ? { i: 0, score: 0, results: [] } : { i: s.i + 1 }) });
      setAns("");
    } catch (e) { notify(e.message, "error"); }
    finally { setBusy(false); }
  }
  async function submit(e) {
    e.preventDefault();
    if (!ans.trim()) return;
    setBusy(true);
    try {
      const r = await api.answer(s.q.word_id, ans.trim());
      let meanings = [];
      if (!r.correct) { try { meanings = (await api.lookup(s.q.word)).meanings || []; } catch { /* optional */ } }
      set({
        fb: { ...r, ans: ans.trim(), meanings }, phase: "feedback",
        score: s.score + (r.correct ? 1 : 0),
        results: [...s.results, { word: s.q.word, verdict: r.verdict, correct: r.correct }],
      });
    } catch (e2) { notify(e2.message, "error"); }
    finally { setBusy(false); }
  }

  if (s.phase === "setup") return (
    <section className="center">
      <h1 className="hero">Test what you<br /><i>actually know.</i></h1>
      <p className="lead">Explain each word in your own words. Close answers count, and every answer schedules the word's next review.</p>
      <label className="muted">Questions: <b>{s.total}</b></label>
      <input type="range" min="3" max="20" value={s.total} onChange={(e) => set({ total: +e.target.value })} />
      <button className="btn big" disabled={busy} onClick={() => next(true)}>{busy ? "Picking a word…" : "Start quiz"}</button>
    </section>
  );

  if (s.phase === "done") return (
    <section className="center">
      <div className="score">{s.score}<span>/{s.total}</span></div>
      <ul className="results">
        {s.results.map((r, i) => (
          <li key={i} className={kind(r.verdict)}><b>{r.word}</b><span>{VERDICT[kind(r.verdict)][0]}</span></li>
        ))}
      </ul>
      <button className="btn big" onClick={() => set({ phase: "setup" })}>Practice again</button>
    </section>
  );

  const fb = s.fb;
  const [emoji, label] = STAGES[fb?.fsrs_state] || ["🌱", fb?.fsrs_state || "Growing"];
  const last = s.i + 1 >= s.total;
  return (
    <section>
      <div className="progress"><div style={{ width: `${((s.i + (fb ? 1 : 0)) / s.total) * 100}%` }} /></div>
      <p className="muted">Question {s.i + 1} of {s.total}</p>
      <h2 className="headword big">{s.q.word}</h2>

      {s.phase === "asking" && (
        <form onSubmit={submit}>
          <textarea rows="4" value={ans} onChange={(e) => setAns(e.target.value)} placeholder="What does this word mean? Say it in your own words." autoFocus />
          <button className="btn" disabled={busy}>{busy ? "Checking…" : "Check answer"}</button>
        </form>
      )}

      {s.phase === "feedback" && (
        <>
          <p className="your">Your answer: {fb.ans}</p>
          <div className={"banner " + kind(fb.verdict)}><b>{VERDICT[kind(fb.verdict)][0]}.</b> {VERDICT[kind(fb.verdict)][1]}</div>
          {fb.meanings.length > 0 && <div className="card"><Meanings items={fb.meanings} /></div>}
          <div className="stage">
            <span className="emoji">{emoji}</span>
            <div><b>{label}</b><div className="muted">You'll see this word again {dueText(fb.next_review)}.</div></div>
          </div>
          <button className="btn" disabled={busy} onClick={() => (last ? set({ phase: "done" }) : next(false))}>
            {last ? "See results" : "Next question"}
          </button>
        </>
      )}
    </section>
  );
}

/* ------------------------------ Vocabulary ------------------------------ */
function Vocabulary() {
  const [items, setItems] = useState(null);
  const [err, setErr] = useState("");
  const [q, setQ] = useState("");

  useEffect(() => {
    api.vocab()
      .then((d) => setItems(Array.isArray(d) ? d : d.words || []))
      .catch((e) => setErr(e.message));
  }, []);

  if (err) return <section><h1 className="hero">My vocabulary</h1><div className="banner partial">Your word list isn't available yet (the app calls GET /words). {err}</div></section>;
  if (!items) return <section><p className="muted">Loading…</p></section>;
  const shown = items.filter((x) => (x.word || String(x)).toLowerCase().includes(q.toLowerCase()));
  return (
    <section>
      <h1 className="hero">My vocabulary</h1>
      <input className="filter" value={q} onChange={(e) => setQ(e.target.value)} placeholder={`Search ${items.length} words`} />
      <div className="grid">
        {shown.map((x, i) => (
          <article key={i} className="card small">
            <h3 className="headword s">{x.word || String(x)}</h3>
            <p className="muted">{(x.meanings || x.definitions || [])[0]?.definition}</p>
          </article>
        ))}
      </div>
      {!items.length && <p className="muted">No saved words yet. Look one up on the Discover tab.</p>}
    </section>
  );
}

/* --------------------------------- App ---------------------------------- */
export default function App() {
  const [tab, setTab] = useState("discover");
  const [toast, setToast] = useState(null);
  const notify = (msg, type = "ok") => { setToast({ msg, type }); setTimeout(() => setToast(null), 4000); };
  const tabs = [["discover", "Discover"], ["practice", "Practice"], ["vocab", "My vocabulary"]];

  return (
    <>
      <header className="nav">
        <div className="brand">🌱 ReadSeed</div>
        <nav>{tabs.map(([k, l]) => <button key={k} className={tab === k ? "active" : ""} onClick={() => setTab(k)}>{l}</button>)}</nav>
      </header>
      <main className="wrap">
        {tab === "discover" && <Discover notify={notify} />}
        {tab === "practice" && <Practice notify={notify} />}
        {tab === "vocab" && <Vocabulary />}
      </main>
      {toast && <div className={"toast " + toast.type}>{toast.msg}</div>}
    </>
  );
}