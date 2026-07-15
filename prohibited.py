import streamlit as st
import pandas as pd
import re
from io import BytesIO

# Keywords
KEYWORDS=[
    "BABY WALKER","MILK","DAIRY","EGG","TREATS","CAT FOOD","DOG FOOD",
    "ANIMAL FOOD","GHEE","ALCOHOL","WINE","ROASTED","MEAT","SAUSAGE",
    "KNIFE","JERKY","BUTTER","FIREARMS","GUNS","WHISKEY",
    "DOG FLEA POWDER","MINIMOOS","MINERAL JUNKIE BITES",
    "UNITED CHEMICALS YELLOWTREAT MUSTARD ALGAECIDE", "BEEF CHEWY"
]

# Columns
TRACKING_COLUMN="Reliable_tracking"
DESCRIPTION_COLUMN="Goods_Description"
WEIGHT_COLUMN="Parcel_item_weight"

# Detection
def detect(df):

    results=[]

    for _,row in df.iterrows():

        text=" ".join(
            str(value)
            for value in row.tolist()
            if pd.notna(value)
        ).upper()

        found=[
            keyword
            for keyword in KEYWORDS
            if re.search(
                re.escape(keyword),
                text
            )
        ]

        if found:

            results.append({

                "Reliable_tracking": row.get(TRACKING_COLUMN, ""),

                "Goods_Description": row.get(DESCRIPTION_COLUMN, ""),

                "Parcel_item_weight": row.get(WEIGHT_COLUMN, ""),

                "Detected_Prohibited_Item": ", ".join(found),

                "Issue":"PROHIBITED ITEM FOUND"
            })

    return pd.DataFrame(results)

# Export
def export_excel(df):

    output=BytesIO()

    with pd.ExcelWriter(
        output,
        engine="xlsxwriter"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Validation_Result"
        )

    return output.getvalue()

# App

def run():

    st.subheader("📄 **PROHIBITED ITEM DETECTION**")

    uploaded_file=st.file_uploader(
        "**Upload Shipment File**",
        type=[
            "xlsx",
            "xls",
            "csv"
        ]
    )

    st.markdown("---")
    st.caption("© 2026 ACB Toolkit | Developed by IT Department")

    if uploaded_file:

        if uploaded_file.name.endswith(".csv"):

            df=pd.read_csv(
                uploaded_file
            )

        else:

            df=pd.read_excel(
                uploaded_file
            )

        required_columns=[
            TRACKING_COLUMN,
            DESCRIPTION_COLUMN,
            WEIGHT_COLUMN
        ]

        missing=[
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing:

            st.error(f"Missing columns: {missing}")

            return

        with st.spinner("Scanning shipment data..."):

            result=detect(df)

        if result.empty:

            st.success("**No prohibited items detected**")

        else:

            st.error(f"{len(result)} shipment(s) flagged")

            st.dataframe(result,use_container_width=True)

            st.download_button(
                "Download Validation Report",
                export_excel(result),
                f"PROHIBITED_ITEMS_{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__=="__main__":

    run()