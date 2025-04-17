import streamlit as st
import pandas as pd
import os
import re
from io import BytesIO
from collections import defaultdict
from cd_parser import extract_c_and_d_data

st.set_page_config(page_title="QSR Validator", layout="wide")
st.title("ECIP QSR Side-by-Side Validator")

# ====== SCHEDULE B EXTRACTION ======
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

# ====== INITIALIZE DATA STRUCTURES ======
ec_data = defaultdict(lambda: pd.Series())
cd_data = {}
bank_names = {}
validation_summary = []

# ====== UPLOAD SCH B FILES ======
st.markdown("### Upload Quarterly QSR files (Schedules A & B only)")
uploaded_files = st.file_uploader("Upload Schedule B Files (Q1–Q4)", type="xlsx", accept_multiple_files=True)

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

# ====== UPLOAD SCH C & D FILES ======
st.markdown("---")
st.markdown("### Upload Annual QSR files (Schedules C & D only)")
annual_files = st.file_uploader("Upload Annual C&D Files", type="xlsx", accept_multiple_files=True, key="annual")

if annual_files:
    for file in annual_files:
        match = re.search(r'EC[-_]?(\d+)', file.name)
        bank_match = re.search(r'_2024[_\s]*(Annual)?[_\s]*(.*)\.xlsx', file.name)
        if match:
            ec = match.group(1).zfill(4)
            bank_name = bank_match.group(2).replace("_", " ").strip() if bank_match else f"EC{ec}"
            extracted = extract_c_and_d_data(file)
            if extracted:
                cd_data[ec] = pd.Series(extracted)
                bank_names[ec] = bank_name

# ====== SHOW COMPARISON PER EC ======
if ec_data and cd_data:
    selected_ec = st.sidebar.selectbox("Choose a bank to view", sorted(ec_data.keys()))
    bank_label = bank_names.get(selected_ec, f"EC{selected_ec}")
    st.subheader(f"{bank_label} – Side-by-Side Comparison")

    df_b = ec_data[selected_ec]
    df_cd = cd_data.get(selected_ec, pd.Series())
    comparison = pd.DataFrame({
        "Schedule B Total": df_b,
        "Schedule C & D Total": df_cd,
    })
    comparison["Difference"] = comparison["Schedule B Total"] - comparison["Schedule C & D Total"]
    st.dataframe(comparison.fillna(0).round(2))

# ====== VALIDATION SUMMARY ======
st.markdown("---")
st.markdown("### Validation Matrix (All Banks with B + C&D data)")

for ec_num in sorted(ec_data.keys()):
    if ec_num in cd_data:
        df_b = ec_data[ec_num]
        df_cd = cd_data[ec_num]
        diff = (df_b - df_cd).fillna(0)
        has_issues = (diff.abs() > 1).any()
        validation_summary.append({
            "Bank": bank_names.get(ec_num, f"EC{ec_num}"),
            "Has Issues": "Yes" if has_issues else "No"
        })

if validation_summary:
    df_matrix = pd.DataFrame(validation_summary)
    st.dataframe(df_matrix, use_container_width=True)


# cd C:\Users\SavannahSummers\Downloads\ecip-helper
# conda activate ecip-helper
# streamlit run qsr_validator_app.py
