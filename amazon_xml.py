import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from io import BytesIO


# ===================================================
# XML HEADER EXTRACTOR
# ===================================================
def extract_header(root):

    header = root.find("manifestHeader")
    data = {}

    if header is None:
        return data

    # Simple fields
    for child in header:
        if len(child) == 0:
            data[child.tag] = child.text

    # shipFromAddress grouped by role
    for addr in header.findall("shipFromAddress"):

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


# ===================================================
# ITEM EXTRACTOR
# ===================================================
def extract_items(root):

    items = []

    for item in root.findall(".//shipmentPackageItemDetail"):

        qty_node = item.find(".//quantity")
        weight_node = item.find(".//weightValue")
        money_node = item.find(".//monetaryAmount")

        items.append({
            "asin": item.findtext("asin", ""),
            "itemID": item.findtext("itemID", ""),
            "hs_code": item.findtext("destinationHTSCode", ""),
            "description": item.findtext("harmonizedTariffDescription", ""),
            "country": item.findtext("countryOfOrigin", ""),
            "eccn": item.findtext("ECCN", ""),

            "quantity": qty_node.text if qty_node is not None else "",
            "quantity_uom": qty_node.attrib.get("unitOfMeasure", "") if qty_node is not None else "",

            "weight": weight_node.text if weight_node is not None else "",
            "weight_uom": weight_node.attrib.get("unitOfMeasure", "") if weight_node is not None else "",

            "unit_price": money_node.text if money_node is not None else "",
            "currency": money_node.attrib.get("currencyISOCode", "") if money_node is not None else "",

            "total_value": item.findtext(".//totalUnitValue/monetaryAmount", "")
        })

    return items


# ===================================================
# BUILD CANADA ROW
# ===================================================
def build_row(header, item):

    seller = header.get("seller", {})
    receiver = header.get("receiver", {})
    shipper = header.get("shipper", {})
    biller = header.get("biller", {})

    return {
        # ---------------- HEADER INFO ----------------
        "Inco_term": header.get("incoterms", ""),
        "Mode_of_transport": "",

        # ---------------- SELLER ----------------
        "Seller_code": "",
        "Seller_name": seller.get("name", ""),
        "Seller_address": seller.get("addressLine1", ""),
        "Seller_city": seller.get("city", ""),
        "Seller_postal_code": seller.get("zip", ""),
        "Seller_state": seller.get("stateProvince", ""),
        "Seller_country": seller.get("countryCode", ""),
        "Seller_phone_number": "555-555-5555",
        "Seller_email": "email@email.com",

        # ---------------- PICKUP (SHIPPER) ----------------
        "Pickup_code": "",
        "Pickup_name": shipper.get("name", ""),
        "Pickup_address": shipper.get("addressLine1", ""),
        "Pickup_city": shipper.get("city", ""),
        "Pickup_postal_code": shipper.get("zip", ""),
        "Pickup_state": shipper.get("stateProvince", ""),
        "Pickup_country": shipper.get("countryCode", ""),

        # ---------------- BUYER (RECEIVER) ----------------
        "Buyer_code": "",
        "Buyer_name": receiver.get("name", ""),
        "Buyer_address": receiver.get("addressLine1", ""),
        "Buyer_city": receiver.get("city", ""),
        "Buyer_postal_code": receiver.get("zip", ""),
        "Buyer_province": receiver.get("stateProvince", ""),
        "Buyer_country": receiver.get("countryCode", ""),
        "Buyer_phone_number": "555-555-5555",
        "Buyer_email": "email@email.com",

        # ---------------- ORDER ----------------
        "Order_number": header.get("invoiceTitle", ""),
        "Reliable_tracking": header.get("CCN", ""),
        "Client_Internal_tracking": header.get("trackingID", ""),

        # ---------------- PACKAGE / ITEM ----------------
        "Parcel_item_weight": item.get("weight", ""),
        "Parcel_item_weight_UOM": item.get("weight_uom", ""),

        "Width": "",
        "Length": "",
        "Height": "",
        "Width_Length_Height_UOM": "",

        # ---------------- PRODUCT ----------------
        "Product_code": item.get("asin", ""),
        "Currency_code": item.get("currency", ""),

        "Package_no": item.get("quantity", ""),
        "Quantity": item.get("quantity", ""),
        "Quantity_UOM": "PK",

        "Unit_price": item.get("unit_price", ""),

        "UNDG": "",

        "Total_value_of_item": "",
        "Total_value_of_parcel": "",

        # ---------------- CUSTOMS ----------------
        "HS_code": item.get("hs_code", ""),
        "Goods_Description": item.get("description", ""),
        "Country_of_origin": item.get("country", ""),

        # ---------------- OTHERS ----------------
        "Url": "",
        "Importer_number": header.get("merchantId", ""),
        "Importer_party_id": header.get("merchantId", ""),

        "AutoCalc_Provincial_Rate": "C",
        "CBSA_Port_of_Release": "",
        "CBSA_Warehouse_Sub_Location_Code": "",
        "Port_of_Discharge": "",
        "Port_of_Discharge_Sublocation Code": "",
        "IID_Y/N": "",
        "PGA Flag": "",
        "Category": "",
        "MAWB #": "",
        "Carrier code": header.get("carrierName", ""),
        "Manifest Only": "",
        "Movement Type": "",
        "TARIFF_TREATMENT_CODE": "",
        "External Reference 2": header.get("PONumber", "")
    }


