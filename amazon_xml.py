import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from io import BytesIO
import re

# XML HEADER EXTRACTOR
def normalize_name(name):
    
    name = str(name).lower().strip()
    name = re.sub(r"[,.&()\-]", "", name)
    name = " ".join(name.split())
    return name

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

# ITEM EXTRACTOR
def extract_items(root):

    items = []

    for item in root.findall(".//shipmentPackageItemDetail"):
        qty_node = item.find(".//quantity")
        weight_node = item.find(".//weightValue")
        money_node = item.find(".//monetaryAmount")

        items.append({
            "asin": item.findtext("asin", ""),
            "itemID": item.findtext("itemID", ""),
            "hs_code": item.findtext("destinationHTSCode", "").replace(".", ""),
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

# BUILD CANADA ROW
def build_row(header, item, mapping_dict):

    seller = header.get("seller", {})
    receiver = header.get("receiver", {})
    shipper = header.get("shipper", {})
    biller = header.get("biller", {})
    
    original_seller_name = seller.get("name", "")
    seller_key = normalize_name(original_seller_name)

    lookup = mapping_dict.get(seller_key, {})

    importer_number = lookup.get("importer_number", "")
    importer_party_id = lookup.get("BroderEze Account", "")

    return {
        
        # ---------------- HEADER INFO ----------------
        "Inco_term": header.get("incoterms", ""),
        "Mode_of_transport": "2",
        
        # ---------------- SELLER ----------------
        "Seller_code": "",
        "Seller_name": str(original_seller_name).strip(),
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
        "Parcel_item_weight_UOM": (
            "LBR" if item.get("weight_uom", "").upper() == "LB"
            else "KGM" if item.get("weight_uom", "").upper() == "KG"
            else item.get("weight_uom", "")
        ),

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
        "Total_value_of_item": item.get("total_value", ""),
        "Total_value_of_parcel": "",
        
        # ---------------- CUSTOMS ----------------
        "HS_code": item.get("hs_code", ""),
        "Goods_Description": item.get("description", ""),
        "Country_of_origin": item.get("country", ""),
        
        # ---------------- OTHERS ----------------
        "Url": "",
        "Importer_number": importer_number,
        "Importer_party_id": importer_party_id,
        
        # ✅ DEFAULT VALUES (WILL BE OVERWRITTEN IF INPUT PROVIDED)
        "AutoCalc_Provincial_Rate": "C",
        "CBSA_Port_of_Release": st.session_state.get("cbsa_port", "0453"),
        "CBSA_Warehouse_Sub_Location_Code": st.session_state.get("cbsa_wh", "9453"),
        "Port_of_Discharge": st.session_state.get("cbsa_discharge", "0453"),
        "Port_of_Discharge_Sublocation Code": st.session_state.get("cbsa_subloc", "9453"),
        
        "IID_Y/N": "Y",
        "PGA Flag": "CFIA",
        "Category": "HVS",
        "MAWB #": "",
        "Carrier code": "1BML",
        "Manifest Only": "",
        "Movement Type": "",
        "TARIFF_TREATMENT_CODE": "2",
        "External Reference 2": header.get("PONumber", "")
    }

# CREATE EXCEL
def create_excel(df):

    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="CANDATA_AMAZON_B2B", index=False)
        worksheet = writer.sheets["CANDATA_AMAZON_B2B"]

        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max(), len(col))
            worksheet.set_column(i, i, max_len + 5)

    output.seek(0)
    return output

# STREAMLIT APP
def run():

    st.subheader("📄 XML → CANDATA UPLOAD FILE")
    st.caption("Amazon XML to CANDATA UPLOAD FILE")

    col1, col2 = st.columns(2)

    with col1:
        uploaded_files = st.file_uploader(
            "Upload XML Files",
            type=["xml"],
            accept_multiple_files=True
        )

    with col2:
        mapping_file = st.file_uploader(
            "Upload Seller Mapping Excel",
            type=["xlsx", "xls"]
        )
    
    st.caption("Note: Please update your Seller Mapping Excel file using the latest online template before uploading. Seller mapping is based on normalized seller names; minor variations may be accepted, but significant differences may cause mapping failures. Please also ensure accurate data entry. CANDATA is strict about formatting, including spaces, special characters (e.g., commas and periods), and spelling. Careful attention to these details will help prevent errors and ensure smoother processing..")

    st.markdown("---")

    # 🔥 NEW INPUT BOXES

    st.subheader("⚙️ CBSA Overwrite Defaults")
    st.caption("Optionally overwrite default CBSA values for Port of Release, Warehouse Sub Location Code, Port of Discharge, and Port of Discharge Sublocation Code. If left blank, defaults will be used in the output file.")

    col1, col2 = st.columns(2)

    with col1:
        st.session_state.cbsa_port = st.text_input("CBSA Port of Release", "0440")
        st.session_state.cbsa_wh = st.text_input("CBSA Warehouse Sub Location Code", "9453")

    with col2:
        st.session_state.cbsa_discharge = st.text_input("Port of Discharge", "0453")
        st.session_state.cbsa_subloc = st.text_input("Port of Discharge Sublocation Code", "9453")

    st.markdown("---")
    st.caption("© 2026 ACB Toolkit | Developed by IT Department")

    if not uploaded_files:
        return

    # LOAD MAPPING
    mapping_dict = {}

    if mapping_file is not None:
        mapping_df = pd.read_excel(mapping_file)
        mapping_df.columns = mapping_df.columns.str.strip()

        for _, row in mapping_df.iterrows():
            account_name = normalize_name(row.get("Account Name", ""))
            mapping_dict[account_name] = {
                "importer_number": str(row.get("Importer Number", "")).strip(),
                "BroderEze Account": str(row.get("BroderEze Account", "")).strip()
            }
            

    all_rows = []
    
    with st.status("Processing files...", expanded=False) as status:
        for uploaded_file in uploaded_files:
            try:
                tree = ET.parse(uploaded_file)
                root = tree.getroot()

                header = extract_header(root)
                items = extract_items(root)

                for item in items:
                    all_rows.append(
                        build_row(header, item, mapping_dict)
                    )

                status.write(f"Completed: {uploaded_file.name}")

            except Exception as e:
                status.write(f"Error: {uploaded_file.name} → {str(e)}")

    status.write(f"✅ **Total Loaded {len(mapping_dict)} Seller Mapping.**")

    status.update(label="Processing complete", state="complete")
    
    df = pd.DataFrame(all_rows)

    unique_tracking_count = df["Reliable_tracking"].nunique()

    duplicate_tracking_count = (
        df["Reliable_tracking"]
        .duplicated(keep=False)
        .sum()
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "**Duplicate Reliable Tracking Rows**",
            f"{duplicate_tracking_count:,}"
        )
        
    with col2:
        st.metric(
            "**Unique Reliable Tracking**",
            f"{unique_tracking_count:,}"
        )
        
    df = df.sort_values(by="Reliable_tracking", ascending=True)

    df['Unit_price'] = pd.to_numeric(df['Unit_price'], errors='coerce').fillna(0)
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)

    df['Total_value_of_item'] = (df['Unit_price'] * df['Quantity']).round(2)

    df['Total_value_of_parcel'] = df.groupby('Reliable_tracking')['Total_value_of_item'].transform('sum').round(2)

    st.dataframe(df, use_container_width=True)

    excel_data = create_excel(df)

    st.download_button(
        label="⬇ Download Canada Upload File",
        data=excel_data,
        file_name=f"AMAZON_B2B_CANDATA_UPLOAD_{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ENTRY
if __name__ == "__main__":
    run()