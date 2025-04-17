import streamlit as st
import pandas as pd
import os
import re
from io import BytesIO
from collections import defaultdict
from cd_parser import extract_c_and_d_data

st.set_page_config(page_title="QSR Validator", layout="wide")
st.title("ECIP QSR Side-by-Side Validator")

st.markdown("Upload individual QSR Excel files (Schedule B for Q1–Q4) below:")

uploaded_files = st.file_uploader("Quarterly QSR Excel Files", type="xlsx", accept_multiple_files=True)

def extract_sch_b(file, ec_number):
    try:
        df = pd.read_excel(file, sheet_name="Sch B", header=None)
        if df.shape[0] < 20:
            return None

        col_map = {
            4:  "Sch C1 People # Loans (LMI Borrowers)",
            6:  "Sch C1 People $ Volume (LMI Borrowers)",
            8:  "Sch C1 People # Loans (Other Targeted Populations)",
            10: "Sch C1 People $ Volume (Other Targeted Populations)",
            12: "Sch C1 People # Loans (Low Income Borrowers Deep)",
            14: "Sch C1 People $ Volume (Low Income Borrowers Deep)",
            16: "Sch C1 People # Loans (Mortgage Lending Other Deep)",
            18: "Sch C1 People $ Volume (Mortgage Lending Other Deep)",
            52: "Sch C2 Business # Loans",
            54: "Sch C2 Business $ Volume",
            20: "Sch D1 Rural # Loans",
            22: "Sch D1 Rural $ Volume",
            24: "Sch D2 Urban # Loans",
            26: "Sch D2 Urban $ Volume",
            28: "Sch D3 Underserved # Loans",
            30: "Sch D3 Underserved $ Volume",
            32: "Sch D4 Minority # Loans",
            34: "Sch D4 Minority $ Volume",
            36: "Sch D5 Poverty # Loans",
            38: "Sch D5 Poverty $ Volume",
            40: "Sch D6 Reserv # Loans",
            42: "Sch D6 Reserv $ Volume",
            44: "Sch D7 Terr or PR # Loans",
            46: "Sch D7 Terr or PR $ Volume",
        }

        row = df.iloc[19, list(col_map.keys())].astype(str).replace(r"[^0-9.-]", "", regex=True)
        row = pd.to_numeric(row, errors="coerce").fillna(0)
        return row.rename(index=col_map)

    except Exception as e:
        st.warning(f"Failed to process EC{ec_number} — {e}")
        return None

ec_data = defaultdict(lambda: pd.Series())
bank_names = {}

if uploaded_files:
    for file in uploaded_files:
        filename = file.name
        match = re.search(r'EC[-_]?(\d+)', filename)
        bank_match = re.search(r'_Q\d+_(.*)\.xlsx', filename)
        if match:
            ec_num = match.group(1).zfill(4)
            bank_name = bank_match.group(1).replace("_", " ").strip() if bank_match else f"EC{ec_num}"
            extracted = extract_sch_b(file, ec_num)
            if extracted is not None:
                ec_data[ec_num] = ec_data[ec_num].add(extracted, fill_value=0)
                bank_names[ec_num] = bank_name

    if ec_data:
        selected_ec = st.sidebar.selectbox("Choose EC to view", list(ec_data.keys()))
        st.subheader(f"{bank_names.get(selected_ec, f'EC{selected_ec}')} – Schedule B Totals (Q1–Q4)")
        st.dataframe(ec_data[selected_ec].reset_index().rename(columns={"index": "Category", 0: "Value"}))

st.markdown("---")
st.markdown("Upload your Annual QSR files with Schedule C and D data:")

annual_files = st.file_uploader("Annual QSR Excel Files", type="xlsx", accept_multiple_files=True, key="annual")
cd_data = {}

if annual_files:
    for file in annual_files:
        match = re.search(r'EC[-_]?(\d+)', file.name)
        bank_match = re.search(r'_2024[_\s]*Annual[_\s]*(.*)\.xlsx', file.name)
        if match:
            ec = match.group(1).zfill(4)
            bank_name = bank_match.group(1).replace("_", " ").strip() if bank_match else f"EC{ec}"
            extracted = extract_c_and_d_data(file)
            if extracted:
                cd_data[ec] = pd.Series(extracted)
                bank_names[ec] = bank_name

    if selected_ec in ec_data and selected_ec in cd_data:
        st.markdown(f"Schedule B vs C&D Comparison for {bank_names.get(selected_ec)}")
        df_b = ec_data[selected_ec]
        df_cd = cd_data[selected_ec]
        combined = pd.DataFrame({
            "Schedule B Total": df_b,
            "Schedule C & D Total": df_cd,
        })
        combined["Difference"] = combined["Schedule B Total"] - combined["Schedule C & D Total"]
        st.dataframe(combined.fillna(0).round(2))



# cd C:\Users\SavannahSummers\Downloads\ecip-helper
# conda activate ecip-helper
# streamlit run qsr_validator_app.py
