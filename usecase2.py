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


def run_usecase2():
    print("Running Use Case 2...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM crimes", conn)

    # Ensure Date conversion
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Year'] = df['Date'].dt.year
        df['Month'] = df['Date'].dt.month
        df['DayOfWeek'] = df['Date'].dt.day_name()

    # 1. Crime Trend Over Years
    # Plot total number of crimes per year
    crimes_per_year = df.groupby('Year').size().reset_index(name='Total_Crimes')

    plt.figure(figsize=(8, 4))
    plt.plot(crimes_per_year['Year'], crimes_per_year['Total_Crimes'], marker='o', color='blue')
    plt.title("Total Number of Crimes Per Year")
    plt.xlabel("Year")
    plt.ylabel("Number of Crimes")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "crime_trend_yearly.png"))
    plt.close()

    # Visual interpretation check
    trend_direction = "decreasing" if crimes_per_year['Total_Crimes'].iloc[-1] < crimes_per_year['Total_Crimes'].iloc[0] else "rising"
    print(f"Visual Interpretation: The overall crime trend is {trend_direction}.")

    # 2. Crime Distribution by Category
    # Bar chart of top 10 crime categories (Primary Type)
    top10_crimes = df['primary_type'].value_counts().head(10).reset_index()
    top10_crimes.columns = ['Primary_Type', 'Count']
    top10_crimes['Percentage'] = (top10_crimes['Count'] / len(df)) * 100

    plt.figure(figsize=(9, 4.5))
    plt.barh(top10_crimes['Primary_Type'], top10_crimes['Count'], color='skyblue')
    plt.xlabel("Count")
    plt.ylabel("Primary Crime Type")
    plt.title("Top 10 Crime Categories")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "top_10_crime_types.png"))
    plt.close()

    most_frequent_crime = top10_crimes['Primary_Type'].iloc[0]
    print(f"\nTop 10 Crime Categories:\n{top10_crimes}")

    # 3. Arrests and Crime Outcomes
    # What percentage of crimes result in arrest?
    # Handle boolean or int representation of arrest column
    df['arrest_bool'] = df['arrest'].apply(lambda x: True if str(x).lower() in ['true', '1'] else False)
    arrest_rate = df['arrest_bool'].mean() * 100
    print(f"\nOverall Arrest Rate: {arrest_rate:.2f}%")

    # Check arrest rate consistency across years
    yearly_arrest_rate = df.groupby('Year')['arrest_bool'].mean() * 100
    print(f"Yearly Arrest Rates:\n{yearly_arrest_rate}")

    # 4. Heatmap of Crime by Month and Day of Week
    # Use Seaborn heatmap of crime frequency pivoted by Month vs DayOfWeek
    pivot_table = df.pivot_table(index='DayOfWeek', columns='Month', aggfunc='size', fill_value=0)
    
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    existing_days = [d for d in days_order if d in pivot_table.index]
    pivot_table = pivot_table.reindex(existing_days)

    plt.figure(figsize=(9, 4.5))
    sns.heatmap(pivot_table, annot=True, fmt='d', cmap='Blues')
    plt.title("Heatmap of Crime by Month and Day of Week")
    plt.xlabel("Month")
    plt.ylabel("Day of Week")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "heatmap_month_day.png"))
    plt.close()

    monthly_counts = df.groupby('Month').size()
    highest_crime_month = monthly_counts.idxmax()

    # 5. Top Community Areas
    # List top 10 community areas with highest crime counts using readable names
    community_lookup = pd.read_sql("SELECT community_code, community_name FROM city_community", conn)
    community_lookup['community_code'] = pd.to_numeric(community_lookup['community_code'], errors='coerce')

    top10_communities = (
        df['community_code']
        .dropna()
        .astype(int)
        .value_counts()
        .head(10)
        .reset_index()
    )
    top10_communities.columns = ['community_code', 'crime_count']

    top10_communities = top10_communities.merge(
        community_lookup[['community_code', 'community_name']],
        on='community_code',
        how='left'
    )
    top10_communities['community_name'] = top10_communities['community_name'].fillna('Unknown')
    top10_communities = top10_communities[['community_name', 'crime_count']]

    plt.figure(figsize=(8, 4))
    plt.bar(top10_communities['community_name'], top10_communities['crime_count'], color='coral')
    plt.xlabel("Community Area")
    plt.ylabel("Crime Count")
    plt.title("Top 10 Community Areas with Highest Crime Counts")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "top_community_areas.png"))
    plt.close()

    # Answer Questions
    print("\n--- Questions & Answers ---")
    print(f"1. Which crime category is most frequent? {most_frequent_crime}")
    print(f"2. Is the arrest rate consistent across different years? Yearly rates range from {yearly_arrest_rate.min():.2f}% to {yearly_arrest_rate.max():.2f}%.")
    print(f"3. Which month has the highest crime frequency? Month {highest_crime_month}")

    conn.close()

    return {
        "total_crimes": len(df),
        "arrest_rate": round(arrest_rate, 2),
        "most_frequent_crime": most_frequent_crime,
        "highest_crime_month": int(highest_crime_month),
        "yearly_trend": crimes_per_year.to_dict(orient='records'),
        "top_categories": top10_crimes.to_dict(orient='records'),
        "top_communities": top10_communities.to_dict(orient='records'),
        "charts": {
            "crime_trend": "crime_trend_yearly.png",
            "top_categories": "top_10_crime_types.png",
            "heatmap": "heatmap_month_day.png",
            "top_communities": "top_community_areas.png"
        }
    }


if __name__ == "__main__":
    run_usecase2()
