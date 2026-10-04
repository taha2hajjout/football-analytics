import os, sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import streamlit as st
from pymongo import MongoClient
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="PL Analytics", page_icon="⚽", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@600;700&family=Inter:wght@400;500;600&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap');

/* ── Base ── */
html, body, .stApp, p, div, label { font-family: 'Inter', sans-serif !important; }

/* ── Sidebar arrows: font restore + no-font fallback ── */
.material-symbols-rounded {
    font-family: 'Material Symbols Rounded' !important;
    font-feature-settings: 'liga' 1 !important;
    font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24 !important;
    font-style: normal; letter-spacing: normal; text-transform: none;
    white-space: nowrap; -webkit-font-smoothing: antialiased;
    display: inline-block;
}
[data-testid="collapsedControl"] button .material-symbols-rounded,
section[data-testid="stSidebar"] button .material-symbols-rounded {
    font-size: 0 !important; color: transparent !important;
    display: inline-block; width: 20px; height: 20px;
}
[data-testid="collapsedControl"] button .material-symbols-rounded::after {
    content: "▶"; font-size: 18px; color: #8892b0; font-family: Arial, sans-serif !important;
}
section[data-testid="stSidebar"] button .material-symbols-rounded::after {
    content: "◀"; font-size: 18px; color: #8892b0; font-family: Arial, sans-serif !important;
}

