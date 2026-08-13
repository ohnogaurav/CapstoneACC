import os
import sqlite3
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Set file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "chicago_crime.db")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def run_usecase4():
    print("Running Use Case 4...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Design & Populate Summary Tables in SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 3. Database Stored Views
    # Create views in SQLite: vw_crime_yearly and vw_crime_by_category
    cursor.execute("DROP VIEW IF EXISTS vw_crime_yearly")
    cursor.execute("""
        CREATE VIEW vw_crime_yearly AS
        SELECT 
            Year,
            COUNT(*) AS total_crimes,
            SUM(CASE WHEN arrest = 1 OR arrest = 'True' THEN 1 ELSE 0 END) AS total_arrests
        FROM crimes
        WHERE Year IS NOT NULL
        GROUP BY Year
        ORDER BY Year ASC
    """)

    cursor.execute("DROP VIEW IF EXISTS vw_crime_by_category")
    cursor.execute("""
        CREATE VIEW vw_crime_by_category AS
        SELECT 
            primary_type,
            COUNT(*) AS crime_count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM crimes), 2) AS percentage
        FROM crimes
        GROUP BY primary_type
        ORDER BY crime_count DESC
    """)

    conn.commit()

    # 4. Pandas Integration
    # Read these views into Pandas DataFrames for further analysis
    df_yearly = pd.read_sql("SELECT * FROM vw_crime_yearly", conn)
    df_category = pd.read_sql("SELECT * FROM vw_crime_by_category", conn)

    # 2. SQLite Queries
    # - Crime count per year
    print("\n1. Crime count per year (from view):")
    print(df_yearly[['Year', 'total_crimes']])

    # - Top 5 crime types and their percentages
    df_top5 = pd.read_sql("SELECT * FROM vw_crime_by_category LIMIT 5", conn)
    print("\n2. Top 5 crime types and percentages:")
    print(df_top5)

    # - Arrest count per year
    print("\n3. Arrest count per year (from view):")
    print(df_yearly[['Year', 'total_arrests']])

    conn.close()

    # 5. Visualization from SQLite Data
    # Plot SQL extracted data with Matplotlib and Seaborn
    plt.figure(figsize=(8, 4))
    sns.barplot(data=df_yearly, x='Year', y='total_crimes', color='steelblue')
    plt.title("SQL Extracted Data: Crime Count Per Year")
    plt.xlabel("Year")
    plt.ylabel("Total Crimes")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "sql_yearly_crimes.png"))
    plt.close()

    print("\nVisualization from SQL data saved successfully.")

    return {
        "vw_crime_yearly": df_yearly.to_dict(orient='records'),
        "top5_crime_types": df_top5.to_dict(orient='records'),
        "all_categories_view": df_category.to_dict(orient='records')
    }


if __name__ == "__main__":
    run_usecase4()
