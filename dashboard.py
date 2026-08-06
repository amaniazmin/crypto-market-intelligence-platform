import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Crypto Dashboard", layout="wide")
st.title("🚀 Crypto Market Intelligence Dashboard")

# --- MAIN SELECTION ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("### Select a Coin:")
    display_coin = st.selectbox("", ["BTC", "ETH", "SOL"], label_visibility="collapsed")

# --- MAP USER NAMES TO API CODES ---
coin_map = {
    "BTC": "BTCUSDT",
    "ETH": "ETHUSDT",
    "SOL": "SOLUSDT"
}
coin = coin_map[display_coin]

# --- CONSERVATIVE CURVE ML PREDICTION FUNCTION ---
def predict_trend(df, days_ahead=21):
    data = df.copy()
    data['Day_Num'] = (data['Date'] - data['Date'].min()).dt.days
    
    X = data[['Day_Num']].values
    y = data['Close'].values
    
    # Change from degree 3 to degree 2 (Gentle curve, prevents extreme spikes)
    poly = PolynomialFeatures(degree=2)
    X_poly = poly.fit_transform(X)
    
    model = LinearRegression()
    model.fit(X_poly, y)
    
    last_day = data['Day_Num'].max()
    future_days = np.array(range(last_day + 1, last_day + days_ahead + 1)).reshape(-1, 1)
    
    future_days_poly = poly.transform(future_days)
    future_prices = model.predict(future_days_poly)

    # --- CONSERVATIVE CAP (Prevents massive spikes) ---
    # Calculate the average price of the last 10 days
    avg_last_10_days = df['Close'].tail(10).mean()
    
    # 🛑 NEW SAFETY FIX: If the average is 0 (data hasn't loaded), skip the cap
    if avg_last_10_days == 0 or pd.isna(avg_last_10_days):
        # Return the raw math if data isn't ready, to prevent the graph from breaking
        pass 
    else:
        # Cap the prediction so it doesn't go higher than 50% of the average price
        # and doesn't go lower than -50% of the average price.
        cap_high = avg_last_10_days * 1.5
        cap_low = avg_last_10_days * 0.5
        
        # Apply the cap to the future prices
        future_prices = np.clip(future_prices, cap_low, cap_high)
    # -----------------------------------------------------

    # Create the future dates dataframe
    future_dates = pd.date_range(start=df['Date'].max() + pd.Timedelta(days=1), periods=days_ahead)
    prediction_df = pd.DataFrame({
        'Date': future_dates,
        'Predicted_Price': future_prices
    })
    return prediction_df

# --- FETCH DATA ---
@st.cache_data(ttl=60)
def get_crypto_data(symbol):
    try:
        url = f"https://api.binance.us/api/v3/klines?symbol={symbol}&interval=1d&limit=100"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data, columns=[
                'Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 
                'Close Time', 'Quote Asset Volume', 'Number of Trades', 
                'Taker Buy Base Volume', 'Taker Buy Quote Volume', 'Ignore'
            ])
            
            df['Date'] = pd.to_datetime(df['Open Time'], unit='ms')
            df['Open'] = pd.to_numeric(df['Open'])
            df['High'] = pd.to_numeric(df['High'])
            df['Low'] = pd.to_numeric(df['Low'])
            df['Close'] = pd.to_numeric(df['Close'])
            df['Volume'] = pd.to_numeric(df['Volume'])
            
            return df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        else:
            return None
    except:
        return None

# --- RUN THE FETCH ---
df = get_crypto_data(coin)

if df is not None and not df.empty:
    current_price = df['Close'].iloc[-1]
    st.metric(label=f"{display_coin} Current Price", value=f"${current_price:,.2f}")

    # --- DRAW THE MAIN CHART ---
    st.subheader("Price Chart with 3-Week Conservative Prediction")
    
    # Set up the figure
    fig = go.Figure()
    
    # 1. Draw the Real Candles
    fig.add_trace(go.Candlestick(
        x=df['Date'],
        open=df['Open'], 
        high=df['High'],
        low=df['Low'], 
        close=df['Close'],
        name="Actual Price"
    ))
    
    # 2. GENERATE AND DRAW THE CURVED ML PREDICTION (3 WEEKS)
    try:
        prediction_data = predict_trend(df, days_ahead=21)
        
        fig.add_trace(go.Scatter(
            x=prediction_data['Date'],
            y=prediction_data['Predicted_Price'],
            mode='lines+markers',
            line=dict(color='#FFA500', width=4, dash='dot'),
            marker=dict(size=10, symbol='diamond', color='#FFA500'),
            name="3-Week Curve Prediction"
        ))
    except Exception as e:
        st.warning("Prediction unavailable (Not enough data for ML)")

    # --- CHART STYLING ---
    fig.update_layout(
        title=f'{display_coin} Price Analysis',
        yaxis_title='Price (USD)',
        xaxis_title='Date',
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        height=600,
        hovermode='x unified',
        margin=dict(l=40, r=40, t=60, b=40)
    )

    # SHOW THE CHART
    st.plotly_chart(fig, use_container_width=True)

    # --- SHOW DATA TABLE ---
    st.subheader("Historical Data")
    st.dataframe(df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']])

else:
    st.error("⚠️ Could not retrieve data. Please refresh the page.")