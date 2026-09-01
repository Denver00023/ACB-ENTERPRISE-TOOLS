import streamlit as st

import uuid
import sqlite3
from datetime import datetime

from utils.theme import load_css

from modules import (

    #AMAZON MODULES
    amazon_xml,
    amazon_aci_json,
    amazon_xml_gets,

    #APC MODULES
    apc,
    apc_billing,
    apc_billing_header_report,
    apc_client_details,
    apc_pallet_id,
    apc_candata,

    #DATA PROCESSING MODULES
    candata,
    aci_json,
    airshipment,
    prohibited,

    #UTILITY MODULES
    ezclear,
    splitpdf,
    compresspdf,
    hscode,
    bankofcanada,
    

)


# --------PAGE CONFIG----------

st.set_page_config(
    page_title="ACB Enterprise Portal",
    page_icon="assets/qwe1.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------LOAD THEME----------
load_css()
# -------------STATE-----------

if "module" not in st.session_state:
    st.session_state.module = "HOME"

if "active_group" not in st.session_state:
    st.session_state.active_group = None

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# ----SIDEBAR NAVIGATION (ENTERPRISE STYLE) ----------
NAV_GROUPS = {

    "🚚 APC": {
        "🚚 APC sFTP": "APC SFTP",
        "💳 APC BILLING DETAIL": "APC BILLING DETAIL",
        "💳 APC CLIENT DETAILS": "APC CLIENT DETAIL",
        "💳 APC BILLING HEADER": "APC BILLING HEADER REPORT",
        "📦 APC PALLET ID": "APC PALLET ID",
        "📊 APC CANDATA UPLOAD FILE": "APC CANDATA UPLOAD FILE"

    },

    "📦 AMAZON": {
        "📊 AMAZON XML TO CANDATA": "AMAZON XML",
        "📦 AMAZON CANDATA TO JSON": "AMAZON CANDATA TO JSON",
        "📊 AMAZON XML GETS": "AMAZON XML GETS",
    },
    
    "📊 Data Processing": {
        "📊 CANDATA UPLOAD FILE": "CANDATA",
        "📦 ACI JSON": "ACI_JSON",
        "✈️ AIR SHIPMENT":"AIRSHIPMENT",
        "📑 PROHIBITED ITEM DETECTION": "PROHIBITED",
    },

    "🛠 Utilities": {
        "📑 SPLIT PDF": "SPLIT PDF",
        "💱 USD ↔️ CAD FX RATES": "BANK OF CANADA",
        "📑 EZCLEAR": "EZCLEAR",
        "📦 Compress PDF": "COMPRESSPDF",
        "🔎 HSCODE SEARCH": "HSCODE",
    }
}

st.sidebar.markdown(
    '''
    <div class="sidebar-menu-title"> ☰ MENU</div>
    <div class="sidebar-menu-caption">NAVIGATION</div>
    ''',
    unsafe_allow_html=True
)

# NAV_GROUPS FUNCTION
for group_name, items in NAV_GROUPS.items():

    is_open = st.session_state.active_group == group_name

    with st.sidebar.expander(group_name, expanded=is_open):

        for label, module in items.items():

            if st.button(
                label,
                key=f"{group_name}_{module}"
            ):

                st.session_state.module = module
                st.session_state.active_group = group_name
                st.rerun()


# ---------------- MODULES .RUN FROM IMPORT ----------------
    MODULES = {

        #APC MODULES
        "APC SFTP": apc.run,
        "APC BILLING DETAIL": apc_billing.run,
        "APC BILLING HEADER REPORT": apc_billing_header_report.run,
        "APC CLIENT DETAIL": apc_client_details.run,
        "APC PALLET ID": apc_pallet_id.run,
        "APC CANDATA UPLOAD FILE": apc_candata.run,

        #AMAZON MODULES
        "AMAZON XML": amazon_xml.run,
        "AMAZON CANDATA TO JSON": amazon_aci_json.run,
        "AMAZON XML GETS": amazon_xml_gets.run,

        #DATA PROCESSING MODULES
        "CANDATA": candata.run,
        "ACI_JSON": aci_json.run,
        "AIRSHIPMENT": airshipment.run,
        "PROHIBITED": prohibited.run,

        #UTILITY MODULES
        "EZCLEAR": ezclear.run,
        "BANK OF CANADA": bankofcanada.run,
        "COMPRESSPDF": compresspdf.run,
        "HSCODE": hscode.run,
        "SPLIT PDF": splitpdf.run,


    }

# ---------------- HOME PAGE ----------------
if st.session_state.module == "HOME":
    
    st.markdown('<div class="main-header">🚀 ACB Enterprise Portal</div>', unsafe_allow_html=True)
    st.caption('<div class="sub-header">Centralized Automation & Validation System</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        Welcome to ACB Toolkit. Select a module from the sidebar to begin processing.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("© 2026 ACB Toolkit | Developed by IT Department")
else:

    module = st.session_state.module

    if module in MODULES:
        try:
            MODULES[module]()
        except Exception as e:
            st.error(f"Failed loading {module}")
            st.exception(e)

    else:
        st.error(f"Module {module} not registered")