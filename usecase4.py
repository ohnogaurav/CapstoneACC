import os
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "chicago_crime.db")


def run_usecase4():
    """
    Use Case 4: SQLite Database Reporting, Views Creation & Pandas Integration
    """
    print("--- Running Use Case 4: SQLite Database Reporting & Views Integration ---")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Create Stored Views in SQLite
    # View 1: vw_crime_yearly
    cursor.execute("DROP VIEW IF EXISTS vw_crime_yearly")
    cursor.execute("""
        CREATE VIEW vw_crime_yearly AS
        SELECT 
            Year,
            COUNT(*) AS total_crimes,
            SUM(CASE WHEN arrest = 1 OR arrest = 'True' THEN 1 ELSE 0 END) AS total_arrests,
            ROUND(SUM(CASE WHEN arrest = 1 OR arrest = 'True' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS arrest_rate_pct
        FROM crimes
        WHERE Year IS NOT NULL
        GROUP BY Year
        ORDER BY Year ASC
    """)
    
    # View 2: vw_crime_by_category
    cursor.execute("DROP VIEW IF EXISTS vw_crime_by_category")
    cursor.execute("""
        CREATE VIEW vw_crime_by_category AS
        SELECT 
            primary_type,
            COUNT(*) AS crime_count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM crimes), 2) AS percentage_share
        FROM crimes
        GROUP BY primary_type
        ORDER BY crime_count DESC
    """)
    
    conn.commit()
    print("Created database views: 'vw_crime_yearly' and 'vw_crime_by_category'.")
    
    # 2. Execute Required SQL Queries
    # Query 1: Crime count per year
    df_yearly = pd.read_sql("SELECT * FROM vw_crime_yearly", conn)
    
    # Query 2: Top 5 crime types and their percentages
    df_top5_types = pd.read_sql("SELECT * FROM vw_crime_by_category LIMIT 5", conn)
    
    # Query 3: Arrest count per year (from view or direct SQL query)
    query_arrests = """
        SELECT 
            Year,
            SUM(CASE WHEN arrest = 1 OR arrest = 'True' THEN 1 ELSE 0 END) AS arrest_count,
            COUNT(*) AS total_incidents
        FROM crimes
        WHERE Year IS NOT NULL
        GROUP BY Year
        ORDER BY Year ASC
    """
    df_arrest_yearly = pd.read_sql(query_arrests, conn)
    
    # Query 4: Full category distribution view
    df_full_categories = pd.read_sql("SELECT * FROM vw_crime_by_category", conn)
    
    conn.close()
    print("Executed SQL reporting queries successfully.")
    
    return {
        "vw_crime_yearly": df_yearly.to_dict(orient='records'),
        "top5_crime_types": df_top5_types.to_dict(orient='records'),
        "arrest_yearly": df_arrest_yearly.to_dict(orient='records'),
        "all_categories_view": df_full_categories.to_dict(orient='records')
    }


if __name__ == "__main__":
    results = run_usecase4()
    print("Use Case 4 executed successfully.")
