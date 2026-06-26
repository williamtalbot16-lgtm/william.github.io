import streamlit as st
import streamlit.components.v1 as components

# ── React JSX Component ────────────────────────────────────────
# This is the ProspectCRM React app rendered in Streamlit

REACT_APP = """
import { useState, useEffect, useCallback } from "react";

// ── API base (adjust for production) ─────────────────────────
const API = "http://localhost:8000/api";

// ── Palette & design tokens ───────────────────────────────────
// Deep navy base, electric indigo accent, slate neutrals
// Signature: a live status ticker ribbon across the top

const STAGE_META = {
  scraped:    { label: "Scraped",       color: "#64748b", bg: "#f1f5f9" },
  site_built: { label: "Site Built",    color: "#0891b2", bg: "#ecfeff" },
  email_sent: { label: "Email Sent",    color: "#7c3aed", bg: "#f5f3ff" },
  replied:    { label: "Replied",       color: "#d97706", bg: "#fffbeb" },
  interested: { label: "Interested",    color: "#059669", bg: "#ecfdf5" },
  closed:     { label: "Closed 💰",     color: "#16a34a", bg: "#dcfce7" },
  lost:       { label: "Lost",          color: "#dc2626", bg: "#fef2f2" },
};

const STAGES = Object.keys(STAGE_META);

// ── Utility helpers ────────────────────────────────────────────

function ago(iso) {
  if (!iso) return "—";
  const s = Math.floor((Date.now() - new Date(iso)) / 1000);
  if (s < 60) return `${s}s ago`;
  if (s < 3600) return `${Math.floor(s/60)}m ago`;
  if (s < 86400) return `${Math.floor(s/3600)}h ago`;
  return `${Math.floor(s/86400)}d ago`;
}

async function apiFetch(path, opts = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

// ── Shared micro-components ─────────────────────���──────────────

function StageBadge({ stage }) {
  const m = STAGE_META[stage] || { label: stage, color: "#64748b", bg: "#f1f5f9" };
  return (
    <span style={{
      background: m.bg, color: m.color,
      padding: "2px 10px", borderRadius: 999,
      fontSize: 11, fontWeight: 700, letterSpacing: "0.04em",
      whiteSpace: "nowrap",
    }}>{m.label}</span>
  );
}

function Stars({ rating }) {
  const n = Math.round(rating || 0);
  return (
    <span style={{ color: "#f59e0b", fontSize: 13 }}>
      {"★".repeat(n)}{"☆".repeat(5 - n)}
      <span style={{ color: "#94a3b8", marginLeft: 4, fontSize: 11 }}>{rating}</span>
    </span>
  );
}

function Spinner() {
  return (
    <div style={{ textAlign: "center", padding: 40, color: "#94a3b8" }}>
      <div style={{
        display: "inline-block", width: 28, height: 28,
        border: "3px solid #e2e8f0", borderTopColor: "#6366f1",
        borderRadius: "50%", animation: "spin 0.7s linear infinite",
      }} />
      <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
    </div>
  );
}

function EmptyState({ icon, message }) {
  return (
    <div style={{ textAlign: "center", padding: "60px 20px", color: "#94a3b8" }}>
      <div style={{ fontSize: 36, marginBottom: 12 }}>{icon}</div>
      <p style={{ margin: 0, fontSize: 14 }}>{message}</p>
    </div>
  );
}

// ── Launch Job Modal ───────────────────────────────────────────

function LaunchModal({ onClose, onLaunched }) {
  const [city, setCity] = useState("");
  const [niche, setNiche] = useState("");
  const [limit, setLimit] = useState(20);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function submit() {
    if (!city.trim() || !niche.trim()) { setError("City and niche are required."); return; }
    setLoading(true); setError("");
    try {
      const data = await apiFetch("/jobs", {
        method: "POST",
        body: JSON.stringify({ city: city.trim(), niche: niche.trim(), limit }),
      });
      onLaunched(data);
      onClose();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{
      position: "fixed", inset: 0, background: "rgba(15,23,42,0.6)",
      display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100,
    }} onClick={onClose}>
      <div onClick={e => e.stopPropagation()} style={{
        background: "#fff", borderRadius: 16, padding: 32, width: 420,
        boxShadow: "0 20px 60px rgba(0,0,0,0.2)",
      }}>
        <h3 style={{ margin: "0 0 4px", fontSize: 18, color: "#0f172a" }}>Launch Scrape Campaign</h3>
        <p style={{ margin: "0 0 24px", fontSize: 13, color: "#64748b" }}>
          Finds no-website businesses, builds sites, and sends cold emails automatically.
        </p>

        {[
          { label: "City", val: city, set: setCity, ph: "Austin, TX" },
          { label: "Niche", val: niche, set: setNiche, ph: "barbershop" },
        ].map(({ label, val, set, ph }) => (
          <div key={label} style={{ marginBottom: 16 }}>
            <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#475569", marginBottom: 6 }}>
              {label}
            </label>
            <input
              value={val} onChange={e => set(e.target.value)}
              placeholder={ph}
              style={{
                width: "100%", boxSizing: "border-box", padding: "10px 14px",
                border: "1.5px solid #e2e8f0", borderRadius: 8, fontSize: 14,
                outline: "none", color: "#0f172a",
              }}
            />
          </div>
        ))}

        <div style={{ marginBottom: 24 }}>
          <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#475569", marginBottom: 6 }}>
            Max leads: <strong style={{ color: "#6366f1" }}>{limit}</strong>
          </label>
          <input type="range" min={5} max={100} value={limit} onChange={e => setLimit(+e.target.value)}
            style={{ width: "100%" }} />
        </div>

        {error && <p style={{ color: "#dc2626", fontSize: 13, marginBottom: 12 }}>{error}</p>}

        <div style={{ display: "flex", gap: 10 }}>
          <button onClick={onClose} style={{
            flex: 1, padding: "11px 0", borderRadius: 8, border: "1.5px solid #e2e8f0",
            background: "none", cursor: "pointer", fontSize: 14, color: "#64748b",
          }}>Cancel</button>
          <button onClick={submit} disabled={loading} style={{
            flex: 2, padding: "11px 0", borderRadius: 8, border: "none",
            background: loading ? "#a5b4fc" : "#6366f1", color: "#fff",
            cursor: loading ? "not-allowed" : "pointer", fontSize: 14, fontWeight: 700,
          }}>
            {loading ? "Launching…" : "🚀 Launch Campaign"}
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Pipeline Kanban ────────────────────────────────────────────

function PipelineView({ onSelectLead }) {
  const [leads, setLeads] = useState([]);
  const [counts, setCounts] = useState({});
  const [loading, setLoading] = useState(true);
  const [activeStage, setActiveStage] = useState(null);

  useEffect(() => {
    Promise.all([
      apiFetch("/leads/pipeline"),
      apiFetch(`/leads${activeStage ? `?stage=${activeStage}&limit=50` : "?limit=50"}`),
    ]).then(([c, l]) => {
      setCounts(c); setLeads(l.items || []);
    }).catch(console.error).finally(() => setLoading(false));
  }, [activeStage]);

  if (loading) return <Spinner />;

  return (
    <div>
      {/* Stage selector strip */}
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 24 }}>
        <button
          onClick={() => setActiveStage(null)}
          style={{
            padding: "6px 14px", borderRadius: 999, border: "none", cursor: "pointer", fontSize: 12, fontWeight: 600,
            background: !activeStage ? "#6366f1" : "#f1f5f9", color: !activeStage ? "#fff" : "#475569",
          }}
        >All ({Object.values(counts).reduce((a,b) => a+b, 0)})</button>
        {STAGES.map(s => (
          <button key={s} onClick={() => setActiveStage(s === activeStage ? null : s)} style={{
            padding: "6px 14px", borderRadius: 999, border: "none", cursor: "pointer",
            fontSize: 12, fontWeight: 600,
            background: activeStage === s ? STAGE_META[s].color : STAGE_META[s].bg,
            color: activeStage === s ? "#fff" : STAGE_META[s].color,
          }}>{STAGE_META[s].label} ({counts[s] || 0})</button>
        ))}
      </div>

      {/* Leads table */}
      {leads.length === 0 ? (
        <EmptyState icon="🔍" message="No leads yet. Launch a campaign to start prospecting." />
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead>
              <tr style={{ borderBottom: "2px solid #f1f5f9", textAlign: "left" }}>
                {["Business", "City / Niche", "Rating", "Email", "Stage", "Updated", ""].map(h => (
                  <th key={h} style={{ padding: "8px 12px", color: "#94a3b8", fontWeight: 600, fontSize: 11, textTransform: "uppercase", letterSpacing: "0.06em" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {leads.map(lead => (
                <tr key={lead.id} style={{ borderBottom: "1px solid #f8fafc" }}
                  onMouseEnter={e => e.currentTarget.style.background = "#fafbff"}
                  onMouseLeave={e => e.currentTarget.style.background = ""}
                >
                  <td style={{ padding: "10px 12px", fontWeight: 600, color: "#0f172a" }}>{lead.name}</td>
                  <td style={{ padding: "10px 12px", color: "#64748b" }}>{lead.city}<br/><span style={{ fontSize: 11, color: "#94a3b8" }}>{lead.niche}</span></td>
                  <td style={{ padding: "10px 12px" }}><Stars rating={lead.rating} /></td>
                  <td style={{ padding: "10px 12px", color: "#64748b", fontSize: 12 }}>{lead.owner_email || <span style={{ color: "#cbd5e1" }}>—</span>}</td>
                  <td style={{ padding: "10px 12px" }}><StageBadge stage={lead.stage} /></td>
                  <td style={{ padding: "10px 12px", color: "#94a3b8", fontSize: 11 }}>{ago(lead.updated_at)}</td>
                  <td style={{ padding: "10px 12px" }}>
                    <button onClick={() => onSelectLead(lead)} style={{
                      padding: "4px 12px", borderRadius: 6, border: "1.5px solid #e2e8f0",
                      background: "none", cursor: "pointer", fontSize: 12, color: "#6366f1", fontWeight: 600,
                    }}>View</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// ── Activity Feed ──────────────────────────────────────────────

function ActivityFeedView() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch("/leads/activity/feed")
      .then(data => setEvents(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const ICONS = {
    email_sent: "📤", followup_sent: "📨", reply_received: "📬",
    site_built: "🌐", lead_scraped: "🔍", payment_received: "💰",
    stage_changed: "🔄", reply_sent: "↩️", email_error: "⚠️", site_error: "⚠️",
  };

  if (loading) return <Spinner />;
  if (!events.length) return <EmptyState icon="📋" message="No activity yet." />;

  return (
    <div style={{ maxWidth: 640 }}>
      {events.map(ev => (
        <div key={ev.id} style={{
          display: "flex", gap: 12, padding: "12px 0",
          borderBottom: "1px solid #f1f5f9",
        }}>
          <span style={{ fontSize: 18, flexShrink: 0, marginTop: 2 }}>
            {ICONS[ev.event_type] || "•"}
          </span>
          <div style={{ flex: 1 }}>
            <p style={{ margin: 0, fontSize: 13, color: "#1e293b" }}>{ev.description}</p>
            {ev.lead_name && (
              <p style={{ margin: "2px 0 0", fontSize: 11, color: "#94a3b8" }}>{ev.lead_name}</p>
            )}
          </div>
          <span style={{ fontSize: 11, color: "#cbd5e1", whiteSpace: "nowrap", alignSelf: "start", marginTop: 3 }}>
            {ago(ev.created_at)}
          </span>
        </div>
      ))}
    </div>
  );
}

// ── Inbox View ─────────────────────────────────────────────────

function InboxView({ onSelectLead }) {
  const [threads, setThreads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);
  const [thread, setThread] = useState([]);
  const [reply, setReply] = useState("");
  const [drafting, setDrafting] = useState(false);
  const [sending, setSending] = useState(false);

  useEffect(() => {
    apiFetch("/inbox/threads")
      .then(setThreads).catch(console.error).finally(() => setLoading(false));
  }, []);

  async function openThread(t) {
    setSelected(t);
    const data = await apiFetch(`/inbox/thread/${t.lead_id}`);
    setThread(data);
  }

  async function aiDraft() {
    if (!selected) return;
    setDrafting(true);
    const latest = thread.filter(e => e.direction === "inbound").at(-1);
    try {
      const data = await apiFetch("/inbox/draft", {
        method: "POST",
        body: JSON.stringify({ lead_id: selected.lead_id, inbound_text: latest?.body_text || "" }),
      });
      setReply(data.draft);
    } catch (e) { alert(e.message); }
    finally { setDrafting(false); }
  }

  async function sendReply() {
    if (!reply.trim() || !selected) return;
    setSending(true);
    try {
      await apiFetch(`/inbox/reply/${selected.lead_id}`, {
        method: "POST",
        body: JSON.stringify({ body: reply }),
      });
      setReply("");
      openThread(selected);
    } catch (e) { alert(e.message); }
    finally { setSending(false); }
  }

  if (loading) return <Spinner />;

  return (
    <div style={{ display: "flex", gap: 0, height: "calc(100vh - 200px)", border: "1.5px solid #e2e8f0", borderRadius: 12, overflow: "hidden" }}>
      {/* Thread list */}
      <div style={{ width: 280, borderRight: "1.5px solid #e2e8f0", overflowY: "auto", flexShrink: 0 }}>
        {threads.length === 0 && (
          <EmptyState icon="📭" message="No replies yet." />
        )}
        {threads.map(t => (
          <div key={t.lead_id} onClick={() => openThread(t)}
            style={{
              padding: "14px 16px", cursor: "pointer", borderBottom: "1px solid #f1f5f9",
              background: selected?.lead_id === t.lead_id ? "#f5f3ff" : "transparent",
            }}>
            <p style={{ margin: "0 0 3px", fontWeight: 700, fontSize: 13, color: "#0f172a" }}>{t.lead_name}</p>
            <p style={{ margin: "0 0 3px", fontSize: 12, color: "#64748b" }}>{t.subject}</p>
            <p style={{ margin: 0, fontSize: 11, color: "#94a3b8" }}>{t.preview}</p>
            <p style={{ margin: "4px 0 0", fontSize: 11, color: "#cbd5e1" }}>{ago(t.received_at)}</p>
          </div>
        ))}
      </div>

      {/* Thread detail */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
        {!selected ? (
          <EmptyState icon="👆" message="Select a thread to read it" />
        ) : (
          <>
            <div style={{ padding: "16px 20px", borderBottom: "1px solid #f1f5f9", background: "#fafbff" }}>
              <p style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>{selected.lead_name}</p>
              <p style={{ margin: "2px 0 0", fontSize: 12, color: "#64748b" }}>{selected.subject}</p>
            </div>

            {/* Messages */}
            <div style={{ flex: 1, overflowY: "auto", padding: 20, display: "flex", flexDirection: "column", gap: 12 }}>
              {thread.map(msg => (
                <div key={msg.id} style={{
                  alignSelf: msg.direction === "outbound" ? "flex-end" : "flex-start",
                  maxWidth: "80%",
                }}>
                  <div style={{
                    padding: "10px 14px", borderRadius: 12, fontSize: 13, lineHeight: 1.6,
                    background: msg.direction === "outbound" ? "#6366f1" : "#f1f5f9",
                    color: msg.direction === "outbound" ? "#fff" : "#1e293b",
                  }}>
                    {msg.body_text || "—"}
                  </div>
                  <p style={{ margin: "3px 4px 0", fontSize: 10, color: "#94a3b8",
                    textAlign: msg.direction === "outbound" ? "right" : "left" }}>
                    {msg.direction === "outbound" ? "You" : selected.lead_name} · {ago(msg.created_at)}
                    {msg.sequence_num > 1 ? ` · Follow-up #${msg.sequence_num - 1}` : ""}
                  </p>
                </div>
              ))}
            </div>

            {/* Reply composer */}
            <div style={{ padding: 16, borderTop: "1.5px solid #e2e8f0", background: "#fff" }}>
              <textarea
                value={reply} onChange={e => setReply(e.target.value)}
                placeholder="Write a reply…"
                rows={3}
                style={{
                  width: "100%", boxSizing: "border-box", padding: "10px 14px",
                  border: "1.5px solid #e2e8f0", borderRadius: 10, fontSize: 13,
                  resize: "vertical", outline: "none", color: "#0f172a", fontFamily: "inherit",
                }}
              />
              <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
                <button onClick={aiDraft} disabled={drafting} style={{
                  padding: "8px 14px", borderRadius: 8, border: "1.5px solid #c7d2fe",
                  background: "#f5f3ff", color: "#6366f1", cursor: "pointer", fontSize: 12, fontWeight: 600,
                }}>
                  {drafting ? "Drafting…" : "✨ AI Draft"}
                </button>
                <button onClick={sendReply} disabled={sending || !reply.trim()} style={{
                  padding: "8px 20px", borderRadius: 8, border: "none",
                  background: sending ? "#a5b4fc" : "#6366f1", color: "#fff",
                  cursor: "pointer", fontSize: 12, fontWeight: 700, marginLeft: "auto",
                }}>
                  {sending ? "Sending…" : "Send Reply"}
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

// ── Jobs Monitor ───────────────────────────────────────────────

function JobsView() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = () => apiFetch("/jobs").then(setJobs).catch(console.error);
    load();
    const t = setInterval(load, 5000);
    return () => clearInterval(t);
  }, []);

  if (loading && !jobs.length) return <Spinner />;

  const STATUS_COLOR = { pending: "#f59e0b", running: "#6366f1", done: "#16a34a", failed: "#dc2626" };

  return (
    <div>
      {jobs.length === 0 && <EmptyState icon="⚙️" message="No campaigns launched yet." />}
      {jobs.map(job => (
        <div key={job.id} style={{
          border: "1.5px solid #e2e8f0", borderRadius: 12, padding: "16px 20px",
          marginBottom: 12, display: "flex", alignItems: "center", gap: 16,
        }}>
          <div style={{
            width: 10, height: 10, borderRadius: "50%", flexShrink: 0,
            background: STATUS_COLOR[job.status] || "#94a3b8",
            boxShadow: job.status === "running" ? `0 0 0 4px ${STATUS_COLOR.running}33` : "none",
          }} />
          <div style={{ flex: 1 }}>
            <p style={{ margin: 0, fontWeight: 700, color: "#0f172a", fontSize: 14 }}>
              {job.niche} in {job.city}
            </p>
            <p style={{ margin: "2px 0 0", fontSize: 12, color: "#64748b" }}>
              {job.leads_found} leads · limit {job.limit_count}
              {job.error && <span style={{ color: "#dc2626" }}> · {job.error}</span>}
            </p>
          </div>
          <span style={{
            padding: "3px 12px", borderRadius: 999, fontSize: 11, fontWeight: 700,
            background: `${STATUS_COLOR[job.status]}20`, color: STATUS_COLOR[job.status],
          }}>{job.status}</span>
          <span style={{ fontSize: 11, color: "#94a3b8" }}>{ago(job.created_at)}</span>
        </div>
      ))}
    </div>
  );
}

// ── Lead Detail Drawer ─────────────────────────────────────────

function LeadDrawer({ lead, onClose, onStageChange }) {
  const [stage, setStage] = useState(lead.stage);
  const [notes, setNotes] = useState(lead.notes || "");
  const [saving, setSaving] = useState(false);

  async function save() {
    setSaving(true);
    try {
      if (stage !== lead.stage) {
        await apiFetch(`/leads/${lead.id}/stage`, {
          method: "PATCH",
          body: JSON.stringify({ stage, notes }),
        });
        onStageChange();
      } else if (notes !== lead.notes) {
        await apiFetch(`/leads/${lead.id}`, {
          method: "PATCH",
          body: JSON.stringify({ notes }),
        });
      }
      onClose();
    } catch (e) { alert(e.message); }
    finally { setSaving(false); }
  }

  return (
    <div style={{
      position: "fixed", inset: 0, background: "rgba(15,23,42,0.5)",
      display: "flex", justifyContent: "flex-end", zIndex: 100,
    }} onClick={onClose}>
      <div onClick={e => e.stopPropagation()} style={{
        width: 420, background: "#fff", height: "100%", overflowY: "auto",
        boxShadow: "-10px 0 40px rgba(0,0,0,0.15)", padding: 28,
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: 20 }}>
          <div>
            <h3 style={{ margin: "0 0 4px", color: "#0f172a" }}>{lead.name}</h3>
            <StageBadge stage={lead.stage} />
          </div>
          <button onClick={onClose} style={{ background: "none", border: "none", fontSize: 20, cursor: "pointer", color: "#94a3b8" }}>✕</button>
        </div>

        {[
          ["📍 Address", lead.address],
          ["📞 Phone", lead.phone],
          ["📧 Email", lead.owner_email],
          ["⭐ Rating", lead.rating ? `${lead.rating}★ (${lead.review_count} reviews)` : "—"],
          ["🏙️ City", lead.city],
          ["🔧 Niche", lead.niche],
        ].map(([label, val]) => val && (
          <div key={label} style={{ marginBottom: 10, display: "flex", gap: 8, fontSize: 13 }}>
            <span style={{ color: "#94a3b8", minWidth: 100 }}>{label}</span>
            <span style={{ color: "#1e293b", fontWeight: 500 }}>{val}</span>
          </div>
        ))}

        {lead.preview_url && (
          <a href={lead.preview_url} target="_blank" rel="noreferrer" style={{
            display: "block", marginTop: 16, padding: "10px 16px", borderRadius: 8,
            background: "#f5f3ff", color: "#6366f1", textDecoration: "none",
            fontWeight: 600, fontSize: 13, textAlign: "center",
          }}>🌐 View Website Preview →</a>
        )}

        <div style={{ marginTop: 24 }}>
          <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#475569", marginBottom: 6 }}>Stage</label>
          <select value={stage} onChange={e => setStage(e.target.value)} style={{
            width: "100%", padding: "10px 14px", borderRadius: 8,
            border: "1.5px solid #e2e8f0", fontSize: 14, color: "#0f172a",
          }}>
            {STAGES.map(s => <option key={s} value={s}>{STAGE_META[s].label}</option>)}
          </select>
        </div>

        <div style={{ marginTop: 16 }}>
          <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#475569", marginBottom: 6 }}>Notes</label>
          <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={4} style={{
            width: "100%", boxSizing: "border-box", padding: "10px 14px",
            border: "1.5px solid #e2e8f0", borderRadius: 8, fontSize: 14,
            resize: "vertical", color: "#0f172a", fontFamily: "inherit",
          }} />
        </div>

        <button onClick={save} disabled={saving} style={{
          width: "100%", marginTop: 16, padding: "12px 0", borderRadius: 8,
          border: "none", background: saving ? "#a5b4fc" : "#6366f1",
          color: "#fff", fontWeight: 700, fontSize: 14, cursor: "pointer",
        }}>
          {saving ? "Saving…" : "Save Changes"}
        </button>
      </div>
    </div>
  );
}

// ── Stat Card ──────────────────────────────────────────────────

function StatCard({ label, value, sub, accent }) {
  return (
    <div style={{
      background: "#fff", border: "1.5px solid #e2e8f0", borderRadius: 12,
      padding: "18px 20px", flex: 1, minWidth: 120,
    }}>
      <p style={{ margin: "0 0 4px", fontSize: 11, fontWeight: 700, textTransform: "uppercase",
        letterSpacing: "0.06em", color: "#94a3b8" }}>{label}</p>
      <p style={{ margin: 0, fontSize: 28, fontWeight: 800, color: accent || "#0f172a" }}>{value}</p>
      {sub && <p style={{ margin: "4px 0 0", fontSize: 12, color: "#64748b" }}>{sub}</p>}
    </div>
  );
}

// ── Main App ───────────────────────────────────────────────────

export default function App() {
  const [tab, setTab] = useState("pipeline");
  const [showLaunch, setShowLaunch] = useState(false);
  const [selectedLead, setSelectedLead] = useState(null);
  const [counts, setCounts] = useState({});
  const [refreshKey, setRefreshKey] = useState(0);

  const refresh = useCallback(() => setRefreshKey(k => k + 1), []);

  useEffect(() => {
    apiFetch("/leads/pipeline").then(setCounts).catch(console.error);
  }, [refreshKey]);

  const totalLeads   = Object.values(counts).reduce((a, b) => a + b, 0);
  const totalClosed  = counts.closed || 0;
  const totalReplied = (counts.replied || 0) + (counts.interested || 0);

  const TABS = [
    { id: "pipeline", label: "Pipeline" },
    { id: "inbox",    label: "Inbox" },
    { id: "activity", label: "Activity" },
    { id: "jobs",     label: "Campaigns" },
  ];

  return (
    <div style={{ minHeight: "100vh", background: "#f8fafc", fontFamily: "'Inter', system-ui, sans-serif" }}>
      <style>{`* { box-sizing: border-box; } body { margin: 0; }`}</style>

      {/* ── Top nav ── */}
      <nav style={{
        background: "#0f172a", color: "#fff", padding: "0 28px",
        display: "flex", alignItems: "center", gap: 0, height: 56,
      }}>
        <span style={{ fontWeight: 800, fontSize: 15, letterSpacing: "-0.02em", marginRight: 32, color: "#e0e7ff" }}>
          ⚡ ProspectCRM
        </span>
        {TABS.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)} style={{
            padding: "0 16px", height: 56, border: "none", background: "none", cursor: "pointer",
            fontSize: 13, fontWeight: 600, color: tab === t.id ? "#fff" : "#64748b",
            borderBottom: `2px solid ${tab === t.id ? "#818cf8" : "transparent"}`,
          }}>{t.label}</button>
        ))}
        <button onClick={() => setShowLaunch(true)} style={{
          marginLeft: "auto", padding: "8px 18px", borderRadius: 8,
          background: "#6366f1", border: "none", color: "#fff",
          cursor: "pointer", fontWeight: 700, fontSize: 13,
        }}>+ New Campaign</button>
      </nav>

      {/* ── Stats bar ── */}
      <div style={{ background: "#fff", borderBottom: "1.5px solid #e2e8f0", padding: "16px 28px" }}>
        <div style={{ display: "flex", gap: 12, maxWidth: 900 }}>
          <StatCard label="Total Leads" value={totalLeads} />
          <StatCard label="Replies" value={totalReplied} sub="interested or replied" accent="#d97706" />
          <StatCard label="Closed" value={totalClosed} sub="paid customers" accent="#16a34a" />
          <StatCard label="Pending Email" value={counts.email_sent || 0} sub="awaiting reply" accent="#7c3aed" />
        </div>
      </div>

      {/* ── Main content ── */}
      <main style={{ padding: "28px 28px", maxWidth: 1100, margin: "0 auto" }}>
        <div key={`${tab}-${refreshKey}`}>
          {tab === "pipeline" && <PipelineView key={refreshKey} onSelectLead={setSelectedLead} />}
          {tab === "inbox"    && <InboxView onSelectLead={setSelectedLead} />}
          {tab === "activity" && <ActivityFeedView />}
          {tab === "jobs"     && <JobsView />}
        </div>
      </main>

      {/* ── Modals / drawers ── */}
      {showLaunch && (
        <LaunchModal onClose={() => setShowLaunch(false)} onLaunched={() => { refresh(); setTab("jobs"); }} />
      )}
      {selectedLead && (
        <LeadDrawer lead={selectedLead} onClose={() => setSelectedLead(null)} onStageChange={refresh} />
      )}
    </div>
  );
}
"""

# ── Streamlit Page Configuration ──────────────────────────────
st.set_page_config(
    page_title="ProspectCRM",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Render React Component in Streamlit ──────────────────────
st.title("ProspectCRM Dashboard")
st.markdown("---")

# Render the React component using streamlit.components.v1
components.html(
    f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
        <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
        <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    </head>
    <body>
        <div id="root"></div>
        <script type="text/babel">
            {REACT_APP}
            const root = ReactDOM.createRoot(document.getElementById('root'));
            root.render(<App />);
        </script>
    </body>
    </html>
    """,
    height=1200
)
