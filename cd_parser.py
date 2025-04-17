import pandas as pd

def extract_c_and_d_data(file):
    wb = pd.ExcelFile(file)
    extracted = {}

    # Schedule C1 People
    if "Sch C1 People" in wb.sheet_names:
        df_c1 = wb.parse("Sch C1 People", header=None)
        if df_c1.shape[0] >= 21:
            row = df_c1.iloc[20]
            extracted["Sch C1 People # Loans (LMI Borrowers)"] = row[3] + row[5]
            extracted["Sch C1 People $ Volume (LMI Borrowers)"] = row[4] + row[6]
            extracted["Sch C1 People # Loans (Other Targeted Populations)"] = sum(row[i] for i in [11,13,15,17,19,21,23,25])
            extracted["Sch C1 People $ Volume (Other Targeted Populations)"] = sum(row[i] for i in [12,14,16,18,20,22,24,26])

    # Schedule C2 Business
    if "Sch C2 Business" in wb.sheet_names:
        df_c2 = wb.parse("Sch C2 Business", header=None)
        if df_c2.shape[0] >= 21:
            row = df_c2.iloc[20]
            extracted["Sch C2 Business # Loans"] = sum(row[i] for i in range(3, 24, 2))
            extracted["Sch C2 Business $ Volume"] = sum(row[i] for i in range(4, 25, 2))

    # Schedule D Tabs
    d_tabs = {
        "Sch D1 Rural": ("F", "G"),
        "Sch D2 Urban": ("F", "G"),
        "Sch D3 Underserved": ("F", "G"),
        "Sch D4 Minority": ("F", "G"),
        "Sch D5 Poverty": ("F", "G"),
        "Sch D6 Reserv": ("E", "F"),
        "Sch D7 Terr or PR": ("E", "F"),
    }

    for tab, (col_loan, col_dollar) in d_tabs.items():
        if tab in wb.sheet_names:
            df = wb.parse(tab, header=None)
            if df.shape[0] >= 6:
                col_loan_idx = ord(col_loan.upper()) - 65
                col_dollar_idx = ord(col_dollar.upper()) - 65
                extracted[f"{tab} # Loans"] = pd.to_numeric(df.iloc[5:, col_loan_idx], errors="coerce").sum()
                extracted[f"{tab} $ Volume"] = pd.to_numeric(df.iloc[5:, col_dollar_idx], errors="coerce").sum()

    return extracted
