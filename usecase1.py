import os
import sqlite3
import pandas as pd
import numpy as np

# Set file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "chicago_crime.db")
CSV_PATH = os.path.join(DB_DIR, "chicago_crime_dataset.csv")


def run_usecase1():
    print("Running Use Case 1...")

    # 1. Loading data
    df = pd.read_csv(CSV_PATH)
    
    print("\nFirst 10 rows:")
    print(df.head(10))

    print("\nSchema and Data Types:")
    print(df.dtypes)

    rows, cols = df.shape
    print(f"\nNumber of rows: {rows}")
    print(f"Number of columns: {cols}")

    # 2. Claening csv
    # Convert Date column into datetime format
    df['Date'] = pd.to_datetime(df['date'], errors='coerce')

    # Identify and handle missing values for key fields
    df['location_desc'] = df['location_desc'].fillna('Unknown')
    df['block'] = df['block'].fillna('Unknown')
    df['primary_type'] = df['primary_type'].fillna('Unknown')
    df['description'] = df['description'].fillna('Unknown')

    # Standardize categorical fields (strip whitespace, unify case)
    df['primary_type'] = df['primary_type'].astype(str).str.strip().str.upper()
    df['description'] = df['description'].astype(str).str.strip().str.upper()
    df['location_desc'] = df['location_desc'].astype(str).str.strip().str.upper()

    # 3. Generate new features
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['DayOfWeek'] = df['Date'].dt.day_name()

    # 4. Use numpy
    # Calculate percentage of missing values per column using numpy
    null_counts = np.sum(df.isnull().to_numpy(), axis=0)
    missing_pct = (null_counts / len(df)) * 100

    missing_dict = {}
    cols_over_50 = []
    for col_name, pct in zip(df.columns, missing_pct):
        missing_dict[col_name] = round(float(pct), 2)
        if pct > 50:
            cols_over_50.append(col_name)

    print("\nMissing values percentage per column:")
    print(missing_dict)
    print(f"\nColumns with > 50% missing values: {cols_over_50}")

    # Drop columns that are more than 50% missing (they add little analytical value)
    if cols_over_50:
        df = df.drop(columns=cols_over_50)
        print(f"Dropped columns (>50% missing): {cols_over_50}")

    # 5. Insert cleaned data into SQLite
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    # Save main crime dataset into SQLite
    df_to_save = df.copy()
    if 'date' in df_to_save.columns and 'Date' in df_to_save.columns:
        df_to_save = df_to_save.drop(columns=['date'])
    if 'year' in df_to_save.columns and 'Year' in df_to_save.columns:
        df_to_save = df_to_save.drop(columns=['year'])
    df_to_save['Date'] = df_to_save['Date'].astype(str)
    df_to_save.to_sql("crimes", conn, if_exists="replace", index=False)

    # Save reference CSV files into SQLite tables
    ref_files = {
        "city_community": os.path.join(DB_DIR, "chicago_city_community.csv"),
        "district_info": os.path.join(DB_DIR, "chicago_district_ps_info.csv"),
        "beat_info": os.path.join(DB_DIR, "chicago_police_beat_info.csv"),
        "ward_offices": os.path.join(DB_DIR, "chicago_ward_offices.csv"),
        "iucr_codes": os.path.join(DB_DIR, "iucr_codes.csv")
    }

    for table_name, file_path in ref_files.items():
        if os.path.exists(file_path):
            ref_df = pd.read_csv(file_path)
            ref_df.to_sql(table_name, conn, if_exists="replace", index=False)

    conn.close()

    # Answers to questions
    unique_crimes = int(df['primary_type'].nunique())
    invalid_dates = int(df['Date'].isnull().sum())

    print(f"\nHow many unique crime types exist in the dataset? {unique_crimes}")
    print(f"Are there anomalies in date formats? {invalid_dates} invalid dates found.")

    return {
        "rows": rows,
        "cols": cols,
        "schema": {col: str(dtype) for col, dtype in df.dtypes.items()},
        # Only 5 rows are needed for the preview table, so grab 5 directly
        "first_5": df.head(5).to_dict(orient="records"),
        "missing_dict": missing_dict,
        "cols_over_50": cols_over_50,
        "unique_crimes": unique_crimes,
        "invalid_dates": invalid_dates
    }


if __name__ == "__main__":
    run_usecase1()
