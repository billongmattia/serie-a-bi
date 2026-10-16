CSS = """
<style>
/* sfondo e struttura generale */
.stApp { background: radial-gradient(900px 420px at 78% -8%, rgba(37,99,235,.45), transparent 60%), linear-gradient(180deg, #07122B 0%, #0A1A3A 100%); }
/* Si nascondono solo Deploy e menu. L'intestazione resta (trasparente) perché contiene il pulsante che riapre la sidebar. */
[data-testid="stToolbarActions"], [data-testid="stMainMenu"], #MainMenu, footer { display: none !important; }
header[data-testid="stHeader"] { background: transparent !important; pointer-events: none; }
[data-testid="stExpandSidebarButton"] { color: #E8EEFC !important; background: rgba(255,255,255,.1); border-radius: 8px; pointer-events: auto; }
[data-testid="stExpandSidebarButton"] * { color: #E8EEFC !important; }
.block-container { max-width: 1180px; padding-top: 1.2rem; padding-bottom: 2rem; }

/* avvisi (errori, avvertenze) leggibili sia sullo sfondo scuro sia sul pannello bianco */
[data-testid="stAlert"] { background: #FFFFFF; border-left: 4px solid #E5484D; border-radius: 10px; }
[data-testid="stAlert"] * { color: #0F1B3D !important; }

/* sidebar */
section[data-testid="stSidebar"] { background: #07122B; border-right: 1px solid rgba(255,255,255,.08); }
section[data-testid="stSidebar"] * { color: #E8EEFC; }
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] { display: none; }
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] { border-radius: 8px; padding: .45rem .7rem; margin-bottom: .1rem; }
section[data-testid="stSidebar"] .st-key-nav_active [data-testid="stPageLink-NavLink"] { background: #1E5BFF !important; font-weight: 700; }
.logo { padding: .6rem .4rem 1rem .4rem; line-height: 1; }
.logo .l1 { display: block; font-size: 1.7rem; font-weight: 900; letter-spacing: .01em; color: #FFFFFF; }
.logo .l2 { display: block; font-size: 1.7rem; font-weight: 900; letter-spacing: .01em; background: linear-gradient(90deg, #3B82F6, #22A559); -webkit-background-clip: text; background-clip: text; color: transparent; }
.tricolor { height: 3px; width: 56px; margin: 1.2rem 0 .6rem 0; background: linear-gradient(90deg, #22A559 33%, #FFFFFF 33% 66%, #E5484D 66%); }
.side-foot { font-size: .78rem; line-height: 1.5; opacity: .85; }

/* intestazione */
.st-key-hero { position: relative; overflow: hidden; border-radius: 14px; padding: 1rem 1.4rem; border: 1px solid rgba(80,140,255,.35); background: radial-gradient(500px 220px at 85% 0%, rgba(59,130,246,.55), transparent 70%), linear-gradient(120deg, #07122B 0%, #0B2A6B 100%); }
.st-key-hero::after { content: ""; position: absolute; right: 24px; top: -20px; width: 200px; height: 200px; background: linear-gradient(160deg, rgba(37,99,235,.85), rgba(37,99,235,0) 75%); clip-path: polygon(50% 0, 100% 100%, 0 100%); pointer-events: none; opacity: .5; }
.st-key-hero label, .st-key-hero p, .st-key-hero [data-testid="stWidgetLabel"] * { color: #E8EEFC !important; }
.hero-kicker { font-size: .72rem; font-weight: 700; letter-spacing: .08em; color: #5EA0FF; text-transform: uppercase; }
.hero-title { margin: .1rem 0 .2rem 0; font-size: 2.2rem; font-weight: 900; line-height: 1.05; text-transform: uppercase; color: #FFFFFF; }
.hero-title span { color: #2F7BFF; }
.hero-sub { margin: 0; color: #DCE6FF; font-size: .95rem; }

/* pannello bianco */
.st-key-panel { background: #FFFFFF; border-radius: 12px; border: 1px solid #D6E4FF; padding: 1.2rem 1.4rem; margin-top: .9rem; }
.panel-title { margin: 0; font-size: 1.7rem; font-weight: 900; letter-spacing: .005em; text-transform: uppercase; color: #0F1B3D; }
.panel-sub { margin: .1rem 0 1rem 0; color: #475569; font-size: .92rem; }
.card-title { display: flex; align-items: center; gap: .5rem; font-weight: 800; font-size: 1.02rem; color: #0F1B3D; margin: .2rem 0 .4rem 0; }

/* schede KPI */
.kpi-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(148px, 1fr)); gap: .8rem; margin-bottom: 1rem; }
.kpi { display: flex; gap: .7rem; align-items: center; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: .75rem .85rem; box-shadow: 0 1px 2px rgba(15,27,61,.05); }
.kpi-icon { flex: 0 0 auto; width: 38px; height: 38px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; }
.kpi-icon.blue { background: #E0EAFF; } .kpi-icon.green { background: #DCFCE7; } .kpi-icon.red { background: #FEE2E2; } .kpi-icon.yellow { background: #FEF3C7; } .kpi-icon.grey { background: #F1F5F9; }
.kpi-label { font-size: .75rem; color: #64748B; }
.kpi-value { font-size: 1.7rem; font-weight: 800; line-height: 1.1; color: #0F1B3D; }
.kpi-note { font-size: .72rem; color: #64748B; }
.kpi-delta { font-size: .78rem; font-weight: 700; }
.kpi-delta.good { color: #15803D; } .kpi-delta.bad { color: #DC2626; }

/* tabelle */
table.tbl { width: 100%; border-collapse: collapse; font-size: .85rem; color: #0F1B3D; }
table.tbl th { background: #F1F5F9; color: #0F1B3D; font-weight: 800; padding: .5rem .5rem; text-align: left; border-bottom: 1px solid #E2E8F0; }
table.tbl td { padding: .38rem .5rem; border-bottom: 1px solid #EEF2F7; }
table.tbl .num { text-align: right; }
table.tbl .pos { font-weight: 800; }
.dots { display: inline-flex; gap: 4px; align-items: center; }
.dot { display: inline-block; width: 12px; height: 12px; border-radius: 50%; }
.dot.w { background: #22A559; } .dot.d { background: #9CA3AF; } .dot.l { background: #E5484D; }

/* ultime partite */
.match-row { display: grid; grid-template-columns: 1fr auto 1fr auto; gap: .6rem; align-items: center; border-left: 4px solid #9CA3AF; background: #FFFFFF; padding: .5rem .7rem; margin-bottom: .35rem; border-bottom: 1px solid #EEF2F7; color: #0F1B3D; font-size: .9rem; }
.match-row.w { border-left-color: #22A559; } .match-row.d { border-left-color: #9CA3AF; } .match-row.l { border-left-color: #E5484D; }
.match-score { font-weight: 800; }
.badge { width: 26px; height: 26px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #FFFFFF; font-weight: 800; font-size: .8rem; }
.badge.w { background: #22A559; } .badge.d { background: #9CA3AF; } .badge.l { background: #E5484D; }
</style>
"""
