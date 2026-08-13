import os
import sqlite3
import pandas as pd
import numpy as np

# Path configurations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "chicago_crime.db")

CRIME_CSV = os.path.join(DB_DIR, "chicago_crime_dataset.csv")
COMMUNITY_CSV = os.path.join(DB_DIR, "chicago_city_community.csv")
DISTRICT_CSV = os.path.join(DB_DIR, "chicago_district_ps_info.csv")
BEAT_CSV = os.path.join(DB_DIR, "chicago_police_beat_info.csv")
WARD_CSV = os.path.join(DB_DIR, "chicago_ward_offices.csv")
IUCR_CSV = os.path.join(DB_DIR, "iucr_codes.csv")


def run_usecase1():
    """
    Use Case 1: Load, Clean, Feature Engineer, and Ingest Chicago Crime Data into SQLite.
    """
    print("--- Running Use Case 1: Data Loading, Cleaning & Ingestion ---")
    
    # 1. Load the dataset (CSV) into Pandas DataFrame
    df = pd.read_csv(CRIME_CSV)
    
    rows, cols = df.shape
    first_10 = df.head(10)
    schema_info = df.dtypes.to_dict()
    
    print(f"Loaded dataset with {rows} rows and {cols} columns.")
    
    # 2. NumPy Missing Value Analysis
    missing_counts = df.isnull().sum()
    missing_pct_numpy = np.round((df.isnull().sum().to_numpy() / len(df)) * 100, 2)
    missing_analysis = {}
    
    cols_over_50 = []
    for idx, col_name in enumerate(df.columns):
        pct = missing_pct_numpy[idx]
        count = int(missing_counts[col_name])
        missing_analysis[col_name] = {"count": count, "percentage": pct}
        if pct > 50.0:
            cols_over_50.append((col_name, pct))
            
    print(f"Columns with > 50% missing values: {cols_over_50 if cols_over_50 else 'None'}")
    
    # 3. Clean Dataset & Handle Missing Values (Preserve Data Policy)
    # Categorical fields: fill missing values with "Unknown"
    categorical_cols = ['location_desc', 'block', 'primary_type', 'description', 'fbi_code']
    for c in categorical_cols:
        if c in df.columns:
            df[c] = df[c].fillna("Unknown").astype(str).str.strip().str.upper()
            
    # Preserve numeric/location missing fields as NaN (do not blindly drop rows)
    # 4. Date Conversion & Feature Engineering
    # Explicitly create df['Date'] from lower-case df['date']
    df['Date'] = pd.to_datetime(df['date'], errors='coerce')
    
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['DayOfWeek'] = df['Date'].dt.day_name()
    df['Hour'] = df['Date'].dt.hour
    
    # 5. Calculate Metrics & Anomaly Checks
    unique_crime_types = int(df['primary_type'].nunique())
    invalid_dates_count = int(df['Date'].isnull().sum())
    min_date = str(df['Date'].min())
    max_date = str(df['Date'].max())
    
    # 6. Database Table Insertion into SQLite
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    
    # Insert main cleaned crimes dataset
    # Convert Timestamp column to string format for SQLite compatibility
    df_to_save = df.copy()
    # Deduplicate columns case-insensitively keeping the uppercase/latest version
    cols_seen = {}
    cols_to_keep = []
    for col in df_to_save.columns:
        lower_col = col.lower()
        if lower_col in cols_seen:
            # Drop previous instance if we have a new capitalized version
            cols_to_keep.remove(cols_seen[lower_col])
        cols_seen[lower_col] = col
        cols_to_keep.append(col)
    
    df_to_save = df_to_save[cols_to_keep]
    df_to_save['Date'] = df_to_save['Date'].astype(str)
    df_to_save.to_sql("crimes", conn, if_exists="replace", index=False)
    
    # Load reference datasets into SQLite
    ref_files = {
        "city_community": COMMUNITY_CSV,
        "district_info": DISTRICT_CSV,
        "beat_info": BEAT_CSV,
        "ward_offices": WARD_CSV,
        "iucr_codes": IUCR_CSV
    }
    
    for table_name, csv_path in ref_files.items():
        if os.path.exists(csv_path):
            ref_df = pd.read_csv(csv_path)
            ref_df.to_sql(table_name, conn, if_exists="replace", index=False)
            print(f"Loaded {len(ref_df)} rows into table '{table_name}'.")
            
    conn.close()
    print("Database SQLite ingestion complete.")
    
    return {
        "rows": rows,
        "cols": cols,
        "schema": {col: str(dtype) for col, dtype in schema_info.items()},
        "first_10": first_10.to_dict(orient="records"),
        "missing_analysis": missing_analysis,
        "cols_over_50": cols_over_50,
        "unique_crime_types": unique_crime_types,
        "invalid_dates_count": invalid_dates_count,
        "date_range": f"{min_date} to {max_date}",
        "primary_types_list": sorted(df['primary_type'].unique().tolist())
    }


if __name__ == "__main__":
    results = run_usecase1()
    print("Use Case 1 executed successfully.")
