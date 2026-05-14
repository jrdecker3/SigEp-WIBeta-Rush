"""
ΣΦΕ UW–Madison Fall 2026 Recruitment Tracker
=============================================
Setup:
    pip install streamlit pandas

Run:
    streamlit run app.py
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json, os, datetime

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SigEp Rush 2026",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; }

.top-banner {
    background: linear-gradient(135deg, #CC0000 0%, #990000 100%);
    border-radius: 12px; padding: 1.1rem 1.5rem;
    display: flex; align-items: center; gap: 14px;
    margin-bottom: 1.4rem; box-shadow: 0 4px 18px rgba(204,0,0,0.25);
}
.crest {
    width: 44px; height: 44px; background: rgba(255,255,255,0.18);
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-size: 15px; font-weight: 700; color: white; letter-spacing: 1px; flex-shrink: 0;
}
.banner-title { color: white; font-size: 18px; font-weight: 600; line-height: 1.2; }
.banner-sub   { color: rgba(255,255,255,0.75); font-size: 12px; margin-top: 2px; }

.stat-row { display: grid; grid-template-columns: repeat(5,1fr); gap: 10px; margin-bottom: 1.25rem; }
.stat-card { background: white; border-radius: 10px; border: 1px solid rgba(0,0,0,0.09); padding: .85rem 1rem; }
.stat-card.accent { border-left: 3px solid #CC0000; }
.stat-label { font-size: 11px; font-weight: 600; color: #777; text-transform: uppercase; letter-spacing: .5px; margin-bottom: 5px; }
.stat-num { font-size: 26px; font-weight: 700; color: #1a1a1a; line-height: 1; }

.section-hdr {
    font-size: 13px; font-weight: 600; color: #444;
    text-transform: uppercase; letter-spacing: .5px;
    margin-bottom: .6rem; margin-top: .2rem;
    padding-bottom: .4rem; border-bottom: 1px solid rgba(0,0,0,0.08);
}

/* Mass delete warning box */
.delete-zone {
    background: #fff5f5; border: 1.5px solid #ffcccc;
    border-radius: 10px; padding: 1rem 1.25rem; margin-bottom: 1rem;
}
.delete-zone-title { font-size: 13px; font-weight: 700; color: #b71c1c;
    text-transform: uppercase; letter-spacing: .5px; margin-bottom: .4rem; }
.delete-zone-sub { font-size: 13px; color: #666; margin-bottom: .75rem; }

.badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.badge-responded { background:#e3eeff; color:#1a4fa0; }
.badge-read      { background:#fff3e0; color:#9a5c00; }
.badge-waiting   { background:#ffeaea; color:#b71c1c; }
.badge-none      { background:#f0efeb; color:#555; }

.pnm-card {
    background: white; border-radius: 10px;
    border: 1px solid rgba(0,0,0,0.09);
    padding: .9rem 1.1rem; margin-bottom: .55rem;
}
.pnm-card.selected { border-color: #CC0000; background: #fff8f8; }
.pnm-name { font-size: 15px; font-weight: 600; color: #1a1a1a; }
.pnm-ig   { font-size: 13px; color: #CC0000; font-weight: 500; }
.pnm-meta { font-size: 12px; color: #888; margin-top: 3px; }

div[data-testid="stCheckbox"] > label { font-size: 14px !important; }
div[data-testid="stSelectbox"] > label { font-size: 12px !important; font-weight: 600 !important; }
div[data-testid="stTextInput"] > label { font-size: 12px !important; font-weight: 600 !important; }
.stButton > button { border-radius: 7px !important; font-family: 'DM Sans', sans-serif !important; font-weight: 500 !important; }
.stButton > button[kind="primary"] { background: #CC0000 !important; border-color: #CC0000 !important; }
.stButton > button[kind="primary"]:hover { background: #990000 !important; border-color: #990000 !important; }
div[data-testid="stExpander"] { border: 1px solid rgba(0,0,0,0.09) !important; border-radius: 10px !important; background: white !important; }
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pnms.json")

def load():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE) as f:
        return json.load(f)

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def new_id():
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")

if "pnms" not in st.session_state:
    st.session_state.pnms = load()
if "selected_ids" not in st.session_state:
    st.session_state.selected_ids = set()
if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = False

STATUS_OPTS = ["—", "Waiting on response", "Read", "Responded"]
STATUS_BADGE = {
    "—":                   ("badge-none",      "Not contacted"),
    "Waiting on response": ("badge-waiting",   "Waiting on response"),
    "Read":                ("badge-read",      "Read"),
    "Responded":           ("badge-responded", "Responded"),
}

def status_badge(s):
    cls, label = STATUS_BADGE.get(s, ("badge-none", s))
    return f'<span class="badge {cls}">{label}</span>'

# ── Banner ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-banner">
  <div class="crest">ΣΦΕ</div>
  <div>
    <div class="banner-title">Sigma Phi Epsilon — UW Madison</div>
    <div class="banner-sub">Fall 2026 Rush · Potential New Member Tracker</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Stats ─────────────────────────────────────────────────────────────────────
pnms = st.session_state.pnms
total     = len(pnms)
reached   = sum(1 for p in pnms if p.get("reached"))
responded = sum(1 for p in pnms if p.get("dm_status") == "Responded")
waiting   = sum(1 for p in pnms if p.get("dm_status") == "Waiting on response")
read_ct   = sum(1 for p in pnms if p.get("dm_status") == "Read")

st.markdown(f"""
<div class="stat-row">
  <div class="stat-card accent"><div class="stat-label">Total PNMs</div><div class="stat-num">{total}</div></div>
  <div class="stat-card"><div class="stat-label">Reached Out</div><div class="stat-num">{reached}</div></div>
  <div class="stat-card"><div class="stat-label">Responded</div><div class="stat-num">{responded}</div></div>
  <div class="stat-card"><div class="stat-label">Read / Seen</div><div class="stat-num">{read_ct}</div></div>
  <div class="stat-card"><div class="stat-label">Waiting</div><div class="stat-num">{waiting}</div></div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_list, tab_add, tab_bulk, tab_import = st.tabs([
    "📋  PNM List", "➕  Add PNM", "🗑️  Mass Delete", "📂  Import / Export"
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — PNM LIST
# ════════════════════════════════════════════════════════════════════════════
with tab_list:
    col_s, col_f, col_r = st.columns([3, 1.5, 1])
    with col_s:
        search = st.text_input("🔍 Search", placeholder="Name, school, city, interests...", label_visibility="collapsed")
    with col_f:
        filt = st.selectbox("Filter", ["All", "Not contacted", "Waiting on response", "Read", "Responded"], label_visibility="collapsed")
    with col_r:
        sort_by = st.selectbox("Sort", ["Name", "Date added", "Status"], label_visibility="collapsed")

    visible = list(st.session_state.pnms)
    if search:
        q = search.lower()
        visible = [p for p in visible if q in " ".join([
            p.get("fname",""), p.get("lname",""), p.get("ig",""),
            p.get("hs",""), p.get("city",""), p.get("interests",""),
            p.get("activities",""), p.get("notes","")
        ]).lower()]
    if filt != "All":
        if filt == "Not contacted":
            visible = [p for p in visible if not p.get("reached") and p.get("dm_status","—") == "—"]
        else:
            visible = [p for p in visible if p.get("dm_status","—") == filt]
    if sort_by == "Name":
        visible.sort(key=lambda p: (p.get("lname",""), p.get("fname","")))
    elif sort_by == "Date added":
        visible.sort(key=lambda p: p.get("added",""), reverse=True)
    elif sort_by == "Status":
        order = {"Responded":0,"Read":1,"Waiting on response":2,"—":3}
        visible.sort(key=lambda p: order.get(p.get("dm_status","—"), 4))

    st.markdown(f"<div style='font-size:12.5px;color:#888;margin-bottom:.75rem'>{len(visible)} of {total} PNMs</div>", unsafe_allow_html=True)

    if not visible:
        st.info("No PNMs match your search. Adjust the filter or add someone in the Add PNM tab.")

    for p in visible:
        real_idx = next((i for i, x in enumerate(st.session_state.pnms) if x["id"] == p["id"]), None)
        if real_idx is None:
            continue

        ig_url = f"https://instagram.com/{p['ig']}" if p.get("ig") else None
        ig_display = f"@{p['ig']}" if p.get("ig") else "—"
        meta_parts = [x for x in [p.get("hs"), p.get("city"), p.get("major")] if x]
        meta_str = "  ·  ".join(meta_parts) if meta_parts else ""

        st.markdown(f"""
        <div class="pnm-card">
          <div style="display:flex;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;gap:6px">
            <div>
              <div class="pnm-name">{p.get('fname','')} {p.get('lname','')}</div>
              {'<a class="pnm-ig" href="' + ig_url + '" target="_blank">' + ig_display + ' ↗</a>' if ig_url else f'<div class="pnm-meta">{ig_display}</div>'}
              {'<div class="pnm-meta">' + meta_str + '</div>' if meta_str else ''}
            </div>
            <div>{status_badge(p.get("dm_status","—"))}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4, c5 = st.columns([1.2, 1.8, 2.5, 1, 1])

        with c1:
            reached_val = st.checkbox("Reached out", value=p.get("reached", False), key=f"reached_{p['id']}")
            if reached_val != p.get("reached", False):
                st.session_state.pnms[real_idx]["reached"] = reached_val
                save(st.session_state.pnms)
                st.rerun()

        with c2:
            cur_status = p.get("dm_status", "—")
            new_status = st.selectbox("DM Status", STATUS_OPTS,
                index=STATUS_OPTS.index(cur_status) if cur_status in STATUS_OPTS else 0,
                key=f"status_{p['id']}", label_visibility="collapsed")
            if new_status != cur_status:
                st.session_state.pnms[real_idx]["dm_status"] = new_status
                if new_status != "—":
                    st.session_state.pnms[real_idx]["reached"] = True
                save(st.session_state.pnms)
                st.rerun()

        with c3:
            notes_val = st.text_input("Notes", value=p.get("notes",""),
                placeholder="Add a note...", key=f"notes_{p['id']}", label_visibility="collapsed")
            if notes_val != p.get("notes",""):
                st.session_state.pnms[real_idx]["notes"] = notes_val
                save(st.session_state.pnms)

        with c4:
            with st.expander("Details"):
                st.caption(f"**High School:** {p.get('hs') or '—'}")
                st.caption(f"**Hometown:** {p.get('city') or '—'}")
                st.caption(f"**Major:** {p.get('major') or '—'}")
                st.caption(f"**Activities:** {p.get('activities') or '—'}")
                st.caption(f"**Interests:** {p.get('interests') or '—'}")
                st.caption(f"**Added:** {p.get('added') or '—'}")

        with c5:
            if st.button("🗑", key=f"del_{p['id']}", help="Remove this PNM"):
                st.session_state.pnms = [x for x in st.session_state.pnms if x["id"] != p["id"]]
                st.session_state.selected_ids.discard(p["id"])
                save(st.session_state.pnms)
                st.rerun()

        st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — ADD PNM
# ════════════════════════════════════════════════════════════════════════════
with tab_add:
    st.markdown('<div class="section-hdr">New Potential New Member</div>', unsafe_allow_html=True)

    with st.form("add_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1: fname = st.text_input("First name *", placeholder="Jake")
        with c2: lname = st.text_input("Last name *", placeholder="Smith")
        with c3: ig    = st.text_input("Instagram handle", placeholder="@jakesmith")

        c4, c5, c6 = st.columns(3)
        with c4: hs    = st.text_input("High school", placeholder="Waukesha South HS")
        with c5: city  = st.text_input("Hometown", placeholder="Waukesha, WI")
        with c6: major = st.text_input("Intended major", placeholder="Business")

        c7, c8, c9 = st.columns(3)
        with c7: activities = st.text_input("Sports / activities", placeholder="Football, NHS")
        with c8: interests  = st.text_input("Interests", placeholder="Finance, outdoors, golf")
        with c9: dm_status  = st.selectbox("DM Status", STATUS_OPTS)

        notes = st.text_area("Notes", placeholder="Mutual connections, events attended, anything useful...", height=90)
        submitted = st.form_submit_button("Add to database", type="primary", use_container_width=True)

        if submitted:
            if not fname.strip() or not lname.strip():
                st.error("First and last name are required.")
            else:
                entry = {
                    "id": new_id(), "fname": fname.strip(), "lname": lname.strip(),
                    "ig": ig.strip().lstrip("@"), "hs": hs.strip(), "city": city.strip(),
                    "major": major.strip(), "activities": activities.strip(),
                    "interests": interests.strip(), "notes": notes.strip(),
                    "dm_status": dm_status, "reached": dm_status != "—",
                    "added": datetime.datetime.now().strftime("%m/%d/%Y"),
                }
                st.session_state.pnms.append(entry)
                save(st.session_state.pnms)
                st.success(f"✅ {fname} {lname} added to the database!")
                st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — MASS DELETE  (pure HTML/JS — zero Streamlit rerenders on checkbox)
# ════════════════════════════════════════════════════════════════════════════
with tab_bulk:
    st.markdown('<div class="section-hdr">Mass Delete</div>', unsafe_allow_html=True)

    if not st.session_state.pnms:
        st.info("No PNMs in the database yet.")
    else:
        sorted_pnms = sorted(
            st.session_state.pnms,
            key=lambda p: (p.get("lname",""), p.get("fname",""))
        )

        # Build JSON for JS to consume
        pnm_json = json.dumps([{
            "id":      p["id"],
            "name":    f"{p.get('fname','')} {p.get('lname','')}",
            "ig":      p.get("ig",""),
            "hs":      p.get("hs",""),
            "status":  p.get("dm_status","—"),
            "reached": p.get("reached", False),
        } for p in sorted_pnms])

        # Render the whole UI as a single HTML blob — JS handles everything
        st.components.v1.html(f"""
<!DOCTYPE html>
<html>
<head>
<style>
  *{{box-sizing:border-box;margin:0;padding:0;font-family:'DM Sans',system-ui,sans-serif}}
  body{{background:transparent;padding:0}}
  .toolbar{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px}}
  .qbtn{{padding:7px 14px;border-radius:7px;border:1px solid rgba(0,0,0,0.15);
    background:#fff;font-size:13px;font-weight:500;cursor:pointer;transition:background .1s}}
  .qbtn:hover{{background:#f0efeb}}
  .counter{{margin-left:auto;display:flex;align-items:center;font-size:13px;
    color:#666;font-weight:500;white-space:nowrap}}
  .tbl{{width:100%;border-collapse:collapse;font-size:13.5px}}
  .tbl thead th{{text-align:left;font-size:11px;font-weight:600;color:#777;
    text-transform:uppercase;letter-spacing:.4px;padding:8px 10px;
    background:#f7f6f2;border-bottom:1px solid rgba(0,0,0,0.09)}}
  .tbl tbody tr{{border-bottom:1px solid rgba(0,0,0,0.06);transition:background .08s}}
  .tbl tbody tr:hover{{background:#faf9f6}}
  .tbl tbody tr.selected{{background:#fff8f8}}
  .tbl td{{padding:9px 10px;vertical-align:middle}}
  .tbl td input[type=checkbox]{{width:16px;height:16px;cursor:pointer;accent-color:#CC0000}}
  .name{{font-weight:600;color:#1a1a1a}}
  .meta{{font-size:12px;color:#888;margin-top:2px}}
  .badge{{display:inline-block;padding:2px 9px;border-radius:20px;font-size:11.5px;font-weight:600}}
  .badge-none      {{background:#f0efeb;color:#555}}
  .badge-responded {{background:#e3eeff;color:#1a4fa0}}
  .badge-read      {{background:#fff3e0;color:#9a5c00}}
  .badge-waiting   {{background:#ffeaea;color:#b71c1c}}
  .danger{{background:#fff5f5;border:1.5px solid #ffcccc;border-radius:10px;
    padding:14px 16px;margin-top:14px}}
  .danger-title{{font-size:12px;font-weight:700;color:#b71c1c;
    text-transform:uppercase;letter-spacing:.5px;margin-bottom:5px}}
  .danger-sub{{font-size:13px;color:#666;margin-bottom:12px}}
  .del-btn{{width:100%;padding:11px;border-radius:8px;border:none;
    background:#CC0000;color:#fff;font-size:14px;font-weight:600;
    cursor:pointer;transition:background .15s}}
  .del-btn:hover{{background:#990000}}
  .del-btn:disabled{{background:#ccc;cursor:not-allowed}}
  .confirm-row{{display:none;gap:10px;margin-top:10px}}
  .confirm-row.show{{display:flex}}
  .confirm-yes{{flex:1;padding:10px;border-radius:8px;border:none;
    background:#b71c1c;color:#fff;font-size:13.5px;font-weight:600;cursor:pointer}}
  .confirm-no{{flex:1;padding:10px;border-radius:8px;
    border:1px solid rgba(0,0,0,0.15);background:#fff;
    font-size:13.5px;font-weight:500;cursor:pointer}}
  .warn{{color:#b71c1c;font-size:13px;font-weight:600;margin-bottom:8px;display:none}}
  .warn.show{{display:block}}
</style>
</head>
<body>

<div class="toolbar">
  <button class="qbtn" onclick="selectAll()">✅ All</button>
  <button class="qbtn" onclick="selectNone()">☐ None</button>
  <button class="qbtn" onclick="selectByStatus('Responded')">📬 Responded</button>
  <button class="qbtn" onclick="selectByStatus('Waiting on response')">⏳ Waiting</button>
  <button class="qbtn" onclick="selectNotContacted()">🔕 Not contacted</button>
  <div class="counter"><span id="counter">0 selected</span></div>
</div>

<table class="tbl">
  <thead>
    <tr>
      <th style="width:36px"></th>
      <th>Name · Instagram · School</th>
      <th>Status</th>
      <th>Reached out</th>
    </tr>
  </thead>
  <tbody id="tbody"></tbody>
</table>

<div class="danger">
  <div class="danger-title">⚠️ Danger zone</div>
  <div class="danger-sub">Deletions are permanent. Export a CSV backup first if needed.</div>
  <div class="warn" id="warn">Please select at least one PNM.</div>
  <button class="del-btn" id="delBtn" onclick="startDelete()">🗑️ Delete selected</button>
  <div class="confirm-row" id="confirmRow">
    <button class="confirm-no"  onclick="cancelDelete()">Cancel</button>
    <button class="confirm-yes" id="confirmYes">Yes, delete them</button>
  </div>
</div>

<script>
const DATA = {pnm_json};
const BADGE = {{
  '—':                   ['badge-none',      'Not contacted'],
  'Waiting on response': ['badge-waiting',   'Waiting on response'],
  'Read':                ['badge-read',      'Read'],
  'Responded':           ['badge-responded', 'Responded'],
}};

// Render table rows
const tbody = document.getElementById('tbody');
DATA.forEach(p => {{
  const [bcls, blbl] = BADGE[p.status] || ['badge-none', p.status];
  const meta = [p.ig ? '@'+p.ig : '', p.hs].filter(Boolean).join(' · ');
  const tr = document.createElement('tr');
  tr.dataset.id     = p.id;
  tr.dataset.status = p.status;
  tr.dataset.reached= p.reached ? '1' : '0';
  tr.innerHTML = `
    <td><input type="checkbox" onchange="onCheck(this)"></td>
    <td>
      <div class="name">${{p.name}}</div>
      ${{meta ? `<div class="meta">${{meta}}</div>` : ''}}
    </td>
    <td><span class="badge ${{bcls}}">${{blbl}}</span></td>
    <td style="font-size:13px;color:#555">${{p.reached ? '✅ Yes' : '—'}}</td>
  `;
  tbody.appendChild(tr);
}});

function getChecked() {{
  return [...document.querySelectorAll('#tbody input[type=checkbox]:checked')]
    .map(cb => cb.closest('tr').dataset.id);
}}
function updateCounter() {{
  const n = getChecked().length;
  document.getElementById('counter').textContent = n + ' selected';
  document.getElementById('delBtn').disabled = n === 0;
}}
function onCheck(cb) {{
  cb.closest('tr').classList.toggle('selected', cb.checked);
  updateCounter();
  // reset confirm if user changes selection
  document.getElementById('confirmRow').classList.remove('show');
}}

function selectAll()  {{ setAll(true)  }}
function selectNone() {{ setAll(false) }}
function setAll(val) {{
  document.querySelectorAll('#tbody input[type=checkbox]').forEach(cb => {{
    cb.checked = val;
    cb.closest('tr').classList.toggle('selected', val);
  }});
  updateCounter();
  document.getElementById('confirmRow').classList.remove('show');
}}
function selectByStatus(status) {{
  document.querySelectorAll('#tbody tr').forEach(tr => {{
    const match = tr.dataset.status === status;
    tr.querySelector('input').checked = match;
    tr.classList.toggle('selected', match);
  }});
  updateCounter();
  document.getElementById('confirmRow').classList.remove('show');
}}
function selectNotContacted() {{
  document.querySelectorAll('#tbody tr').forEach(tr => {{
    const match = tr.dataset.status === '—' && tr.dataset.reached === '0';
    tr.querySelector('input').checked = match;
    tr.classList.toggle('selected', match);
  }});
  updateCounter();
  document.getElementById('confirmRow').classList.remove('show');
}}

function startDelete() {{
  const ids = getChecked();
  if (ids.length === 0) {{
    document.getElementById('warn').classList.add('show');
    return;
  }}
  document.getElementById('warn').classList.remove('show');
  const btn = document.getElementById('confirmYes');
  btn.textContent = `Yes, delete ${{ids.length}} PNM${{ids.length !== 1 ? 's' : ''}}`;
  document.getElementById('confirmRow').classList.add('show');
  btn.onclick = () => doDelete(ids);
}}
function cancelDelete() {{
  document.getElementById('confirmRow').classList.remove('show');
}}

function doDelete(ids) {{
  // Write IDs into a hidden Streamlit text_input via DOM, then trigger change
  const joined = ids.join(',');
  // Post to parent frame via postMessage so Streamlit can catch it
  window.parent.postMessage({{type:'sigep_delete', ids: joined}}, '*');
}}

updateCounter();
</script>
</body>
</html>
""", height=min(120 + len(sorted_pnms) * 48, 800), scrolling=True)

        # ── Receive the delete message via a hidden text input ────────────
        st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
        st.caption("After selecting names above, paste the IDs here to confirm deletion — or use the typed entry below.")

        # Simpler fallback: text area where user pastes names to delete by name
        st.markdown("**Or type names to delete** (one per line, First Last):")
        with st.form("name_delete_form"):
            names_input = st.text_area(
                "Names to delete",
                placeholder="Jake Smith\nAlex Johnson\nMike Williams",
                height=120,
                label_visibility="collapsed"
            )
            col_d1, col_d2 = st.columns([3,1])
            with col_d2:
                do_delete = st.form_submit_button("🗑️ Delete", type="primary", use_container_width=True)

            if do_delete:
                lines = [l.strip().lower() for l in names_input.strip().splitlines() if l.strip()]
                if not lines:
                    st.warning("Enter at least one name.")
                else:
                    before = len(st.session_state.pnms)
                    st.session_state.pnms = [
                        p for p in st.session_state.pnms
                        if f"{p.get('fname','')} {p.get('lname','')}".lower() not in lines
                    ]
                    removed = before - len(st.session_state.pnms)
                    save(st.session_state.pnms)
                    st.session_state.selected_ids = set()
                    if removed:
                        st.success(f"✅ Deleted {removed} PNM{'s' if removed != 1 else ''}.")
                        st.rerun()
                    else:
                        st.warning("No matches found. Check spelling — use First Last format.")

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — IMPORT / EXPORT
# ════════════════════════════════════════════════════════════════════════════
with tab_import:
    col_exp, col_imp = st.columns(2)

    with col_exp:
        st.markdown('<div class="section-hdr">Export to CSV</div>', unsafe_allow_html=True)
        st.markdown("Download the full database as a spreadsheet. Open in Google Sheets or Excel.")

        if st.session_state.pnms:
            rows = []
            for p in st.session_state.pnms:
                ig_h = p.get("ig","")
                rows.append({
                    "First Name":       p.get("fname",""),
                    "Last Name":        p.get("lname",""),
                    "Instagram Handle": f"@{ig_h}" if ig_h else "",
                    "Instagram URL":    f"https://instagram.com/{ig_h}" if ig_h else "",
                    "High School":      p.get("hs",""),
                    "Hometown":         p.get("city",""),
                    "Major":            p.get("major",""),
                    "Activities":       p.get("activities",""),
                    "Interests":        p.get("interests",""),
                    "Notes":            p.get("notes",""),
                    "Reached Out":      "Yes" if p.get("reached") else "No",
                    "DM Status":        p.get("dm_status","—"),
                    "Date Added":       p.get("added",""),
                })
            df = pd.DataFrame(rows)
            st.download_button("⬇️  Download CSV", data=df.to_csv(index=False).encode(),
                file_name="sigep_recruitment_fall2026.csv", mime="text/csv",
                use_container_width=True, type="primary")
        else:
            st.info("No PNMs to export yet.")

    with col_imp:
        st.markdown('<div class="section-hdr">Import from CSV</div>', unsafe_allow_html=True)
        st.markdown("Upload a CSV exported from this app, or any spreadsheet with First Name, Last Name, Instagram Handle columns.")

        uploaded = st.file_uploader("Choose CSV file", type=["csv"], label_visibility="collapsed")
        if uploaded:
            try:
                df_in = pd.read_csv(uploaded)
                df_in.columns = [c.strip() for c in df_in.columns]
                status_map = {"Waiting on response":"Waiting on response","Read":"Read","Responded":"Responded"}
                added_count = 0
                for _, row in df_in.iterrows():
                    fn = str(row.get("First Name","")).strip()
                    ln = str(row.get("Last Name","")).strip()
                    if not fn or not ln or fn == "nan": continue
                    ig_i = str(row.get("Instagram Handle","")).strip().lstrip("@")
                    if ig_i == "nan": ig_i = ""
                    entry = {
                        "id":         new_id() + str(added_count),
                        "fname":      fn, "lname": ln, "ig": ig_i,
                        "hs":         str(row.get("High School","")).strip().replace("nan",""),
                        "city":       str(row.get("Hometown","")).strip().replace("nan",""),
                        "major":      str(row.get("Major","")).strip().replace("nan",""),
                        "activities": str(row.get("Activities","")).strip().replace("nan",""),
                        "interests":  str(row.get("Interests","")).strip().replace("nan",""),
                        "notes":      str(row.get("Notes","")).strip().replace("nan",""),
                        "dm_status":  status_map.get(str(row.get("DM Status","")).strip(), "—"),
                        "reached":    str(row.get("Reached Out","")).strip().lower() == "yes",
                        "added":      str(row.get("Date Added", datetime.datetime.now().strftime("%m/%d/%Y"))).strip(),
                    }
                    st.session_state.pnms.append(entry)
                    added_count += 1
                save(st.session_state.pnms)
                st.success(f"✅ Imported {added_count} PNM(s) successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Import failed: {e}")
