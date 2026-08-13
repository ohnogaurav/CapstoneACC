import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Set file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "chicago_crime.db")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def run_usecase3():
    print("Running Use Case 3...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM crimes", conn)
    conn.close()

    # Ensure Date conversion
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # 1. Crime Intensity by Time
    df['Hour'] = df['Date'].dt.hour
    crimes_by_hour = df.groupby('Hour').size()

    plt.figure(figsize=(8, 4))
    plt.plot(crimes_by_hour.index, crimes_by_hour.values, marker='o', color='red')
    plt.title("Crime Intensity by Hour of Day")
    plt.xlabel("Hour of Day (0-23)")
    plt.ylabel("Number of Crimes")
    plt.xticks(range(0, 24))
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "hourly_crime_intensity.png"))
    plt.close()

    peak_hour = int(crimes_by_hour.idxmax())
    peak_count = int(crimes_by_hour.max())
    print(f"Hourly Distribution Peak: Hour {peak_hour} with {peak_count} crimes.")

    # 2. Community Area Clusters Using NumPy
    # Use NumPy functions to compute mean crime per community area
    comm_counts = df['community_code'].dropna().astype(int).value_counts()
    comm_array = comm_counts.to_numpy()

    mean_crime_per_community = np.mean(comm_array)
    print(f"\nMean crimes per community area (NumPy): {mean_crime_per_community:.2f}")

    # Use box plot to identify outliers
    plt.figure(figsize=(8, 4))
    plt.boxplot(comm_array, vert=False)
    plt.title("Box Plot of Crime Counts per Community Area")
    plt.xlabel("Crime Count")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "community_box_plot.png"))
    plt.close()

    # Use IQR method to list extreme outliers
    q1 = np.percentile(comm_array, 25)
    q3 = np.percentile(comm_array, 75)
    iqr = q3 - q1
    upper_bound = q3 + 1.5 * iqr

    outlier_communities = comm_counts[comm_counts > upper_bound]
    outliers_list = []
    for comm_id, count in outlier_communities.items():
        outliers_list.append({"community_code": int(comm_id), "crime_count": int(count)})

    print(f"Q1: {q1}, Q3: {q3}, IQR: {iqr}, Upper Bound: {upper_bound}")
    print(f"Extreme Outlier Communities (IQR Method):\n{outlier_communities}")

    # 3. Crime Cross-Correlation
    # Use Pandas .corr() on numeric features
    df['arrest_num'] = df['arrest'].apply(lambda x: 1 if str(x).lower() in ['true', '1'] else 0)
    df['domestic_num'] = df['domestic'].apply(lambda x: 1 if str(x).lower() in ['true', '1'] else 0)

    numeric_cols = ['Year', 'Month', 'Hour', 'arrest_num', 'domestic_num', 'community_code', 'district_code', 'ward_no']
    available_cols = [c for c in numeric_cols if c in df.columns]

    corr_matrix = df[available_cols].corr()

    plt.figure(figsize=(8, 6))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title("Crime Features Correlation Matrix")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "correlation_heatmap.png"))
    plt.close()

    print("\nCorrelation matrix calculated successfully.")

    return {
        "peak_hour": peak_hour,
        "peak_count": peak_count,
        "mean_crime_per_comm": round(float(mean_crime_per_community), 2),
        "iqr_stats": {
            "q1": round(float(q1), 2),
            "q3": round(float(q3), 2),
            "iqr": round(float(iqr), 2),
            "upper_bound": round(float(upper_bound), 2)
        },
        "outliers_list": outliers_list,
        "charts": {
            "hourly_intensity": "hourly_crime_intensity.png",
            "box_plot": "community_box_plot.png",
            "correlation": "correlation_heatmap.png"
        }
    }


if __name__ == "__main__":
    run_usecase3()
