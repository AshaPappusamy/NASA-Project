import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import date

# Page configuration
st.set_page_config(page_title="NASA Asteroid Dashboard", layout="wide")

# -----------------------------
# Database connection (TiDB Cloud)
# -----------------------------
host = 'gateway01.ap-southeast-1.prod.aws.tidbcloud.com'
user = '3qKZvyc8Bw7Ckf1.root'
password = 'ixPIapSBo4owm2Qf'
database = 'Asteroid_Nasa'
port = 4000
engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}")

# Title
st.title("🚀 NASA Near-Earth Object (NEO) Insights")

# Predefined queries
query_options = [
    "1. Count how many times each asteroid has approached Earth",
    "2. Average velocity of each asteroid",
    "3. Tell me the top 10 fastest asteroids",
    "4. Hazardous asteroids that approached > 3 times",
    "5. Tell me the Months with most asteroid approaches",
    "6. Which is the fastest ever approach",
    "7. List the Sorted asteroids by Max Diameter",
    "8. Asteroids getting closer over time",
    "9. Closest approach per asteroid",
    "10. Velocity > 50,000 km/h",
    "11. Approach count per month",
    "12. Whihch are the brightest asteroid",
    "13. Hazardous vs Non-Hazardous count",
    "14. Passed closer than 1 lunar distance",
    "15. Passed within 0.05 AU",
    # Extra 5 queries
    "16. Average diameter of hazardous asteroids",
    "17. Largest diameter asteroid",
    "18. Fastest hazardous asteroid",
    "19. Asteroids with multiple close approaches in a month",
    "20. Asteroids passing within 0.1 AU and hazardous"
]

selected_query = st.selectbox("Select a query to run:", query_options)
# Sidebar Filters
st.sidebar.header("Filter Criteria")

with engine.connect() as conn:
    # Getting actual date range
    date_range = conn.execute(text("SELECT MIN(close_approach_date), MAX(close_approach_date) FROM close_approach")).fetchone()
    min_date = date_range[0]
    max_date = date_range[1]

st.sidebar.info(f"Available data from {min_date} to {max_date}")

# Separating Start and End Date
start_date = st.sidebar.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

# AU range
au_range = st.sidebar.slider("Astronomical Units (AU)", 0.0, 5.0, (0.0, 0.5), 0.01)

# Lunar distance
lunar_range = st.sidebar.slider("Lunar Distance (LD)", 0, 500, (0, 100), 1)

# Velocity
velocity_range = st.sidebar.slider("Relative Velocity (km/h)", 0, 200000, (0, 150000), 1000)

# Diameter
diameter_min = st.sidebar.number_input("Min Diameter (km)", 0.0, 50.0, 0.0, 0.1)
diameter_max = st.sidebar.number_input("Max Diameter (km)", 0.0, 50.0, 10.0, 0.1)

# Hazardous state
hazardous_state = st.sidebar.selectbox("Hazardous Asteroid?", ["All", "Yes", "No"])

# Building Filter SQL
filter_query = f"""
SELECT a.name, ca.close_approach_date, ca.astronomical, ca.miss_distance_lunar,
       ca.relative_velocity_kmph, a.estimated_diameter_min_km, a.estimated_diameter_max_km,
       a.hazardous_asteroid
FROM close_approach ca
JOIN asteroids a ON ca.neo_reference_id = a.id
WHERE ca.close_approach_date BETWEEN '{start_date}' AND '{end_date}'
AND ca.astronomical BETWEEN {au_range[0]} AND {au_range[1]}
AND ca.miss_distance_lunar BETWEEN {lunar_range[0]} AND {lunar_range[1]}
AND ca.relative_velocity_kmph BETWEEN {velocity_range[0]} AND {velocity_range[1]}
AND a.estimated_diameter_min_km >= {diameter_min}
AND a.estimated_diameter_max_km <= {diameter_max}
"""

if hazardous_state == "Yes":
    filter_query += " AND a.hazardous_asteroid = TRUE"
elif hazardous_state == "No":
    filter_query += " AND a.hazardous_asteroid = FALSE"

# Displaying Filtered Data
st.subheader("Filtered Asteroid Data")
with engine.connect() as conn:
    filtered_df = pd.read_sql(text(filter_query), conn)
st.dataframe(filtered_df)

# Predefined Queries Execution
st.subheader("Predefined Queries Results")
with engine.connect() as conn:
    if selected_query.startswith("1"):
        result = conn.execute(text("""
            SELECT neo_reference_id, COUNT(*) AS approach_count
            FROM close_approach
            GROUP BY neo_reference_id
            ORDER BY approach_count DESC;
        """)).fetchall()

# Displaying query results
if 'result' in locals():
    st.write(result)
