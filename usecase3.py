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


def run_usecase3():
    """
    Use Case 3: Statistical Insights & Pattern Detection
    """
    print("--- Running Use Case 3: Statistical Insights & Pattern Detection ---")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM crimes", conn)
    conn.close()
    
    # Ensure Date conversion and Hour extraction
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        if 'Hour' not in df.columns or df['Hour'].isnull().all():
            df['Hour'] = df['Date'].dt.hour
        if 'Year' not in df.columns or df['Year'].isnull().all():
            df['Year'] = df['Date'].dt.year
        if 'Month' not in df.columns or df['Month'].isnull().all():
            df['Month'] = df['Date'].dt.month
            
    # Set aesthetics
    sns.set_theme(style="whitegrid")
    
    # 1. Hourly Crime Intensity
    hourly_counts = df.groupby('Hour').size().reset_index(name='crime_count')
    plt.figure(figsize=(9, 4.5))
    ax1 = sns.lineplot(data=hourly_counts, x='Hour', y='crime_count', marker='o', color='#e74c3c', linewidth=2.5)
    plt.xticks(range(0, 24))
    
    # Highlight peak hour
    peak_row = hourly_counts.loc[hourly_counts['crime_count'].idxmax()]
    ax1.annotate(f"Peak: Hour {int(peak_row['Hour'])} ({int(peak_row['crime_count'])} crimes)",
                 (peak_row['Hour'], peak_row['crime_count']),
                 textcoords="offset points", xytext=(0, 10), ha='center', fontweight='bold', color='#c0392b')
                 
    plt.title("Hourly Crime Intensity Distribution (24-Hour Clock)", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Hour of Day (0 - 23)", fontsize=11)
    plt.ylabel("Number of Crimes", fontsize=11)
    plt.tight_layout()
    chart1_path = os.path.join(OUTPUT_DIR, "hourly_crime_intensity.png")
    plt.savefig(chart1_path, dpi=150)
    plt.close()
    
    # 2. Community Area Analysis (Mean & Boxplot & IQR Outliers)
    comm_series = df['community_code'].dropna().astype(int).value_counts()
    comm_counts_np = comm_series.to_numpy()
    
    mean_crime_per_comm = float(np.mean(comm_counts_np))
    median_crime_per_comm = float(np.median(comm_counts_np))
    
    q1 = float(np.percentile(comm_counts_np, 25))
    q3 = float(np.percentile(comm_counts_np, 75))
    iqr = q3 - q1
    upper_bound = q3 + 1.5 * iqr
    lower_bound = max(0, q1 - 1.5 * iqr)
    
    outliers_series = comm_series[comm_series > upper_bound]
    outliers_list = []
    for comm_code, count in outliers_series.items():
        outliers_list.append({"community_code": int(comm_code), "crime_count": int(count)})
        
    plt.figure(figsize=(8, 4))
    sns.boxplot(x=comm_counts_np, color='#3498db', flierprops={'markerfacecolor': '#e74c3c', 'markersize': 8})
    plt.title("Distribution of Crime Counts Across Community Areas (Box Plot)", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Crime Count per Community Area", fontsize=11)
    plt.tight_layout()
    chart2_path = os.path.join(OUTPUT_DIR, "community_box_plot.png")
    plt.savefig(chart2_path, dpi=150)
    plt.close()
    
    # 3. Crime Cross-Correlation Heatmap
    # Select numerical columns for correlation calculation
    num_cols = ['Year', 'Month', 'Hour', 'arrest', 'domestic', 'community_code', 'district_code', 'ward_no']
    available_num_cols = [c for c in num_cols if c in df.columns]
    
    corr_df = df[available_num_cols].astype(float)
    corr_matrix = corr_df.corr()
    
    plt.figure(figsize=(8, 6.5))
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap='coolwarm', vmin=-1, vmax=1, linewidths=0.5)
    plt.title("Crime Features Cross-Correlation Matrix", fontsize=13, fontweight='bold', pad=12)
    plt.tight_layout()
    chart3_path = os.path.join(OUTPUT_DIR, "correlation_heatmap.png")
    plt.savefig(chart3_path, dpi=150)
    plt.close()
    
    print("Use Case 3 statistical insights generated successfully.")
    
    return {
        "hourly_distribution": hourly_counts.to_dict(orient='records'),
        "peak_hour": int(peak_row['Hour']),
        "peak_hour_count": int(peak_row['crime_count']),
        "mean_crime_per_comm": round(mean_crime_per_comm, 2),
        "median_crime_per_comm": round(median_crime_per_comm, 2),
        "iqr_stats": {
            "q1": round(q1, 2),
            "q3": round(q3, 2),
            "iqr": round(iqr, 2),
            "upper_bound": round(upper_bound, 2),
            "lower_bound": round(lower_bound, 2)
        },
        "outliers_list": outliers_list,
        "charts": {
            "hourly_intensity": "hourly_crime_intensity.png",
            "box_plot": "community_box_plot.png",
            "correlation": "correlation_heatmap.png"
        }
    }


if __name__ == "__main__":
    results = run_usecase3()
    print("Use Case 3 executed successfully.")
