import streamlit as st
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="AI Energy Dashboard", layout="wide")

st.title("⚡ AI-Powered Energy Forecasting System")

# Load model
try:
    model = joblib.load("models/energy_model.pkl")
except:
    st.error("Run main.py first!")
    st.stop()

# -------------------------------
# FILE UPLOAD FEATURE 🔥
# -------------------------------
st.sidebar.header("📂 Upload Your Dataset")

uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

def process_uploaded_file(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()

    # detect datetime column
    for col in df.columns:
        if "datetime" in col.lower():
            df[col] = pd.to_datetime(df[col])
            df.set_index(col, inplace=True)
            break

    # rename energy column
    df.rename(columns={df.columns[0]: "Energy"}, inplace=True)

    return df

# -------------------------------
# LOAD DATA
# -------------------------------
@st.cache_data
def load_default_data():
    all_data = []

    for file in os.listdir("data"):
        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join("data", file))
            df.columns = df.columns.str.strip()

            for col in df.columns:
                if "datetime" in col.lower():
                    df[col] = pd.to_datetime(df[col])
                    df.set_index(col, inplace=True)
                    break

            df.rename(columns={df.columns[0]: "Energy"}, inplace=True)
            df["region"] = file.replace(".csv", "")

            all_data.append(df)

    return pd.concat(all_data)

# Choose data source
if uploaded_file is not None:
    data = process_uploaded_file(uploaded_file)
    st.success("✅ Using uploaded dataset")
else:
    data = load_default_data()
    st.info("Using default dataset")

# -------------------------------
# SIDEBAR INPUTS
# -------------------------------
st.sidebar.header("🔮 Prediction Inputs")

hour = st.sidebar.slider("Hour", 0, 23, 12)
day = st.sidebar.slider("Day (0=Mon)", 0, 6, 3)
month = st.sidebar.slider("Month", 1, 12, 6)

lag_1 = st.sidebar.number_input("Previous Hour Energy", value=10000)
lag_24 = st.sidebar.number_input("Previous Day Same Hour", value=12000)
rolling = st.sidebar.number_input("24hr Avg Energy", value=11000)

# -------------------------------
# PREDICTION
# -------------------------------
if st.sidebar.button("Predict"):
    features = [[hour, day, month, lag_1, lag_24, rolling]]
    pred = model.predict(features)
    st.success(f"⚡ Predicted Energy: {pred[0]:.2f} MW")

# -------------------------------
# VISUALIZATION
# -------------------------------
st.subheader("📊 Energy Trend")
st.line_chart(data['Energy'].head(1000))

from src.anomaly import detect_anomalies

# -------------------------------
# ANOMALY DETECTION 🔥
# -------------------------------
st.subheader("🚨 Anomaly Detection (Energy Spikes)")

anomaly_data = detect_anomalies(data.copy())

anomalies = anomaly_data[anomaly_data['anomaly'] != 0]

st.write(f"⚠️ Total anomalies detected: {len(anomalies)}")

st.line_chart(anomaly_data['Energy'].head(500))

if not anomalies.empty:
    st.warning("⚡ Unusual energy spikes detected!")
else:
    st.success("✅ Energy usage is stable")

# -------------------------------
# SMART INSIGHTS 🔥
# -------------------------------
st.subheader("🧠 Smart Insights")

peak_hour = data.groupby(data.index.hour)['Energy'].mean().idxmax()
avg_usage = data['Energy'].mean()
max_usage = data['Energy'].max()

st.markdown(f"""
### 📊 Insights:

- 🔥 Peak energy usage occurs at **{peak_hour}:00**
- ⚡ Average consumption is **{avg_usage:.2f} MW**
- 🚀 Maximum recorded usage is **{max_usage:.2f} MW**
""")

# Trend detection
trend = data['Energy'].tail(50)

if trend.iloc[-1] > trend.iloc[0]:
    st.info("📈 Energy usage trend is increasing")
else:
    st.info("📉 Energy usage trend is decreasing")

# -------------------------------
# PEAK ANALYSIS
# -------------------------------
st.subheader("🔥 Peak Hour Analysis")

peak_hour = data.groupby(data.index.hour)['Energy'].mean().idxmax()
st.info(f"⚡ Peak usage hour: {peak_hour}:00")

# -------------------------------
# REGION FILTER (ONLY DEFAULT DATA)
# -------------------------------
if 'region' in data.columns:
    st.subheader("🌍 Region-wise Analysis")

    regions = data['region'].unique()
    selected_region = st.selectbox("Select Region", regions)

    filtered = data[data['region'] == selected_region]
    st.line_chart(filtered['Energy'].head(500))

# -------------------------------
# DISTRIBUTION
# -------------------------------
st.subheader("📈 Load Distribution")
st.bar_chart(data['Energy'].head(100))

st.markdown("### 🚀 Built for Smart Cities & Energy Optimization")