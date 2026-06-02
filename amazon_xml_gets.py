import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from io import BytesIO


# TEMPLATE COLUMNS (FINAL CORRECTED)

TEMPLATE_COLUMNS = [
    "Inco_term",
    "Mode_of_transport",
    "Seller_code",
    "Seller_name",
    "Seller_address",
    "Seller_city",
    "Seller_postal_code",
    "Seller_state",
    "Seller_country",
    "Seller_phone_number",
    "Seller_email",

    "Pickup_code",
    "Pickup_name",
    "Pickup_address",
    "Pickup_city",
    "Pickup_postal_code",
    "Pickup_state",
    "Pickup_country",

    "Buyer_code",
    "Buyer_name",
    "Buyer_address",
    "Buyer_city",
    "Buyer_postal_code",
    "Buyer_province",
    "Buyer_country",
    "Buyer_phone_number",
    "Buyer_email",

    "Order_number",
    "Reliable_tracking",
    "Client_Internal_tracking",

    "Parcel_item_weight",
    "Parcel_item_weight_UOM",
    "Width",
    "Length",
    "Height",
    "Width_Length_Height_UOM",

    "Product_part",
    "Currency_code",
    "Package_no",
    "Quantity",
    "Quantity_UOM",
    "Unit_price",
    "UNDG",

    "Total_value_of_item",
    "Total_value_of_parcel",

    "HS_code",
    "Goods_Description",
    "Country_of_origin",
    "Url",

    "Importer_number",
    "Importer_party_id",

    "AutoCalc_Provincial_Rate",
    "CBSA_Port_of_Release",
    "CBSA_Warehouse_Sub_Location_Code",
    "Port_of_Discharge",

    "IID_Y/N",
    "TARIFF_TREATMENT_CODE"
]



# HEADER RULES (1:1 MATCH WITH TEMPLATE_COLUMNS)

HEADER_RULES = [
    "O,1…8 AN",
    "M,1 N",
    "O,1…35 AN",
    "M,1…70 AN",
    "M,1…105 AN",
    "M,1…35 AN",
    "M,1…9 AN",
    "M,1…9 A",
    "M,1…3 A",
    "M,1…50 N",
    "M,1…100 AN",

    "O,1…35 AN",
    "M,1…70 AN",
    "M,1…105 AN",
    "M,1…35 AN",
    "M,1…9 AN",
    "M,1…9 A",
    "M,1…3 A",

    "O,1…35 AN",
    "M,1…70 AN",
    "M,1…105 AN",
    "M,1…35 AN",
    "M,1…9 AN",
    "M,1…9 A",
    "M,1…3 A",
    "M,1…50 N",
    "M,1…100 AN",

    "M,1…35 AN",
    "M,1…35 AN",
    "M,1…70 AN",

    "M,1…20 N",
    "M,1…3 A",
    "O,1…10 N",
    "O,1…10 N",
    "O,1…10 N",
    "O,1…3 A",

    "O,1…35 AN",
    "M,1…3 A",
    "M,1…8 N",
    "M,1…18 N",
    "M,1…3 A",
    "M,1…18 N",
    "O,4 N",

    "M,1…18 N",
    "M,1…18 N",

    "M,10 N",
    "M,1…256 AN",
    "M,1…3 A",
    "O,1…70 AN",

    "O,15 AN",
    "O,1…50 AN",

    "O,1 A",
    "M,4 N",
    "O,4 N",
    "O,4 N",

    "O,1 A",
    "M,2 N"
]



# IMPORTER MAP

IMPORTER_MAP = {
    "AIOR": "789682689RM0002",
    "SIOR": ""
}


# XML HEADER EXTRACTOR

def extract_header(root):

    header = root.find(".//manifestHeader")
    data = {}

    if header is None:
        return data

    for child in header:
        if len(child) == 0:
            data[child.tag] = child.text

    for addr in header.findall(".//shipFromAddress"):

        role = (addr.attrib.get("AddressType", "")).lower()

        data[role] = {
            "name": addr.findtext("name", ""),
            "addressLine1": addr.findtext("addressLine1", ""),
            "city": addr.findtext("city", ""),
            "zip": addr.findtext("zip", ""),
            "stateProvince": addr.findtext(".//stateProvince", ""),
            "countryCode": addr.findtext("countryCode", "")
        }

    return data



# ITEM EXTRACTOR

def extract_items(root):

    items = []

    for item in root.findall(".//shipmentPackageItemDetail"):

        qty_node = item.find(".//quantity")
        weight_node = item.find(".//weightValue")
        money_node = item.find(".//monetaryAmount")

        items.append({
            "asin": item.findtext("asin", ""),
            "hs_code": item.findtext("destinationHTSCode", "").replace(".", ""),
            "description": item.findtext("harmonizedTariffDescription", ""),
            "country": item.findtext("countryOfOrigin", ""),

            "quantity": qty_node.text if qty_node is not None else "",
            "weight": weight_node.text if weight_node is not None else "",
            "weight_uom": weight_node.attrib.get("unitOfMeasure", "") if weight_node is not None else "",

            "unit_price": money_node.text if money_node is not None else "",
            "currency": money_node.attrib.get("currencyISOCode", "") if money_node is not None else "",

            "total_value": item.findtext(".//totalUnitValue/monetaryAmount", "")
        })

    return items


