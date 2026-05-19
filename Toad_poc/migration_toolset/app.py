"""
Toad Migration Toolset - Streamlit UI
Run: streamlit run app.py  (from migration_toolset/ directory)
"""

import base64
import contextlib
import csv
import io
import os
import sys
import glob

import streamlit as st

# ── Path setup ───────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.join(BASE_DIR, 'tools')
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

INPUT_DIR   = os.path.join(BASE_DIR, 'input')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
GLOBAL_DIR  = os.path.join(BASE_DIR, 'global')

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title='Toad Migration Toolset',
    page_icon='🔧',
    layout='wide',
    initial_sidebar_state='expanded',
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

    /* ── Sidebar ─────────────────────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 3px solid #5EE340;
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
    .main .block-container {
        background-color: #FFFFFF;
        padding-top: 0.2rem;
    }

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
    .stTabs [data-baseweb="tab-list"] {
        background-color: #F5F7FA;
        border-radius: 8px 8px 0 0;
        gap: 4px;
        padding: 4px 4px 0 4px;
        border-bottom: 2px solid #DDE3EC;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px 6px 0 0;
        font-weight: 600;
        font-size: 13px;
        color: #4A6278;
        padding: 8px 16px;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #FFFFFF;
        color: #000000 !important;
        border-bottom: 3px solid #5EE340 !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #000000 !important;
        background-color: #EDF0F5;
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
    }


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


def _read_file(path):
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception:
        return ''


def _show_output(text, label='Output'):
    if text.strip():
        st.markdown(f'<div class="section-title">{label}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="output-box">{text}</div>', unsafe_allow_html=True)


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


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    logo_path = os.path.join(BASE_DIR, 'assets', 'nxzen_logo.png')
    if os.path.exists(logo_path):
        st.image(logo_path, width=140)
    st.title('🔧 Migration Toolset')
    st.caption('Toad → Azure Data Factory')
    st.divider()

    # Run mode
    st.subheader('Run Mode')
    run_mode = st.radio('run_mode', ['Single Report', 'Batch Run'],
                        horizontal=True, label_visibility='collapsed')

    st.divider()

    report_name = None  # default

    if run_mode == 'Single Report':
        st.subheader('Report')
        reports = _existing_reports()
        sel_mode = st.radio('sel_mode', ['Choose existing', 'Enter name'],
                            horizontal=True, label_visibility='collapsed')

        if sel_mode == 'Choose existing':
            report_name = st.selectbox('Report', reports,
                                       placeholder='-- select --',
                                       index=None) if reports else None
            if not reports:
                st.info('No reports yet. Upload a file in the Sanitize tab.')
        else:
            report_name = st.text_input('Report name',
                                        placeholder='e.g. BC_BIMIO_267_Daily')
            if report_name:
                report_name = report_name.strip()

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
            }
            for step, label in STEP_LABELS.items():
                done = status.get(step, False)
                icon = '✅' if done else '⭕'
                st.markdown(f'{icon} **Step {step}** — {label}')
        else:
            st.info('Select or enter a report name above.')

    else:  # Batch Run
        st.subheader('Batch Selection')
        all_files = _input_files()
        total = len(all_files)

        if total == 0:
            st.warning('No files in input/ yet.')
        else:
            st.caption(f'{total} file(s) found in input/')

            # Select first N
            nc1, nc2 = st.columns([2, 1])
            with nc1:
                first_n = st.number_input('Select first N files', min_value=1,
                                          max_value=total, value=min(10, total),
                                          step=1, key='batch_first_n')
            with nc2:
                st.markdown('<div style="margin-top:28px"></div>',
                            unsafe_allow_html=True)
                if st.button('Select', use_container_width=True, key='btn_first_n'):
                    st.session_state['batch_files'] = all_files[:int(first_n)]

            # Select all
            if st.button(f'Select All ({total})', use_container_width=True):
                st.session_state['batch_files'] = all_files

            # Manual multi-select
            selected = st.multiselect(
                'Or pick individual files',
                all_files,
                default=st.session_state.get('batch_files', []),
                key='batch_multiselect',
            )
            st.session_state['batch_files'] = selected
            st.caption(f'{len(selected)} file(s) selected')

        st.divider()
        if 'batch_results' in st.session_state:
            results = st.session_state['batch_results']
            done_count = sum(1 for r in results if all(
                r.get(f't{i}', False) for i in range(1, 6)))
            st.metric('Completed', f'{done_count} / {len(results)}')

    st.divider()
    st.caption('All tools run locally. No Azure connections made.')


# ─────────────────────────────────────────────────────────────────────────────
# Main header  (fixed height ≈ 1 inch / 96px)
# ─────────────────────────────────────────────────────────────────────────────

_logo_path = os.path.join(BASE_DIR, 'assets', 'nxzen_logo.png')
_logo_b64  = ''
if os.path.exists(_logo_path):
    with open(_logo_path, 'rb') as _f:
        _logo_b64 = base64.b64encode(_f.read()).decode()

_logo_img = (f'<img src="data:image/png;base64,{_logo_b64}" '
             f'style="height:56px;object-fit:contain;" />'
             if _logo_b64 else '')

st.markdown(f"""
<div style="
    display: flex;
    align-items: center;
    gap: 16px;
    height: 96px;
    padding: 0 8px;
    background: #ffffff;
    border-bottom: 2px solid #5EE340;
    margin-bottom: 12px;
">
    {_logo_img}
    <span style="font-size:20px;font-weight:700;color:#000000;letter-spacing:-0.3px;">
        🔧 Toad Migration Toolset
    </span>
</div>
""", unsafe_allow_html=True)

if run_mode == 'Single Report':
    if report_name:
        st.caption(f'Working on: **{report_name}**')
    else:
        st.caption('Select a report in the sidebar to begin.')
else:
    n_sel = len(st.session_state.get('batch_files', []))
    st.caption(f'Batch mode — {n_sel} file(s) selected')

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# BATCH MODE
# ─────────────────────────────────────────────────────────────────────────────

if run_mode == 'Batch Run':
    st.subheader('Batch Run')

    batch_files = st.session_state.get('batch_files', [])

    if not batch_files:
        st.info('Select files to process using the sidebar — type a number and click Select, '
                'use Select All, or pick individual files from the multiselect.')
    else:
        st.markdown(f'**{len(batch_files)} file(s) queued:**')
        with st.expander('Show selected files', expanded=False):
            for f in batch_files:
                st.text(f'  {f}')

        st.divider()

        # Tool selection
        st.markdown('**Select tools to run for each report:**')
        bc1, bc2, bc3, bc4, bc5 = st.columns(5)
        with bc1: run_t1 = st.checkbox('Tool 1\nSanitize',      value=True,  key='b_t1')
        with bc2: run_t2 = st.checkbox('Tool 2\nADF Templates', value=True,  key='b_t2')
        with bc3: run_t3 = st.checkbox('Tool 3\nConfig Setup',  value=True,  key='b_t3')
        with bc4: run_t4 = st.checkbox('Tool 4\nDeploy Scripts',value=False, key='b_t4')
        with bc5: run_t5 = st.checkbox('Tool 5\nBlob Upload',   value=False, key='b_t5')

        # Options row
        oc1, oc2, oc3 = st.columns([1, 1, 2])
        with oc1: batch_poc  = st.checkbox('POC mode (Tool 3)', key='b_poc')
        with oc2: batch_verb = st.checkbox('Verbose output',    key='b_verb')
        with oc3: batch_rg   = st.text_input('Resource Group (Tool 4)',
                                             placeholder='<your-resource-group>',
                                             key='b_rg')

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
            rg = batch_rg.strip() or '<your-resource-group>'

            results = []
            progress_bar = st.progress(0, text='Starting...')
            status_box   = st.empty()

            for idx, fname in enumerate(batch_files):
                xml_path = os.path.join(INPUT_DIR, fname)
                row = {'file': fname, 'report_name': '', 't1': None, 't2': None,
                       't3': None, 't4': None, 't5': None, 'errors': []}

                pct  = (idx) / len(batch_files)
                progress_bar.progress(pct, text=f'Processing {idx+1}/{len(batch_files)}: {fname}')
                status_box.info(f'Processing: **{fname}**')

                # Tool 1 — always run if selected (provides report_name)
                if run_t1:
                    ok, out = _capture(sanitize_file, xml_path, registry, batch_verb)
                    registry.save()
                    row['t1'] = ok
                    if not ok:
                        row['errors'].append(f'Tool 1: {out.splitlines()[-1] if out.strip() else "failed"}')
                    else:
                        # Extract report_name from output line
                        for line in out.splitlines():
                            if 'Sanitized' in line and ':' in line:
                                path_part = line.split(':', 1)[1].strip()
                                rn = os.path.basename(os.path.dirname(path_part))
                                if rn:
                                    row['report_name'] = rn
                                break
                        # Fallback: derive from filename
                        if not row['report_name']:
                            row['report_name'] = os.path.splitext(fname)[0]
                else:
                    # Derive report_name from filename as fallback
                    row['report_name'] = os.path.splitext(fname)[0]

                rn = row['report_name']

                # Tools 2-5 need a report_name
                if rn:
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
                        ok, out = _capture(generate_deploy, rn, rg, batch_verb)
                        row['t4'] = ok
                        if not ok:
                            row['errors'].append(f'Tool 4: {out.splitlines()[-1] if out.strip() else "failed"}')

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
            rows = []
            for r in results:
                rows.append({
                    'File':         r['file'],
                    'Report Name':  r['report_name'] or '(unknown)',
                    'Tool 1':       _cell(r['t1']),
                    'Tool 2':       _cell(r['t2']),
                    'Tool 3':       _cell(r['t3']),
                    'Tool 4':       _cell(r['t4']),
                    'Tool 5':       _cell(r['t5']),
                    'Errors':       ' | '.join(r['errors']) if r['errors'] else '',
                })
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Summary metrics
            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                total = len(results)
                st.metric('Total files', total)
            with mc2:
                ok_count = sum(1 for r in results
                               if all(r.get(f't{i}') is not False
                                      for i in range(1, 6)))
                st.metric('All steps OK', ok_count)
            with mc3:
                err_count = sum(1 for r in results if r['errors'])
                st.metric('With errors', err_count)

            if st.button('Clear results', key='btn_clear_batch'):
                del st.session_state['batch_results']
                st.rerun()

    # Stop here — don't show single-report tabs in batch mode
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# SINGLE REPORT — Tabs
# ─────────────────────────────────────────────────────────────────────────────

# Tabs
tabs = st.tabs([
    '1 - Sanitize',
    '2 - ADF Templates',
    '3 - Config Setup',
    '4 - Deploy Scripts',
    '5 - Blob Upload',
    '6 - POC Tools',
])


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
                registry.save()

            st.session_state['tool1_output'] = output
            st.session_state['tool1_ok'] = ok

    # Show results
    if 'tool1_output' in st.session_state:
        ok     = st.session_state['tool1_ok']
        output = st.session_state['tool1_output']

        if ok:
            st.success('Sanitization complete.')
        else:
            st.error('Sanitization failed. See output below.')

        _show_output(output, 'Tool 1 Output')

        # Show mapping CSV if it exists
        if report_name:
            mapping_path = os.path.join(REPORTS_DIR, report_name, 'sanitized',
                                        f'{report_name}_mapping.csv')
            if os.path.exists(mapping_path):
                with st.expander('View mapping table (real → mock)'):
                    try:
                        import pandas as pd
                        df = pd.read_csv(mapping_path)
                        st.dataframe(df, use_container_width=True)
                    except Exception:
                        st.code(_read_file(mapping_path))

                _download('Download mapping CSV', mapping_path, 'text/csv')

            san_path = os.path.join(REPORTS_DIR, report_name, 'sanitized',
                                    f'{report_name}_sanitized.txt')
            _download('Download sanitized XML', san_path)


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
                from tool2_adf_generator import generate_adf
                with st.spinner('Generating ADF ARM templates...'):
                    ok, output = _capture(generate_adf, report_name, verbose2)
                st.session_state['tool2_output'] = output
                st.session_state['tool2_ok'] = ok

        if 'tool2_output' in st.session_state:
            ok     = st.session_state['tool2_ok']
            output = st.session_state['tool2_output']

            if ok:
                st.success('ADF templates generated.')
            else:
                st.error('Generation failed. See output below.')

            _show_output(output, 'Tool 2 Output')

            # List generated files
            adf_dir = os.path.join(REPORTS_DIR, report_name, 'adf')
            if os.path.exists(adf_dir):
                with st.expander('View generated files'):
                    all_files = glob.glob(os.path.join(adf_dir, '**', '*.json'), recursive=True)
                    for fp in sorted(all_files):
                        rel = os.path.relpath(fp, adf_dir)
                        st.code(rel, language=None)

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
                from tool3_config_setup import generate_config
                with st.spinner('Generating config SQL...'):
                    ok, output = _capture(generate_config, report_name, verbose3, poc_mode)
                st.session_state['tool3_output'] = output
                st.session_state['tool3_ok'] = ok

        if 'tool3_output' in st.session_state:
            ok     = st.session_state['tool3_ok']
            output = st.session_state['tool3_output']

            if ok:
                st.success('Config SQL generated.')
            else:
                st.error('Generation failed. See output below.')

            _show_output(output, 'Tool 3 Output')

            config_dir = os.path.join(REPORTS_DIR, report_name, 'config')
            sql_path   = os.path.join(config_dir, f'{report_name}_config_data.sql')
            ddl_path   = os.path.join(GLOBAL_DIR, 'config', 'config_schema_ddl.sql')

            c1, c2 = st.columns(2)
            with c1:
                if os.path.exists(sql_path):
                    with st.expander('Preview config data SQL'):
                        st.code(_read_file(sql_path), language='sql')
                    _download('Download config_data.sql', sql_path, 'text/plain')
            with c2:
                if os.path.exists(ddl_path):
                    with st.expander('Preview schema DDL'):
                        st.code(_read_file(ddl_path), language='sql')
                    _download('Download config_schema_ddl.sql', ddl_path, 'text/plain')

            st.info('Run order:\n'
                    '1. `global/config/config_schema_ddl.sql` — once per environment\n'
                    '2. `reports/.../config/..._config_data.sql` — once per report')


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — Deploy Scripts (Tool 4)
# ─────────────────────────────────────────────────────────────────────────────

with tabs[3]:
    st.subheader('Step 4 — ADF Deployment Scripts')
    st.caption('Generates PowerShell + bash az deployment scripts (bootstrap once / per-report).')

    if not report_name:
        st.warning('Select a report in the sidebar first.')
    else:
        arm_path = os.path.join(REPORTS_DIR, report_name, 'adf', 'arm_template.json')
        if not _prereq(os.path.exists(arm_path),
                       'ARM template not found. Run Step 2 first.'):
            pass
        else:
            st.success('ARM template found.')

            c1, c2 = st.columns([1, 1])
            with c1:
                rg_name = st.text_input('Resource Group name (optional)',
                                        placeholder='e.g. rg-toad-poc-uksouth',
                                        key='tool4_rg')
            with c2:
                verbose4 = st.checkbox('Verbose output', key='tool4_verbose')

            if st.button('▶  Generate Deploy Scripts', type='primary', key='btn_tool4'):
                from tool4_adf_deploy import generate_deploy
                rg = rg_name.strip() if rg_name else '<your-resource-group>'
                with st.spinner('Generating deployment scripts...'):
                    ok, output = _capture(generate_deploy, report_name, rg, verbose4)
                st.session_state['tool4_output'] = output
                st.session_state['tool4_ok'] = ok

        if 'tool4_output' in st.session_state:
            ok     = st.session_state['tool4_ok']
            output = st.session_state['tool4_output']

            if ok:
                st.success('Deployment scripts generated.')
            else:
                st.error('Generation failed. See output below.')

            _show_output(output, 'Tool 4 Output')

            deploy_dir = os.path.join(REPORTS_DIR, report_name, 'adf', 'deploy')
            safe_name  = ''.join(c if c.isalnum() or c == '_' else '_' for c in report_name)

            if os.path.exists(deploy_dir):
                checklist_path = os.path.join(deploy_dir, 'deployment_checklist.txt')
                if os.path.exists(checklist_path):
                    with st.expander('Deployment Checklist', expanded=True):
                        st.code(_read_file(checklist_path), language=None)

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
    st.caption('Generates az storage blob upload scripts for Excel (.xlsm) report templates.')

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
            xlsm_dir = os.path.join(GLOBAL_DIR, 'xlsm_templates', report_name)
            existing_xlsm = glob.glob(os.path.join(xlsm_dir, '*.xlsm'))

            st.markdown('**Upload Excel template (.xlsm)**')
            xlsm_upload = st.file_uploader(
                'Upload .xlsm template file',
                type=['xlsm'], key='tool5_xlsm')
            if xlsm_upload:
                os.makedirs(xlsm_dir, exist_ok=True)
                dest = os.path.join(xlsm_dir, xlsm_upload.name)
                with open(dest, 'wb') as f:
                    f.write(xlsm_upload.read())
                st.success(f'Saved to global/xlsm_templates/{report_name}/{xlsm_upload.name}')
                existing_xlsm = glob.glob(os.path.join(xlsm_dir, '*.xlsm'))

            if existing_xlsm:
                st.info('Templates in local folder:\n' +
                        '\n'.join(f'  - {os.path.basename(p)}' for p in existing_xlsm))
            else:
                st.warning(f'No .xlsm file found in global/xlsm_templates/{report_name}/. '
                           'Upload one above.')

            verbose5 = st.checkbox('Verbose output', key='tool5_verbose')

            if st.button('▶  Generate Blob Upload Scripts', type='primary', key='btn_tool5'):
                from tool5_blob_upload import generate_upload
                with st.spinner('Generating upload scripts...'):
                    ok, output = _capture(generate_upload, report_name, verbose5)
                st.session_state['tool5_output'] = output
                st.session_state['tool5_ok'] = ok

        if 'tool5_output' in st.session_state:
            ok     = st.session_state['tool5_ok']
            output = st.session_state['tool5_output']

            if ok:
                st.success('Blob upload scripts generated.')
            else:
                st.error('Generation failed. See output below.')

            _show_output(output, 'Tool 5 Output')

            blob_dir  = os.path.join(REPORTS_DIR, report_name, 'blob')
            safe_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in report_name)

            if os.path.exists(blob_dir):
                checklist_path = os.path.join(blob_dir, 'blob_checklist.txt')
                if os.path.exists(checklist_path):
                    with st.expander('Blob Upload Checklist', expanded=True):
                        st.code(_read_file(checklist_path), language=None)

                cols = st.columns(2)
                with cols[0]:
                    _download('Download upload PS1',
                              os.path.join(blob_dir, f'upload_{safe_name}.ps1'), 'text/plain')
                with cols[1]:
                    _download('Download upload SH',
                              os.path.join(blob_dir, f'upload_{safe_name}.sh'), 'text/plain')


# ─────────────────────────────────────────────────────────────────────────────
# TAB 6 — POC Tools (Tool 1.01 + Tool 1.02)
# ─────────────────────────────────────────────────────────────────────────────

with tabs[5]:
    st.subheader('POC Tools (Dev / Feasibility only)')
    st.caption('These tools generate synthetic test data and DDL scripts. '
               'Not needed for production migration — POC only.')

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
