import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "chicago_crime.db")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def run_usecase2():
    """
    Use Case 2: Exploratory Data Analysis & Visualizations
    """
    print("--- Running Use Case 2: Exploratory Data Analysis & Visualization ---")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM crimes", conn)
    conn.close()
    
    # Ensure Date parsing if needed
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        if 'Year' not in df.columns or df['Year'].isnull().all():
            df['Year'] = df['Date'].dt.year
        if 'Month' not in df.columns or df['Month'].isnull().all():
            df['Month'] = df['Date'].dt.month
        if 'DayOfWeek' not in df.columns or df['DayOfWeek'].isnull().all():
            df['DayOfWeek'] = df['Date'].dt.day_name()
            
    # Set aesthetics
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({'font.size': 10})
    
    # 1. Crime Trend Over Years
    yearly_counts = df.groupby('Year').size().reset_index(name='crime_count')
    plt.figure(figsize=(8, 4.5))
    ax1 = sns.lineplot(data=yearly_counts, x='Year', y='crime_count', marker='o', color='#1f77b4', linewidth=2.5)
    sns.scatterplot(data=yearly_counts, x='Year', y='crime_count', color='#1f77b4', s=70)
    
    for _, row in yearly_counts.iterrows():
        ax1.annotate(f"{int(row['crime_count'])}", 
                     (row['Year'], row['crime_count']),
                     textcoords="offset points", xytext=(0, 8), ha='center', fontweight='bold')
                     
    plt.title("Total Crimes Reported per Year in Chicago", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Year", fontsize=11)
    plt.ylabel("Number of Crimes", fontsize=11)
    plt.tight_layout()
    chart1_path = os.path.join(OUTPUT_DIR, "crime_trend_yearly.png")
    plt.savefig(chart1_path, dpi=150)
    plt.close()
    
    # 2. Top 10 Crime Categories (Primary Type)
    cat_counts = df['primary_type'].value_counts().head(10).reset_index()
    cat_counts.columns = ['primary_type', 'count']
    cat_counts['percentage'] = (cat_counts['count'] / len(df)) * 100
    
    plt.figure(figsize=(9, 5))
    ax2 = sns.barplot(data=cat_counts, y='primary_type', x='count', palette='Blues_r')
    for idx, row in cat_counts.iterrows():
        ax2.text(row['count'] + 5, idx, f"{int(row['count'])} ({row['percentage']:.1f}%)", 
                 va='center', fontsize=9.5, fontweight='bold')
                 
    plt.title("Top 10 Most Common Crime Categories", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Crime Count", fontsize=11)
    plt.ylabel("Primary Type", fontsize=11)
    plt.tight_layout()
    chart2_path = os.path.join(OUTPUT_DIR, "top_10_crime_types.png")
    plt.savefig(chart2_path, dpi=150)
    plt.close()
    
    # 3. Overall Arrest Rate
    arrest_rate = float(df['arrest'].mean() * 100)
    total_crimes = len(df)
    total_arrests = int(df['arrest'].sum())
    
    # 4. Heatmap of Crime by Month and Day of Week
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot_month_day = df.pivot_table(index='DayOfWeek', columns='Month', aggfunc='size', fill_value=0)
    # Reindex days of week correctly
    pivot_month_day = pivot_month_day.reindex([d for d in days_order if d in pivot_month_day.index])
    
    plt.figure(figsize=(9, 5))
    sns.heatmap(pivot_month_day, annot=True, fmt='d', cmap='YlOrRd', cbar=True, linewidths=0.5)
    plt.title("Crime Frequency Heatmap (Day of Week vs Month)", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Month", fontsize=11)
    plt.ylabel("Day of Week", fontsize=11)
    plt.tight_layout()
    chart3_path = os.path.join(OUTPUT_DIR, "heatmap_month_day.png")
    plt.savefig(chart3_path, dpi=150)
    plt.close()
    
    # 5. Top 10 Community Areas
    comm_df = df.dropna(subset=['community_code']).copy()
    comm_df['community_code'] = comm_df['community_code'].astype(int)
    top_comm = comm_df['community_code'].value_counts().head(10).reset_index()
    top_comm.columns = ['community_code', 'count']
    top_comm['community_code_str'] = top_comm['community_code'].astype(str)
    
    plt.figure(figsize=(9, 4.5))
    ax4 = sns.barplot(data=top_comm, x='community_code_str', y='count', palette='Reds_r')
    for idx, row in top_comm.iterrows():
        ax4.text(idx, row['count'] + 1, f"{int(row['count'])}", ha='center', fontsize=9.5, fontweight='bold')
        
    plt.title("Top 10 Community Areas by Crime Count", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Community Area Code", fontsize=11)
    plt.ylabel("Number of Reported Crimes", fontsize=11)
    plt.tight_layout()
    chart4_path = os.path.join(OUTPUT_DIR, "top_community_areas.png")
    plt.savefig(chart4_path, dpi=150)
    plt.close()
    
    print("Use Case 2 visual charts generated successfully.")
    
    return {
        "total_crimes": total_crimes,
        "total_arrests": total_arrests,
        "arrest_rate": round(arrest_rate, 2),
        "yearly_trend": yearly_counts.to_dict(orient='records'),
        "top_categories": cat_counts.to_dict(orient='records'),
        "top_communities": top_comm.to_dict(orient='records'),
        "charts": {
            "crime_trend": "crime_trend_yearly.png",
            "top_categories": "top_10_crime_types.png",
            "heatmap": "heatmap_month_day.png",
            "top_communities": "top_community_areas.png"
        }
    }


if __name__ == "__main__":
    results = run_usecase2()
    print("Use Case 2 executed successfully.")
