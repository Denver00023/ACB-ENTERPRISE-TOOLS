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
    layout="wide"
)


# -------------STATE-----------

if "module" not in st.session_state:
    st.session_state.module = "HOME"


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
    height: 90px;              /* SAME HEIGHT */
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

</style>
""", unsafe_allow_html=True)


# ----SIDEBAR NAVIGATION (ENTERPRISE STYLE) ----------

st.sidebar.title("☰ MENU")

st.sidebar.caption("NAVIGATION")

if st.sidebar.button("🚚 APC SFTP"):
    st.session_state.module = "APC"

if st.sidebar.button("🗃️ CANDATA UPLOAD FILE"):
    st.session_state.module = "CANDATA"

if st.sidebar.button("🛒 AMAZON B2B XML TO CANDATA UPLOAD FILE"):
    st.session_state.module = "AMAZON_XML"

if st.sidebar.button("📦 AMAZON CANDATA TO JSON"):
    st.session_state.module = "AMAZON_ACI_JSON"

if st.sidebar.button("🛒 AMAZON B2B XML TO GETS UPLOAD FILE"):
    st.session_state.module = "AMAZON_XML_GETS"

if st.sidebar.button("💳 APC BILLING DETAIL REPORT"):
    st.session_state.module = "APC_BILLING"

if st.sidebar.button("💳 APC BILLING HEADER REPORT"):
    st.session_state.module = "APC_BILLING_HEADER_REPORT"

if st.sidebar.button("💳 APC CLIENT DETAILS"):
    st.session_state.module = "APC_CLIENT_DETAILS"

if st.sidebar.button("📦🔄 ACI JSON SHIPMENT CONVERTER"):
    st.session_state.module = "JSON"

if st.sidebar.button("💱 USD ↔️ CAD FX RATES"):
    st.session_state.module = "BANKOFCANADA"

if st.sidebar.button("📄 SPLIT PDF BATCHER"):
    st.session_state.module = "SPLITPDF"

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


elif st.session_state.module == "APC":
    apc.run()

elif st.session_state.module == "BANKOFCANADA":
    bankofcanada.run()

elif st.session_state.module == "SPLITPDF":
    splitpdf.run()

elif st.session_state.module == "CANDATA":
    candata.run()

elif st.session_state.module == "APC_BILLING":
    output = apc_billing.run()

elif st.session_state.module == "APC_BILLING_HEADER_REPORT":
    output = apc_billing_header_report.run()

elif st.session_state.module == "APC_CLIENT_DETAILS":
    output = apc_client_details.run()

elif st.session_state.module == "AMAZON_XML":
    amazon_xml.run()

elif st.session_state.module == "AMAZON_ACI_JSON":
    amazon_aci_json.run()

elif st.session_state.module == "JSON":
    aci_json.run()

elif st.session_state.module == "AMAZON_XML_GETS":
    amazon_xml_gets.run()