"""
ΣΦΕ UW–Madison Fall 2026 Recruitment Tracker
=============================================
Setup:
    pip install streamlit pandas

Run:
    streamlit run app.py
"""

import streamlit as st
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
# TAB 3 — MASS DELETE  (fast: single form, no per-checkbox reruns)
# ════════════════════════════════════════════════════════════════════════════
with tab_bulk:
    st.markdown('<div class="section-hdr">Mass Delete</div>', unsafe_allow_html=True)

    if not st.session_state.pnms:
        st.info("No PNMs in the database yet.")
    else:
        # ── Pre-select shortcuts (outside form so they fire instantly) ────
        st.markdown("**Step 1 — Use a shortcut or tick boxes below, then hit Delete.**")
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        qa, qb, qc, qd, qe = st.columns(5)
        with qa:
            if st.button("✅ All", use_container_width=True):
                st.session_state.selected_ids = {p["id"] for p in st.session_state.pnms}
                st.rerun()
        with qb:
            if st.button("☐ None", use_container_width=True):
                st.session_state.selected_ids = set()
                st.rerun()
        with qc:
            if st.button("📬 Responded", use_container_width=True):
                st.session_state.selected_ids = {p["id"] for p in st.session_state.pnms if p.get("dm_status") == "Responded"}
                st.rerun()
        with qd:
            if st.button("⏳ Waiting", use_container_width=True):
                st.session_state.selected_ids = {p["id"] for p in st.session_state.pnms if p.get("dm_status") == "Waiting on response"}
                st.rerun()
        with qe:
            if st.button("🔕 Not contacted", use_container_width=True):
                st.session_state.selected_ids = {p["id"] for p in st.session_state.pnms if not p.get("reached") and p.get("dm_status","—") == "—"}
                st.rerun()

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # ── Single form — all checkboxes submit together, zero mid-list reruns ──
        sorted_pnms = sorted(st.session_state.pnms, key=lambda p: (p.get("lname",""), p.get("fname","")))

        with st.form("bulk_delete_form", clear_on_submit=False):

            # Table header
            st.markdown("""
            <div style='display:grid;grid-template-columns:32px 1fr 160px 140px;
                gap:0;padding:6px 4px;background:#f7f6f2;border-radius:8px 8px 0 0;
                border:1px solid rgba(0,0,0,0.09);border-bottom:none;
                font-size:11px;font-weight:600;color:#777;text-transform:uppercase;letter-spacing:.4px'>
              <div></div>
              <div>Name · Instagram · School</div>
              <div>Status</div>
              <div>Reached out</div>
            </div>
            """, unsafe_allow_html=True)

            # Rows — rendered as pure HTML, only checkboxes are Streamlit widgets
            checkbox_state = {}
            for i, p in enumerate(sorted_pnms):
                pid      = p["id"]
                name     = f"{p.get('fname','')} {p.get('lname','')}"
                ig_txt   = f"@{p['ig']}" if p.get("ig") else ""
                hs_txt   = p.get("hs","")
                meta     = " · ".join(filter(None, [ig_txt, hs_txt]))
                badge_cls, badge_lbl = STATUS_BADGE.get(p.get("dm_status","—"), ("badge-none","—"))
                reached_txt = "✅ Yes" if p.get("reached") else "—"
                row_bg   = "#fff8f8" if pid in st.session_state.selected_ids else "white"
                border_c = "#ffcccc" if pid in st.session_state.selected_ids else "rgba(0,0,0,0.09)"

                col_chk, col_info, col_status, col_reached = st.columns([0.25, 3.5, 1.2, 1.1])

                with col_chk:
                    checkbox_state[pid] = st.checkbox(
                        label=name,
                        value=pid in st.session_state.selected_ids,
                        key=f"bform_{pid}",
                        label_visibility="collapsed"
                    )
                with col_info:
                    st.markdown(
                        f"<div style='padding:4px 0;font-size:13.5px;font-weight:600'>{name}"
                        f"<span style='font-weight:400;color:#888;font-size:12px'>"
                        f"{'  ·  ' + meta if meta else ''}</span></div>",
                        unsafe_allow_html=True
                    )
                with col_status:
                    st.markdown(
                        f"<div style='padding:4px 0'><span class='badge {badge_cls}'>{badge_lbl}</span></div>",
                        unsafe_allow_html=True
                    )
                with col_reached:
                    st.markdown(
                        f"<div style='padding:4px 0;font-size:13px;color:#555'>{reached_txt}</div>",
                        unsafe_allow_html=True
                    )

                if i < len(sorted_pnms) - 1:
                    st.markdown("<hr style='margin:0;border:none;border-top:1px solid rgba(0,0,0,0.06)'>", unsafe_allow_html=True)

            # ── Submit row ────────────────────────────────────────────────
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

            # Count how many are currently ticked (based on saved state)
            preview_count = len(st.session_state.selected_ids)
            st.markdown(f"""
            <div class="delete-zone">
              <div class="delete-zone-title">⚠️ Danger zone</div>
              <div class="delete-zone-sub">
                {preview_count} PNM{'s' if preview_count != 1 else ''} currently selected.
                Ticking boxes above updates the selection — then click the button to delete.
                This cannot be undone. Export a CSV backup first if needed.
              </div>
            </div>
            """, unsafe_allow_html=True)

            submitted_delete = st.form_submit_button(
                "🗑️  Apply selection & Delete",
                type="primary",
                use_container_width=True
            )

            if submitted_delete:
                # Read all checkbox values from form submission
                to_delete = {pid for pid, checked in checkbox_state.items() if checked}
                n = len(to_delete)
                if n == 0:
                    st.warning("No PNMs selected — tick at least one box.")
                else:
                    st.session_state.pnms = [
                        p for p in st.session_state.pnms if p["id"] not in to_delete
                    ]
                    save(st.session_state.pnms)
                    st.session_state.selected_ids = set()
                    st.session_state.confirm_delete = False
                    st.success(f"✅ {n} PNM{'s' if n != 1 else ''} deleted.")
                    st.rerun()

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
