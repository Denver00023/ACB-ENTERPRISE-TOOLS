import streamlit as st
import requests
import pandas as pd
from datetime import date, timedelta



# ROLLING WINDOW ENGINE

def get_rolling_window(days: int):
    today = date.today() - timedelta(days=1)  # 👈 SAFE (Canada delay)
    start_date = today - timedelta(days=days)
    return start_date, today


# MAIN APP

def run():

    st.set_page_config(page_title="FX Rate (Bank of Canada)", page_icon="assets/qwe1.ico")

    st.subheader("💱 FX Rate (Bank of Canada)")
    st.caption("Flexible FX Dashboard (Rolling + Custom Range)")

    # SERIES
    
    series = st.selectbox("Currency Pair", ["FXUSDCAD"])

    # MODE SWITCH
    
    mode = st.radio(
        "Select Mode",
        ["Rolling Window", "Custom Date Range"]
    )

    # INPUTS
    
    if mode == "Rolling Window":

        days_back = st.number_input(
            "Rolling Window (Days)",
            min_value=1,
            max_value=365,
            value=7
        )

        start, end = get_rolling_window(days_back)

    else:
        col1, col2 = st.columns(2)

        with col1:
            start = st.date_input("Start Date", value=date.today() - timedelta(days=7))

        with col2:
            end = st.date_input("End Date", value=date.today() - timedelta(days=1))

    st.info(f"📅 Selected Range: {start} → {end}")

    st.markdown("---")
    st.caption("© 2026 ACB Toolkit | Developed by IT Department")

    # AUTO FETCH (NO BUTTON)
    
    url = (
        f"https://www.bankofcanada.ca/valet/observations/"
        f"{series}?start_date={start}&end_date={end}"
    )

    res = requests.get(url)

    if res.status_code != 200:
        st.error("❌ API Error")
        st.text(res.text)
        return

    data = res.json()

    # PARSE DATA
    
    rows = []

    for obs in data.get("observations", []):
        value = obs.get(series, {}).get("v")

        if value:
            rows.append({
                "Date": obs["d"],
                "Rate": float(value)
            })

    if not rows:
        st.warning("No data found for selected range")
        return

    df = pd.DataFrame(rows)
    df["Date"] = pd.to_datetime(df["Date"])

    # CALCULATIONS
    
    min_row = df.loc[df["Rate"].idxmin()]
    max_row = df.loc[df["Rate"].idxmax()]
    avg_rate = df["Rate"].mean()

    def inv(x):
        return round(1 / x, 4)

    # STYLE
    
    st.markdown("""
    <style>
    .fx-card {
        background: #ffffff;
        padding: 18px;
        border-radius: 16px;
        border-left: 6px solid #385144;
        box-shadow: 0 8px 20px rgba(0,0,0,0.05);
        transition: 0.2s;
    }

    .fx-card:hover {
        transform: translateY(-5px);
    }

    .fx-title {
        font-size: 18px;
        font-weight: 700;
        color: #385144;
    }

    .fx-value {
        font-size: 22px;
        font-weight: 700;
    }

    .fx-sub {
        font-size: 13px;
        color: #6B7280;
    }
    </style>
    """, unsafe_allow_html=True)

    # SUMMARY CARDS
    
    st.subheader("📊 FX Summary (USD → CAD)")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class="fx-card">
            <div class="fx-title">🔽 Low</div>
            <div class="fx-value">{min_row['Rate']:.4f} CAD</div>
            <div class="fx-sub">{min_row['Date'].date()}</div>
            <div class="fx-sub">USD: {inv(min_row['Rate']):.4f}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="fx-card">
            <div class="fx-title">📊 Average</div>
            <div class="fx-value">{avg_rate:.4f} CAD</div>
            <div class="fx-sub">{start} → {end}</div>
            <div class="fx-sub">USD: {inv(avg_rate):.4f}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="fx-card">
            <div class="fx-title">🔼 High</div>
            <div class="fx-value">{max_row['Rate']:.4f} CAD</div>
            <div class="fx-sub">{max_row['Date'].date()}</div>
            <div class="fx-sub">USD: {inv(max_row['Rate']):.4f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # TABLE
    
    st.subheader("📄 Exchange Rates")
    st.dataframe(df, use_container_width=True)

    # DOWNLOAD

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Download CSV",
        csv,
        "fx_rates.csv",
        "text/csv"
    )