# ROW BUILDER (STRICT TEMPLATE ORDER)

def build_row(header, item):

    seller = header.get("seller", {})
    receiver = header.get("receiver", {})
    shipper = header.get("shipper", {})

    return {

        "Inco_term": header.get("incoterms", ""),
        "Mode_of_transport": "2",

        "Seller_code": "",
        "Seller_name": seller.get("name", ""),
        "Seller_address": seller.get("addressLine1", ""),
        "Seller_city": seller.get("city", ""),
        "Seller_postal_code": seller.get("zip", ""),
        "Seller_state": seller.get("stateProvince", ""),
        "Seller_country": seller.get("countryCode", ""),
        "Seller_phone_number": "555-555-5555",
        "Seller_email": "email@email.com",

        "Pickup_code": "",
        "Pickup_name": shipper.get("name", ""),
        "Pickup_address": shipper.get("addressLine1", ""),
        "Pickup_city": shipper.get("city", ""),
        "Pickup_postal_code": shipper.get("zip", ""),
        "Pickup_state": shipper.get("stateProvince", ""),
        "Pickup_country": shipper.get("countryCode", ""),

        "Buyer_code": "",
        "Buyer_name": receiver.get("name", ""),
        "Buyer_address": receiver.get("addressLine1", ""),
        "Buyer_city": receiver.get("city", ""),
        "Buyer_postal_code": receiver.get("zip", ""),
        "Buyer_province": receiver.get("stateProvince", ""),
        "Buyer_country": receiver.get("countryCode", ""),
        "Buyer_phone_number": "555-555-5555",
        "Buyer_email": "email@email.com",

        "Order_number": header.get("invoiceTitle", ""),
        "Reliable_tracking": header.get("CCN", ""),
        "Client_Internal_tracking": header.get("trackingID", ""),

        "Parcel_item_weight": item.get("weight", ""),

        "Parcel_item_weight_UOM": (
            "LBR" if item.get("weight_uom", "").upper() == "LB"
            else "KGM" if item.get("weight_uom", "").upper() == "KG"
            else item.get("weight_uom", "")
        ),

        "Width": "",
        "Length": "",
        "Height": "",
        "Width_Length_Height_UOM": "",

        "Product_part": item.get("asin", ""),
        "Currency_code": item.get("currency", ""),

        "Package_no": item.get("quantity", ""),
        "Quantity": item.get("quantity", ""),
        "Quantity_UOM": "PK",

        "Unit_price": item.get("unit_price", ""),
        "UNDG": "",

        "Total_value_of_item": item.get("total_value", ""),
        "Total_value_of_parcel": "",

        "HS_code": item.get("hs_code", ""),
        "Goods_Description": item.get("description", ""),
        "Country_of_origin": item.get("country", ""),

        "Url": "",

        "Importer_number": IMPORTER_MAP.get(
            header.get("importerType", "").upper(),
            ""
        ),

        "Importer_party_id": "",

        "AutoCalc_Provincial_Rate": "C",
        "CBSA_Port_of_Release": "0453",
        "CBSA_Warehouse_Sub_Location_Code": "3801",
        "Port_of_Discharge": "",

        "IID_Y/N": "Y",
        "TARIFF_TREATMENT_CODE": "2"
    }



# EXCEL GENERATOR

def create_excel(df):

    output = BytesIO()

    df = df.reindex(columns=TEMPLATE_COLUMNS)

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:

        df.to_excel(
            writer,
            sheet_name="CANADA_UPLOAD",
            index=False,
            startrow=2,
            header=False
        )

        ws = writer.sheets["CANADA_UPLOAD"]

        # ROW 0 → HEADER

        for i, col in enumerate(TEMPLATE_COLUMNS):
            ws.write(0, i, col)

        # ROW 1 → RULES

        for i, rule in enumerate(HEADER_RULES):
            ws.write(1, i, rule)

    output.seek(0)
    return output


# STREAMLIT APP

def run():

    st.title("📄 XML → GETS Upload Tool")

    files = st.file_uploader("Upload XML Files", type=["xml"], accept_multiple_files=True)

    st.markdown("---")
    st.caption("© 2026 ACB Toolkit | Developed by IT Department")

    if not files:
        return

    rows = []

    for f in files:

        try:
            root = ET.parse(f).getroot()

            header = extract_header(root)
            items = extract_items(root)

            for item in items:
                rows.append(build_row(header, item))

            st.success(f"Processed: {f.name}")

        except Exception as e:
            st.error(str(e))

    df = pd.DataFrame(rows)


    # 🔥 CALCULATIONS FIRST

    df['Unit_price'] = pd.to_numeric(df['Unit_price'], errors='coerce').fillna(0)
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)

    df['Total_value_of_item'] = (df['Unit_price'] * df['Quantity']).round(2)

    df['Total_value_of_parcel'] = df.groupby(
        'Reliable_tracking'
    )['Total_value_of_item'].transform('sum').round(2)


    # SHOW FINAL DATA

    st.dataframe(df, use_container_width=True)

    # CREATE EXCEL LAST (IMPORTANT)
    excel = create_excel(df)

    st.download_button(
        "⬇ Download GETS File",
        excel,
        file_name="AMAZON_B2B_GETS_UPLOAD_FILE.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


if __name__ == "__main__":
    run()