/* page header */
.ph { margin-bottom: 1.5rem; }
.ph h2 {
    font-family: 'Oswald', sans-serif !important;
    font-size: 1.9rem; font-weight: 700; letter-spacing: 1px;
    text-transform: uppercase; margin: 0;
    background: linear-gradient(90deg, #e8edf5 0%, #00ff9d 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.ph p { color: #8892b0; font-size: 0.82rem; margin: 4px 0 0; }

/* stat card */
.sc {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 16px 20px;
}
.sc .lbl { color: #8892b0; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; }
.sc .val { font-family: 'Oswald', sans-serif; font-size: 1.8rem; font-weight: 700; color: #e8edf5; }
.sc .sub { font-size: 0.75rem; color: #4a5568; margin-top: 2px; }

/* zone legend */
.zleg { display: flex; gap: 16px; margin: 8px 0 16px; flex-wrap: wrap; }
.zi   { display: flex; align-items: center; gap: 6px; font-size: 0.72rem; color: #8892b0; }
.zd   { width: 10px; height: 10px; border-radius: 2px; }

/* form badges */
.fb {
    display: inline-flex; align-items: center; justify-content: center;
    width: 20px; height: 20px; border-radius: 50%;
    font-size: 0.62rem; font-weight: 700; margin: 0 1px;
}
.fw { background: rgba(0,255,157,0.15); color: #00ff9d; border: 1px solid rgba(0,255,157,0.35); }
.fd { background: rgba(255,159,28,0.15); color: #ff9f1c; border: 1px solid rgba(255,159,28,0.3); }
.fl { background: rgba(255,77,109,0.15); color: #ff4d6d; border: 1px solid rgba(255,77,109,0.3); }

/* standings table */
.stbl { width: 100%; border-collapse: collapse; }
.stbl th {
    font-size: 0.68rem; text-transform: uppercase; letter-spacing: 1px;
    color: #4a5568; padding: 8px 10px; border-bottom: 1px solid rgba(255,255,255,0.07);
    text-align: center; font-weight: 500;
}
.stbl th.tl { text-align: left; }
.stbl td { padding: 10px 10px; text-align: center; font-size: 0.87rem; color: #e8edf5; }
.stbl td.tl { text-align: left; }
.stbl tr { border-bottom: 1px solid rgba(255,255,255,0.03); transition: background 0.15s; }
.stbl tr:hover { background: rgba(255,255,255,0.04) !important; }
.pn  { font-family: 'Oswald', sans-serif; font-weight: 700; color: #4a5568; }
.tn  { font-weight: 600; }
.pts { font-family: 'Oswald', sans-serif; font-weight: 700; color: #ffd166; }
.gdp { color: #00ff9d; }
.gdn { color: #ff4d6d; }
.gd0 { color: #8892b0; }
.zcl  { border-left: 3px solid #4f7fff; background: rgba(79,127,255,0.08); }
.zel  { border-left: 3px solid #ff9f1c; background: rgba(255,159,28,0.08); }
.zrl  { border-left: 3px solid #ff4d6d; background: rgba(255,77,109,0.08); }

/* match card */
.mc {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px; padding: 12px 18px;
    display: grid; grid-template-columns: 1fr 80px 1fr;
    align-items: center; gap: 10px; margin-bottom: 6px;
    transition: border-color 0.2s;
}
.mc:hover { border-color: rgba(255,255,255,0.12); }
.mh { text-align: right; font-weight: 600; font-size: 0.88rem; }
.ma { text-align: left;  font-weight: 600; font-size: 0.88rem; }
.ms {
    font-family: 'Oswald', sans-serif; font-weight: 700; font-size: 1.15rem;
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px; padding: 4px 0; text-align: center;
}
.ms.live { color: #00ff9d; border-color: rgba(0,255,157,0.3); }
.mdh {
    font-family: 'Oswald', sans-serif; font-size: 0.72rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 2px; color: #4a5568;
    padding: 16px 0 8px; border-bottom: 1px solid rgba(255,255,255,0.06); margin-bottom: 8px;
}
.sbf { font-size: 0.65rem; color: #4a5568; }
.sbl { font-size: 0.65rem; color: #00ff9d; font-weight: 600; }
.sbs { font-size: 0.65rem; color: #4f7fff; }

/* club header (desktop) */
.club-hdr {
    display: flex; align-items: center; gap: 24px;
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px; padding: 24px 28px; margin-bottom: 24px;
}
.club-hdr-meta {
    margin-left: auto; display: grid; grid-template-columns: 1fr 1fr;
    gap: 16px 32px; text-align: right;
}

/* prediction bars */
.pb  { display: flex; align-items: center; gap: 12px; padding: 9px 0; border-bottom: 1px solid rgba(255,255,255,0.03); }
.pbt { font-weight: 600; font-size: 0.87rem; min-width: 190px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.pbg { flex: 1; height: 9px; background: rgba(255,255,255,0.05); border-radius: 999px; overflow: hidden; }
.pbf { height: 100%; border-radius: 999px; }
.ppp { font-family: 'Oswald', sans-serif; font-weight: 700; font-size: 0.95rem; min-width: 48px; text-align: right; }

/* podium */
.pod {
    border-radius: 14px; padding: 20px 16px; text-align: center;
    border: 1px solid rgba(255,255,255,0.1);
}
.pod1 { background: linear-gradient(160deg,rgba(255,209,102,0.1),rgba(255,209,102,0.03)); border-color: rgba(255,209,102,0.3); }
.pod2 { background: linear-gradient(160deg,rgba(200,215,235,0.07),rgba(200,215,235,0.02)); border-color: rgba(200,215,235,0.2); }
.pod3 { background: linear-gradient(160deg,rgba(205,127,50,0.08),rgba(205,127,50,0.02)); border-color: rgba(205,127,50,0.2); }
.pod-medal { font-size: 2rem; }
.pod-team  { font-family: 'Oswald', sans-serif; font-size: 0.95rem; font-weight: 600; margin: 8px 0 4px; text-transform: uppercase; letter-spacing: 0.5px; }
.pod-pct   { font-family: 'Oswald', sans-serif; font-size: 2rem; font-weight: 700; }
.pod1 .pod-pct { color: #ffd166; }
.pod2 .pod-pct { color: #c8d7eb; }
.pod3 .pod-pct { color: #cd7f32; }
.pod-lbl { font-size: 0.68rem; color: #4a5568; text-transform: uppercase; letter-spacing: 1px; }

/* ══════════════════════════════════════════════════
   MOBILE  ≤ 768px  (phones + small tablets)
══════════════════════════════════════════════════ */
@media (max-width: 768px) {

  /* hide sidebar + toggle button entirely */
  section[data-testid="stSidebar"],
  [data-testid="stSidebar"],
  [data-testid="collapsedControl"] { display: none !important; }

  /* full-width main area + room for bottom nav */
  [data-testid="stAppViewContainer"] > section { flex: 1 1 100% !important; max-width: 100% !important; }
  [data-testid="block-container"], .stMainBlockContainer {
      padding: 0.75rem 0.75rem 74px !important;
      max-width: 100vw !important; width: 100% !important;
  }

  /* stack ALL Streamlit columns → full width */
  [data-testid="stHorizontalBlock"]                            { flex-wrap: wrap !important; gap: 8px !important; }
  [data-testid="stHorizontalBlock"] > [data-testid="column"]  { min-width: 100% !important; flex: 1 1 100% !important; }

  /* page header */
  .ph { margin-bottom: 1rem; }
  .ph h2 { font-size: 1.35rem; }
  .ph p  { font-size: 0.73rem; }

  /* stat cards: 2×2 grid using flex-wrap on the column block
     (each .sc fills its stacked column — full width looks clean) */
  .sc           { padding: 11px 14px; border-radius: 10px; }
  .sc .lbl      { font-size: 0.62rem; }
  .sc .val      { font-size: 1.4rem; }
  .sc .sub      { font-size: 0.7rem; }

  /* standings — horizontal scroll, smaller text */
  .stbl-wrap    { overflow-x: auto; -webkit-overflow-scrolling: touch; border-radius: 8px; }
  .stbl         { min-width: 480px; }
  .stbl th      { font-size: 0.6rem; padding: 7px 5px; }
  .stbl td      { font-size: 0.78rem; padding: 8px 5px; }
  .fb           { width: 17px; height: 17px; font-size: 0.57rem; }

  /* match cards */
  .mc           { grid-template-columns: 1fr 52px 1fr; gap: 4px; padding: 9px 9px; border-radius: 10px; }
  .mh, .ma      { font-size: 0.75rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .ms           { font-size: 0.92rem; padding: 3px 0; }
  .mdh          { font-size: 0.6rem; letter-spacing: 1.5px; }

  /* top scorers: hide chart, full-width list */
  [data-testid="stPlotlyChart"] { display: none !important; }

  /* club header: stack vertically, center-aligned */
  .club-hdr {
      flex-direction: column !important;
      text-align: center !important;
      padding: 16px 14px !important;
      gap: 12px !important;
  }
  .club-hdr-meta { margin-left: 0 !important; text-align: center !important; }

  /* prediction bars */
  .pb           { gap: 8px; }
  .pbt          { min-width: 0; width: 100px; font-size: 0.75rem; }
  .ppp          { font-size: 0.85rem; min-width: 40px; }

  /* podium cards — keep 3-col but compress */
  .pod          { padding: 11px 7px; border-radius: 11px; }
  .pod-medal    { font-size: 1.5rem; }
  .pod-team     { font-size: 0.7rem; margin: 5px 0 3px; }
  .pod-pct      { font-size: 1.5rem; }
  .pod-lbl      { font-size: 0.57rem; }

  /* mobile refresh button strip */
  .mob-refresh  { display: block !important; margin-bottom: 12px; }

}

/* ══════════════════════════════════════════════════
   EXTRA SMALL  ≤ 390px  (iPhone SE, iPhone 12/13/14/15 standard)
══════════════════════════════════════════════════ */
@media (max-width: 390px) {
  [data-testid="block-container"], .stMainBlockContainer { padding: 0.6rem 0.6rem 74px !important; }
  .ph h2        { font-size: 1.2rem; }
  .mc           { grid-template-columns: 1fr 46px 1fr; gap: 3px; padding: 8px 7px; }
  .mh, .ma      { font-size: 0.7rem; }
  .ms           { font-size: 0.85rem; }
  .pbt          { width: 85px; font-size: 0.7rem; }
  .pod          { padding: 9px 5px; }
  .pod-pct      { font-size: 1.3rem; }
  .pod-team     { font-size: 0.65rem; }
  .stbl td      { font-size: 0.72rem; padding: 7px 4px; }
  .stbl th      { font-size: 0.57rem; padding: 6px 4px; }
}

/* ══════════════════════════════════════════════════
   MINI  ≤ 320px  (iPhone SE 1st gen)
══════════════════════════════════════════════════ */
@media (max-width: 320px) {
  .ph h2        { font-size: 1.05rem; }
  .sc .val      { font-size: 1.2rem; }
  .mc           { grid-template-columns: 1fr 40px 1fr; gap: 2px; padding: 7px 5px; }
  .mh, .ma      { font-size: 0.65rem; }
  .ms           { font-size: 0.78rem; }
  /* podium: single column stacked at 320px */
  [data-testid="stHorizontalBlock"]:has(.pod) > [data-testid="column"] {
      min-width: 100% !important;
  }
  .pbt          { width: 72px; font-size: 0.65rem; }
  .ppp          { font-size: 0.75rem; min-width: 34px; }
}

/* ══════════════════════════════════════════════════
   TABLET  415px – 768px  (large phones, iPad mini)
══════════════════════════════════════════════════ */
@media (min-width: 415px) and (max-width: 768px) {
  /* stat cards — 2×2 layout: override full-stack to 50% pairs */
  [data-testid="stHorizontalBlock"] > [data-testid="column"] {
      min-width: calc(50% - 4px) !important;
      flex: 1 1 calc(50% - 4px) !important;
  }
  .pbt { width: 120px; }
}

/* ══════════════════════════════════════════════════
   BOTTOM NAV — mobile only
══════════════════════════════════════════════════ */
.mob-nav        { display: none; }
.mob-refresh    { display: none; }

@media (max-width: 768px) {
  .mob-nav {
      display: flex !important;
      position: fixed; bottom: 0; left: 0; right: 0; z-index: 99999;
      background: #0d1221;
      border-top: 1px solid rgba(255,255,255,0.14);
      height: 58px;
      /* iPhone safe area */
      padding-bottom: env(safe-area-inset-bottom, 0px);
  }
  .mob-nav button {
      flex: 1; display: flex; flex-direction: column;
      align-items: center; justify-content: center; gap: 3px;
      background: none; border: none; outline: none;
      color: #4a5568; cursor: pointer;
      font-size: 0.53rem; font-weight: 700;
      text-transform: uppercase; letter-spacing: 0.4px;
      -webkit-tap-highlight-color: transparent;
      min-height: 44px;
      transition: color 0.12s;
      font-family: 'Inter', sans-serif;
  }
  .mob-nav button.act          { color: #00ff9d; }
  .mob-nav button:active       { opacity: 0.7; }
  .mob-nav .ni                 { font-size: 1.35rem; line-height: 1; }
  .mob-nav button.act .ni      { filter: drop-shadow(0 0 6px rgba(0,255,157,0.5)); }
}
</style>
""", unsafe_allow_html=True)


# ── DB ──────────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_db():
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    return client["football_analytics"]

db = get_db()


# ── Sidebar ─────────────────────────────────────────────────────────────────────
meta         = db.meta.find_one({}, {"_id": 0}) or {}
season       = meta.get("season")
season_label = f"{season}/{str(season+1)[-2:]}" if season else "—"

PAGES = ["Standings", "Matches", "Top Scorers", "Clubs", "Predictions"]
NAV_ICONS = {"Standings": "🏆", "Matches": "⚽", "Top Scorers": "🥅", "Clubs": "🛡️", "Predictions": "📊"}

# mobile nav reads ?page= query param; sidebar radio for desktop
qp = st.query_params.get("page", "Standings")
default_idx = PAGES.index(qp) if qp in PAGES else 0

with st.sidebar:
    st.markdown("## ⚽ PL Analytics")
    st.caption(f"PREMIER LEAGUE · {season_label}")
    st.divider()
    page = st.radio("", PAGES, index=default_idx, label_visibility="collapsed")
    st.divider()
    if st.button("⟳  Refresh Data", use_container_width=True):
        from fetcher.fetcher import fetch_all
        from predictor.predictor import run_simulation
        try:
            with st.spinner("Detecting season & fetching data (~30s)..."):
                fetch_all()
            with st.spinner("Running predictions..."):
                run_simulation()
            st.success("Updated!")
            st.rerun()
        except Exception as e:
            st.error(f"Fetch failed: {e}")

# ── Mobile bottom nav (rendered on every page) ───────────────────────────────
_nav_links = "".join(
    f'<button onclick="window.parent.location.href=\'?page={p}\'" class="{"act" if page == p else ""}">'
    f'<span class="ni">{NAV_ICONS[p]}</span>{p}</button>'
    for p in PAGES
)
st.markdown(f'<nav class="mob-nav">{_nav_links}</nav>', unsafe_allow_html=True)

# ── Mobile-only refresh strip (sidebar is hidden on mobile) ──────────────────
st.markdown('<div class="mob-refresh">', unsafe_allow_html=True)
if st.button("⟳  Refresh Data", key="mob_refresh", use_container_width=True):
    from fetcher.fetcher import fetch_all
    from predictor.predictor import run_simulation
    try:
        with st.spinner("Fetching data..."):
            fetch_all()
        with st.spinner("Running predictions..."):
            run_simulation()
        st.success("Updated!")
        st.rerun()
    except Exception as e:
        st.error(f"Fetch failed: {e}")
st.markdown('</div>', unsafe_allow_html=True)


# ── helpers ─────────────────────────────────────────────────────────────────────
def form_badges(form_str):
    out = []
    for ch in (form_str or "").split(","):
        ch = ch.strip()
        if   ch == "W": out.append('<span class="fb fw">W</span>')
        elif ch == "D": out.append('<span class="fb fd">D</span>')
        elif ch == "L": out.append('<span class="fb fl">L</span>')
    return "".join(out)

def gd_cell(gd):
    if gd > 0: return f'<span class="gdp">+{gd}</span>'
    if gd < 0: return f'<span class="gdn">{gd}</span>'
    return '<span class="gd0">0</span>'

def zone_cls(pos):
    if pos <= 4:  return "zcl"
    if pos <= 6:  return "zel"
    if pos >= 18: return "zrl"
    return ""


# ══════════════════════════════════════════════════════════════════════════════
# STANDINGS
# ══════════════════════════════════════════════════════════════════════════════
if page == "Standings":
    st.markdown(f'<div class="ph"><h2>League Table</h2><p>Premier League {season_label}</p></div>',
                unsafe_allow_html=True)

    standings = list(db.standings.find({}, {"_id": 0}))
    if not standings:
        st.warning("No data — click **Refresh Data** in the sidebar.")
        st.stop()

    standings.sort(key=lambda r: r["position"])
    leader  = standings[0]
    played  = max(r["playedGames"] for r in standings)
    goals   = sum(r["goalsFor"] for r in standings)

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, "Leader",         leader["team"]["name"],  f'{leader["points"]} pts'),
        (c2, "Matchday",       played,                  "gameweeks played"),
        (c3, "Goals Scored",   goals,                   f'{round(goals/max(played*20,1),2)} per match'),
        (c4, "Clubs",          20,                      "Premier League teams"),
    ]
    for col, lbl, val, sub in cards:
        with col:
            st.markdown(
                f'<div class="sc"><div class="lbl">{lbl}</div>'
                f'<div class="val">{val}</div><div class="sub">{sub}</div></div>',
                unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div class="zleg">'
        '<div class="zi"><div class="zd" style="background:#4f7fff"></div>Champions League (1-4)</div>'
        '<div class="zi"><div class="zd" style="background:#ff9f1c"></div>Europa League (5-6)</div>'
        '<div class="zi"><div class="zd" style="background:#ff4d6d"></div>Relegation (18-20)</div>'
        '</div>',
        unsafe_allow_html=True)

    rows_html = ""
    for row in standings:
        pos   = row["position"]
        crest = row["team"].get("crest", "")
        logo  = f'<img src="{crest}" width="22" height="22" style="vertical-align:middle;margin-right:8px;object-fit:contain">' if crest else ""
        rows_html += (
            f'<tr class="{zone_cls(pos)}">'
            f'<td><span class="pn">{pos}</span></td>'
            f'<td class="tl">{logo}<span class="tn">{row["team"]["name"]}</span></td>'
            f'<td>{row["playedGames"]}</td>'
            f'<td>{row["won"]}</td>'
            f'<td>{row["draw"]}</td>'
            f'<td>{row["lost"]}</td>'
            f'<td>{row["goalsFor"]}</td>'
            f'<td>{row["goalsAgainst"]}</td>'
            f'<td>{gd_cell(row["goalDifference"])}</td>'
            f'<td><span class="pts">{row["points"]}</span></td>'
            f'<td>{form_badges(row.get("form", ""))}</td>'
            f'</tr>'
        )

    st.markdown(
        '<div class="stbl-wrap"><table class="stbl"><thead><tr>'
        '<th>#</th><th class="tl">Team</th>'
        '<th>MP</th><th>W</th><th>D</th><th>L</th>'
        '<th>GF</th><th>GA</th><th>GD</th><th>PTS</th><th>Form</th>'
        f'</tr></thead><tbody>{rows_html}</tbody></table></div>',
        unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MATCHES
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Matches":
    st.markdown('<div class="ph"><h2>Fixtures &amp; Results</h2><p>All Premier League matches</p></div>',
                unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        status_f = st.selectbox("Status", ["All", "FINISHED", "SCHEDULED", "LIVE"])
    with c2:
        all_md = sorted([m for m in db.matches.distinct("matchday") if m])
        md_f = st.selectbox("Matchday", ["All"] + [str(m) for m in all_md])

    query = {}
    if status_f != "All": query["status"] = status_f
    if md_f    != "All":  query["matchday"] = int(md_f)

    matches = list(db.matches.find(query, {"_id": 0}))
    if not matches:
        st.warning("No matches for these filters.")
        st.stop()

    matches.sort(key=lambda m: (m.get("matchday", 0), m.get("utcDate", "")))

    html  = ""
    cur_md = None
    for m in matches:
        md = m.get("matchday", "")
        if md != cur_md:
            cur_md = md
            html += f'<div class="mdh">Matchday {md}</div>'

        ft   = ((m.get("score") or {}).get("fullTime")) or {}
        hs   = ft.get("home")
        aw   = ft.get("away")
        stat = m.get("status", "")
        date = m.get("utcDate", "")[:10]

        if stat == "LIVE":
            score_html = '<div class="ms live">LIVE</div>'
            badge      = '<span class="sbl">● LIVE</span>'
        elif hs is not None:
            score_html = f'<div class="ms">{hs} - {aw}</div>'
            badge      = '<span class="sbf">FT</span>'
        else:
            score_html = '<div class="ms">vs</div>'
            badge      = f'<span class="sbs">{date}</span>'

        html += (
            f'<div class="mc">'
            f'<div class="mh">{m["homeTeam"]["name"]}<br><small>{badge}</small></div>'
            f'{score_html}'
            f'<div class="ma">{m["awayTeam"]["name"]}</div>'
            f'</div>'
        )

    st.markdown(html, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TOP SCORERS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Top Scorers":
    st.markdown('<div class="ph"><h2>Top Scorers</h2><p>Golden boot race</p></div>',
                unsafe_allow_html=True)

    scorers = list(db.scorers.find({}, {"_id": 0}))
    if not scorers:
        st.warning("No scorer data — click **Refresh Data**.")
        st.stop()

    rows = sorted([
        {"Player":  s["player"]["name"],
         "Team":    s["team"]["name"],
         "Goals":   s.get("goals") or 0,
         "Assists": s.get("assists") or 0,
         "Played":  s.get("playedMatches") or 0}
        for s in scorers
    ], key=lambda x: x["Goals"], reverse=True)

    top10  = rows[:10]
    medals = {0: "🥇", 1: "🥈", 2: "🥉"}
    max_g  = top10[0]["Goals"] if top10 else 1

    col_list, col_chart = st.columns([2, 3])

    with col_list:
        html = ""
        for i, r in enumerate(top10):
            rank = medals.get(i, f"#{i+1}")
            bar_w = int(r["Goals"] / max_g * 100)
            color = "#ffd166" if i == 0 else "#00ff9d" if i < 3 else "#4f7fff"
            html += (
                f'<div style="display:grid;grid-template-columns:36px 1fr auto;align-items:center;'
                f'gap:12px;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.04);">'
                f'<div style="font-family:Oswald,sans-serif;font-size:1rem;font-weight:700;'
                f'color:{"#ffd166" if i<3 else "#4a5568"};text-align:center">{rank}</div>'
                f'<div>'
                f'<div style="font-weight:600;font-size:0.88rem">{r["Player"]}</div>'
                f'<div style="font-size:0.73rem;color:#8892b0">{r["Team"]}</div>'
                f'<div style="height:4px;background:rgba(255,255,255,0.06);border-radius:999px;margin-top:6px">'
                f'<div style="height:100%;width:{bar_w}%;background:{color};border-radius:999px"></div></div>'
                f'</div>'
                f'<div style="font-family:Oswald,sans-serif;font-size:1.5rem;font-weight:700;color:{color}">'
                f'{r["Goals"]}</div>'
                f'</div>'
            )
        st.markdown(html, unsafe_allow_html=True)

    with col_chart:
        names  = [r["Player"].split()[-1] for r in top10]
        goals  = [r["Goals"] for r in top10]
        colors = ["#ffd166" if i == 0 else "#00ff9d" if i < 3 else "#4f7fff"
                  for i in range(len(top10))]

        fig = go.Figure(go.Bar(
            y=names, x=goals, orientation="h",
            marker=dict(color=colors, line=dict(width=0)),
            text=goals, textposition="outside",
            textfont=dict(color="#e8edf5", size=12, family="Oswald"),
            hovertemplate="<b>%{y}</b>: %{x} goals<extra></extra>",
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=40, t=10, b=10), height=380,
            yaxis=dict(autorange="reversed", tickfont=dict(size=12, color="#e8edf5"),
                       gridcolor="rgba(255,255,255,0.04)"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(size=11, color="#8892b0"),
                       zeroline=False),
            bargap=0.3,
            font=dict(family="Inter"),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ══════════════════════════════════════════════════════════════════════════════
# CLUBS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Clubs":
    from datetime import date

    def calc_age(dob_str):
        """Calculate age from a YYYY-MM-DD date string."""
        if not dob_str:
            return "—"
        try:
            dob = date.fromisoformat(dob_str[:10])
            today = date.today()
            return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        except Exception:
            return "—"

    # Short position labels — the API returns long names like "Centre-Back"
    POS_SHORT = {
        "Goalkeeper":         "GK",
        "Centre-Back":        "CB",
        "Left-Back":          "LB",
        "Right-Back":         "RB",
        "Defensive Midfield": "DM",
        "Central Midfield":   "CM",
        "Attacking Midfield": "AM",
        "Left Midfield":      "LM",
        "Right Midfield":     "RM",
        "Left Winger":        "LW",
        "Right Winger":       "RW",
        "Centre-Forward":     "CF",
        "Second Striker":     "SS",
        "Offence":            "FW",
        "Defence":            "DEF",
        "Midfield":           "MID",
    }
    POS_COLOR = {
        "GK":  "#ffd166", "CB": "#4f7fff", "LB": "#4f7fff", "RB": "#4f7fff",
        "DM":  "#00ff9d", "CM": "#00ff9d", "AM": "#00ff9d", "LM": "#00ff9d",
        "RM":  "#00ff9d", "LW": "#ff9f1c", "RW": "#ff9f1c", "CF": "#ff4d6d",
        "SS":  "#ff4d6d", "FW": "#ff4d6d", "DEF": "#4f7fff", "MID": "#00ff9d",
    }

    teams = list(db.teams.find({}, {"_id": 0}))
    if not teams:
        st.warning("No club data yet — click **Refresh Data** in the sidebar.")
        st.stop()

    teams.sort(key=lambda t: t.get("name", ""))

    # Build name → doc lookup
    team_map = {t["name"]: t for t in teams}

    # Club selector with logo
    team_names = [t["name"] for t in teams]
    selected   = st.selectbox("Select a club", team_names)
    club       = team_map[selected]

    # Build scorer lookup: player name → {goals, assists}
    scorers_raw = list(db.scorers.find({}, {"_id": 0}))
    scorer_map  = {
        s["player"]["name"]: {"goals": s.get("goals") or 0, "assists": s.get("assists") or 0}
        for s in scorers_raw
    }

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Club header ──────────────────────────────────────────────────────────
    crest   = club.get("crest", "")
    coach   = (club.get("coach") or {}).get("name", "Unknown")
    stadium = club.get("venue", "Unknown")
    founded = club.get("founded", "—")
    colors  = club.get("clubColors", "—")
    short   = club.get("shortName", club["name"])

    logo_tag = f'<img src="{crest}" style="width:80px;height:80px;object-fit:contain;flex-shrink:0">' if crest else '<span style="font-size:3rem">⚽</span>'

    st.markdown(f"""
    <div class="club-hdr">
      <div>{logo_tag}</div>
      <div>
        <div style="font-family:Oswald,sans-serif;font-size:1.8rem;font-weight:700;
                    letter-spacing:1px;text-transform:uppercase">{club["name"]}</div>
        <div style="color:#8892b0;font-size:0.82rem;margin-top:4px">{colors}</div>
      </div>
      <div class="club-hdr-meta">
        <div><div style="font-size:0.68rem;color:#4a5568;text-transform:uppercase;letter-spacing:1px">Stadium</div>
             <div style="font-weight:600;font-size:0.92rem">{stadium}</div></div>
        <div><div style="font-size:0.68rem;color:#4a5568;text-transform:uppercase;letter-spacing:1px">Founded</div>
             <div style="font-weight:600;font-size:0.92rem">{founded}</div></div>
        <div><div style="font-size:0.68rem;color:#4a5568;text-transform:uppercase;letter-spacing:1px">Manager</div>
             <div style="font-weight:600;font-size:0.92rem">{coach}</div></div>
        <div><div style="font-size:0.68rem;color:#4a5568;text-transform:uppercase;letter-spacing:1px">Players</div>
             <div style="font-weight:600;font-size:0.92rem">{len(club.get("squad", []))}</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Squad ────────────────────────────────────────────────────────────────
    squad = sorted(club.get("squad", []),
                   key=lambda p: (p.get("position") or "Z", p.get("name") or ""))

    if not squad:
        st.info("Squad data not available for this club.")
        st.stop()

    # Group by position category for a nicer layout
    groups = {"Goalkeepers": [], "Defenders": [], "Midfielders": [], "Forwards": []}
    for player in squad:
        pos = player.get("position") or ""
        if "Goalkeeper" in pos:
            groups["Goalkeepers"].append(player)
        elif any(x in pos for x in ["Back", "Defence"]):
            groups["Defenders"].append(player)
        elif any(x in pos for x in ["Midfield", "Midfield"]):
            groups["Midfielders"].append(player)
        else:
            groups["Forwards"].append(player)

    for group_name, players in groups.items():
        if not players:
            continue

        st.markdown(
            f'<div style="font-family:Oswald,sans-serif;font-size:0.8rem;font-weight:600;'
            f'text-transform:uppercase;letter-spacing:2px;color:#4a5568;'
            f'padding:16px 0 8px;border-bottom:1px solid rgba(255,255,255,0.06);'
            f'margin-bottom:10px">{group_name}</div>',
            unsafe_allow_html=True)

        html = ""
        for p in players:
            name    = p.get("name", "Unknown")
            pos_raw = p.get("position") or "—"
            pos_s   = POS_SHORT.get(pos_raw, pos_raw[:3].upper())
            pos_col = POS_COLOR.get(pos_s, "#8892b0")
            nat     = p.get("nationality") or "—"
            age     = calc_age(p.get("dateOfBirth"))
            num     = p.get("shirtNumber")
            num_str = str(num) if num else "—"

            # Cross-reference scorer data
            sc      = scorer_map.get(name, {})
            goals   = sc.get("goals", 0)
            assists = sc.get("assists", 0)
            g_tag   = (f'<span style="background:rgba(255,77,109,0.15);color:#ff4d6d;'
                       f'border-radius:4px;padding:1px 7px;font-size:0.72rem;font-weight:700">'
                       f'⚽ {goals}</span>') if goals else ""
            a_tag   = (f'<span style="background:rgba(0,255,157,0.1);color:#00ff9d;'
                       f'border-radius:4px;padding:1px 7px;font-size:0.72rem;font-weight:700">'
                       f'🎯 {assists}</span>') if assists else ""

            html += (
                f'<div style="display:grid;grid-template-columns:36px 36px 1fr auto auto auto;'
                f'align-items:center;gap:10px;padding:9px 12px;'
                f'border-bottom:1px solid rgba(255,255,255,0.03);'
                f'transition:background 0.15s" '
                f'onmouseover="this.style.background=\'rgba(255,255,255,0.04)\'" '
                f'onmouseout="this.style.background=\'\'">'

                # shirt number
                f'<div style="font-family:Oswald,sans-serif;font-weight:700;'
                f'color:#4a5568;text-align:center">{num_str}</div>'

                # position badge
                f'<div style="background:{pos_col}22;color:{pos_col};border:1px solid {pos_col}55;'
                f'border-radius:5px;padding:2px 5px;font-size:0.65rem;'
                f'font-weight:700;text-align:center">{pos_s}</div>'

                # name
                f'<div style="font-weight:600;font-size:0.88rem">{name}</div>'

                # nationality
                f'<div style="font-size:0.78rem;color:#8892b0;min-width:100px">{nat}</div>'

                # age
                f'<div style="font-size:0.78rem;color:#4a5568;min-width:40px;text-align:center">'
                f'{"age "+str(age) if age != "—" else "—"}</div>'

                # goals / assists badges (empty if none)
                f'<div style="display:flex;gap:6px">{g_tag}{a_tag}</div>'

                f'</div>'
            )

        st.markdown(html, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PREDICTIONS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Predictions":
    st.markdown(
        '<div class="ph"><h2>Championship Forecast</h2>'
        '<p>Monte Carlo · 10,000 simulated seasons · recalculated each gameweek</p></div>',
        unsafe_allow_html=True)

    pred_doc = db.predictions.find_one({}, {"_id": 0})

    if not pred_doc:
        st.warning("No predictions yet.")
        if st.button("Run Simulation Now"):
            from predictor.predictor import run_simulation
            with st.spinner("Simulating 10,000 seasons..."):
                run_simulation()
            st.success("Done!")
            st.rerun()
        st.stop()

    predictions = pred_doc["predictions"]
    rows = sorted(
        [(t, p) for t, p in predictions.items() if p > 0],
        key=lambda x: x[1], reverse=True
    )

    # podium — top 3
    top3    = rows[:3]
    medals  = ["🥇", "🥈", "🥉"]
    classes = ["pod1", "pod2", "pod3"]
    c1, c2, c3 = st.columns(3)
    for col, (team, pct), medal, cls in zip([c1, c2, c3], top3, medals, classes):
        with col:
            st.markdown(
                f'<div class="pod {cls}">'
                f'<div class="pod-medal">{medal}</div>'
                f'<div class="pod-team">{team}</div>'
                f'<div class="pod-pct">{pct}%</div>'
                f'<div class="pod-lbl">win probability</div>'
                f'</div>',
                unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # probability bars
    max_pct = rows[0][1] if rows else 1
    html = ""
    for i, (team, pct) in enumerate(rows):
        w     = pct / max_pct * 100
        color = "#ffd166" if i == 0 else "#00ff9d" if pct > 5 else "#4f7fff"
        html += (
            f'<div class="pb">'
            f'<div class="pbt">{team}</div>'
            f'<div class="pbg"><div class="pbf" style="width:{w:.1f}%;background:{color}"></div></div>'
            f'<div class="ppp" style="color:{color}">{pct}%</div>'
            f'</div>'
        )
    st.markdown(html, unsafe_allow_html=True)

    with st.expander("How is this calculated?"):
        st.markdown("""
        Each team gets a **strength score**: points per game (60%) + goal difference per game (20%) + recent form (20%).

        For each remaining match, a weighted random outcome is drawn (with home advantage).
        This is repeated **10,000 times** — the % shows how often each team finishes top.
        """)
