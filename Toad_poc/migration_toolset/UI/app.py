"""
Nxzen Migration Studio - Streamlit UI
Run: streamlit run app.py  (from migration_toolset/UI/ directory)
"""

import contextlib
import csv
import io
import json
import os
import sys

# Force UTF-8 output so terminal shows English instead of garbled characters
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import glob

import streamlit as st

# ── Path setup ───────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(BASE_DIR, 'tools')
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

INPUT_DIR   = os.path.join(BASE_DIR, 'input')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
GLOBAL_DIR       = os.path.join(BASE_DIR, 'global')
FUNC_WRITER_DIR  = os.path.join(BASE_DIR, 'func_excel_writer')
UI_DIR           = os.path.dirname(os.path.abspath(__file__))

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title='Nxzen Migration Studio',
    page_icon='🔧',
    layout='wide',
    initial_sidebar_state='expanded',
    menu_items={},
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── nxzen brand colours ──────────────────────────────────────────────────
       Green accent : #5EE340
       Black        : #000000
       Dark grey    : #111111
       Mid grey     : #222222
       Off-white bg : #F5F7FA
       Border grey  : #DDE3EC
    ───────────────────────────────────────────────────────────────────────── */

    /* ── Global font ─────────────────────────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    /* ── Compact full-viewport layout (no browser scrollbars) ───────────── */
    html, body { overflow: hidden !important; height: 100vh !important; }
    .stApp { height: 100vh !important; overflow: hidden !important; }
    [data-testid="stAppViewContainer"] { height: 100vh !important; overflow: hidden !important; }
    [data-testid="stMain"] {
        height: 100vh !important;
        overflow: hidden !important;
    }
    .main .block-container {
        height: calc(100vh - 3.8rem) !important;
        max-height: calc(100vh - 3.8rem) !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        padding-bottom: 0.5rem !important;
    }
    [data-testid="stSidebar"] {
        height: 100vh !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
    }

    /* ── Sidebar ─────────────────────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 3px solid #5EE340;
    }
    /* Hide the sidebar's own internal header strip (collapse button row) */
    [data-testid="stSidebarHeader"] {
        display: none !important;
    }
    /* Pull all sidebar content to the very top */
    [data-testid="stSidebar"] > div:first-child,
    [data-testid="stSidebarContent"],
    [data-testid="stSidebar"] section,
    [data-testid="stSidebar"] .block-container {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {
        color: #C8D6E5 !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] small {
        color: #7A9BBF !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: #222222 !important;
        margin-top: 0.3rem !important;
        margin-bottom: 0.3rem !important;
    }
    /* Run Mode radio — label and buttons on same row */
    [data-testid="stSidebar"] [data-testid="stRadio"] {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        gap: 0.5rem !important;
        margin-top: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] > label:first-child {
        white-space: nowrap !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        margin-bottom: 0 !important;
        flex-shrink: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] > div {
        display: flex !important;
        flex-direction: row !important;
    }
    /* Sidebar checkbox list — compact */
    [data-testid="stSidebar"] [data-testid="stCheckbox"] {
        margin-bottom: 0 !important;
        padding: 1px 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stCheckbox"] label {
        font-size: 0.78rem !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        max-width: 190px !important;
    }
    /* Sidebar radio + selectbox */
    [data-testid="stSidebar"] [data-testid="stRadio"] label,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] label {
        color: #C8D6E5 !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background-color: #111111 !important;
        border-color: #222222 !important;
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] input {
        background-color: #111111 !important;
        color: #FFFFFF !important;
        border-color: #222222 !important;
    }
    /* Sidebar metric */
    [data-testid="stSidebar"] [data-testid="metric-container"] {
        background: #111111;
        border-left: 3px solid #5EE340;
        border-radius: 6px;
        padding: 8px 12px;
    }
    [data-testid="stSidebar"] [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #5EE340 !important;
    }

    /* ── Main area background ─────────────────────────────────────────────── */
    .main .block-container { background-color: #FFFFFF; }

    /* ── Hide deploy button, main menu and right-side toolbar ───────────── */
    [data-testid="stDeployButton"] { display: none !important; }
    #MainMenu { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    /* Make Streamlit header transparent so it doesn't visually block content */
    [data-testid="stHeader"],
    header[data-testid="stHeader"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    /* Push main content below the transparent header bar (~3rem height) */
    .block-container { padding-top: 3.5rem !important; }

    /* ── Page title ──────────────────────────────────────────────────────── */
    h1 { color: #000000 !important; font-weight: 800 !important; }
    h2 { color: #111111 !important; font-weight: 700 !important; }
    h3 { color: #222222 !important; font-weight: 600 !important; }

    /* ── Divider ─────────────────────────────────────────────────────────── */
    hr { border-color: #DDE3EC !important; }

    /* ── Primary buttons (green) ─────────────────────────────────────────── */
    .stButton > button[kind="primary"] {
        background-color: #5EE340 !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        padding: 10px 24px !important;
        transition: background 0.2s ease !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #4CC832 !important;
        color: #000000 !important;
    }
    /* Secondary buttons */
    .stButton > button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1.5px solid #000000 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #F5F7FA !important;
        border-color: #5EE340 !important;
        color: #000000 !important;
    }
    /* All other buttons (use_container_width, etc.) */
    .stButton > button:not([kind]) {
        border-radius: 6px !important;
        font-weight: 600 !important;
        border: 1.5px solid #DDE3EC !important;
    }
    .stButton > button:not([kind]):hover {
        border-color: #5EE340 !important;
        color: #000000 !important;
    }

    /* ── Tabs ────────────────────────────────────────────────────────────── */
    .stTabs {
        border: 2px solid #5EE340;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 0 16px rgba(94,227,64,0.12), 0 4px 16px rgba(0,0,0,0.15);
        background: #ffffff;
    }
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(135deg, #0d0d0d 0%, #1c1c1c 50%, #0d0d0d 100%);
        border-radius: 14px 14px 0 0;
        gap: 4px;
        padding: 6px 8px 0 8px;
        border-bottom: 2px solid #5EE340;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        font-weight: 600;
        font-size: 13px;
        color: #aaaaaa;
        padding: 8px 16px;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #1a1a1a;
        color: #5EE340 !important;
        border-bottom: 3px solid #5EE340 !important;
        text-shadow: 0 0 10px rgba(94,227,64,0.4);
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #ffffff !important;
        background-color: #222222;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding: 16px;
        background: #ffffff;
        border-radius: 0 0 14px 14px;
    }

    /* ── Metrics ─────────────────────────────────────────────────────────── */
    [data-testid="metric-container"] {
        background: #F5F7FA;
        border: 1px solid #DDE3EC;
        border-left: 4px solid #5EE340;
        border-radius: 8px;
        padding: 16px !important;
    }
    [data-testid="stMetricValue"] {
        color: #000000 !important;
        font-weight: 800 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #4A6278 !important;
        font-size: 13px !important;
    }

    /* ── Success / info / warning / error alerts ─────────────────────────── */
    [data-testid="stAlert"][kind="success"] {
        background-color: #EDFAE7;
        border-left: 4px solid #5EE340;
        color: #1A4D10;
        border-radius: 6px;
    }
    [data-testid="stAlert"][kind="info"] {
        background-color: #EBF4FF;
        border-left: 4px solid #222222;
        border-radius: 6px;
    }
    [data-testid="stAlert"][kind="warning"] {
        background-color: #FFF8E1;
        border-left: 4px solid #F9A825;
        border-radius: 6px;
    }
    [data-testid="stAlert"][kind="error"] {
        background-color: #FDECEA;
        border-left: 4px solid #C62828;
        border-radius: 6px;
    }

    /* ── Expanders ───────────────────────────────────────────────────────── */
    [data-testid="stExpander"] {
        border: 1px solid #DDE3EC !important;
        border-radius: 8px !important;
    }
    [data-testid="stExpander"] summary {
        font-weight: 600;
        color: #111111;
    }
    [data-testid="stExpander"] summary:hover {
        color: #5EE340;
    }

    /* ── Dataframe ───────────────────────────────────────────────────────── */
    [data-testid="stDataFrame"] {
        border: 1px solid #DDE3EC;
        border-radius: 8px;
        overflow: hidden;
    }

    /* ── File uploader ───────────────────────────────────────────────────── */
    [data-testid="stFileUploader"] {
        border: 2px dashed #DDE3EC;
        border-radius: 8px;
        padding: 8px;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #5EE340;
    }

    /* ── Number input ────────────────────────────────────────────────────── */
    input[type="number"], input[type="text"] {
        border-radius: 6px !important;
    }
    input[type="number"]:focus, input[type="text"]:focus {
        border-color: #5EE340 !important;
        box-shadow: 0 0 0 2px rgba(94,227,64,0.2) !important;
    }

    /* ── Progress bar ────────────────────────────────────────────────────── */
    [data-testid="stProgressBar"] > div > div {
        background-color: #5EE340 !important;
    }

    /* ── Spinner ─────────────────────────────────────────────────────────── */
    [data-testid="stSpinner"] > div {
        border-top-color: #5EE340 !important;
    }

    /* ── Download button ─────────────────────────────────────────────────── */
    [data-testid="stDownloadButton"] > button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        background-color: #222222 !important;
    }

    /* ── Custom components ───────────────────────────────────────────────── */
    .output-box {
        background: #000000;
        color: #C8D6E5;
        font-family: 'Courier New', monospace;
        font-size: 12.5px;
        padding: 16px;
        border-radius: 8px;
        border-left: 4px solid #5EE340;
        white-space: pre-wrap;
        max-height: 380px;
        overflow-y: auto;
    }
    .section-title {
        font-size: 14px;
        font-weight: 700;
        color: #111111;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .step-badge {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        margin-right: 6px;
        letter-spacing: 0.3px;
    }
    .badge-done { background: #EDFAE7; color: #1A6610; border: 1px solid #5EE340; }
    .badge-todo { background: #FDECEA; color: #C62828; border: 1px solid #EF9A9A; }
    .badge-warn { background: #FFF8E1; color: #856404; border: 1px solid #F9A825; }

    /* ── Checkbox accent ─────────────────────────────────────────────────── */
    [data-testid="stCheckbox"] svg { color: #5EE340 !important; }

    /* ── Multiselect tags ────────────────────────────────────────────────── */
    [data-testid="stMultiSelect"] [data-baseweb="tag"] {
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }

    /* ── Nxzen logo — rotating scanner animation ────────────────────────── */
    /* A bright green beam rotates around the logo like a data scanner/radar */
    @keyframes nxzen-scan {
        0%   {
            transform: scale(1.0);
            filter: drop-shadow( 7px  0   12px rgba(94,227,64,1.0))
                    drop-shadow( 0    0    5px rgba(94,227,64,0.3));
        }
        25%  {
            transform: scale(1.05);
            filter: drop-shadow( 0    7px 12px rgba(94,227,64,1.0))
                    drop-shadow( 0    0    5px rgba(94,227,64,0.3));
        }
        50%  {
            transform: scale(1.08);
            filter: drop-shadow(-7px  0   12px rgba(94,227,64,1.0))
                    drop-shadow( 0    0    5px rgba(94,227,64,0.3));
        }
        75%  {
            transform: scale(1.05);
            filter: drop-shadow( 0   -7px 12px rgba(94,227,64,1.0))
                    drop-shadow( 0    0    5px rgba(94,227,64,0.3));
        }
        100% {
            transform: scale(1.0);
            filter: drop-shadow( 7px  0   12px rgba(94,227,64,1.0))
                    drop-shadow( 0    0    5px rgba(94,227,64,0.3));
        }
    }
    .nxzen-logo-anim {
        animation: nxzen-scan 2.5s linear infinite;
        display: inline-block;
    }

    /* ── "Migration Studio" gradient colour flow ────────────────────────── */
    @keyframes colour-flow {
        0%,100% { color: #ffffff; }
        50%      { color: #5EE340; }
    }
    .migrate-letter {
        display: inline-block;
        font-size: 32px;
        font-weight: 700;
        letter-spacing: 1px;
        animation: colour-flow 10s ease-in-out infinite;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _capture(func, *args, **kwargs):
    """Call func(*args, **kwargs), capture stdout, return (ok, text)."""
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            func(*args, **kwargs)
        return True, buf.getvalue()
    except SystemExit as e:
        ok = (str(e) == '0' or e.code == 0)
        return ok, buf.getvalue()
    except Exception:
        import traceback
        return False, buf.getvalue() + '\n' + traceback.format_exc()


def _step_status(report_name):
    r = os.path.join(REPORTS_DIR, report_name)
    return {
        1: os.path.exists(os.path.join(r, 'sanitized', f'{report_name}_sanitized.txt')),
        2: os.path.exists(os.path.join(r, 'adf', 'arm_template.json')),
        3: os.path.exists(os.path.join(r, 'config', f'{report_name}_config_data.sql')),
        4: os.path.exists(os.path.join(r, 'adf', 'deploy', 'deployment_checklist.txt')),
        5: os.path.exists(os.path.join(r, 'blob', 'blob_checklist.txt')),
        6: _func_url_is_set(report_name),
    }


def _func_url_is_set(report_name):
    """Return True if excel_writer_url has been updated from its placeholder in the ARM template."""
    import json as _json
    arm_path = os.path.join(REPORTS_DIR, report_name, 'adf', 'arm_template.json')
    if not os.path.exists(arm_path):
        return False
    try:
        with open(arm_path, encoding='utf-8') as f:
            arm = _json.load(f)
        for res in arm.get('resources', []):
            params = res.get('properties', {}).get('parameters', {})
            if 'excel_writer_url' in params:
                val = params['excel_writer_url'].get('defaultValue', '')
                return bool(val) and '<' not in val and val.startswith('https://')
    except Exception:
        pass
    return False


def _get_excel_writer_url(report_name):
    """Return the current excel_writer_url defaultValue from the ARM template, or ''."""
    import json as _json
    arm_path = os.path.join(REPORTS_DIR, report_name, 'adf', 'arm_template.json')
    if not os.path.exists(arm_path):
        return ''
    try:
        with open(arm_path, encoding='utf-8') as f:
            arm = _json.load(f)
        for res in arm.get('resources', []):
            params = res.get('properties', {}).get('parameters', {})
            if 'excel_writer_url' in params:
                return params['excel_writer_url'].get('defaultValue', '')
    except Exception:
        pass
    return ''


def _existing_reports():
    if not os.path.exists(REPORTS_DIR):
        return []
    return sorted(d for d in os.listdir(REPORTS_DIR)
                  if os.path.isdir(os.path.join(REPORTS_DIR, d)))


def _input_files():
    if not os.path.exists(INPUT_DIR):
        return []
    return sorted(f for f in os.listdir(INPUT_DIR)
                  if f.lower().endswith(('.txt', '.xml')))


def _write_process_log(report_name, step, step_name, ok, output):
    """Append a timestamped log file to reports/<report>/process_log/."""
    from datetime import datetime
    log_dir = os.path.join(REPORTS_DIR, report_name, 'process_log')
    os.makedirs(log_dir, exist_ok=True)
    ts = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    status = 'SUCCESS' if ok else 'FAILED'
    fname = f'{ts}_step{step}_{step_name}_{status}.txt'
    header = (
        f'Report   : {report_name}\n'
        f'Step     : {step} — {step_name}\n'
        f'Status   : {status}\n'
        f'Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
        f'{"─" * 60}\n\n'
    )
    with open(os.path.join(log_dir, fname), 'w', encoding='utf-8') as f:
        f.write(header + output)


def _clear_from_step(report_name, from_step):
    """Delete output folders for from_step and all following steps, clear session state."""
    import shutil
    r = os.path.join(REPORTS_DIR, report_name)

    # Output directories owned by each step
    STEP_DIRS = {
        1: [os.path.join(r, 'sanitized')],
        2: [os.path.join(r, 'adf')],
        3: [os.path.join(r, 'config')],
        4: [os.path.join(r, 'adf', 'deploy')],
        5: [os.path.join(r, 'blob')],
    }
    # Session state keys owned by each step
    STEP_KEYS = {
        1: ['tool1_output', 'tool1_ok'],
        2: ['tool2_output', 'tool2_ok'],
        3: ['tool3_output', 'tool3_ok'],
        4: ['tool4_output', 'tool4_ok', 'tool4_az_output', 'tool4_az_ok'],
        5: ['tool5_output', 'tool5_ok'],
        6: ['tool6_deploy_output', 'tool6_deploy_ok', 'tool6_test_output', 'tool6_test_ok',
            'tool6_pre_test_output', 'tool6_pre_test_ok', 'tool6_pre_test_url', 'tool6_pre_test_saved'],
    }
    for step in range(from_step, 7):
        for d in STEP_DIRS.get(step, []):
            if os.path.exists(d):
                shutil.rmtree(d)
        for key in STEP_KEYS.get(step, []):
            st.session_state.pop(key, None)


def _read_file(path):
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception:
        return ''


@st.dialog('Output', width='large')
def _output_popup(label, text):
    st.markdown(f'**{label}**')
    st.code(text, language='text')


def _show_output(text, label='Output'):
    if text.strip():
        btn_key = f'view_{label.lower().replace(" ", "_").replace(".", "_")}'
        if st.button(f'📋 View {label}', key=btn_key):
            _output_popup(label, text)


def _download(label, path, mime='text/plain'):
    if os.path.exists(path):
        content = _read_file(path)
        st.download_button(label, data=content,
                           file_name=os.path.basename(path), mime=mime)


def _prereq(condition, message):
    if not condition:
        st.warning(message)
        return False
    return True


def _badge(done):
    cls  = 'badge-done' if done else 'badge-todo'
    text = 'Done' if done else 'Pending'
    return f'<span class="step-badge {cls}">{text}</span>'


def _get_clear_all_counts():
    """Return dict of current resource counts from SQL + ADF. Returns None on config error."""
    import subprocess
    import shutil
    import json as _json
    AZ = shutil.which('az') or r'C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd'
    cfg_path = os.path.join(GLOBAL_DIR, 'poc_azure_config.json')
    if not os.path.exists(cfg_path):
        return None
    with open(cfg_path, encoding='utf-8') as f:
        cfg = _json.load(f)
    counts = {}
    # SQL counts via az CLI (avoids needing pymssql installed in UI env)
    try:
        sql_pass = subprocess.run(
            [AZ, 'keyvault', 'secret', 'show',
             '--vault-name', cfg['keyvault_name'],
             '--name', 'azuresql-db-password', '--query', 'value', '-o', 'tsv'],
            capture_output=True, text=True, timeout=30
        ).stdout.strip()
        import pymssql as _mssql
        conn = _mssql.connect(
            server=f"{cfg['sql_server']}.database.windows.net",
            user=cfg['sql_admin_user'], password=sql_pass,
            database=cfg['sql_database'], port=1433, login_timeout=15)
        cur = conn.cursor()
        for tbl in ('config.report', 'config.report_sql', 'config.report_email'):
            try:
                cur.execute(f'SELECT COUNT(*) FROM {tbl}')
                counts[tbl] = cur.fetchone()[0]
            except Exception:
                counts[tbl] = '?'
        conn.close()
    except Exception:
        counts['config.report'] = counts['config.report_sql'] = counts['config.report_email'] = '?'
    # ADF counts
    rg  = cfg['resource_group']
    adf = cfg['adf_name']
    for label, args in [
        ('adf_pipelines',       ['datafactory', 'pipeline',       'list']),
        ('adf_triggers',        ['datafactory', 'trigger',        'list']),
        ('adf_datasets',        ['datafactory', 'dataset',        'list']),
        ('adf_linked_services', ['datafactory', 'linked-service', 'list']),
    ]:
        try:
            result = subprocess.run(
                [AZ] + args + ['--factory-name', adf, '--resource-group', rg],
                capture_output=True, text=True, timeout=30)
            counts[label] = len(_json.loads(result.stdout)) if result.returncode == 0 else '?'
        except Exception:
            counts[label] = '?'
    return counts


def _run_clear_all():
    """Delete all SQL config rows and all ADF resources. Returns (ok, log)."""
    import subprocess
    import shutil
    import json as _json
    AZ = shutil.which('az') or r'C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd'
    cfg_path = os.path.join(GLOBAL_DIR, 'poc_azure_config.json')
    if not os.path.exists(cfg_path):
        return False, 'poc_azure_config.json not found in global/.'
    with open(cfg_path, encoding='utf-8') as f:
        cfg = _json.load(f)
    rg  = cfg['resource_group']
    adf = cfg['adf_name']
    lines = []

    # ── SQL: delete config rows ──────────────────────────────────────────────
    lines.append('── SQL Config ──────────────────────────────')
    try:
        sql_pass = subprocess.run(
            [AZ, 'keyvault', 'secret', 'show',
             '--vault-name', cfg['keyvault_name'],
             '--name', 'azuresql-db-password', '--query', 'value', '-o', 'tsv'],
            capture_output=True, text=True, timeout=30
        ).stdout.strip()
        import pymssql as _mssql
        conn = _mssql.connect(
            server=f"{cfg['sql_server']}.database.windows.net",
            user=cfg['sql_admin_user'], password=sql_pass,
            database=cfg['sql_database'], port=1433, login_timeout=15)
        cur = conn.cursor()
        for tbl in ('config.report_email', 'config.report_sql', 'config.report'):
            cur.execute(f'DELETE FROM {tbl}')
            lines.append(f'  DELETE {tbl}: {cur.rowcount} rows')
        conn.commit()
        conn.close()
    except Exception as e:
        lines.append(f'  ERROR: {e}')
        return False, '\n'.join(lines)

    # ── ADF: stop + delete triggers ──────────────────────────────────────────
    lines.append('')
    lines.append('── ADF Triggers ────────────────────────────')
    try:
        r = subprocess.run([AZ, 'datafactory', 'trigger', 'list',
                            '--factory-name', adf, '--resource-group', rg],
                           capture_output=True, text=True, timeout=30)
        triggers = [t['name'] for t in _json.loads(r.stdout)] if r.returncode == 0 else []
        for name in triggers:
            subprocess.run([AZ, 'datafactory', 'trigger', 'stop',
                            '--factory-name', adf, '--resource-group', rg, '--name', name],
                           capture_output=True, text=True, timeout=60)
            subprocess.run([AZ, 'datafactory', 'trigger', 'delete',
                            '--factory-name', adf, '--resource-group', rg, '--name', name, '--yes'],
                           capture_output=True, text=True, timeout=30)
            lines.append(f'  Deleted: {name}')
        if not triggers:
            lines.append('  (none)')
    except Exception as e:
        lines.append(f'  ERROR: {e}')

    # ── ADF: delete pipelines, datasets, linked services ────────────────────
    for label, resource in [('Pipelines', 'pipeline'), ('Datasets', 'dataset'),
                             ('Linked Services', 'linked-service')]:
        lines.append('')
        lines.append(f'── ADF {label} ─────────────────────────────')
        try:
            r = subprocess.run([AZ, 'datafactory', resource, 'list',
                                '--factory-name', adf, '--resource-group', rg],
                               capture_output=True, text=True, timeout=30)
            items = [i['name'] for i in _json.loads(r.stdout)] if r.returncode == 0 else []
            for name in items:
                subprocess.run([AZ, 'datafactory', resource, 'delete',
                                '--factory-name', adf, '--resource-group', rg,
                                '--name', name, '--yes'],
                               capture_output=True, text=True, timeout=30)
                lines.append(f'  Deleted: {name}')
            if not items:
                lines.append('  (none)')
        except Exception as e:
            lines.append(f'  ERROR: {e}')

    lines.append('')
    lines.append('── Done ────────────────────────────────────')
    return True, '\n'.join(lines)


def _run_disable_reports(report_names):
    """Set is_active = 'N' in SQL and stop ADF trigger for each report."""
    import subprocess, shutil, json as _json, re as _re
    AZ = shutil.which('az') or r'C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd'
    cfg_path = os.path.join(GLOBAL_DIR, 'poc_azure_config.json')
    if not os.path.exists(cfg_path):
        return False, 'poc_azure_config.json not found.'
    with open(cfg_path, encoding='utf-8') as f:
        cfg = _json.load(f)
    rg = cfg['resource_group']
    adf = cfg['adf_name']
    lines = []

    lines.append('── SQL: disable reports ────────────────────')
    try:
        sql_pass = subprocess.run(
            [AZ, 'keyvault', 'secret', 'show', '--vault-name', cfg['keyvault_name'],
             '--name', 'azuresql-db-password', '--query', 'value', '-o', 'tsv'],
            capture_output=True, text=True, timeout=30
        ).stdout.strip()
        import pymssql as _mssql
        conn = _mssql.connect(
            server=f"{cfg['sql_server']}.database.windows.net",
            user=cfg['sql_admin_user'], password=sql_pass,
            database=cfg['sql_database'], port=1433, login_timeout=15)
        cur = conn.cursor()
        for rn in report_names:
            cur.execute("UPDATE config.report SET is_active = 'N' WHERE report_name = %s", (rn,))
            lines.append(f'  {rn}: {cur.rowcount} row(s) set inactive')
        conn.commit()
        conn.close()
    except Exception as e:
        lines.append(f'  SQL ERROR: {e}')
        return False, '\n'.join(lines)

    lines.append('')
    lines.append('── ADF: stop triggers ──────────────────────')
    for rn in report_names:
        safe = _re.sub(r'[^A-Za-z0-9_]', '_', rn)
        trig = f'TR_{safe}_0600'
        r = subprocess.run([AZ, 'datafactory', 'trigger', 'stop',
                            '--factory-name', adf, '--resource-group', rg, '--name', trig],
                           capture_output=True, text=True, timeout=60)
        lines.append(f'  {trig}: {"stopped" if r.returncode == 0 else r.stderr.strip() or "not found"}')

    lines.append('')
    lines.append('── Done ────────────────────────────────────')
    return True, '\n'.join(lines)


def _run_func_deploy():
    """Run deploy_func.ps1 to deploy the Excel Writer Azure Function."""
    import subprocess
    script_path = os.path.join(FUNC_WRITER_DIR, 'deploy', 'deploy_func.ps1')
    if not os.path.exists(script_path):
        return False, 'deploy_func.ps1 not found in func_excel_writer/deploy/'
    cfg_path = os.path.join(GLOBAL_DIR, 'poc_azure_config.json')
    if not os.path.exists(cfg_path):
        return False, 'poc_azure_config.json not found in global/'
    try:
        result = subprocess.run(
            ['powershell', '-ExecutionPolicy', 'Bypass', '-File', script_path],
            capture_output=True, text=True, timeout=360,
            cwd=os.path.join(FUNC_WRITER_DIR, 'deploy')
        )
        output = (result.stdout or '') + ('\n' + result.stderr.strip() if result.stderr.strip() else '')
        return result.returncode == 0, output.strip()
    except FileNotFoundError:
        return False, 'PowerShell not found — ensure PowerShell is installed and on PATH.'
    except subprocess.TimeoutExpired:
        return False, 'Deployment timed out after 6 minutes.'


def _run_unit_tests():
    """Run test_unit.py inside func_excel_writer/ using pytest or unittest."""
    import subprocess
    test_path = os.path.join(FUNC_WRITER_DIR, 'test_unit.py')
    if not os.path.exists(test_path):
        return False, 'test_unit.py not found in func_excel_writer/'
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', test_path, '-v', '--tb=short', '--no-header'],
            capture_output=True, text=True, timeout=60,
            cwd=FUNC_WRITER_DIR
        )
        output = (result.stdout or '') + ('\n' + result.stderr.strip() if result.stderr.strip() else '')
        return result.returncode == 0, output.strip()
    except Exception:
        # Fallback to unittest if pytest is not installed
        try:
            result = subprocess.run(
                [sys.executable, test_path],
                capture_output=True, text=True, timeout=60,
                cwd=FUNC_WRITER_DIR
            )
            output = (result.stdout or '') + ('\n' + result.stderr.strip() if result.stderr.strip() else '')
            return result.returncode == 0, output.strip()
        except subprocess.TimeoutExpired:
            return False, 'Unit tests timed out.'
        except Exception as e:
            return False, f'Error running tests: {e}'


def _update_excel_writer_url_in_obj(obj, url):
    """Recursively replace excel_writer_url defaultValue in a JSON object. Returns True if any change was made."""
    changed = False
    if isinstance(obj, dict):
        if 'excel_writer_url' in obj and isinstance(obj['excel_writer_url'], dict):
            if 'defaultValue' in obj['excel_writer_url']:
                obj['excel_writer_url']['defaultValue'] = url
                changed = True
        for v in obj.values():
            if _update_excel_writer_url_in_obj(v, url):
                changed = True
    elif isinstance(obj, list):
        for item in obj:
            if _update_excel_writer_url_in_obj(item, url):
                changed = True
    return changed


def _save_excel_writer_url(report_name, url):
    """Update excel_writer_url defaultValue in ARM templates and pipeline JSON files. Returns (count_updated, [filenames])."""
    import json as _json
    import glob as _glob
    adf_dir = os.path.join(REPORTS_DIR, report_name, 'adf')
    candidates = [
        os.path.join(adf_dir, 'arm_template.json'),
        os.path.join(adf_dir, 'arm_template_bootstrap.json'),
    ]
    pipeline_dir = os.path.join(adf_dir, 'pipelines')
    if os.path.exists(pipeline_dir):
        candidates.extend(_glob.glob(os.path.join(pipeline_dir, '*.json')))

    updated, names = 0, []
    for fpath in candidates:
        if not os.path.exists(fpath):
            continue
        with open(fpath, encoding='utf-8') as f:
            data = _json.load(f)
        if _update_excel_writer_url_in_obj(data, url):
            with open(fpath, 'w', encoding='utf-8') as f:
                _json.dump(data, f, indent=4)
            updated += 1
            names.append(os.path.basename(fpath))
    return updated, names


def _run_az_deploy(report_name, deploy_func_app=False):
    import subprocess, json as _json, shutil, re as _re, os as _os

    AZ = shutil.which('az') or r'C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd'

    SQLCMD = shutil.which('sqlcmd')
    if not SQLCMD:
        for _candidate in [
            r'C:\Program Files\Microsoft SQL Server\Client SDK\ODBC\170\Tools\Binn\SQLCMD.EXE',
            r'C:\Program Files\Microsoft SQL Server\Client SDK\ODBC\130\Tools\Binn\SQLCMD.EXE',
            r'C:\Program Files\Microsoft SQL Server\160\Tools\Binn\sqlcmd.exe',
            r'C:\Program Files\Microsoft SQL Server\150\Tools\Binn\sqlcmd.exe',
            r'C:\Program Files\Microsoft SQL Server\140\Tools\Binn\sqlcmd.exe',
        ]:
            if os.path.exists(_candidate):
                SQLCMD = _candidate
                break

    cfg_path = os.path.join(GLOBAL_DIR, 'poc_azure_config.json')
    if not os.path.exists(cfg_path):
        return False, 'poc_azure_config.json not found in global/.'
    with open(cfg_path, encoding='utf-8') as f:
        cfg = _json.load(f)

    sub = cfg['subscription_id']
    rg  = cfg['resource_group']
    loc = cfg['location']
    kv  = cfg['keyvault_name']
    srv = cfg['sql_server']
    db  = cfg['sql_database']
    usr = cfg['sql_admin_user']

    arm_path    = os.path.join(REPORTS_DIR, report_name, 'adf', 'arm_template.json')
    params_path = os.path.join(REPORTS_DIR, report_name, 'adf', 'arm_template_parameters.json')

    config_ddl_path  = os.path.join(GLOBAL_DIR, 'config', 'config_schema_ddl.sql')
    config_data_path = os.path.join(REPORTS_DIR, report_name, 'config', f'{report_name}_config_data.sql')
    table_ddl_path   = os.path.join(REPORTS_DIR, report_name, 'ddl', f'{report_name}_ddl.sql')

    lines = []

    # ── Phase 0: Excel Writer function deployment (optional) ─────────────────
    if deploy_func_app:
        lines.append('═' * 60)
        lines.append('PHASE 0 — Excel Writer Function Deployment')
        lines.append('═' * 60)

        func_script = os.path.join(FUNC_WRITER_DIR, 'deploy', 'deploy_func.ps1')
        if not os.path.exists(func_script):
            lines.append('SKIP — deploy_func.ps1 not found in func_excel_writer/deploy/')
        else:
            lines.append('\n>> Running deploy_func.ps1 ...')
            try:
                func_result = subprocess.run(
                    ['powershell', '-ExecutionPolicy', 'Bypass', '-File', func_script],
                    capture_output=True, text=True, timeout=360,
                    cwd=os.path.join(FUNC_WRITER_DIR, 'deploy')
                )
                if func_result.stdout:
                    lines.append(func_result.stdout.strip())
                if func_result.stderr.strip():
                    lines.append(func_result.stderr.strip())

                if func_result.returncode == 0:
                    url_match = _re.search(
                        r'https://[^\s]+/api/excel_writer[^\s]*',
                        func_result.stdout
                    )
                    if url_match:
                        func_url = url_match.group(0).rstrip(')')
                        lines.append(f'\n  Function URL: {func_url}')
                        n, names = _save_excel_writer_url(report_name, func_url)
                        if n:
                            lines.append(f'  excel_writer_url saved to {n} ARM template file(s).')
                    else:
                        lines.append('  WARNING: Function deployed but URL could not be parsed from output.')
                        lines.append('  Enter it manually in Tab 6 — Excel Writer.')
                else:
                    lines.append(f'  ERROR: Function deployment failed (exit {func_result.returncode})')
                    lines.append('  Continuing with ADF deployment...')
            except FileNotFoundError:
                lines.append('  ERROR: PowerShell not found — function deployment skipped.')
            except subprocess.TimeoutExpired:
                lines.append('  ERROR: Function deployment timed out after 6 minutes — skipping.')

        lines.append('\nPhase 0 complete.')
        lines.append('')

    # ── Pre-deployment: fill parameters + substitute $(placeholders) ────────────
    import tempfile as _tempfile
    _PARAM_MAP = {
        'factoryName':          cfg.get('adf_name', ''),
        'azure_sql_server':     cfg.get('sql_server', ''),
        'azure_sql_db':         cfg.get('sql_database', ''),
        'key_vault_name':       cfg.get('keyvault_name', ''),
        'storage_account_name': cfg.get('storage_account', ''),
        # logic_app_email_url intentionally excluded — security constraint (never in config)
    }

    # 1. Fill arm_template_parameters.json with real values
    try:
        with open(params_path, encoding='utf-8') as _f:
            _params_data = _json.load(_f)
        _params_changed = False
        for _pk, _pv in _PARAM_MAP.items():
            if _pv and _pk in _params_data.get('parameters', {}):
                _params_data['parameters'][_pk]['value'] = _pv
                _params_changed = True
        if _params_changed:
            with open(params_path, 'w', encoding='utf-8') as _f:
                _json.dump(_params_data, _f, indent=4)
    except Exception as _e:
        lines.append(f'WARNING: could not auto-fill parameters file: {_e}')

    # 2. Substitute $(placeholder) strings in ARM template → temp file
    _tmp_arm_path = None
    _arm_deploy_path = arm_path
    try:
        _arm_text = open(arm_path, encoding='utf-8').read()
        _arm_modified = _arm_text
        for _pk, _pv in _PARAM_MAP.items():
            if _pv:
                _arm_modified = _arm_modified.replace(f'$({_pk})', _pv)
        if _arm_modified != _arm_text:
            _tmp_fd, _tmp_arm_path = _tempfile.mkstemp(suffix='.json', prefix='adf_arm_')
            with _os.fdopen(_tmp_fd, 'w', encoding='utf-8') as _f:
                _f.write(_arm_modified)
            _arm_deploy_path = _tmp_arm_path
    except Exception as _e:
        lines.append(f'WARNING: could not substitute ARM template placeholders: {_e}')

    def _cleanup_tmp():
        if _tmp_arm_path and _os.path.exists(_tmp_arm_path):
            try: _os.unlink(_tmp_arm_path)
            except Exception: pass

    lines.append('═' * 60)
    lines.append('PHASE 1 — ADF ARM Template Deployment')
    lines.append('═' * 60)

    adf_steps = [
        ([AZ, 'account', 'set', '--subscription', sub],
         f'Setting subscription {sub}'),
        ([AZ, 'group', 'create', '--name', rg, '--location', loc],
         f'Ensuring resource group {rg} exists'),
        ([AZ, 'deployment', 'group', 'create',
          '--resource-group', rg,
          '--template-file', _arm_deploy_path,
          '--parameters', f'@{params_path}',
          '--name', f'deploy-{report_name}'],
         f'Deploying ARM template for {report_name}'),
    ]

    for cmd, desc in adf_steps:
        lines.append(f'\n>> {desc}')
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            if result.stdout:
                lines.append(result.stdout.strip())
            if result.stderr:
                lines.append(result.stderr.strip())
            if result.returncode != 0:
                lines.append(f'ERROR: step failed (exit {result.returncode})')
                _cleanup_tmp(); return False, '\n'.join(lines)
        except FileNotFoundError:
            lines.append('ERROR: az CLI not found. Install Azure CLI and run "az login" first.')
            _cleanup_tmp(); return False, '\n'.join(lines)
        except subprocess.TimeoutExpired:
            lines.append('ERROR: deployment timed out after 3 minutes.')
            _cleanup_tmp(); return False, '\n'.join(lines)

    lines.append('\nPhase 1 complete — ADF deployed.')

    lines.append('\n' + '═' * 60)
    lines.append('PHASE 2 — Database Script Execution')
    lines.append('═' * 60)

    lines.append(f'\n>> Retrieving SQL password from Key Vault ({kv})')
    try:
        kv_result = subprocess.run(
            [AZ, 'keyvault', 'secret', 'show',
             '--vault-name', kv,
             '--name', 'azuresql-db-password',
             '--query', 'value',
             '-o', 'tsv'],
            capture_output=True, text=True, timeout=30
        )
        if kv_result.returncode != 0:
            lines.append('ERROR: Could not retrieve SQL password from Key Vault.')
            lines.append(kv_result.stderr.strip())
            lines.append('Database scripts NOT executed — check az login and Key Vault permissions.')
            _cleanup_tmp(); return False, '\n'.join(lines)
        sql_pwd = kv_result.stdout.strip()
        lines.append('SQL password retrieved.')
    except Exception as e:
        lines.append(f'ERROR: Key Vault error: {e}')
        lines.append('Database scripts NOT executed — check az login and Key Vault permissions.')
        _cleanup_tmp(); return False, '\n'.join(lines)

    server_fqdn = f'{srv}.database.windows.net'

    def _exec_sql_file(sql_path, description):
        if not os.path.exists(sql_path):
            lines.append(f'\n>> {description}')
            lines.append(f'  SKIP — file not found: {os.path.relpath(sql_path, BASE_DIR)}')
            return True
        lines.append(f'\n>> {description}')
        lines.append(f'  File: {os.path.relpath(sql_path, BASE_DIR)}')
        if SQLCMD:
            try:
                r = subprocess.run(
                    [SQLCMD, '-S', server_fqdn, '-d', db, '-U', usr,
                     '-P', sql_pwd, '-i', sql_path, '-b', '-I'],
                    capture_output=True, text=True, timeout=120
                )
                if r.stdout: lines.append(r.stdout.strip())
                if r.stderr: lines.append(r.stderr.strip())
                if r.returncode != 0:
                    lines.append(f'  ERROR: sqlcmd exited {r.returncode}')
                    return False
                lines.append('  OK')
                return True
            except subprocess.TimeoutExpired:
                lines.append('  ERROR: SQL execution timed out after 2 minutes.')
                return False
        try:
            import pyodbc, re as _re
            conn_str = (
                f'DRIVER={{ODBC Driver 18 for SQL Server}};'
                f'SERVER={server_fqdn};DATABASE={db};UID={usr};PWD={sql_pwd};'
                f'Encrypt=yes;TrustServerCertificate=no;'
            )
            with open(sql_path, encoding='utf-8') as _f:
                sql_text = _f.read()
            batches = [b.strip() for b in _re.split(r'^\s*GO\s*$', sql_text,
                       flags=_re.IGNORECASE | _re.MULTILINE) if b.strip()]
            conn = pyodbc.connect(conn_str, autocommit=True, timeout=30)
            cur  = conn.cursor()
            for batch in batches:
                cur.execute(batch)
            cur.close(); conn.close()
            lines.append(f'  OK — {len(batches)} batch(es) executed via pyodbc')
            return True
        except Exception as _e:
            lines.append(f'  ERROR: {_e}')
            return False

    for sql_path, desc in [
        (config_ddl_path,  'Config schema DDL (global — once per environment)'),
        (config_data_path, f'Config data SQL (report: {report_name})'),
        (table_ddl_path,   f'Table DDL — mock data (POC only, report: {report_name})'),
    ]:
        if not _exec_sql_file(sql_path, desc):
            _cleanup_tmp(); return False, '\n'.join(lines)

    lines.append('\n' + '═' * 60)
    lines.append('Deployment completed successfully.')
    lines.append('  ADF pipeline and triggers deployed.')
    lines.append('  Database scripts executed against: ' + server_fqdn)
    lines.append('═' * 60)
    if _tmp_arm_path and _os.path.exists(_tmp_arm_path):
        try: _os.unlink(_tmp_arm_path)
        except Exception: pass
    return True, '\n'.join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    logo_path = os.path.join(BASE_DIR, 'assets', 'nxzen_logo.png')
    if os.path.exists(logo_path):
        st.image(logo_path, width=140)

    # Run mode — options driven by UI/ui_config.json run_modes flags
    _ui_cfg_path = os.path.join(UI_DIR, 'ui_config.json')
    _run_modes_cfg = {'single_report': True, 'batch_run': True}
    if os.path.exists(_ui_cfg_path):
        try:
            with open(_ui_cfg_path, encoding='utf-8') as _f:
                _rm = json.load(_f).get('run_modes', {})
            _run_modes_cfg['single_report'] = bool(_rm.get('single_report', True))
            _run_modes_cfg['batch_run']     = bool(_rm.get('batch_run',     True))
        except Exception:
            pass

    _mode_options = []
    if _run_modes_cfg['single_report']:
        _mode_options.append('Single Report')
    if _run_modes_cfg['batch_run']:
        _mode_options.append('Batch Run')

    if not _mode_options:
        st.warning('No run modes enabled in poc_team_config.json.')
        run_mode = None
    else:
        run_mode = st.radio('Run Mode', _mode_options,
                            horizontal=True, label_visibility='visible')

    st.divider()

    report_name = None  # default

    if run_mode == 'Single Report':
        st.subheader('Report')

        existing   = _existing_reports()
        existing_s = set(existing)
        from_input = [
            os.path.splitext(f)[0]
            for f in _input_files()
            if not f.startswith('_')
        ]
        unprocessed = [n for n in from_input if n not in existing_s]

        # Unified list: processed first, then not-yet-processed from input/
        all_options = existing + unprocessed

        def _fmt(name):
            return f'{name}  ✅' if name in existing_s else f'{name}  (new)'

        report_name = st.selectbox(
            'Select report',
            all_options,
            index=None,
            placeholder='-- select --',
            format_func=_fmt,
            key='sidebar_report_sel',
        ) if all_options else None

        if not all_options:
            st.info('No reports or input files found.')

        # Manual entry override
        manual = st.text_input('Or type name manually',
                               placeholder='e.g. BC_BIMIO_267_Daily',
                               key='sidebar_manual_rn')
        if manual.strip():
            report_name = manual.strip()

        st.divider()

        # Step status
        if report_name:
            status = _step_status(report_name)
            st.subheader('Progress')
            STEP_LABELS = {
                1: 'Sanitize',
                2: 'ADF Templates',
                3: 'Config Setup',
                4: 'Deploy Scripts',
                5: 'Blob Upload',
                6: 'Excel Writer URL',
            }
            for step, label in STEP_LABELS.items():
                done = status.get(step, False)
                icon = '✅' if done else '⭕'
                st.markdown(f'{icon} **Step {step}** — {label}')
        else:
            st.info('Select or enter a report name above.')

    else:  # Batch Run
        st.subheader('Batch Selection')

        # Unified list: existing reports (✅) + unprocessed input files (new)
        _b_existing  = _existing_reports()
        _b_existing_s = set(_b_existing)
        _b_new = [os.path.splitext(f)[0] for f in _input_files()
                  if not f.startswith('_') and os.path.splitext(f)[0] not in _b_existing_s]
        all_items = _b_existing + _b_new
        total = len(all_items)

        def _b_label(name):
            return f'{name}  ✅' if name in _b_existing_s else f'{name}  (new)'

        if total == 0:
            st.warning('No reports or input files found.')
        else:
            # Select All / Deselect All toggle
            all_checked = st.checkbox(f'Select All ({total})', key='batch_select_all')

            # When the toggle changes, push the new state into every individual key
            _prev_all = st.session_state.get('_batch_prev_all')
            if all_checked != _prev_all:
                for _n in all_items:
                    st.session_state[f'bchk_{_n}'] = all_checked
                st.session_state['_batch_prev_all'] = all_checked

            st.markdown('<div style="margin:4px 0"></div>', unsafe_allow_html=True)

            # Individual checkboxes
            selected = []
            for name in all_items:
                _k = f'bchk_{name}'
                if _k not in st.session_state:
                    st.session_state[_k] = False
                if st.checkbox(_b_label(name), key=_k):
                    selected.append(name)

            st.session_state['batch_files'] = selected
            st.caption(f'{len(selected)} of {total} selected')

        st.divider()
        if 'batch_results' in st.session_state:
            results = st.session_state['batch_results']
            done_count = sum(1 for r in results if all(
                r.get(f't{i}') is not False for i in range(1, 6)))
            st.metric('Completed', f'{done_count} / {len(results)}')

    st.divider()
    st.caption('All tools run locally. No Azure connections made.')


# ─────────────────────────────────────────────────────────────────────────────
# Main header  (fixed height ≈ 1 inch / 96px)
# ─────────────────────────────────────────────────────────────────────────────

import base64 as _b64
_logo_b64 = ''
_logo_file = os.path.join(BASE_DIR, 'assets', 'nxzen_logo.png')
if os.path.exists(_logo_file):
    with open(_logo_file, 'rb') as _f:
        _logo_b64 = _b64.b64encode(_f.read()).decode()
_logo_html = (
    f'<div class="nxzen-logo-anim" style="'
    f'display:inline-block; vertical-align:middle; margin-right:18px;'
    f'width:90px; height:70px;'
    f'background-image:url(\'data:image/png;base64,{_logo_b64}\');'
    f'background-size:90px auto;'
    f'background-repeat:no-repeat;'
    f'background-position:top center;'
    f'"></div>'
) if _logo_b64 else ''

_wave_html = ''.join(
    f'<span class="migrate-letter" style="animation-delay:{i * 0.08:.2f}s;">'
    f'{"&nbsp;" if c == " " else c}</span>'
    for i, c in enumerate('Migration Studio')
)

st.markdown(f"""
<div style="
    display: flex;
    align-items: center;
    justify-content: center;
    height: 110px;
    padding: 0 32px;
    background: linear-gradient(135deg, #0d0d0d 0%, #1c1c1c 50%, #0d0d0d 100%);
    border: 2px solid #5EE340;
    border-radius: 16px;
    box-shadow: 0 0 28px rgba(94,227,64,0.25), 0 6px 24px rgba(0,0,0,0.55);
    margin-bottom: 12px;
    position: relative;
    overflow: hidden;
">
    <div style="
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(94,227,64,0.6), transparent);
    "></div>
    <span style="display:flex; align-items:center;">
        {_logo_html}{_wave_html}
    </span>
    <div style="
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(94,227,64,0.35), transparent);
    "></div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SINGLE REPORT — Tabs (placed directly below header)
# ─────────────────────────────────────────────────────────────────────────────

if run_mode == 'Single Report':
    tabs = st.tabs([
        '1 - Sanitize',
        '2 - ADF Templates',
        '3 - Config Setup',
        '4 - Deploy Scripts',
        '5 - Blob Upload',
        '6 - Excel Writer',
        '7 - POC Tools',
    ])

# ─────────────────────────────────────────────────────────────────────────────
# BATCH MODE
# ─────────────────────────────────────────────────────────────────────────────

if run_mode == 'Batch Run':
    st.subheader('Batch Run')

    batch_action = st.radio(
        'Action',
        ['Add / Update', 'Disable'],
        horizontal=True,
        key='batch_action',
    )

    batch_files = st.session_state.get('batch_files', [])

    if not batch_files:
        st.info('Select reports using the sidebar checkboxes.')
    else:
        st.markdown(f'**{len(batch_files)} report(s) selected:**')
        with st.expander('Show selected', expanded=False):
            for f in batch_files:
                st.text(f'  {f}')

        st.divider()

        # ── Add / Update ──────────────────────────────────────────────────
        if batch_action == 'Add / Update':
            st.markdown('**Select tools to run for each report:**')
            bc1, bc2, bc3, bc4, bc5 = st.columns(5)
            with bc1: run_t1 = st.checkbox('Tool 1\nSanitize',        value=True,  key='b_t1')
            with bc2: run_t2 = st.checkbox('Tool 2\nADF Templates',   value=True,  key='b_t2')
            with bc3: run_t3 = st.checkbox('Tool 3\nConfig Setup',    value=True,  key='b_t3')
            with bc4: run_t4 = st.checkbox('Tool 4\nDeploy to Azure', value=False, key='b_t4')
            with bc5: run_t5 = st.checkbox('Tool 5\nBlob Upload',    value=False, key='b_t5')

            if run_t4:
                st.caption('Tool 4 will generate scripts **and** deploy to Azure POC '
                           '(az CLI + SQL execution). Make sure you have run `az login` first.')

            oc1, oc2 = st.columns([1, 1])
            with oc1: batch_poc  = st.checkbox('POC mode (Tool 3)', key='b_poc')
            with oc2: batch_verb = st.checkbox('Verbose output',    key='b_verb')

            st.divider()

            if st.button('▶  Run Batch', type='primary', key='btn_batch'):
                from tool1_sanitize import sanitize_file
                from utils.mapping_registry import MappingRegistry
                from tool2_adf_generator import generate_adf
                from tool3_config_setup import generate_config
                from tool4_adf_deploy import generate_deploy
                from tool5_blob_upload import generate_upload

                registry_path = os.path.join(GLOBAL_DIR, 'mapping_registry.csv')
                registry = MappingRegistry(registry_path)

                results = []
                progress_bar = st.progress(0, text='Starting...')
                status_box   = st.empty()

                for idx, label in enumerate(batch_files):
                    pct = idx / len(batch_files)
                    progress_bar.progress(pct, text=f'Processing {idx+1}/{len(batch_files)}: {label}')
                    status_box.info(f'Processing: **{label}**')

                    # Report name = input filename stem (same as label for new files)
                    rn = label
                    fname = next(
                        (f for f in os.listdir(INPUT_DIR)
                         if not f.startswith('_') and os.path.splitext(f)[0] == label),
                        None,
                    )
                    xml_path = os.path.join(INPUT_DIR, fname) if fname else None

                    row = {
                        'file': fname or label,
                        'report_name': rn,
                        't1': None, 't2': None, 't3': None,
                        't4': None, 't5': None, 'errors': [],
                    }

                    # Tool 1 — sanitize (requires input file)
                    if run_t1:
                        if xml_path and os.path.exists(xml_path):
                            ok, out = _capture(sanitize_file, xml_path, registry, batch_verb)
                            registry._save()
                            row['t1'] = ok
                            if not ok:
                                row['errors'].append(f'Tool 1: {out.splitlines()[-1] if out.strip() else "failed"}')
                        else:
                            row['t1'] = None  # no input file — skip silently

                    if run_t2:
                        ok, out = _capture(generate_adf, rn, batch_verb)
                        row['t2'] = ok
                        if not ok:
                            row['errors'].append(f'Tool 2: {out.splitlines()[-1] if out.strip() else "failed"}')

                    if run_t3:
                        ok, out = _capture(generate_config, rn, batch_verb, batch_poc)
                        row['t3'] = ok
                        if not ok:
                            row['errors'].append(f'Tool 3: {out.splitlines()[-1] if out.strip() else "failed"}')

                    if run_t4:
                        ok, out = _capture(generate_deploy, rn, verbose=batch_verb)
                        if not ok:
                            row['t4'] = False
                            row['errors'].append(f'Tool 4 (scripts): {out.splitlines()[-1] if out.strip() else "failed"}')
                        else:
                            status_box.info(f'Deploying to Azure: **{rn}**')
                            az_ok, az_out = _run_az_deploy(rn)
                            row['t4'] = az_ok
                            row['t4_az_out'] = az_out
                            if not az_ok:
                                last = next((l for l in reversed(az_out.splitlines()) if l.strip()), 'failed')
                                row['errors'].append(f'Tool 4 (deploy): {last}')

                    if run_t5:
                        ok, out = _capture(generate_upload, rn, batch_verb)
                        row['t5'] = ok
                        if not ok:
                            row['errors'].append(f'Tool 5: {out.splitlines()[-1] if out.strip() else "failed"}')

                    results.append(row)

                progress_bar.progress(1.0, text='Done!')
                status_box.empty()
                st.session_state['batch_results'] = results
                st.rerun()

            # Show results table
            if 'batch_results' in st.session_state:
                results = st.session_state['batch_results']
                st.divider()
                st.subheader('Results')

                def _cell(val):
                    if val is True:  return '✅'
                    if val is False: return '❌'
                    return '—'

                import pandas as pd
                rows_data = []
                for r in results:
                    row_dict = {
                        'Report Name':  r['report_name'] or r['file'],
                        'Tool 1':       _cell(r['t1']),
                        'Tool 2':       _cell(r['t2']),
                        'Tool 3':       _cell(r['t3']),
                        'Tool 4':       _cell(r['t4']),
                        'Tool 5':       _cell(r['t5']),
                        'Errors':       ' | '.join(r['errors']) if r['errors'] else '',
                    }
                    rows_data.append(row_dict)
                df = pd.DataFrame(rows_data)
                st.dataframe(df, use_container_width=True, hide_index=True)

                az_results = [r for r in results if r.get('t4_az_out')]
                if az_results:
                    st.markdown('**Deploy output (click to view per report):**')
                    for r in az_results:
                        rn_label = r['report_name'] or r['file']
                        icon = '✅' if r.get('t4') else '❌'
                        if st.button(f'{icon} {rn_label} — View Deploy Output',
                                     key=f'view_az_{rn_label}'):
                            _output_popup(f'Deploy Output — {rn_label}', r['t4_az_out'])

                mc1, mc2, mc3 = st.columns(3)
                with mc1: st.metric('Total', len(results))
                with mc2:
                    ok_count = sum(1 for r in results
                                   if all(r.get(f't{i}') is not False for i in range(1, 6)))
                    st.metric('All steps OK', ok_count)
                with mc3:
                    st.metric('With errors', sum(1 for r in results if r['errors']))

                if st.button('Clear results', key='btn_clear_batch'):
                    del st.session_state['batch_results']
                    st.rerun()

        # ── Disable ───────────────────────────────────────────────────────
        elif batch_action == 'Disable':
            st.info(
                'Disabling a report sets `is_active = N` in the SQL config and stops '
                'its ADF trigger. The report folder, ARM templates, and all other files '
                'are left untouched.'
            )
            st.markdown('**Reports to disable:** ' + ', '.join(f'`{r}`' for r in batch_files))
            disable_confirm = st.checkbox(
                'I understand — disable the selected reports',
                key='batch_disable_confirm',
            )
            if st.button('⏸  Disable Selected', type='primary', key='btn_batch_disable',
                         disabled=not disable_confirm):
                ok, out = _run_disable_reports(batch_files)
                if ok:
                    st.success('Done.')
                else:
                    st.error('Completed with errors — see output below.')
                st.code(out, language=None)

    # Stop here — don't show single-report tabs in batch mode
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Sanitize (Tool 1)
# ─────────────────────────────────────────────────────────────────────────────

with tabs[0]:
    st.subheader('Step 1 — Sanitize Toad XML')
    st.caption('Replace all sensitive values (emails, passwords, servers, UNC paths) with safe mock values.')

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('**Option A — Upload a new file**')
        uploaded = st.file_uploader('Upload Toad XML (.txt or .xml)',
                                    type=['txt', 'xml'], key='tool1_upload')
        if uploaded:
            os.makedirs(INPUT_DIR, exist_ok=True)
            dest = os.path.join(INPUT_DIR, uploaded.name)
            with open(dest, 'wb') as f:
                f.write(uploaded.read())
            st.success(f'Saved to input/{uploaded.name}')

    with col2:
        st.markdown('**Option B — Use existing file from input/**')
        input_files = _input_files()
        selected_file = st.selectbox('File in input/', input_files,
                                     index=None, placeholder='-- select --',
                                     key='tool1_select') if input_files else None
        if not input_files:
            st.info('No files in input/ yet. Upload one on the left.')

    st.divider()
    verbose1 = st.checkbox('Verbose output', key='tool1_verbose')

    if st.button('▶  Run Sanitize', type='primary', key='btn_tool1'):
        if report_name:
            _clear_from_step(report_name, 1)
        # Determine which file to process
        file_to_process = None
        if uploaded:
            file_to_process = os.path.join(INPUT_DIR, uploaded.name)
        elif selected_file:
            file_to_process = os.path.join(INPUT_DIR, selected_file)

        if not file_to_process:
            st.error('Please upload a file or select one from input/.')
        else:
            from tool1_sanitize import sanitize_file
            from utils.mapping_registry import MappingRegistry

            registry_path = os.path.join(GLOBAL_DIR, 'mapping_registry.csv')
            registry = MappingRegistry(registry_path)

            with st.spinner('Sanitizing...'):
                ok, output = _capture(sanitize_file, file_to_process, registry, verbose1)
                registry._save()

            st.session_state['tool1_output'] = output
            st.session_state['tool1_ok'] = ok
            if report_name:
                _write_process_log(report_name, 1, 'sanitize', ok, output)

    # Show results
    if 'tool1_output' in st.session_state:
        ok     = st.session_state['tool1_ok']
        output = st.session_state['tool1_output']

        if ok:
            st.success('Sanitization complete.')
        else:
            st.error('Sanitization failed. See output below.')

        if report_name:
            mapping_path = os.path.join(REPORTS_DIR, report_name, 'sanitized',
                                        f'{report_name}_mapping.csv')
            san_path = os.path.join(REPORTS_DIR, report_name, 'sanitized',
                                    f'{report_name}_sanitized.txt')

            btn_c1, btn_c2 = st.columns([1, 1])
            with btn_c1:
                _show_output(output, 'Tool 1 Output')
            with btn_c2:
                if os.path.exists(mapping_path):
                    if st.button('📋 View Mapping Table', key='view_mapping'):
                        _output_popup(f'Mapping Table — {report_name}',
                                      _read_file(mapping_path))

            if os.path.exists(mapping_path):
                _download('Download mapping CSV', mapping_path, 'text/csv')
            _download('Download sanitized XML', san_path)
        else:
            _show_output(output, 'Tool 1 Output')


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — ADF Templates (Tool 2)
# ─────────────────────────────────────────────────────────────────────────────

with tabs[1]:
    st.subheader('Step 2 — Generate ADF ARM Templates')
    st.caption('Generates Linked Services, Datasets, Pipeline JSON and combined ARM template.')

    if not report_name:
        st.warning('Select a report in the sidebar first.')
    else:
        san_path = os.path.join(REPORTS_DIR, report_name, 'sanitized',
                                f'{report_name}_sanitized.txt')
        if not _prereq(os.path.exists(san_path),
                       'Sanitized XML not found. Run Step 1 first.'):
            pass
        else:
            st.success(f'Sanitized XML found: {san_path}')
            verbose2 = st.checkbox('Verbose output', key='tool2_verbose')

            if st.button('▶  Generate ADF Templates', type='primary', key='btn_tool2'):
                _clear_from_step(report_name, 2)
                from tool2_adf_generator import generate_adf
                with st.spinner('Generating ADF ARM templates...'):
                    ok, output = _capture(generate_adf, report_name, verbose2)
                st.session_state['tool2_output'] = output
                st.session_state['tool2_ok'] = ok
                _write_process_log(report_name, 2, 'adf_templates', ok, output)

        if 'tool2_output' in st.session_state:
            ok     = st.session_state['tool2_ok']
            output = st.session_state['tool2_output']

            if ok:
                st.success('ADF templates generated.')
            else:
                st.error('Generation failed. See output below.')

            adf_dir = os.path.join(REPORTS_DIR, report_name, 'adf')

            btn_c1, btn_c2 = st.columns([1, 1])
            with btn_c1:
                _show_output(output, 'Tool 2 Output')
            with btn_c2:
                if os.path.exists(adf_dir):
                    all_json = glob.glob(os.path.join(adf_dir, '**', '*.json'), recursive=True)
                    if all_json:
                        file_list = '\n'.join(os.path.relpath(fp, adf_dir) for fp in sorted(all_json))
                        if st.button('📋 View Generated Files', key='view_adf_files'):
                            _output_popup(f'Generated ADF Files — {report_name}', file_list)

                arm_path    = os.path.join(adf_dir, 'arm_template.json')
                params_path = os.path.join(adf_dir, 'arm_template_parameters.json')
                c1, c2 = st.columns(2)
                with c1:
                    _download('Download arm_template.json', arm_path, 'application/json')
                with c2:
                    _download('Download arm_template_parameters.json', params_path, 'application/json')


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — Config Setup (Tool 3)
# ─────────────────────────────────────────────────────────────────────────────

with tabs[2]:
    st.subheader('Step 3 — Config Schema + Data Setup')
    st.caption('Generates config schema DDL and per-report INSERT SQL (emails, SQL queries, template info).')

    if not report_name:
        st.warning('Select a report in the sidebar first.')
    else:
        san_path = os.path.join(REPORTS_DIR, report_name, 'sanitized',
                                f'{report_name}_sanitized.txt')
        if not _prereq(os.path.exists(san_path),
                       'Sanitized XML not found. Run Step 1 first.'):
            pass
        else:
            st.success(f'Sanitized XML found.')

            c1, c2 = st.columns([1, 1])
            with c1:
                verbose3 = st.checkbox('Verbose output', key='tool3_verbose')
            with c2:
                poc_mode = st.checkbox(
                    'POC mode (use dev team emails from poc_team_config.json)',
                    key='tool3_poc')

            poc_path = os.path.join(GLOBAL_DIR, 'poc_team_config.json')
            if poc_mode and not os.path.exists(poc_path):
                st.warning('poc_team_config.json not found in global/. '
                           'Create it with your dev team emails before using POC mode.')

            if st.button('▶  Generate Config SQL', type='primary', key='btn_tool3'):
                _clear_from_step(report_name, 3)
                from tool3_config_setup import generate_config
                with st.spinner('Generating config SQL...'):
                    ok, output = _capture(generate_config, report_name, verbose3, poc_mode)
                st.session_state['tool3_output'] = output
                st.session_state['tool3_ok'] = ok
                _write_process_log(report_name, 3, 'config_setup', ok, output)

        if 'tool3_output' in st.session_state:
            ok     = st.session_state['tool3_ok']
            output = st.session_state['tool3_output']

            if ok:
                st.success('Config SQL generated.')
            else:
                st.error('Generation failed. See output below.')

            config_dir = os.path.join(REPORTS_DIR, report_name, 'config')
            sql_path   = os.path.join(config_dir, f'{report_name}_config_data.sql')
            ddl_path   = os.path.join(GLOBAL_DIR, 'config', 'config_schema_ddl.sql')

            btn_c1, btn_c2, btn_c3 = st.columns([1, 1, 1])
            with btn_c1:
                _show_output(output, 'Tool 3 Output')
            with btn_c2:
                if os.path.exists(sql_path):
                    if st.button('📋 View Config Data SQL', key='view_config_sql'):
                        _output_popup(f'Config Data SQL — {report_name}', _read_file(sql_path))
            with btn_c3:
                if os.path.exists(ddl_path):
                    if st.button('📋 View Schema DDL', key='view_schema_ddl'):
                        _output_popup('Config Schema DDL', _read_file(ddl_path))

            dl_c1, dl_c2 = st.columns(2)
            with dl_c1:
                if os.path.exists(sql_path):
                    _download('Download config_data.sql', sql_path, 'text/plain')
            with dl_c2:
                if os.path.exists(ddl_path):
                    _download('Download config_schema_ddl.sql', ddl_path, 'text/plain')

            st.info('Run order:\n'
                    '1. `global/config/config_schema_ddl.sql` — once per environment\n'
                    '2. `reports/.../config/..._config_data.sql` — once per report')


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — Deploy Scripts (Tool 4)
# ─────────────────────────────────────────────────────────────────────────────

with tabs[3]:
    st.subheader('Step 4 — ADF Deployment Scripts')
    st.caption('Generates deployment scripts and optionally auto-deploys to Azure POC.')

    if not report_name:
        st.warning('Select a report in the sidebar first.')
    else:
        arm_path = os.path.join(REPORTS_DIR, report_name, 'adf', 'arm_template.json')
        if not _prereq(os.path.exists(arm_path),
                       'ARM template not found. Run Step 2 first.'):
            pass
        else:
            st.success('ARM template found.')

            verbose4 = st.checkbox('Verbose output', key='tool4_verbose')

            col_gen, col_deploy = st.columns([1, 1])
            with col_gen:
                if st.button('▶  Generate Deploy Scripts', type='primary', key='btn_tool4'):
                    _clear_from_step(report_name, 4)
                    from tool4_adf_deploy import generate_deploy
                    with st.spinner('Generating deployment scripts...'):
                        ok, output = _capture(generate_deploy, report_name, verbose=verbose4)
                    st.session_state['tool4_output'] = output
                    st.session_state['tool4_ok'] = ok
                    _write_process_log(report_name, 4, 'deploy_scripts', ok, output)

            with col_deploy:
                az_cfg_path = os.path.join(GLOBAL_DIR, 'poc_azure_config.json')
                if os.path.exists(az_cfg_path):
                    func_script_exists = os.path.exists(
                        os.path.join(FUNC_WRITER_DIR, 'deploy', 'deploy_func.ps1'))
                    deploy_func_cb = st.checkbox(
                        'Include Excel Writer function deployment',
                        value=func_script_exists and not _func_url_is_set(report_name),
                        key='t4_deploy_func',
                        help='Runs deploy_func.ps1 first, then saves the function URL into the '
                             'ARM template before deploying ADF.',
                        disabled=not func_script_exists,
                    )

                    # ── Excel Writer URL (Step 6 inline) ──────────────────────
                    st.markdown('**Excel Writer URL**')
                    _cur_url = _get_excel_writer_url(report_name)
                    if _func_url_is_set(report_name):
                        st.caption('✅ URL is set')
                    else:
                        st.caption('⚠️ Placeholder — paste the deployed Function URL below')
                    t4_url_input = st.text_input(
                        'Function URL',
                        value=_cur_url,
                        key='t4_excel_writer_url',
                        label_visibility='collapsed',
                        placeholder='https://func-excel-writer-poc.azurewebsites.net/api/excel_writer?code=...',
                    )

                    if st.button('🚀  Deploy to Azure POC', type='primary', key='btn_az_deploy'):
                        _url_to_save = (t4_url_input or '').strip()
                        if _url_to_save and _url_to_save != _cur_url:
                            _save_excel_writer_url(report_name, _url_to_save)
                        spinner_msg = (
                            'Deploying Excel Writer function + ADF — this may take a few minutes...'
                            if deploy_func_cb else
                            'Deploying to Azure POC — this may take a minute...'
                        )
                        with st.spinner(spinner_msg):
                            ok, output = _run_az_deploy(report_name,
                                                        deploy_func_app=deploy_func_cb)
                        st.session_state['tool4_az_output'] = output
                        st.session_state['tool4_az_ok'] = ok
                        _write_process_log(report_name, 4, 'azure_deploy', ok, output)
                else:
                    st.caption('poc_azure_config.json not found in global/')

        if 'tool4_output' in st.session_state or 'tool4_az_output' in st.session_state:
            deploy_dir = os.path.join(REPORTS_DIR, report_name, 'adf', 'deploy')
            safe_name  = ''.join(c if c.isalnum() or c == '_' else '_' for c in report_name)

            # Status messages
            if 'tool4_output' in st.session_state:
                if st.session_state['tool4_ok']:
                    st.success('Deployment scripts generated.')
                else:
                    st.error('Script generation failed.')

            if 'tool4_az_output' in st.session_state:
                if st.session_state['tool4_az_ok']:
                    st.success('Deployed to Azure POC successfully.')
                else:
                    st.error('Azure deployment failed. View output for details.')

            # Popup buttons row
            btn_cols = st.columns([1, 1, 1, 2])
            with btn_cols[0]:
                if 'tool4_output' in st.session_state:
                    _show_output(st.session_state['tool4_output'], 'Tool 4 Output')
            with btn_cols[1]:
                if 'tool4_az_output' in st.session_state:
                    if st.button('📋 View Deploy Output', key='view_az_output'):
                        _output_popup(f'Azure Deployment Output — {report_name}',
                                      st.session_state['tool4_az_output'])
            with btn_cols[2]:
                if os.path.exists(deploy_dir):
                    checklist_path = os.path.join(deploy_dir, 'deployment_checklist.txt')
                    if os.path.exists(checklist_path):
                        if st.button('📋 View Deployment Checklist', key='view_checklist'):
                            _output_popup(f'Deployment Checklist — {report_name}',
                                          _read_file(checklist_path))

                cols = st.columns(4)
                scripts = [
                    ('deploy_bootstrap.ps1', 'Bootstrap PS1'),
                    ('deploy_bootstrap.sh',  'Bootstrap SH'),
                    (f'deploy_{safe_name}.ps1', 'Report PS1'),
                    (f'deploy_{safe_name}.sh',  'Report SH'),
                ]
                for i, (fname, label) in enumerate(scripts):
                    with cols[i]:
                        _download(f'Download {label}',
                                  os.path.join(deploy_dir, fname), 'text/plain')


# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 — Blob Upload (Tool 5)
# ─────────────────────────────────────────────────────────────────────────────

with tabs[4]:
    st.subheader('Step 5 — Blob Upload Scripts')
    st.caption('Generates az storage blob upload scripts — templates upload to the shared '
               '`toad-poc-reports/templates/` container; report output goes to a per-report container.')

    if not report_name:
        st.warning('Select a report in the sidebar first.')
    else:
        san_path = os.path.join(REPORTS_DIR, report_name, 'sanitized',
                                f'{report_name}_sanitized.txt')
        if not _prereq(os.path.exists(san_path),
                       'Sanitized XML not found. Run Step 1 first.'):
            pass
        else:
            st.success('Sanitized XML found.')

            # XLSM template upload widget
            xlsm_dir = os.path.join(BASE_DIR, 'report_templates')
            os.makedirs(xlsm_dir, exist_ok=True)
            existing_xlsm = glob.glob(os.path.join(xlsm_dir, '*.xlsm'))

            st.markdown('**Upload Excel template (.xlsm)**')
            xlsm_upload = st.file_uploader(
                'Upload .xlsm template file',
                type=['xlsm'], key='tool5_xlsm')
            if xlsm_upload:
                dest = os.path.join(xlsm_dir, xlsm_upload.name)
                with open(dest, 'wb') as f:
                    f.write(xlsm_upload.read())
                st.success(f'Saved to report_templates/{xlsm_upload.name}')
                existing_xlsm = glob.glob(os.path.join(xlsm_dir, '*.xlsm'))

            if existing_xlsm:
                st.info('Templates in report_templates/:\n' +
                        '\n'.join(f'  - {os.path.basename(p)}' for p in existing_xlsm))
            else:
                st.warning('No .xlsm file found in report_templates/. Upload one above.')

            verbose5 = st.checkbox('Verbose output', key='tool5_verbose')

            if st.button('▶  Generate Blob Upload Scripts', type='primary', key='btn_tool5'):
                _clear_from_step(report_name, 5)
                from tool5_blob_upload import generate_upload
                with st.spinner('Generating upload scripts...'):
                    ok, output = _capture(generate_upload, report_name, verbose5)
                st.session_state['tool5_output'] = output
                st.session_state['tool5_ok'] = ok
                _write_process_log(report_name, 5, 'blob_upload', ok, output)

        if 'tool5_output' in st.session_state:
            ok     = st.session_state['tool5_ok']
            output = st.session_state['tool5_output']

            if ok:
                st.success('Blob upload scripts generated.')
            else:
                st.error('Generation failed. See output below.')

            blob_dir  = os.path.join(REPORTS_DIR, report_name, 'blob')
            safe_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in report_name)

            btn_c1, btn_c2 = st.columns([1, 1])
            with btn_c1:
                _show_output(output, 'Tool 5 Output')
            with btn_c2:
                if os.path.exists(blob_dir):
                    checklist_path = os.path.join(blob_dir, 'blob_checklist.txt')
                    if os.path.exists(checklist_path):
                        if st.button('📋 View Blob Checklist', key='view_blob_checklist'):
                            _output_popup(f'Blob Upload Checklist — {report_name}',
                                          _read_file(checklist_path))

                cols = st.columns(2)
                with cols[0]:
                    _download('Download upload PS1',
                              os.path.join(blob_dir, f'upload_{safe_name}.ps1'), 'text/plain')
                with cols[1]:
                    _download('Download upload SH',
                              os.path.join(blob_dir, f'upload_{safe_name}.sh'), 'text/plain')


# ─────────────────────────────────────────────────────────────────────────────
# TAB 6 — Excel Writer Function
# ─────────────────────────────────────────────────────────────────────────────

with tabs[5]:
    st.subheader('Step 6 — Excel Writer Function')
    st.caption(
        'Deploy the Azure Function that populates Excel (.xlsm) templates with report data, '
        'then configure the function URL in this report\'s ARM template.'
    )

    # ── Section A: Environment (one-time deploy + unit tests) ─────────────────
    st.markdown('### Environment Setup (once per Azure environment)')

    env_c1, env_c2 = st.columns([1, 1])

    with env_c1:
        st.markdown('**Deploy to Azure POC**')
        st.markdown(
            'Runs `deploy_func.ps1` which:\n'
            '- Creates the Function App (Python 3.11, consumption)\n'
            '- Assigns managed identity + Key Vault access\n'
            '- Sets connection strings as Key Vault references\n'
            '- Zip-deploys the function code'
        )
        az_cfg_path = os.path.join(GLOBAL_DIR, 'poc_azure_config.json')
        if not os.path.exists(az_cfg_path):
            st.warning('poc_azure_config.json not found in global/ — required for deployment.')
        elif not os.path.exists(os.path.join(FUNC_WRITER_DIR, 'deploy', 'deploy_func.ps1')):
            st.warning('deploy_func.ps1 not found in func_excel_writer/deploy/')
        else:
            if st.button('🚀  Deploy to Azure POC', type='primary', key='btn_func_deploy'):
                with st.spinner('Deploying Excel Writer function — this may take a few minutes...'):
                    ok, output = _run_func_deploy()
                st.session_state['tool6_deploy_output'] = output
                st.session_state['tool6_deploy_ok'] = ok

        if 'tool6_deploy_ok' in st.session_state:
            if st.session_state['tool6_deploy_ok']:
                st.success('Function deployed successfully.')
            else:
                st.error('Deployment failed. View output for details.')
            if st.button('📋 View Deploy Output', key='view_func_deploy_out'):
                _output_popup('Excel Writer — Deploy Output',
                              st.session_state['tool6_deploy_output'])

    with env_c2:
        st.markdown('**Unit Tests (no Azure needed)**')
        st.markdown(
            'Runs `test_unit.py` — verifies the Excel template-writing logic '
            'in isolation using in-memory files. No Azure connections required.'
        )
        test_py = os.path.join(FUNC_WRITER_DIR, 'test_unit.py')
        if not os.path.exists(test_py):
            st.warning('test_unit.py not found in func_excel_writer/')
        else:
            if st.button('▶  Run Unit Tests', type='primary', key='btn_func_tests'):
                with st.spinner('Running unit tests...'):
                    ok, output = _run_unit_tests()
                st.session_state['tool6_test_output'] = output
                st.session_state['tool6_test_ok'] = ok

        if 'tool6_test_ok' in st.session_state:
            if st.session_state['tool6_test_ok']:
                st.success('All unit tests passed.')
            else:
                st.error('One or more unit tests failed.')
            if st.button('📋 View Test Output', key='view_func_test_out'):
                _output_popup('Excel Writer — Unit Test Output',
                              st.session_state['tool6_test_output'])

    st.divider()

    # ── Section B: Per-report function URL configuration ─────────────────────
    st.markdown('### Configure Function URL (per report)')

    if not report_name:
        st.warning('Select a report in the sidebar first.')
    else:
        arm_path = os.path.join(REPORTS_DIR, report_name, 'adf', 'arm_template.json')
        if not _prereq(os.path.exists(arm_path),
                       'ARM template not found. Run Step 2 (ADF Templates) first.'):
            pass
        else:
            import json as _json_t6

            # Read current value from the ARM template
            current_url = ''
            try:
                with open(arm_path, encoding='utf-8') as _f:
                    _arm = _json_t6.load(_f)
                for _res in _arm.get('resources', []):
                    _params = _res.get('properties', {}).get('parameters', {})
                    if 'excel_writer_url' in _params:
                        current_url = _params['excel_writer_url'].get('defaultValue', '')
                        break
            except Exception:
                pass

            is_placeholder = not current_url or '<' in current_url
            if is_placeholder:
                st.warning(f'Function URL is not yet configured.  Current value: `{current_url}`')
            else:
                st.success(f'Function URL is set: `{current_url}`')

            st.markdown('**Enter the function URL** (printed at the end of `deploy_func.ps1` output):')
            new_url = st.text_input(
                'excel_writer_url',
                value='' if is_placeholder else current_url,
                placeholder='https://<func-app>.azurewebsites.net/api/excel_writer?code=...',
                key='t6_url_input',
                label_visibility='collapsed',
            )

            if st.button('💾  Save URL to ARM Templates', type='primary', key='btn_save_url'):
                if not new_url.strip():
                    st.error('Enter a URL before saving.')
                elif not new_url.strip().startswith('https://'):
                    st.error('URL must start with https://')
                else:
                    n, names = _save_excel_writer_url(report_name, new_url.strip())
                    if n:
                        st.success(f'URL saved to {n} file(s): {", ".join(names)}')
                    else:
                        st.warning('No files were updated — excel_writer_url parameter not found in ARM templates.')

            st.divider()

            # ── Section C: Integration testing ───────────────────────────────
            st.markdown('### Integration Testing')
            st.caption(
                'Deploys the function, saves its URL into the ARM template, '
                'then shows the command to run the integration test locally.'
            )

            func_script_exists = os.path.exists(
                os.path.join(FUNC_WRITER_DIR, 'deploy', 'deploy_func.ps1'))

            if not func_script_exists:
                st.warning('deploy_func.ps1 not found — cannot deploy function from here.')
            else:
                if st.button('🚀  Deploy Function & Update ARM Template',
                             type='primary', key='btn_pre_test_deploy'):
                    with st.spinner('Deploying Excel Writer function...'):
                        dep_ok, dep_out = _run_func_deploy()
                    st.session_state['tool6_pre_test_output'] = dep_out
                    st.session_state['tool6_pre_test_ok']     = dep_ok

                    if dep_ok:
                        import re as _re_t6
                        url_m = _re_t6.search(
                            r'https://[^\s]+/api/excel_writer[^\s]*', dep_out)
                        if url_m:
                            extracted = url_m.group(0).rstrip(')')
                            n, names = _save_excel_writer_url(report_name, extracted)
                            st.session_state['tool6_pre_test_url'] = extracted
                            st.session_state['tool6_pre_test_saved'] = n
                        else:
                            st.session_state.pop('tool6_pre_test_url', None)
                            st.session_state['tool6_pre_test_saved'] = 0

            # Show deploy result
            if 'tool6_pre_test_ok' in st.session_state:
                pre_ok  = st.session_state['tool6_pre_test_ok']
                pre_out = st.session_state['tool6_pre_test_output']
                pre_url = st.session_state.get('tool6_pre_test_url', '')
                pre_n   = st.session_state.get('tool6_pre_test_saved', 0)

                if pre_ok:
                    if pre_url:
                        st.success(f'Function deployed. URL: `{pre_url}`')
                        if pre_n:
                            st.success(f'ARM template updated ({pre_n} file(s)).')
                    else:
                        st.warning(
                            'Function deployed but URL could not be parsed from output. '
                            'Copy it from the output below and save it via the input field above.')
                else:
                    st.error('Function deployment failed.')

                if st.button('📋 View Deploy Output', key='view_pre_test_out'):
                    _output_popup('Pre-test Deploy Output', pre_out)

            st.divider()

            # Show integration test command (always, so user can copy it)
            from datetime import date as _date
            today_str = _date.today().strftime('%d.%m.%Y')

            int_cmd = (
                f'cd {FUNC_WRITER_DIR}\n'
                f'python test_integration.py {report_name} {today_str}'
            )
            st.markdown('**Run this command locally once the function is deployed:**')
            st.code(int_cmd, language='bash')

            tmpl_path = os.path.join(FUNC_WRITER_DIR, 'local.settings.json.template')
            if os.path.exists(tmpl_path):
                st.info(
                    'Copy `func_excel_writer/local.settings.json.template` → '
                    '`func_excel_writer/local.settings.json` and fill in your connection '
                    'strings before running the integration test.'
                )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 7 — POC Tools (Tool 1.01 + Tool 1.02)
# ─────────────────────────────────────────────────────────────────────────────

with tabs[6]:
    st.subheader('POC Tools (Dev / Feasibility only)')
    st.caption('These tools generate synthetic test data and DDL scripts. '
               'Not needed for production migration — POC only.')

    # ── Reset Environment ──────────────────────────────────────────────────────
    with st.expander('🗑️  Reset Environment — Clear All Config & ADF', expanded=False):
        st.warning(
            '**This will permanently delete:**\n'
            '- All rows in `config.report`, `config.report_sql`, `config.report_email`\n'
            '- All ADF triggers, pipelines, datasets, and linked services\n\n'
            'Local report files are **not** affected. You can re-deploy from scratch via the UI.'
        )

        # Live counts
        if st.button('🔍  Check current state', key='btn_clear_check'):
            with st.spinner('Checking Azure + SQL...'):
                counts = _get_clear_all_counts()
            st.session_state['clear_all_counts'] = counts

        if 'clear_all_counts' in st.session_state:
            c = st.session_state['clear_all_counts']
            if c:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('**SQL Config DB**')
                    st.markdown(f'- `config.report` — **{c.get("config.report", "?")}** rows')
                    st.markdown(f'- `config.report_sql` — **{c.get("config.report_sql", "?")}** rows')
                    st.markdown(f'- `config.report_email` — **{c.get("config.report_email", "?")}** rows')
                with col2:
                    st.markdown('**Azure Data Factory**')
                    st.markdown(f'- Pipelines — **{c.get("adf_pipelines", "?")}**')
                    st.markdown(f'- Triggers — **{c.get("adf_triggers", "?")}**')
                    st.markdown(f'- Datasets — **{c.get("adf_datasets", "?")}**')
                    st.markdown(f'- Linked Services — **{c.get("adf_linked_services", "?")}**')
            else:
                st.error('Could not read config — check poc_azure_config.json exists.')

        st.divider()
        confirm = st.checkbox(
            'I understand this will delete all config data and ADF resources',
            key='clear_all_confirm')
        if st.button('🗑️  Clear All', type='primary', disabled=not confirm, key='btn_clear_all'):
            with st.spinner('Clearing SQL config and ADF resources...'):
                ok, log = _run_clear_all()
            st.session_state['clear_all_output'] = log
            st.session_state['clear_all_ok'] = ok
            st.session_state.pop('clear_all_counts', None)

        if 'clear_all_output' in st.session_state:
            if st.session_state['clear_all_ok']:
                st.success('Environment cleared successfully.')
            else:
                st.error('Clear failed — see details below.')
            _show_output(st.session_state['clear_all_output'], 'Clear All Output')

    st.divider()

    if not report_name:
        st.warning('Select a report in the sidebar first.')
    else:
        # ── Tool 1.01 ──────────────────────────────────────────────────────────
        st.markdown('### Tool 1.01 — Mock Data Generator')
        st.caption('Reads 10 seed rows from input/seed/{report}/ and generates synthetic mock data.')

        seed_dir = os.path.join(INPUT_DIR, 'seed', report_name)
        if os.path.exists(seed_dir):
            seed_files = glob.glob(os.path.join(seed_dir, '*.csv'))
            st.success(f'{len(seed_files)} seed file(s) found in input/seed/{report_name}/')
        else:
            st.warning(f'No seed files found in input/seed/{report_name}/. '
                       'Place one CSV per table there first.')

        c1, c2 = st.columns([1, 1])
        with c1:
            n_rows = st.number_input('Rows to generate', min_value=100, max_value=10000,
                                     value=1000, step=100, key='tool101_rows')
        with c2:
            verbose101 = st.checkbox('Verbose output', key='tool101_verbose')

        if st.button('▶  Generate Mock Data', key='btn_tool101'):
            from tool1_01_mock_data import generate_report
            with st.spinner('Generating mock data...'):
                ok, output = _capture(generate_report, report_name, n_rows, verbose101)
            st.session_state['tool101_output'] = output
            st.session_state['tool101_ok'] = ok

        if 'tool101_output' in st.session_state:
            ok     = st.session_state['tool101_ok']
            output = st.session_state['tool101_output']
            if ok:
                st.success('Mock data generated.')
            else:
                st.error('Failed. See output below.')
            _show_output(output, 'Tool 1.01 Output')

            mock_dir = os.path.join(REPORTS_DIR, report_name, 'mock_data')
            if os.path.exists(mock_dir):
                csvs = glob.glob(os.path.join(mock_dir, '*.csv'))
                if csvs:
                    sel = st.selectbox('Preview table', [os.path.basename(p) for p in sorted(csvs)],
                                       key='tool101_preview_sel')
                    if sel:
                        try:
                            import pandas as pd
                            df = pd.read_csv(os.path.join(mock_dir, sel))
                            st.dataframe(df.head(20), use_container_width=True)
                        except Exception as e:
                            st.error(str(e))

        st.divider()

        # ── Tool 1.02 ──────────────────────────────────────────────────────────
        st.markdown('### Tool 1.02 — DDL Generator')
        st.caption('Infers SQL column types from mock data and generates CREATE TABLE DDL scripts.')

        mock_dir = os.path.join(REPORTS_DIR, report_name, 'mock_data')
        if not _prereq(os.path.exists(mock_dir),
                       'Mock data not found. Run Tool 1.01 first.'):
            pass
        else:
            verbose102 = st.checkbox('Verbose output', key='tool102_verbose')

            if st.button('▶  Generate DDL', key='btn_tool102'):
                from tool1_02_ddl_generator import generate_ddl
                with st.spinner('Generating DDL...'):
                    ok, output = _capture(generate_ddl, report_name, verbose102)
                st.session_state['tool102_output'] = output
                st.session_state['tool102_ok'] = ok

            if 'tool102_output' in st.session_state:
                ok     = st.session_state['tool102_ok']
                output = st.session_state['tool102_output']
                if ok:
                    st.success('DDL generated.')
                else:
                    st.error('Failed. See output below.')
                _show_output(output, 'Tool 1.02 Output')

                ddl_path = os.path.join(REPORTS_DIR, report_name, 'ddl',
                                        f'{report_name}_ddl.sql')
                if os.path.exists(ddl_path):
                    with st.expander('Preview DDL'):
                        st.code(_read_file(ddl_path), language='sql')
                    _download('Download DDL SQL', ddl_path, 'text/plain')
