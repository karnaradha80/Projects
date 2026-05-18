"""
Toad Migration Toolset - Streamlit UI
Run: streamlit run app.py  (from migration_toolset/ directory)
"""

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
    .step-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 6px;
    }
    .badge-done  { background:#d4edda; color:#155724; }
    .badge-todo  { background:#f8d7da; color:#721c24; }
    .badge-warn  { background:#fff3cd; color:#856404; }
    .output-box  {
        background:#1e1e1e; color:#d4d4d4;
        font-family: monospace; font-size: 13px;
        padding: 14px; border-radius: 6px;
        white-space: pre-wrap; max-height: 380px;
        overflow-y: auto;
    }
    .section-title { font-size: 15px; font-weight: 700; margin-bottom: 4px; }
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
    st.title('🔧 Migration Toolset')
    st.caption('Toad → Azure Data Factory')
    st.divider()

    # Report selection
    st.subheader('Report')
    reports = _existing_reports()
    mode = st.radio('Select mode', ['Choose existing', 'Enter name'],
                    horizontal=True, label_visibility='collapsed')

    if mode == 'Choose existing':
        report_name = st.selectbox('Report', reports,
                                   placeholder='-- select --',
                                   index=None) if reports else None
        if not reports:
            st.info('No reports yet. Upload a file in the Sanitize tab.')
    else:
        report_name = st.text_input('Report name', placeholder='e.g. BC_BIMIO_267_Daily')
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

    st.divider()
    st.caption('All tools run locally. No Azure connections made.')


# ─────────────────────────────────────────────────────────────────────────────
# Main header
# ─────────────────────────────────────────────────────────────────────────────

st.title('🔧 Toad Migration Toolset')
if report_name:
    st.caption(f'Working on: **{report_name}**')
else:
    st.caption('Select a report in the sidebar to begin.')

st.divider()

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
