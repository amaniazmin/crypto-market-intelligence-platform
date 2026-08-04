"""
Crypto Market Intelligence Dashboard
Professional design with dark theme and enhanced visuals
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import time
import json
import base64

# API Configuration
API_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Crypto Market Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS - Professional Dark Theme
# ============================================================================
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #1a1f35 50%, #0d1117 100%);
    }
    
    /* Text colors */
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 40px rgba(247, 151, 30, 0.3);
        margin-bottom: 0;
    }
    
    .sub-title {
        color: #8892b0;
        font-size: 1rem;
        margin-top: -5px;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 1.2rem 1rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(247, 151, 30, 0.3);
        box-shadow: 0 12px 40px rgba(247, 151, 30, 0.1);
    }
    
    .metric-label {
        color: #8892b0;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 0;
    }
    
    .metric-value {
        color: #ffffff;
        font-size: 1.6rem;
        font-weight: 700;
        margin: 4px 0 0 0;
        letter-spacing: -0.5px;
    }
    
    .metric-change-positive {
        color: #00c853;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .metric-change-negative {
        color: #ff1744;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .metric-change-neutral {
        color: #8892b0;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    /* Crypto Card */
    .crypto-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.01) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 1rem;
        margin: 4px 0;
        transition: all 0.3s ease;
    }
    
    .crypto-card:hover {
        border-color: rgba(247, 151, 30, 0.2);
        background: rgba(255,255,255,0.06);
    }
    
    .crypto-symbol {
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: 700;
    }
    
    .crypto-name {
        color: #8892b0;
        font-size: 0.75rem;
    }
    
    .crypto-price {
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 4px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
        background: transparent;
        color: #8892b0;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
        color: #0a0e1a !important;
        font-weight: 600;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
        color: #0a0e1a;
        font-weight: 600;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1.2rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(247, 151, 30, 0.3);
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
    }
    
    /* Slider */
    .stSlider > div > div {
        color: #f7971e !important;
    }
    
    /* Headers */
    .section-header {
        color: #ffffff;
        font-size: 1.3rem;
        font-weight: 600;
        margin: 1rem 0 0.5rem 0;
        letter-spacing: -0.3px;
    }
    
    /* Dataframe */
    .stDataFrame {
        background: rgba(255,255,255,0.02) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: rgba(10, 14, 26, 0.95) !important;
    }
    
    /* Welcome text */
    .welcome-text {
        color: #8892b0;
        font-size: 0.9rem;
    }
    
    .highlight {
        color: #f7971e;
        font-weight: 600;
    }
    
    /* Status indicator */
    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #00c853;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.3; }
        100% { opacity: 1; }
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.02);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #f7971e, #ffd200);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "token" not in st.session_state:
        st.session_state.token = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = datetime.now()


def login(username: str, password: str) -> bool:
    """Authenticate user with the API."""
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"username": username, "password": password},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            st.session_state.username = username
            st.session_state.authenticated = True
            st.session_state.last_refresh = datetime.now()
            return True
        else:
            st.error("❌ Invalid username or password")
            return False
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API server. Please make sure it's running.")
        return False


def api_request(endpoint: str, params: dict = None) -> dict:
    """Make authenticated API request."""
    if not st.session_state.token:
        return None
    
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.get(
            f"{API_URL}{endpoint}",
            headers=headers,
            params=params,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception:
        return None


def fetch_latest_prices(limit: int = 50):
    """Fetch latest crypto prices."""
    return api_request(f"/prices/latest?limit={limit}")


def fetch_price_history(symbol: str, days: int = 7):
    """Fetch historical price data."""
    return api_request(f"/prices/history/{symbol}?days={days}")


def fetch_top_performers(limit: int = 10):
    """Fetch top performing cryptocurrencies."""
    return api_request(f"/prices/top?limit={limit}")


def create_professional_chart(history_data, symbol: str, days: int):
    """Create professional dark theme chart."""
    if not history_data:
        return None
    
    df = pd.DataFrame(history_data)
    df['last_updated'] = pd.to_datetime(df['last_updated'])
    df = df.sort_values('last_updated')
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.65, 0.35]
    )
    
    # Main price line with gradient fill
    fig.add_trace(
        go.Scatter(
            x=df['last_updated'],
            y=df['current_price'],
            mode='lines',
            name=symbol,
            line=dict(color='#ffd700', width=2.5),
            fill='tozeroy',
            fillcolor='rgba(255, 215, 0, 0.15)'
        ),
        row=1, col=1
    )
    
    # Moving averages
    if len(df) > 7:
        df['MA7'] = df['current_price'].rolling(window=7).mean()
        df['MA30'] = df['current_price'].rolling(window=30).mean()
        
        fig.add_trace(
            go.Scatter(
                x=df['last_updated'],
                y=df['MA7'],
                mode='lines',
                name='MA 7d',
                line=dict(color='#ff6b6b', width=1.5, dash='dash')
            ),
            row=1, col=1
        )
        
        if len(df) > 30:
            fig.add_trace(
                go.Scatter(
                    x=df['last_updated'],
                    y=df['MA30'],
                    mode='lines',
                    name='MA 30d',
                    line=dict(color='#4ecdc4', width=1.5, dash='dash')
                ),
                row=1, col=1
            )
    
    # Volume bars
    if 'total_volume' in df.columns:
        colors = ['#00c853' if change >= 0 else '#ff1744' 
                  for change in df['price_change_percentage_24h'].fillna(0)]
        
        fig.add_trace(
            go.Bar(
                x=df['last_updated'],
                y=df['total_volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.6
            ),
            row=2, col=1
        )
    
    # Professional dark layout
    fig.update_layout(
        title=dict(
            text=f"<b>{symbol}</b> Price History ({days} days)",
            font=dict(size=22, color='#ffffff'),
            x=0.5
        ),
        hovermode='x unified',
        template='plotly_dark',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color='#8892b0')
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=30, r=30, t=60, b=30)
    )
    
    # Axis styling
    fig.update_xaxes(
        gridcolor='rgba(255,255,255,0.05)',
        tickfont=dict(color='#8892b0'),
        title_font=dict(color='#8892b0')
    )
    fig.update_yaxes(
        gridcolor='rgba(255,255,255,0.05)',
        tickfont=dict(color='#8892b0'),
        title_font=dict(color='#8892b0'),
        row=1, col=1
    )
    fig.update_yaxes(
        gridcolor='rgba(255,255,255,0.05)',
        tickfont=dict(color='#8892b0'),
        row=2, col=1
    )
    
    return fig


def show_login_page():
    """Display the login page."""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style="text-align:center; padding: 2rem 0;">
                <h1 style="font-size:4rem; font-weight:800; background:linear-gradient(135deg,#f7971e,#ffd200); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                    📊 Crypto Intelligence
                </h1>
                <p style="color:#8892b0; font-size:1.2rem; margin-top:-10px;">
                    Enterprise-grade cryptocurrency market analytics
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown("""
                <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:16px; padding:2rem;">
                    <h3 style="color:#ffffff; text-align:center;">🔐 Secure Login</h3>
            """, unsafe_allow_html=True)
            
            username = st.text_input("Username", placeholder="Enter your username", key="login_username")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
            
            if st.button("🚀 Login", use_container_width=True, type="primary"):
                if username and password:
                    if login(username, password):
                        st.success("✅ Login successful!")
                        st.rerun()
                else:
                    st.warning("Please enter both username and password")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("""
            <div style="text-align:center; color:#8892b0; font-size:0.8rem;">
                <p>Demo Accounts</p>
                <code style="background:rgba(255,255,255,0.05); padding:4px 12px; border-radius:6px; margin:0 4px;">admin / Admin@123</code>
                <code style="background:rgba(255,255,255,0.05); padding:4px 12px; border-radius:6px; margin:0 4px;">analyst / Analyst@123</code>
                <code style="background:rgba(255,255,255,0.05); padding:4px 12px; border-radius:6px; margin:0 4px;">viewer / Viewer@123</code>
            </div>
        """, unsafe_allow_html=True)


def show_dashboard():
    """Main dashboard view."""
    # Header
    col1, col2, col3, col4 = st.columns([2.5, 1, 1, 0.8])
    with col1:
        st.markdown("""
            <div>
                <h1 style="font-size:2rem; font-weight:800; background:linear-gradient(135deg,#f7971e,#ffd200); -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin:0;">
                    📊 Crypto Dashboard
                </h1>
                <p style="color:#8892b0; margin:0; font-size:0.85rem;">
                    <span class="status-dot" style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#00c853; animation:pulse 2s infinite; vertical-align:middle; margin-right:6px;"></span>
                    Live | Welcome, <span style="color:#f7971e;">{}</span>
                </p>
            </div>
        """.format(st.session_state.username), unsafe_allow_html=True)
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    with col3:
        if st.button("⏱️ Auto", use_container_width=True):
            st.info("Auto-refresh every 60s")
    with col4:
        if st.button("🚪", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.token = None
            st.rerun()
    
    st.markdown("---")
    
    # Fetch data
    with st.spinner("Loading market data..."):
        prices = fetch_latest_prices(30)
    
    if not prices:
        st.error("❌ Unable to fetch data. Please make sure the API server is running.")
        return
    
    df = pd.DataFrame(prices)
    
    # ============================================================================
    # METRIC CARDS
    # ============================================================================
    col1, col2, col3, col4, col5 = st.columns(5)
    
    btc = df[df['symbol'] == 'BTC']
    eth = df[df['symbol'] == 'ETH']
    
    total_mcap = df['market_cap'].sum()
    total_volume = df['total_volume'].sum()
    avg_change = df['price_change_percentage_24h'].mean()
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <p class="metric-label">💰 Total Market Cap</p>
                <p class="metric-value">${total_mcap/1e12:.2f}T</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <p class="metric-label">📊 24h Volume</p>
                <p class="metric-value">${total_volume/1e9:.2f}B</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        change_class = "metric-change-positive" if avg_change >= 0 else "metric-change-negative"
        arrow = "▲" if avg_change >= 0 else "▼"
        st.markdown(f"""
            <div class="metric-card">
                <p class="metric-label">📈 Avg 24h Change</p>
                <p class="metric-value">{avg_change:.2f}%</p>
                <p class="{change_class}">{arrow} {abs(avg_change):.2f}%</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if not btc.empty:
            btc_price = btc.iloc[0]['current_price']
            st.markdown(f"""
                <div class="metric-card">
                    <p class="metric-label">₿ Bitcoin</p>
                    <p class="metric-value">${btc_price:,.2f}</p>
                </div>
            """, unsafe_allow_html=True)
    
    with col5:
        if not eth.empty:
            eth_price = eth.iloc[0]['current_price']
            st.markdown(f"""
                <div class="metric-card">
                    <p class="metric-label">⟠ Ethereum</p>
                    <p class="metric-value">${eth_price:,.2f}</p>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ============================================================================
    # TABS
    # ============================================================================
    tab1, tab2, tab3 = st.tabs(["📈 Price Chart", "🏦 All Cryptos", "🚀 Top Performers"])
    
    with tab1:
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown('<p style="color:#8892b0; font-size:0.8rem; font-weight:600;">Select Cryptocurrency</p>', unsafe_allow_html=True)
            symbols = df['symbol'].unique().tolist()
            selected_symbol = st.selectbox("", symbols, index=0, label_visibility="collapsed")
            
            st.markdown('<p style="color:#8892b0; font-size:0.8rem; font-weight:600; margin-top:10px;">Days of History</p>', unsafe_allow_html=True)
            days = st.slider("", 1, 30, 7, label_visibility="collapsed")
            
            if st.button("📊 Update Chart", use_container_width=True):
                pass
        
        with col2:
            with st.spinner(f"Loading {selected_symbol} data..."):
                history = fetch_price_history(selected_symbol, days)
            
            if history:
                fig = create_professional_chart(history, selected_symbol, days)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No data available")
            else:
                st.info("ℹ️ Not enough historical data. Please run the ingestion script.")
    
    with tab2:
        st.markdown('<p class="section-header">🏦 All Cryptocurrencies</p>', unsafe_allow_html=True)
        
        table_df = df[['symbol', 'name', 'current_price', 'price_change_percentage_24h', 'market_cap']].head(20).copy()
        table_df.columns = ['Symbol', 'Name', 'Price (USD)', '24h Change', 'Market Cap']
        table_df['Price (USD)'] = table_df['Price (USD)'].apply(lambda x: f"${x:,.2f}")
        table_df['Market Cap'] = table_df['Market Cap'].apply(lambda x: f"${x/1e9:.2f}B")
        table_df['24h Change'] = table_df['24h Change'].apply(lambda x: f"{x:.2f}%")
        
        # Color code changes
        def color_change(val):
            if isinstance(val, str) and '%' in val:
                try:
                    num = float(val.replace('%', ''))
                    return 'color: #00c853' if num > 0 else 'color: #ff1744' if num < 0 else 'color: #8892b0'
                except:
                    return ''
            return ''
        
        styled = table_df.style.applymap(color_change, subset=['24h Change'])
        styled = styled.set_properties(**{'text-align': 'center'})
        
        st.dataframe(
            styled,
            use_container_width=True,
            height=400
        )
    
    with tab3:
        st.markdown('<p class="section-header">🚀 Top Performers (24h)</p>', unsafe_allow_html=True)
        
        top_df = df.nlargest(10, 'price_change_percentage_24h')
        cols = st.columns(min(5, len(top_df)))
        
        for i, (idx, row) in enumerate(top_df.iterrows()):
            if i >= len(cols):
                break
            with cols[i % len(cols)]:
                change = row['price_change_percentage_24h']
                color = "#00c853" if change > 0 else "#ff1744" if change < 0 else "#8892b0"
                arrow = "⬆" if change > 0 else "⬇" if change < 0 else "➡"
                
                st.markdown(f"""
                    <div style="text-align:center;padding:15px;border-radius:12px;
                                background:rgba(255,255,255,0.03);
                                border:1px solid rgba(255,255,255,0.06);
                                margin:5px;">
                        <h3 style="color:#ffffff;margin:0;">{row['symbol']}</h3>
                        <p style="color:#8892b0;font-size:0.7rem;margin:0;">{row['name']}</p>
                        <p style="color:#ffffff;font-size:1.1rem;font-weight:600;margin:5px 0;">
                            ${row['current_price']:,.2f}
                        </p>
                        <p style="color:{color};font-weight:bold;font-size:1rem;">
                            {arrow} {change:.2f}%
                        </p>
                        <p style="color:#8892b0;font-size:0.7rem;margin:0;">
                            ${row['market_cap']/1e9:.2f}B
                        </p>
                    </div>
                """, unsafe_allow_html=True)


def main():
    """Main application entry point."""
    init_session_state()
    
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_dashboard()


if __name__ == "__main__":
    main()