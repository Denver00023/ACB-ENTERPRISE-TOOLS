import streamlit as st

import apc
import bankofcanada
import candata
import splitpdf
import amazon_xml
import apc_billing
import aci_json
import amazon_xml_gets
import apc_billing_header_report
import apc_client_details
import amazon_aci_json

# --------PAGE CONFIG----------

st.set_page_config(
    page_title="ACB Enterprise Portal",
    page_icon="assets/qwe1.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)


# -------------STATE-----------

if "module" not in st.session_state:
    st.session_state.module = "HOME"

if "active_group" not in st.session_state:
    st.session_state.active_group = None

# -------CORPORATE UI STYLE----------------------

st.markdown("""
<style>

/* GLOBAL BACKGROUND */
body {
    background-color: #F8F5F2;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: #385144;
}

/* SIDEBAR TEXT */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label {
    color: #F8F5F2 !important;
}              
/* SIDEBAR TEXT */
section[data-testid="stSidebar"] * {
    color: #F8F5F2 !important;
}

/* HEADER */
.main-header {
    font-size: 42px;
    font-weight: 800;
    color: #385144;
}

.sub-header {
    color: #6B7280;
    margin-bottom: 20px;
}

/* CARDS (optional dashboard) */
.card {
    background: #333c43;
    padding: 14px;
    color: white;
    border-radius: 14px;
    border-left: 6px solid #385144;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
}
/* =====🎯 FIX BUTTON STYLE (CENTER + SAME SIZE) */

.stButton > button {
    width: 260px;               /* SAME WIDTH */
    height: 60px;              /* SAME HEIGHT */
    display: flex;
    align-items: center;        /* vertical center */
    justify-content: center;    /* horizontal center */
    text-align: center;

    font-size: 20px;
    font-weight: 700;

    background: linear-gradient(135deg, #385144, #2D4036, #333c43);
    color: white;

    border-radius: 18px;
    border: none;

    box-shadow: 0 10px 25px rgba(0,0,0,0.15);

    white-space: pre-line; /* allows line break */
}

/* Hover effect */
.stButton > button:hover {
    transform: translateY(-6px);
    box-shadow: 0 15px 35px rgba(0,0,0,0.25);
}

/* CENTER BUTTONS IN COLUMN */
div[data-testid="column"] {
    display: flex;
    justify-content: center;
}

/* SIDEBAR EXPANDER HEADER */
section[data-testid="stSidebar"] .streamlit-expanderHeader {
    background: #2D4036 !important;
    color: white !important;
    font-weight: 700 !important;
    border-radius: 10px;
    padding: 8px 12px;
}

/* WHEN EXPANDED */
section[data-testid="stSidebar"] details[open] summary {
    background: #4b6a60 !important;
    color: white !important;
    border-radius: 10px;
}

/* EXPANDER CONTENT */
section[data-testid="stSidebar"] details {
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 10px;
    margin-bottom: 8px;
}

/* HOVER EFFECT */
section[data-testid="stSidebar"] summary:hover {
    background: #5f8377 !important;
    color: white !important;
}
            
/* GROUP CARD */
section[data-testid="stSidebar"] details {
    background: rgba(255,255,255,0.08);
    border-radius: 12px;
    margin-bottom: 10px;
    overflow: hidden;
    border: none;
}

/* GROUP TITLE */
section[data-testid="stSidebar"] summary {
    padding: 12px !important;
    font-size: 15px;
    font-weight: 700;
    color: white !important;
}

/* ACTIVE GROUP */
section[data-testid="stSidebar"] details[open] summary {
    background: linear-gradient(
        90deg,
        #4b6a60,
        #385144
    ) !important;
}
            
/* Open group */
section[data-testid="stSidebar"] details[open] summary {

    background:
        linear-gradient(
            90deg,
            #5f8377,
            #385144
        )
        !important;
}

div[data-testid="column"] {
    display:flex;
    justify-content:center;
}

section[data-testid="stSidebar"] details {
    background:rgba(255,255,255,0.08);
    border-radius:14px;
    margin-bottom:10px;
    border:none;
    overflow:hidden;
}                     

            
/* REMOVE UGLY DEFAULT BORDER */
section[data-testid="stSidebar"] details div[role="group"] {
    border-top: none !important;
}           
</style>
""", unsafe_allow_html=True)


# ----SIDEBAR NAVIGATION (ENTERPRISE STYLE) ----------
NAV_GROUPS = {

    "🚚 APC": {
        "🚚 APC sFTP": "APC SFTP",
        "💳 APC BILLING DETAIL": "APC BILLING",
        "💳 APC CLIENT DETAILS": "APC CLIENT DETAILS",
        "💳 APC BILLING HEADER": "APC BILLING HEADER",
    },

    "📦 AMAZON": {
        "📊 AMAZON XML TO CANDATA": "AMAZON_XML",
        "📦 AMAZON ACI JSON": "AMAZON_ACI_JSON",
        "📊 AMAZON XML GETS": "AMAZON_XML_GETS",
    },
    
    "📊 Data Processing": {
        "📊 CANDATA UPLOAD FILE": "CANDATA",
        "📦 ACI JSON": "JSON",
    },

    "🛠 Utilities": {
        "📑 Split PDF": "SPLIT_PDF",
        "💱 ": "BANK OF CANADA",
    }
}

st.sidebar.title("☰ MENU")

st.sidebar.caption("NAVIGATION")

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

#if st.sidebar.button("🚚 APC SFTP"):
    #st.session_state.module = "APC"

#if st.sidebar.button("🗃️ CANDATA UPLOAD FILE"):
    #st.session_state.module = "CANDATA"

#if st.sidebar.button("🛒 AMAZON B2B XML TO CANDATA UPLOAD FILE"):
    #st.session_state.module = "AMAZON_XML"

#if st.sidebar.button("📦 AMAZON CANDATA TO JSON"):
    #st.session_state.module = "AMAZON_ACI_JSON"

#if st.sidebar.button("🛒 AMAZON B2B XML TO GETS UPLOAD FILE"):
    #st.session_state.module = "AMAZON_XML_GETS"

#if st.sidebar.button("💳 APC BILLING DETAIL REPORT"):
    #st.session_state.module = "APC_BILLING"

#if st.sidebar.button("💳 APC BILLING HEADER REPORT"):
    #st.session_state.module = "APC_BILLING_HEADER_REPORT"

#if st.sidebar.button("💳 APC CLIENT DETAILS"):
    #st.session_state.module = "APC_CLIENT_DETAILS"

#if st.sidebar.button("📦🔄 ACI JSON SHIPMENT CONVERTER"):
    #st.session_state.module = "JSON"

#if st.sidebar.button("💱 USD ↔️ CAD FX RATES"):
    #st.session_state.module = "BANKOFCANADA"

#if st.sidebar.button("📄 SPLIT PDF BATCHER"):
    #st.session_state.module = "SPLITPDF"

    # MODULES .RUN FROM IMPORT
    MODULES = {

        "APC SFTP": apc.run,
        "BANK OF CANADA": bankofcanada.run,
        "CANDATA": candata.run,
        "SPLIT PDF": splitpdf.run,
        "JSON": aci_json.run,
        "APC BILLING": apc_billing.run,
        "APC BILLING HEADER REPORT": apc_billing_header_report.run,
        "APC CLIENT DETAIL": apc_client_details.run,
        "AMAZON XML": amazon_xml.run,
        "AMAZON CANDATA TO JSON ": amazon_aci_json.run,
        "AMAZON XML GETS": amazon_xml_gets.run,

    }
# -------ROUTING ENGINE--------
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
    try:
        MODULES[st.session_state.module]()
    except Exception as e:
        st.error(f"Module Error: {e}")

#elif st.session_state.module == "APC":
    #apc.run()

#elif st.session_state.module == "BANKOFCANADA":
    #bankofcanada.run()

#elif st.session_state.module == "SPLITPDF":
    #splitpdf.run()

#elif st.session_state.module == "CANDATA":
    #candata.run()

#elif st.session_state.module == "APC_BILLING":
    #output = apc_billing.run()

#elif st.session_state.module == "APC_BILLING_HEADER_REPORT":
    #output = apc_billing_header_report.run()

#elif st.session_state.module == "APC_CLIENT_DETAILS":
    #output = apc_client_details.run()

#elif st.session_state.module == "AMAZON_XML":
    #amazon_xml.run()

#elif st.session_state.module == "AMAZON_ACI_JSON":
    #amazon_aci_json.run()

#elif st.session_state.module == "JSON":
    #aci_json.run()

#elif st.session_state.module == "AMAZON_XML_GETS":
    #amazon_xml_gets.run()