# ===================================================
# CREATE EXCEL (ONE SHEET ONLY)
# ===================================================
def create_excel(df):

    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="CANADA_UPLOAD", index=False)

        worksheet = writer.sheets["CANADA_UPLOAD"]

        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max(), len(col))
            worksheet.set_column(i, i, max_len + 5)

    output.seek(0)
    return output


# ===================================================
# STREAMLIT APP
# ===================================================
def run():

    st.title("📄 XML → CANDATA UPLOAD FILE")
    st.caption("Amazon XML to CANDATA UPLOAD FILE")

    uploaded_files = st.file_uploader(
        "Upload XML Files",
        type=["xml"],
        accept_multiple_files=True
    )

    if not uploaded_files:
        return

    all_rows = []

    for uploaded_file in uploaded_files:

        try:

            tree = ET.parse(uploaded_file)
            root = tree.getroot()

            header = extract_header(root)
            items = extract_items(root)

            for item in items:
                all_rows.append(build_row(header, item))

            st.success(f"Processed: {uploaded_file.name}")

        except Exception as e:
            st.error(f"Error in {uploaded_file.name}: {str(e)}")

    if not all_rows:
        st.warning("No data extracted")
        return

    df = pd.DataFrame(all_rows)

    # Ensure numeric conversion
    df['Unit_price'] = pd.to_numeric(df['Unit_price'], errors='coerce').fillna(0)
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)

    # 1. COMPUTE ITEM TOTAL
    df['Total_value_of_item'] = df['Unit_price'] * df['Quantity']

    # 2. COMPUTE PARCEL TOTAL (GROUP BY RELIABLE_TRACKING)
    df['Total_value_of_parcel'] = df.groupby(
        'Reliable_tracking'
    )['Total_value_of_item'].transform('sum')

    # FORMAT TO 2 DECIMALS
    df['Total_value_of_item'] = df['Total_value_of_item'].round(2)
    df['Total_value_of_parcel'] = df['Total_value_of_parcel'].round(2)

    st.dataframe(df, use_container_width=True)

    excel_data = create_excel(df)

    st.download_button(
        label="⬇ Download Canada Upload File",
        data=excel_data,
        file_name="AMAZON_B2B_CANDATA_UPLOAD_TEMPLATE.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ===================================================
# ENTRY
# ===================================================
if __name__ == "__main__":
    run()