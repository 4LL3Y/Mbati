import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from utils.data import get_binance_data
from streamlit_autorefresh import st_autorefresh

# Set page config
st.set_page_config(page_title="MBATI", layout="wide")

# Inject CSS
st.markdown("""
    <style>
    /* Focus ring for inputs and dropdowns */
    .css-1cpxqw2:focus, .css-1cpxqw2:focus-visible {
        border-color: #000000 !important;
        box-shadow: 0 0 0 1px #000000 !important;
    }

    /* Multiselect selected tags — clean gray + black border */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #f2f2f2 !important;
        color: black !important;
        border: 1px solid #000000 !important;
        border-radius: 8px !important;
        padding: 3px 6px !important;
    }

    /* Rounded dropdowns and text inputs */
    .stSelectbox div[data-baseweb="select"],
    .stTextInput > div > div > input {
        border-radius: 8px !important;
    }

    /* Rounded alerts */
    .stAlert {
        border-radius: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Title & tagline
st.title("MBATI")
st.markdown("### _Built for strategies that don't follow the rules._")

# Selection area
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    symbol = st.selectbox("Cryptocurrency", ["BTCUSDT", "ETHUSDT"])
with col2:
    interval = st.selectbox("Time Frame", ["5m", "15m", "1h", "1d"])
with col3:
    indicator = st.selectbox("Indicator", ["Moving Average (MA)"])

# Auto-refresh interval setup
refresh_map = {
    "5m": 30 * 1000,
    "15m": 60 * 1000,
    "1h": 2 * 60 * 1000,
    "1d": 10 * 60 * 1000,
}
st_autorefresh(interval=refresh_map[interval], key="crypto_autorefresh")



# Moving Average section
st.subheader("Moving Average Settings")

default_ma_options = [3, 6, 9, 12, 15, 20, 30, 50, 100]
selected_ma_periods = st.multiselect(
    "Select one or more MA periods",
    options=default_ma_options,
    default=[6]
)

custom_input = st.text_input(
    "Or enter custom MA periods (comma-separated)", 
    value="", 
    help="Example: 7, 13, 21"
)

# Parse custom input safely
try:
    custom_periods = [
        int(x.strip()) for x in custom_input.split(",") 
        if x.strip().isdigit() and int(x.strip()) > 0
    ]
except Exception:
    custom_periods = []

# Merge and sort all selected MA periods
ma_periods = sorted(set(selected_ma_periods + custom_periods))


# Alert logic section
st.subheader("Alert Logic")

alert_type = st.selectbox(
    "Choose alert condition",
    [
        "Close crosses above MA",
        "Close crosses below MA",
        "Close above MA",
        "Close below MA",
        "No alert",
    ],
    index=0,
)

# Load data from Binance
df = get_binance_data(symbol, interval)

if df is not None and ma_periods:
    ma_columns = []
    for period in ma_periods:
        col_name = f"MA{period}"
        df[col_name] = df["close"].rolling(period).mean()
        ma_columns.append(col_name)

    selected_ma = ma_columns[0]  # use first MA for alert logic

    # Alert trigger logic
    alert = False
    if alert_type == "Close crosses above MA":
        alert = (
            df["close"].iloc[-1] > df[selected_ma].iloc[-1] and
            df["close"].iloc[-2] <= df[selected_ma].iloc[-2]
        )
    elif alert_type == "Close crosses below MA":
        alert = (
            df["close"].iloc[-1] < df[selected_ma].iloc[-1] and
            df["close"].iloc[-2] >= df[selected_ma].iloc[-2]
        )
    elif alert_type == "Close above MA":
        alert = df["close"].iloc[-1] > df[selected_ma].iloc[-1]
    elif alert_type == "Close below MA":
        alert = df["close"].iloc[-1] < df[selected_ma].iloc[-1]

    # Plot chart
    st.subheader("Price Chart")

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="Price"
    ))

    for col in ma_columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[col],
            mode="lines",
            name=col,
            line=dict(width=2, color="red")
        ))

    st.plotly_chart(fig, use_container_width=True)

    # Show alert result
    if alert:
        st.warning(f"Alert: **{alert_type}** triggered for `{selected_ma}`")
    else:
        st.success("No alert triggered.")
else:
    st.error("⚠️ Failed to fetch data or select at least one MA period.")
