import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf

from data_fetcher import DataFetcher
from technical_analysis import TechnicalAnalysis
from decision_engine import DecisionEngine
from chart_generator import ChartGenerator
from sector_analysis import SectorAnalysis
from pattern_recognition import PatternRecognition
from financial_data import FinancialData
from options_analysis import OptionsAnalysis
from enhanced_analysis import EnhancedAnalysis
from alert_system import AlertSystem
from indicator_explanations import get_indicator_explanation, format_explanation_for_display
from market_overview import MarketOverview
from financial_wellness import FinancialWellnessAnalyzer
from youtube_integration import YouTubeVideoFetcher
from stock_groups_cache import StockGroupsCache

# Page configuration
st.set_page_config(
    page_title="BeatTheMarket - Stock Analysis Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Mobile-friendly CSS
st.markdown("""
<style>
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 12px;
            padding: 4px 8px;
        }
        .metric-container {
            flex-direction: column;
            align-items: stretch;
        }
    }
    
    /* Enhanced styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    
    .indicator-signal {
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
        font-weight: bold;
    }
    
    .signal-buy { background-color: #28a745; color: white; }
    .signal-sell { background-color: #dc3545; color: white; }
    .signal-hold { background-color: #6c757d; color: white; }
    
    .news-sentiment-positive { border-left: 4px solid #28a745; }
    .news-sentiment-negative { border-left: 4px solid #dc3545; }
    .news-sentiment-neutral { border-left: 4px solid #6c757d; }
    
    /* Light sea blue button styling */
    .stButton > button {
        background-color: #87CEEB !important;
        color: #1e3a8a !important;
        border: 1px solid #5fb3d1 !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
    }
    
    .stButton > button:hover {
        background-color: #6bb6d6 !important;
        border: 1px solid #4a9cc4 !important;
        color: #1e3a8a !important;
    }
    
    .stButton > button:focus {
        background-color: #6bb6d6 !important;
        border: 1px solid #4a9cc4 !important;
        color: #1e3a8a !important;
        box-shadow: 0 0 0 0.2rem rgba(135, 206, 235, 0.5) !important;
    }
</style>
""", unsafe_allow_html=True)

def display_welcome_videos_section():
    """Display trading training videos in the welcome area"""
    st.markdown("### 📺 Trading Education Videos")
    
    # Create 2x2 grid for videos
    video_col1, video_col2 = st.columns(2)
    
    with video_col1:
        st.markdown("**📊 Stock Analysis Fundamentals**")
        st.video("https://www.youtube.com/watch?v=p7HKvqRI_Bo")
        
        st.markdown("**📈 Technical Analysis Basics**")
        st.video("https://www.youtube.com/watch?v=08c1Nb8j1Sw")
    
    with video_col2:
        st.markdown("**💹 Day Trading Strategies**")
        st.video("https://www.youtube.com/watch?v=lzYWKoNVsno")
        
        st.markdown("**⚡ Options Trading Explained**")
        st.video("https://www.youtube.com/watch?v=7PM4rNDr4oI")
    
    # Additional video row
    video_col3, video_col4 = st.columns(2)
    
    with video_col3:
        st.markdown("**🎯 Risk Management**")
        st.video("https://www.youtube.com/watch?v=OYq2tD6psxM")
    
    with video_col4:
        st.markdown("**📊 Reading Financial Statements**")
        st.video("https://www.youtube.com/watch?v=nIRGOz9jL5k")

def main():

    
    # Initialize session state
    if 'analysis_data' not in st.session_state:
        st.session_state.analysis_data = None
    if 'last_symbol' not in st.session_state:
        st.session_state.last_symbol = None
    if 'sector_data' not in st.session_state:
        st.session_state.sector_data = None
    if 'pattern_data' not in st.session_state:
        st.session_state.pattern_data = None
    if 'financial_data' not in st.session_state:
        st.session_state.financial_data = None
    if 'news_data' not in st.session_state:
        st.session_state.news_data = None
    if 'options_data' not in st.session_state:
        st.session_state.options_data = None
    if 'enhanced_data' not in st.session_state:
        st.session_state.enhanced_data = None
    
    # Header with modern, newcomer-friendly design
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');
    
    @keyframes glow {
        0% { text-shadow: 0 0 10px #ff6b6b; }
        50% { text-shadow: 0 0 20px #ffa500, 0 0 30px #32cd32; }
        100% { text-shadow: 0 0 10px #ff6b6b; }
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }
    
    .welcome-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        border-radius: 25px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }
    
    .modern-header {
        font-size: 1.4rem;
        font-weight: 800;
        text-transform: uppercase;
        color: white;
        letter-spacing: 1px;
        font-family: 'Poppins', sans-serif;
        line-height: 1.2;
        font-style: italic;
        animation: glow 3s ease-in-out infinite alternate;
        margin-bottom: 0.5rem;
    }
    
    .blinking-subtitle {
        display: block;
        font-size: 0.8rem;
        color: #ffff99;
        font-weight: 600;
        animation: bounce 2s infinite;
        margin-top: 0.5rem;
        font-family: 'Poppins', sans-serif;
    }
    
    .newcomer-badge {
        background: linear-gradient(45deg, #ff6b6b, #ffa500);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-size: 0.7rem;
        font-weight: 600;
        margin-top: 1rem;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-family: 'Poppins', sans-serif;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
    }
    </style>
    <div class="welcome-container">
        <div class="modern-header">
            🚀 BEATTHEMARKET
        </div>
        <div class="blinking-subtitle">SMART STOCK ANALYSIS</div>
        <div class="newcomer-badge">✨ Perfect for Trading Beginners ✨</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Streamlined input layout
    with st.container():
        pass  # Dropdown feature disabled for this release
        
        # Stock symbols input with analyze button
        symbols_col, analyze_col = st.columns([3, 1])
        
        with symbols_col:
            if 'symbols_input' not in st.session_state:
                st.session_state.symbols_input = ""
            
            symbols_input = st.text_input(
                "Stock Symbols", 
                value=st.session_state.symbols_input, 
                placeholder="Type your ticker(s) with comma separator",
                help="Enter up to 5 stock symbols separated by commas. Press Enter to analyze immediately.",
                on_change=lambda: setattr(st.session_state, 'analyze_trigger', True),
                label_visibility="collapsed"
            )
            st.session_state.symbols_input = symbols_input
        
        with analyze_col:
            st.write("")  # Spacing for alignment
            analyze_button = st.button("🔍 Analyze", type="primary", use_container_width=True)
            
            # Check if analysis was triggered by Enter key in text input
            if st.session_state.get('analyze_trigger', False):
                analyze_button = True
                st.session_state.analyze_trigger = False
    
    # Parse symbols first
    symbols_list = [s.strip().upper() for s in symbols_input.split(',') if s.strip()]
    symbols_list = symbols_list[:10]
    
    # Technical Analysis Parameters (collapsible)
    with st.expander("⚙️ Advanced Technical Analysis Settings", expanded=False):
        col_tech1, col_tech2, col_tech3, col_tech4 = st.columns(4)
        
        with col_tech1:
            st.markdown("**Analysis Settings**")
            period_options = {"1M": "1mo", "3M": "3mo", "6M": "6mo", "1Y": "1y", "2Y": "2y"}
            selected_period = st.selectbox("Time Period", list(period_options.keys()), index=3, key="period_advanced")
            period = period_options[selected_period]
            analysis_mode = st.selectbox("Analysis Mode", ["Individual", "Comparison"], key="mode_advanced")
        
        with col_tech2:
            st.markdown("**Moving Averages**")
            sma_period = st.number_input("SMA Period", min_value=5, max_value=200, value=20)
            ema_period = st.number_input("EMA Period", min_value=5, max_value=200, value=20)
        
        with col_tech3:
            st.markdown("**Oscillators**")
            rsi_period = st.number_input("RSI Period", min_value=5, max_value=50, value=14)
            bb_period = st.number_input("Bollinger Bands Period", min_value=5, max_value=50, value=20)
        
        with col_tech4:
            st.markdown("**Volatility & Risk**")
            bb_std = st.number_input("Bollinger Bands Std Dev", min_value=1.0, max_value=3.0, value=2.0, step=0.1)
            atr_period = st.number_input("ATR Period", min_value=5, max_value=50, value=14)
    
    # Handle bulk watchlist
    if st.session_state.get('bulk_watchlist'):
        if isinstance(st.session_state.bulk_watchlist, list):
            st.info(f"💡 Navigate to the 🚨 Alerts tab to add {', '.join(st.session_state.bulk_watchlist)} to your watchlist!")
        else:
            st.info("💡 Navigate to the 🚨 Alerts tab to add stocks to your watchlist!")
        st.session_state.bulk_watchlist = None
    
    # Analysis Results Section (moved after advanced settings)
    # Handle comparison mode
    if analysis_mode == "Comparison" and len(symbols_list) > 1:
        display_stock_comparison(symbols_list, period)
        st.stop()
    
    # Set symbol for single stock mode or first stock for compatibility
    symbol = symbols_list[0] if symbols_list else "AAPL"
    
    # Main content area - Handle multiple stocks
    if analyze_button:
        if len(symbols_list) == 1:
            # Single stock analysis (existing detailed analysis)
            symbol = symbols_list[0]
            with st.spinner(f"Analyzing {symbol}..."):
                try:
                    # Fetch data
                    data_fetcher = DataFetcher()
                    stock_data = data_fetcher.fetch_stock_data(symbol, period)
                    
                    if stock_data is None or stock_data.empty:
                        st.error(f"No data found for symbol '{symbol}'. Please check the symbol and try again.")
                        return
                    
                    # Perform technical analysis
                    ta = TechnicalAnalysis()
                    analysis_results = ta.calculate_all_indicators(
                        stock_data,
                        sma_period=sma_period,
                        ema_period=ema_period,
                        rsi_period=rsi_period,
                        bb_period=bb_period,
                        bb_std=int(bb_std),
                        atr_period=atr_period
                    )
                    
                    # Generate trading decision
                    decision_engine = DecisionEngine()
                    decision_data = decision_engine.generate_decision(analysis_results)
                    
                    # Perform sector analysis
                    sector_analyzer = SectorAnalysis()
                    sector_comparison = sector_analyzer.get_sector_comparison_data(symbol, period)
                    
                    # Perform pattern recognition
                    pattern_analyzer = PatternRecognition()
                    pattern_analysis = pattern_analyzer.analyze_all_patterns(stock_data)
                    
                    # Get financial data and news
                    financial_analyzer = FinancialData()
                    comprehensive_metrics = financial_analyzer.get_comprehensive_metrics(symbol)
                    financial_statements = financial_analyzer.get_financial_statements(symbol)
                    latest_news = financial_analyzer.get_latest_news(symbol)
                    news_sentiment = financial_analyzer.analyze_news_sentiment(latest_news)
                    
                    # Get options analysis
                    try:
                        options_analyzer = OptionsAnalysis()
                        volatility = analysis_results['Volatility'].iloc[-1] if analysis_results is not None and 'Volatility' in analysis_results.columns else 0.2
                        options_strategies = options_analyzer.analyze_option_strategies(symbol, stock_data['Close'].iloc[-1], volatility)
                        profitable_strikes = options_analyzer.get_profitable_strikes(symbol, stock_data['Close'].iloc[-1], volatility)
                    except Exception as e:
                        st.warning(f"Options analysis unavailable: {str(e)}")
                        options_strategies = None
                        profitable_strikes = None
                    
                    # Get enhanced analysis
                    try:
                        enhanced_analyzer = EnhancedAnalysis()
                        stock_info = yf.Ticker(symbol).info
                        sector = stock_info.get('sector', 'Unknown')
                        index_comparison = enhanced_analyzer.get_index_comparison(symbol, period)
                        sector_comparison_enhanced = enhanced_analyzer.get_sector_comparison(symbol, sector, period)
                        individual_indicators = enhanced_analyzer.analyze_individual_indicators(analysis_results)
                        threshold_summary = enhanced_analyzer.generate_threshold_summary(individual_indicators)
                        analyst_recommendations = enhanced_analyzer.get_analyst_recommendations(symbol)
                    except Exception as e:
                        st.warning(f"Enhanced analysis partially unavailable: {str(e)}")
                        index_comparison = None
                        sector_comparison_enhanced = None
                        individual_indicators = None
                        threshold_summary = None
                        analyst_recommendations = None
                    
                    # Store in session state
                    st.session_state.analysis_data = {
                        'stock_data': stock_data,
                        'analysis_results': analysis_results,
                        'analysis_data': analysis_results,  # Include technical analysis data
                        'decision_data': decision_data,
                        'symbol': symbol,
                        'current_price': stock_data['Close'].iloc[-1],
                        'last_update': datetime.now()
                    }
                    st.session_state.sector_data = sector_comparison
                    st.session_state.pattern_data = pattern_analysis
                    st.session_state.financial_data = {
                        'metrics': comprehensive_metrics,
                        'statements': financial_statements
                    }
                    st.session_state.news_data = {
                        'news': latest_news,
                        'sentiment': news_sentiment
                    }
                    st.session_state.options_data = {
                        'strategies': options_strategies,
                        'profitable_strikes': profitable_strikes
                    }
                    st.session_state.enhanced_data = {
                        'index_comparison': index_comparison,
                        'sector_comparison': sector_comparison_enhanced,
                        'individual_indicators': individual_indicators,
                        'threshold_summary': threshold_summary,
                        'analyst_recommendations': analyst_recommendations
                    }
                    
                    # Generate financial wellness report
                    try:
                        wellness_analyzer = FinancialWellnessAnalyzer()
                        wellness_report = wellness_analyzer.generate_wellness_report(
                            symbol, stock_data, analysis_results, decision_data,
                            st.session_state.financial_data, st.session_state.sector_data,
                            st.session_state.options_data, st.session_state.news_data
                        )
                        st.session_state.wellness_report = wellness_report
                    except Exception as e:
                        st.warning("Wellness report temporarily unavailable")
                        st.session_state.wellness_report = None
                    
                    # Fetch relevant YouTube videos
                    try:
                        youtube_fetcher = YouTubeVideoFetcher()
                        indicators_used = ['RSI', 'MACD', 'SMA', 'EMA', 'Bollinger Bands']
                        video_categories = youtube_fetcher.get_video_categories(symbol, indicators_used)
                        st.session_state.youtube_videos = video_categories
                    except Exception as e:
                        st.session_state.youtube_videos = {
                            'stock_analysis': [],
                            'technical_indicators': [],
                            'general_education': []
                        }
                    st.session_state.last_symbol = symbol
                    
                except Exception as e:
                    st.error(f"Error analyzing stock: {str(e)}")
                    return
        
            # Display single stock analysis
            if st.session_state.analysis_data:
                display_enhanced_dashboard()
                
        else:
            # Multiple stocks analysis
            display_multi_stock_analysis(symbols_list, period, sma_period, ema_period, rsi_period, bb_period, int(bb_std), atr_period)
    else:
        # Welcome message
        st.markdown("""
        #### 🎯 Start Your Trading Journey Here!
        
        This platform provides comprehensive technical analysis for stocks using data from Yahoo Finance.
        
        **Features:**
        - Real-time stock data from Yahoo Finance
        - Technical indicators: SMA, EMA, RSI, MACD, Bollinger Bands, ATR
        - Fibonacci retracement levels
        - Support and resistance identification
        - Automated buy/hold/sell recommendations
        - Interactive charts with technical overlays
        
        **How to use:**
        1. Enter a stock symbol in the sidebar (e.g., AAPL, GOOGL, TSLA)
        2. Select your preferred time period
        3. Adjust technical analysis parameters if needed
        4. Click "Analyze Stock" to get started
        """)
        
        # Educational Trading Videos Section
        st.markdown("---")
        st.markdown("### 📚 Trading Education & Market Analytics Videos")
        
        # Fetch educational videos using YouTube API
        try:
            from youtube_integration import YouTubeVideoFetcher
            import os
            
            youtube_fetcher = YouTubeVideoFetcher()
            
            # Check if API key is available
            if not youtube_fetcher.api_key:
                st.warning("YouTube API key not configured. Educational videos unavailable.")
                return
            
            # Search for educational trading content using available methods
            educational_videos = []
            
            # Get general trading videos
            try:
                trading_videos = youtube_fetcher.search_general_trading_videos(max_results=4)
                if trading_videos:
                    educational_videos.extend(trading_videos)
            except Exception as e:
                pass
            
            # Get technical indicator videos
            try:
                indicators = ['RSI', 'MACD', 'Moving Averages', 'Bollinger Bands']
                indicator_videos = youtube_fetcher.search_technical_indicator_videos(indicators, max_results=4)
                if indicator_videos:
                    educational_videos.extend(indicator_videos)
            except Exception as e:
                pass
            
            if educational_videos and len(educational_videos) >= 6:
                # Create 4x2 grid for educational videos
                col1, col2, col3, col4 = st.columns(4)
                
                # First row
                with col1:
                    if len(educational_videos) > 0:
                        video = educational_videos[0]
                        st.markdown(f"<small>**📊 {video.get('title', 'Technical Analysis')[:20]}...**</small>", unsafe_allow_html=True)
                        st.video(f"https://www.youtube.com/watch?v={video['video_id']}")
                
                with col2:
                    if len(educational_videos) > 1:
                        video = educational_videos[1]
                        st.markdown(f"<small>**📈 {video.get('title', 'RSI Strategy')[:20]}...**</small>", unsafe_allow_html=True)
                        st.video(f"https://www.youtube.com/watch?v={video['video_id']}")
                
                with col3:
                    if len(educational_videos) > 2:
                        video = educational_videos[2]
                        st.markdown(f"<small>**💹 {video.get('title', 'MACD Guide')[:20]}...**</small>", unsafe_allow_html=True)
                        st.video(f"https://www.youtube.com/watch?v={video['video_id']}")
                
                with col4:
                    if len(educational_videos) > 3:
                        video = educational_videos[3]
                        st.markdown(f"<small>**⚡ {video.get('title', 'Moving Averages')[:20]}...**</small>", unsafe_allow_html=True)
                        st.video(f"https://www.youtube.com/watch?v={video['video_id']}")
                
                # Second row
                col5, col6, col7, col8 = st.columns(4)
                
                with col5:
                    if len(educational_videos) > 4:
                        video = educational_videos[4]
                        st.markdown(f"<small>**🎯 {video.get('title', 'Support & Resistance')[:20]}...**</small>", unsafe_allow_html=True)
                        st.video(f"https://www.youtube.com/watch?v={video['video_id']}")
                
                with col6:
                    if len(educational_videos) > 5:
                        video = educational_videos[5]
                        st.markdown(f"<small>**📰 {video.get('title', 'Risk Management')[:20]}...**</small>", unsafe_allow_html=True)
                        st.video(f"https://www.youtube.com/watch?v={video['video_id']}")
                
                with col7:
                    if len(educational_videos) > 6:
                        video = educational_videos[6]
                        st.markdown(f"<small>**💼 {video.get('title', 'Chart Patterns')[:20]}...**</small>", unsafe_allow_html=True)
                        st.video(f"https://www.youtube.com/watch?v={video['video_id']}")
                
                with col8:
                    if len(educational_videos) > 7:
                        video = educational_videos[7]
                        st.markdown(f"<small>**🔍 {video.get('title', 'Trading Strategy')[:20]}...**</small>", unsafe_allow_html=True)
                        st.video(f"https://www.youtube.com/watch?v={video['video_id']}")
            else:
                st.info("Loading educational videos...")
                
        except Exception as e:
            st.warning("Educational videos temporarily unavailable. Please check your connection.")

def display_sector_comparison():
    """Display sector comparison and similar performers analysis"""
    sector_data = st.session_state.sector_data
    
    if not sector_data:
        return
    
    st.subheader("🏢 Sector Analysis & Peer Comparison")
    
    # Sector Overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Sector Information")
        target_sector = sector_data.get('target_sector', 'Unknown')
        st.write(f"**Sector:** {target_sector}")
        
        target_metrics = sector_data.get('target_metrics', {})
        sector_averages = sector_data.get('sector_averages', {})
        
        if target_metrics and sector_averages:
            st.write(f"**Your Stock Return:** {target_metrics.get('total_return', 0):.2f}%")
            st.write(f"**Sector Average Return:** {sector_averages.get('avg_return', 0):.2f}%")
            
            # Performance vs sector
            performance_diff = target_metrics.get('total_return', 0) - sector_averages.get('avg_return', 0)
            if performance_diff > 0:
                st.success(f"✅ Outperforming sector by {performance_diff:.2f}%")
            else:
                st.warning(f"⚠️ Underperforming sector by {abs(performance_diff):.2f}%")
    
    with col2:
        st.markdown("### Risk Metrics")
        if target_metrics:
            st.write(f"**Volatility:** {target_metrics.get('volatility', 0):.2f}%")
            st.write(f"**Sharpe Ratio:** {target_metrics.get('sharpe_ratio', 0):.2f}")
            st.write(f"**Max Drawdown:** {target_metrics.get('max_drawdown', 0):.2f}%")
    
    # Top 5 Sector Peers
    st.markdown("### 📊 Top 5 Sector Peers")
    sector_peers = sector_data.get('sector_peers', [])
    
    if sector_peers:
        peers_data = []
        for peer in sector_peers[:5]:
            peers_data.append({
                'Symbol': peer.get('symbol', ''),
                'Current Price': f"${peer.get('current_price', 0):.2f}",
                'Total Return': f"{peer.get('total_return', 0):.2f}%",
                'Volatility': f"{peer.get('volatility', 0):.2f}%",
                'Sharpe Ratio': f"{peer.get('sharpe_ratio', 0):.2f}"
            })
        
        peers_df = pd.DataFrame(peers_data)
        st.dataframe(peers_df, hide_index=True)
    else:
        st.info("No sector peer data available")
    
    # Similar Performers
    st.markdown("### 🔍 Stocks with Similar Performance")
    similar_performers = sector_data.get('similar_performers', [])
    
    if similar_performers:
        similar_data = []
        for stock in similar_performers[:10]:
            similar_data.append({
                'Symbol': stock.get('symbol', ''),
                'Current Price': f"${stock.get('current_price', 0):.2f}",
                'Total Return': f"{stock.get('total_return', 0):.2f}%",
                'Volatility': f"{stock.get('volatility', 0):.2f}%",
                'Sharpe Ratio': f"{stock.get('sharpe_ratio', 0):.2f}",
                'Similarity Score': f"{stock.get('similarity_score', 0):.3f}"
            })
        
        similar_df = pd.DataFrame(similar_data)
        st.dataframe(similar_df, hide_index=True)
        
        st.info("💡 **Similarity Score:** Lower values indicate more similar performance patterns (0.000 = identical)")
    else:
        st.info("No similar performers found")
    
    # Performance Comparison Chart
    st.markdown("### 📈 Performance Comparison Chart")
    
    if sector_peers and target_metrics:
        # Create comparison chart
        fig = go.Figure()
        
        # Add target stock
        fig.add_trace(go.Scatter(
            x=[target_metrics.get('volatility', 0)],
            y=[target_metrics.get('total_return', 0)],
            mode='markers',
            name=f"{sector_data.get('target_symbol', 'Target')} (You)",
            marker=dict(size=15, color='red', symbol='star'),
            text=[f"{sector_data.get('target_symbol', 'Target')}<br>Return: {target_metrics.get('total_return', 0):.2f}%<br>Volatility: {target_metrics.get('volatility', 0):.2f}%"],
            hovertemplate='%{text}<extra></extra>'
        ))
        
        # Add sector peers
        for peer in sector_peers[:5]:
            fig.add_trace(go.Scatter(
                x=[peer.get('volatility', 0)],
                y=[peer.get('total_return', 0)],
                mode='markers',
                name=f"{peer.get('symbol', 'Unknown')} (Peer)",
                marker=dict(size=12, color='blue'),
                text=[f"{peer.get('symbol', 'Unknown')}<br>Return: {peer.get('total_return', 0):.2f}%<br>Volatility: {peer.get('volatility', 0):.2f}%"],
                hovertemplate='%{text}<extra></extra>'
            ))
        
        # Add similar performers
        for stock in similar_performers[:5]:
            fig.add_trace(go.Scatter(
                x=[stock.get('volatility', 0)],
                y=[stock.get('total_return', 0)],
                mode='markers',
                name=f"{stock.get('symbol', 'Unknown')} (Similar)",
                marker=dict(size=10, color='green'),
                text=[f"{stock.get('symbol', 'Unknown')}<br>Return: {stock.get('total_return', 0):.2f}%<br>Volatility: {stock.get('volatility', 0):.2f}%"],
                hovertemplate='%{text}<extra></extra>'
            ))
        
        fig.update_layout(
            title='Risk vs Return Comparison',
            xaxis_title='Volatility (%)',
            yaxis_title='Total Return (%)',
            height=500,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)

def display_pattern_analysis():
    """Display chart pattern analysis"""
    pattern_data = st.session_state.pattern_data
    
    if not pattern_data:
        return
    
    st.subheader("📈 Chart Pattern Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Channels & Trends")
        channels = pattern_data.get('channels', {}).get('channels', [])
        if channels:
            for channel in channels:
                channel_type = channel['type'].replace('_', ' ').title()
                strength = channel.get('strength', 0)
                position = channel.get('current_position', {}).get('position_percent', 0)
                
                st.write(f"**{channel_type}**")
                st.write(f"• Strength: {strength:.2f}")
                st.write(f"• Current Position: {position:.1f}% within channel")
                st.write("---")
        else:
            st.info("No clear channel patterns detected")
        
        st.markdown("### 🔄 Double Patterns")
        double_patterns = pattern_data.get('double_patterns', [])
        if double_patterns:
            for pattern in double_patterns:
                pattern_type = pattern['type'].replace('_', ' ').title()
                target_price = pattern.get('target_price', 0)
                strength = pattern.get('strength', 0)
                
                st.write(f"**{pattern_type}**")
                st.write(f"• Strength: {strength:.2f}")
                st.write(f"• Target Price: ${target_price:.2f}")
                st.write("---")
        else:
            st.info("No double top/bottom patterns detected")
    
    with col2:
        st.markdown("### 👤 Head & Shoulders")
        head_shoulders = pattern_data.get('head_shoulders', [])
        if head_shoulders:
            for pattern in head_shoulders:
                target_price = pattern.get('target_price', 0)
                strength = pattern.get('strength', 0)
                neckline = pattern.get('neckline_price', 0)
                
                st.write(f"**Head & Shoulders Pattern**")
                st.write(f"• Strength: {strength:.2f}")
                st.write(f"• Neckline: ${neckline:.2f}")
                st.write(f"• Target Price: ${target_price:.2f}")
                st.write("---")
        else:
            st.info("No head & shoulders patterns detected")
        
        st.markdown("### 🔢 Multiple Tops/Bottoms")
        multiple_patterns = pattern_data.get('multiple_patterns', [])
        if multiple_patterns:
            for pattern in multiple_patterns:
                pattern_type = pattern['type'].replace('_', ' ').title()
                level = pattern.get('level', 0)
                touches = pattern.get('touches', 0)
                strength = pattern.get('strength', 0)
                
                st.write(f"**{pattern_type}**")
                st.write(f"• Level: ${level:.2f}")
                st.write(f"• Touches: {touches}")
                st.write(f"• Strength: {strength:.2f}")
                st.write("---")
        else:
            st.info("No multiple top/bottom patterns detected")

def display_comprehensive_metrics():
    """Display comprehensive financial metrics table"""
    financial_data = st.session_state.financial_data
    metrics = financial_data.get('metrics', {})
    
    if not metrics:
        return
    
    st.subheader("📊 Comprehensive Financial Metrics")
    
    # Add sector/industry P/E comparison
    symbol = metrics.get('symbol', '')
    st.write(f"Debug: Symbol = {symbol}")  # Debug line
    if symbol:
        try:
            from financial_data import FinancialData
            financial_data_obj = FinancialData()
            pe_comparison = financial_data_obj.get_sector_pe_comparison(symbol)
            st.write(f"Debug: PE comparison = {pe_comparison is not None}")  # Debug line
            
            if pe_comparison and pe_comparison.get('current_pe', 0) > 0:
                st.markdown("#### 🏭 Valuation vs Peers")
                pe_col1, pe_col2, pe_col3, pe_col4 = st.columns(4)
                
                with pe_col1:
                    current_pe = pe_comparison.get('current_pe', 0)
                    st.metric("Current P/E", f"{current_pe:.1f}" if current_pe > 0 else "N/A")
                
                with pe_col2:
                    sector_pe = pe_comparison.get('sector_pe', 0)
                    sector_name = pe_comparison.get('sector', 'Sector')
                    st.metric(f"{sector_name} Avg", f"{sector_pe:.1f}")
                
                with pe_col3:
                    vs_sector = pe_comparison.get('pe_vs_sector_pct', 0)
                    st.metric("vs Sector", f"{vs_sector:+.1f}%", 
                             delta_color="inverse" if vs_sector > 0 else "normal")
                
                with pe_col4:
                    assessment = pe_comparison.get('valuation_assessment', 'Unknown')
                    if "Overvalued" in assessment:
                        st.error(f"📈 {assessment}")
                    elif "Undervalued" in assessment:
                        st.success(f"📉 {assessment}")
                    else:
                        st.info(f"⚖️ {assessment}")
                
                # Industry comparison
                industry_col1, industry_col2 = st.columns(2)
                with industry_col1:
                    industry_name = pe_comparison.get('industry', 'Unknown')
                    st.write(f"**Industry:** {industry_name}")
                with industry_col2:
                    vs_industry = pe_comparison.get('pe_vs_industry_pct', 0)
                    st.write(f"**vs Industry Avg:** {vs_industry:+.1f}%")
        except Exception as e:
            st.write("Sector P/E comparison temporarily unavailable")
    
    st.markdown("---")
    
    # Create the comprehensive metrics table
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Market Data")
        market_data = {
            'Market Cap': f"${metrics.get('market_cap', 0)/1e9:.2f}B" if metrics.get('market_cap', 0) > 0 else "N/A",
            'P/E Ratio': f"{metrics.get('pe_ratio', 0):.2f}" if metrics.get('pe_ratio', 0) > 0 else "N/A",
            'Forward P/E': f"{metrics.get('forward_pe', 0):.2f}" if metrics.get('forward_pe', 0) > 0 else "N/A",
            'PEG Ratio': f"{metrics.get('peg_ratio', 0):.2f}" if metrics.get('peg_ratio', 0) > 0 else "N/A",
            'Price/Sales': f"{metrics.get('price_to_sales', 0):.2f}" if metrics.get('price_to_sales', 0) > 0 else "N/A",
            'Price/Book': f"{metrics.get('price_to_book', 0):.2f}" if metrics.get('price_to_book', 0) > 0 else "N/A",
            'Beta': f"{metrics.get('beta', 0):.2f}" if metrics.get('beta', 0) > 0 else "N/A",
            'Shares Outstanding': f"{metrics.get('shares_outstanding', 0)/1e6:.1f}M" if metrics.get('shares_outstanding', 0) > 0 else "N/A"
        }
        
        for key, value in market_data.items():
            st.write(f"**{key}:** {value}")
    
    with col2:
        st.markdown("### Performance")
        performance_data = {
            'Week': f"{metrics.get('perf_week', 0):.2f}%" if metrics.get('perf_week') is not None else "N/A",
            'Month': f"{metrics.get('perf_month', 0):.2f}%" if metrics.get('perf_month') is not None else "N/A",
            'Quarter': f"{metrics.get('perf_quarter', 0):.2f}%" if metrics.get('perf_quarter') is not None else "N/A",
            'Half Year': f"{metrics.get('perf_half_year', 0):.2f}%" if metrics.get('perf_half_year') is not None else "N/A",
            'Year': f"{metrics.get('perf_year', 0):.2f}%" if metrics.get('perf_year') is not None else "N/A",
            'YTD': f"{metrics.get('perf_ytd', 0):.2f}%" if metrics.get('perf_ytd') is not None else "N/A",
            '52W High': f"{metrics.get('fifty_two_week_high_percent', 0):.2f}%" if metrics.get('fifty_two_week_high_percent') is not None else "N/A",
            '52W Low': f"{metrics.get('fifty_two_week_low_percent', 0):.2f}%" if metrics.get('fifty_two_week_low_percent') is not None else "N/A"
        }
        
        for key, value in performance_data.items():
            st.write(f"**{key}:** {value}")
    
    with col3:
        st.markdown("### Technical & Other")
        technical_data = {
            'RSI (14)': f"{metrics.get('rsi_14', 0):.2f}" if metrics.get('rsi_14', 0) > 0 else "N/A",
            'ATR (14)': f"{metrics.get('atr_14', 0):.2f}" if metrics.get('atr_14', 0) > 0 else "N/A",
            'SMA20': f"{metrics.get('sma_20', 0):.2f}%" if metrics.get('sma_20') is not None else "N/A",
            'SMA50': f"{metrics.get('sma_50', 0):.2f}%" if metrics.get('sma_50') is not None else "N/A",
            'SMA200': f"{metrics.get('sma_200', 0):.2f}%" if metrics.get('sma_200') is not None else "N/A",
            'Short Float': f"{metrics.get('short_float', 0):.2f}%" if metrics.get('short_float', 0) > 0 else "N/A",
            'Target Price': f"${metrics.get('target_price', 0):.2f}" if metrics.get('target_price', 0) > 0 else "N/A",
            'Recommendation': f"{metrics.get('recommendation', 0):.2f}" if metrics.get('recommendation', 0) > 0 else "N/A"
        }
        
        for key, value in technical_data.items():
            st.write(f"**{key}:** {value}")

def display_financial_statements():
    """Display financial statements"""
    financial_data = st.session_state.financial_data
    statements = financial_data.get('statements', {})
    
    if not statements:
        return
    
    st.subheader("📋 Financial Statements")
    
    tab1, tab2, tab3 = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow"])
    
    with tab1:
        st.markdown("### Income Statement")
        income_annual = statements.get('income_statement', {}).get('annual')
        if income_annual is not None and not income_annual.empty:
            st.dataframe(income_annual.head(10))  # Show top 10 rows
        else:
            st.info("Income statement data not available")
    
    with tab2:
        st.markdown("### Balance Sheet")
        balance_annual = statements.get('balance_sheet', {}).get('annual')
        if balance_annual is not None and not balance_annual.empty:
            st.dataframe(balance_annual.head(10))  # Show top 10 rows
        else:
            st.info("Balance sheet data not available")
    
    with tab3:
        st.markdown("### Cash Flow Statement")
        cashflow_annual = statements.get('cash_flow', {}).get('annual')
        if cashflow_annual is not None and not cashflow_annual.empty:
            st.dataframe(cashflow_annual.head(10))  # Show top 10 rows
        else:
            st.info("Cash flow statement data not available")

def display_news_analysis():
    """Display news and sentiment analysis"""
    news_data = st.session_state.news_data
    
    if not news_data:
        return
    
    st.subheader("📰 Latest News & Sentiment Analysis")
    
    # Sentiment Summary
    sentiment = news_data.get('sentiment', {})
    news_items = news_data.get('news', [])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sentiment_label = sentiment.get('sentiment', 'neutral').title()
        sentiment_score = sentiment.get('score', 0)
        
        if sentiment_label == 'Positive':
            st.success(f"📈 **News Sentiment: {sentiment_label}**")
        elif sentiment_label == 'Negative':
            st.error(f"📉 **News Sentiment: {sentiment_label}**")
        else:
            st.info(f"📊 **News Sentiment: {sentiment_label}**")
        
        st.write(f"Score: {sentiment_score:.2f}")
    
    with col2:
        positive_mentions = sentiment.get('positive_mentions', 0)
        negative_mentions = sentiment.get('negative_mentions', 0)
        st.metric("Positive Keywords", positive_mentions)
        st.metric("Negative Keywords", negative_mentions)
    
    with col3:
        total_news = sentiment.get('total_news', 0)
        st.metric("Total News Items", total_news)
    
    # News Items
    st.markdown("### Recent News")
    if news_items:
        for i, news in enumerate(news_items[:5]):  # Show top 5 news items
            with st.expander(f"📰 {news.get('title', 'No title')[:80]}..."):
                st.write(f"**Publisher:** {news.get('publisher', 'Unknown')}")
                st.write(f"**Published:** {news.get('published', 'Unknown')}")
                st.write(f"**Summary:** {news.get('summary', 'No summary available')}")
                if news.get('link'):
                    st.markdown(f"[Read Full Article]({news.get('link')})")
    else:
        st.info("No recent news available")

def display_analysis_results():
    data = st.session_state.analysis_data
    
    # Header with current price and last update
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label=f"{data['symbol']} Current Price",
            value=f"${data['current_price']:.2f}",
            delta=f"{((data['current_price'] / data['stock_data']['Close'].iloc[-2] - 1) * 100):.2f}%"
        )
    
    with col2:
        decision = data['decision_data']['decision']
        confidence = data['decision_data']['confidence']
        
        # Color coding for decision
        if decision == 'BUY':
            delta_color = "normal"
        elif decision == 'SELL':
            delta_color = "inverse"
        else:
            delta_color = "off"
        
        st.metric(
            label="Trading Decision",
            value=decision,
            delta=f"Confidence: {confidence:.0f}%"
        )
    
    with col3:
        rsi_value = data['analysis_results']['RSI'].iloc[-1]
        rsi_signal = "Oversold" if rsi_value < 30 else "Overbought" if rsi_value > 70 else "Neutral"
        st.metric(
            label="RSI (14)",
            value=f"{rsi_value:.1f}",
            delta=rsi_signal
        )
    
    with col4:
        st.metric(
            label="Last Updated",
            value=data['last_update'].strftime("%H:%M:%S"),
            delta=data['last_update'].strftime("%Y-%m-%d")
        )
    
    # Refresh button
    if st.button("🔄 Refresh Data"):
        st.rerun()
    
    # Main chart
    st.subheader("📊 Price Chart with Technical Indicators")
    
    chart_generator = ChartGenerator()
    fig = chart_generator.create_comprehensive_chart(
        data['stock_data'],
        data['analysis_results'],
        data['symbol']
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Technical Analysis Summary
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Technical Indicators Summary")
        
        # Create a summary table
        indicators_data = {
            'Indicator': ['SMA (20)', 'EMA (20)', 'RSI (14)', 'MACD Signal', 'BB Position', 'ATR (14)'],
            'Current Value': [
                f"{data['analysis_results']['SMA'].iloc[-1]:.2f}",
                f"{data['analysis_results']['EMA'].iloc[-1]:.2f}",
                f"{data['analysis_results']['RSI'].iloc[-1]:.1f}",
                "Bullish" if data['analysis_results']['MACD'].iloc[-1] > data['analysis_results']['MACD_Signal'].iloc[-1] else "Bearish",
                "Upper" if data['current_price'] > data['analysis_results']['BB_Upper'].iloc[-1] else "Lower" if data['current_price'] < data['analysis_results']['BB_Lower'].iloc[-1] else "Middle",
                f"{data['analysis_results']['ATR'].iloc[-1]:.2f}"
            ],
            'Signal': [
                "Bullish" if data['current_price'] > data['analysis_results']['SMA'].iloc[-1] else "Bearish",
                "Bullish" if data['current_price'] > data['analysis_results']['EMA'].iloc[-1] else "Bearish",
                "Oversold" if data['analysis_results']['RSI'].iloc[-1] < 30 else "Overbought" if data['analysis_results']['RSI'].iloc[-1] > 70 else "Neutral",
                "Bullish" if data['analysis_results']['MACD'].iloc[-1] > data['analysis_results']['MACD_Signal'].iloc[-1] else "Bearish",
                "Resistance" if data['current_price'] > data['analysis_results']['BB_Upper'].iloc[-1] else "Support" if data['current_price'] < data['analysis_results']['BB_Lower'].iloc[-1] else "Neutral",
                "High Volatility" if data['analysis_results']['ATR'].iloc[-1] > data['analysis_results']['ATR'].mean() else "Low Volatility"
            ]
        }
        
        indicators_df = pd.DataFrame(indicators_data)
        st.dataframe(indicators_df, hide_index=True)
    
    with col2:
        st.subheader("🎯 Support & Resistance Levels")
        
        # Calculate support and resistance levels
        support_resistance = data['decision_data']['support_resistance']
        
        levels_data = {
            'Level Type': ['Strong Support', 'Support', 'Current Price', 'Resistance', 'Strong Resistance'],
            'Price': [
                f"${support_resistance.get('strong_support', 0):.2f}" if support_resistance.get('strong_support') else "N/A",
                f"${support_resistance.get('support', 0):.2f}" if support_resistance.get('support') else "N/A", 
                f"${data['current_price']:.2f}",
                f"${support_resistance.get('resistance', 0):.2f}" if support_resistance.get('resistance') else "N/A",
                f"${support_resistance.get('strong_resistance', 0):.2f}" if support_resistance.get('strong_resistance') else "N/A"
            ],
            'Distance': [
                f"{((support_resistance.get('strong_support', data['current_price']) / data['current_price'] - 1) * 100):+.1f}%" if support_resistance.get('strong_support') else "N/A",
                f"{((support_resistance.get('support', data['current_price']) / data['current_price'] - 1) * 100):+.1f}%" if support_resistance.get('support') else "N/A",
                "0.0%",
                f"{((support_resistance.get('resistance', data['current_price']) / data['current_price'] - 1) * 100):+.1f}%" if support_resistance.get('resistance') else "N/A",
                f"{((support_resistance.get('strong_resistance', data['current_price']) / data['current_price'] - 1) * 100):+.1f}%" if support_resistance.get('strong_resistance') else "N/A"
            ]
        }
        
        levels_df = pd.DataFrame(levels_data)
        st.dataframe(levels_df, hide_index=True)
    
    # Decision Analysis
    st.subheader("🤖 Trading Decision Analysis")
    
    decision_data = data['decision_data']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Decision Factors:**")
        factors = decision_data['factors']
        for factor, weight in factors.items():
            st.write(f"• {factor}: {weight:+.1f}")
    
    with col2:
        st.markdown("**Fibonacci Levels:**")
        fib_levels = data['analysis_results']['fibonacci_levels'].iloc[-1] if 'fibonacci_levels' in data['analysis_results'].columns else {}
        if isinstance(fib_levels, dict):
            for level, price in fib_levels.items():
                st.write(f"• {level}: ${price:.2f}")
        else:
            st.write("• Fibonacci levels not available")
    
    with col3:
        st.markdown("**Risk Assessment:**")
        st.write(f"• Volatility: {decision_data['risk_level']}")
        st.write(f"• Trend Strength: {decision_data['trend_strength']}")
        st.write(f"• Market Sentiment: {decision_data['market_sentiment']}")
    
    # Detailed reasoning
    st.subheader("💡 Decision Reasoning")
    st.write(decision_data['reasoning'])
    
    # Sector Comparison Section
    if st.session_state.sector_data:
        display_sector_comparison()
    
    # Pattern Recognition Section
    if st.session_state.pattern_data:
        display_pattern_analysis()
    
    # Comprehensive Metrics Table
    if st.session_state.financial_data:
        display_comprehensive_metrics()
    
    # Financial Statements
    if st.session_state.financial_data:
        display_financial_statements()
    
    # News and Sentiment Analysis
    if st.session_state.news_data:
        display_news_analysis()

def display_enhanced_dashboard():
    """Display comprehensive mobile-friendly dashboard with all analysis features"""
    data = st.session_state.analysis_data
    
    # Create mobile-friendly tabs for all features
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13 = st.tabs([
        "📊 Overview", "📈 Technical", "🏢 Sectors", "📋 Financials", 
        "📰 News", "🎯 Options", "📉 Patterns", "🔍 Analysis", "🚨 Alerts", "🌍 Markets", "💊 Wellness", "📺 Videos", "📚 Help"
    ])
    
    with tab1:
        display_overview_tab()
    
    with tab2:
        display_technical_indicators_tab()
    
    with tab3:
        display_sectors_indices_tab()
    
    with tab4:
        display_financials_tab()
    
    with tab5:
        display_news_sentiment_tab()
    
    with tab6:
        display_options_strategies_tab()
    
    with tab7:
        display_patterns_tab()
    
    with tab8:
        display_threshold_analysis_tab()
    
    with tab9:
        display_alerts_tab()
    
    with tab10:
        display_markets_tab()
    
    with tab11:
        display_wellness_tab()
    
    with tab12:
        display_videos_tab()
    
    with tab13:
        display_help_tab()

def display_overview_tab():
    """Overview tab with key metrics and decision"""
    data = st.session_state.analysis_data
    
    # Header metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label=f"{data['symbol']} Price",
            value=f"${data['current_price']:.2f}",
            delta=f"{((data['current_price'] / data['stock_data']['Close'].iloc[-2] - 1) * 100):.2f}%"
        )
    
    with col2:
        decision_data = data['decision_data']
        st.metric(
            label="Trading Decision",
            value=decision_data['decision'],
            delta=f"Confidence: {decision_data['confidence']:.0f}%"
        )
    
    with col3:
        rsi_value = data['analysis_results']['RSI'].iloc[-1]
        st.metric(
            label="RSI (14)",
            value=f"{rsi_value:.1f}",
            delta="Oversold" if rsi_value < 30 else "Overbought" if rsi_value > 70 else "Neutral"
        )
    
    with col4:
        st.metric(
            label="Last Updated",
            value=data['last_update'].strftime("%H:%M:%S"),
            delta=data['last_update'].strftime("%Y-%m-%d")
        )
    
    # Trading Levels Section
    st.subheader("🎯 Key Trading Levels")
    if 'analysis_results' in data and not data['analysis_results'].empty:
        latest_data = data['analysis_results'].iloc[-1]
        
        levels_col1, levels_col2, levels_col3, levels_col4 = st.columns(4)
        
        with levels_col1:
            support = latest_data.get('Support_Level', data['current_price'] * 0.95)
            st.metric(
                "Support Level", 
                f"${support:.2f}", 
                f"{((support / data['current_price']) - 1) * 100:+.1f}%"
            )
            
        with levels_col2:
            resistance = latest_data.get('Resistance_Level', data['current_price'] * 1.05)
            st.metric(
                "Resistance Level", 
                f"${resistance:.2f}", 
                f"{((resistance / data['current_price']) - 1) * 100:+.1f}%"
            )
            
        with levels_col3:
            stop_loss = latest_data.get('Stop_Loss', data['current_price'] * 0.92)
            st.metric(
                "Stop Loss", 
                f"${stop_loss:.2f}", 
                f"{((stop_loss / data['current_price']) - 1) * 100:+.1f}%"
            )
            
        with levels_col4:
            short_target = latest_data.get('Short_Term_Target', data['current_price'] * 1.03)
            st.metric(
                "Short Term Target", 
                f"${short_target:.2f}", 
                f"{((short_target / data['current_price']) - 1) * 100:+.1f}%"
            )
            
        # Long term target in a separate row
        st.markdown("### 📈 Long Term Target")
        long_target = latest_data.get('Long_Term_Target', data['current_price'] * 1.08)
        col_long1, col_long2, col_long3 = st.columns([1,1,2])
        
        with col_long1:
            st.metric(
                "Long Term Target", 
                f"${long_target:.2f}", 
                f"{((long_target / data['current_price']) - 1) * 100:+.1f}%"
            )
            
        with col_long2:
            # Risk/Reward Ratio
            risk = data['current_price'] - stop_loss
            reward = short_target - data['current_price']
            risk_reward = reward / risk if risk > 0 else 0
            st.metric(
                "Risk/Reward Ratio", 
                f"1:{risk_reward:.2f}",
                "Good" if risk_reward > 2 else "Fair" if risk_reward > 1 else "Poor"
            )
            
        with col_long3:
            st.info(f"""
            **Trading Setup Summary:**
            - Entry: Current price ${data['current_price']:.2f}
            - Stop Loss: ${stop_loss:.2f} ({((stop_loss / data['current_price']) - 1) * 100:+.1f}%)
            - Target 1: ${short_target:.2f} ({((short_target / data['current_price']) - 1) * 100:+.1f}%)
            - Target 2: ${long_target:.2f} ({((long_target / data['current_price']) - 1) * 100:+.1f}%)
            """)

    # Main chart
    st.subheader("📊 Price Chart with Technical Indicators")
    chart_generator = ChartGenerator()
    fig = chart_generator.create_comprehensive_chart(
        data['stock_data'], data['analysis_results'], data['symbol']
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # YouTube videos section
    if hasattr(st.session_state, 'youtube_videos') and st.session_state.youtube_videos:
        display_youtube_videos_section()

def display_technical_indicators_tab():
    """Individual technical indicators with threshold analysis"""
    if not st.session_state.enhanced_data:
        st.info("Enhanced analysis not available")
        return
    
    enhanced_data = st.session_state.enhanced_data
    individual_indicators = enhanced_data.get('individual_indicators', {})
    threshold_summary = enhanced_data.get('threshold_summary', {})
    
    if threshold_summary:
        st.subheader("🎯 Technical Indicators Threshold Analysis")
        
        # Overall sentiment
        overall_sentiment = threshold_summary.get('overall_sentiment', 'Unknown')
        bullish_count = threshold_summary.get('bullish_count', 0)
        bearish_count = threshold_summary.get('bearish_count', 0)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Overall Sentiment", overall_sentiment)
        with col2:
            st.metric("Bullish Signals", bullish_count)
        with col3:
            st.metric("Bearish Signals", bearish_count)
        
        # Threshold table
        threshold_table = threshold_summary.get('threshold_table', [])
        if threshold_table:
            # Convert all values to strings to avoid serialization issues
            for row in threshold_table:
                for key, value in row.items():
                    row[key] = str(value)
            df = pd.DataFrame(threshold_table)
            st.dataframe(df, use_container_width=True)
    
    # Individual indicator plots
    if individual_indicators:
        st.subheader("📈 Individual Technical Indicators")
        
        data = st.session_state.analysis_data
        analysis_results = data['analysis_results']
        
        # Create individual plots for each indicator
        for indicator_name, indicator_data in individual_indicators.items():
            with st.expander(f"📊 {indicator_name.replace('_', ' ')} Analysis"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Create individual chart for this indicator
                    chart_generator = ChartGenerator()
                    if indicator_name in analysis_results.columns:
                        fig = chart_generator.create_indicator_chart(
                            analysis_results, indicator_name, data['symbol']
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    signal = str(indicator_data.get('signal', 'HOLD'))
                    strength = str(indicator_data.get('strength', 'Neutral'))
                    description = str(indicator_data.get('description', 'No description'))
                    
                    # Signal styling
                    signal_class = f"signal-{signal.lower()}"
                    st.markdown(f"""
                    <div class="indicator-signal {signal_class}">
                        <strong>Signal:</strong> {signal}<br>
                        <strong>Strength:</strong> {strength}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.write(f"**Analysis:** {description}")

def display_sectors_indices_tab():
    """Sector and index comparison"""
    if not st.session_state.enhanced_data:
        st.info("Enhanced analysis not available")
        return
    
    enhanced_data = st.session_state.enhanced_data
    index_comparison = enhanced_data.get('index_comparison', {})
    sector_comparison = enhanced_data.get('sector_comparison', {})
    
    # Index comparison
    if index_comparison:
        st.subheader("📊 Market Indices Comparison")
        indices_data = index_comparison.get('indices', {})
        stock_return = index_comparison.get('stock_return', 0)
        
        comparison_table = []
        for index_name, index_data in indices_data.items():
            comparison_table.append({
                'Index': index_name,
                'Return': f"{index_data['return']:.2f}%",
                'vs Stock': f"{index_data['vs_stock']:.2f}%",
                'Outperforming': "✅" if index_data['outperforming'] else "❌",
                'Current Price': f"{index_data['current_price']:.2f}"
            })
        
        if comparison_table:
            df = pd.DataFrame(comparison_table)
            st.dataframe(df, use_container_width=True)
    
    # Sector comparison
    if sector_comparison:
        st.subheader("🏭 Sector Comparison")
        sector_data = sector_comparison.get('sector_data', {})
        
        if sector_data:
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Stock Return", 
                    f"{sector_comparison.get('stock_return', 0):.2f}%"
                )
            with col2:
                st.metric(
                    "Sector ETF Return",
                    f"{sector_data.get('etf_return', 0):.2f}%",
                    delta=f"{sector_data.get('vs_stock', 0):.2f}% vs stock"
                )
    
    # Display original sector analysis
    if st.session_state.sector_data:
        display_sector_comparison()

def display_financials_tab():
    """Financial statements and comprehensive metrics"""
    if st.session_state.financial_data:
        display_comprehensive_metrics()
        display_financial_statements()

def display_news_sentiment_tab():
    """Enhanced news analysis with sentiment"""
    if st.session_state.news_data:
        display_news_analysis()
        
        # Add analyst recommendations if available
        if st.session_state.enhanced_data:
            analyst_data = st.session_state.enhanced_data.get('analyst_recommendations', {})
            if analyst_data:
                st.subheader("👥 Analyst Recommendations")
                
                analyst_info = analyst_data.get('analyst_data', {})
                rec_text = analyst_data.get('recommendation_text', 'No Rating')
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Recommendation", rec_text)
                with col2:
                    target_price = analyst_info.get('target_mean_price', 0)
                    current_price = analyst_data.get('current_price', 0)
                    if target_price > 0 and current_price > 0:
                        upside = ((target_price / current_price) - 1) * 100
                        st.metric("Target Price", f"${target_price:.2f}", delta=f"{upside:.1f}% upside")
                with col3:
                    st.metric("Analyst Count", analyst_info.get('number_of_analyst_opinions', 0))

def display_options_strategies_tab():
    """Options strategies and profitable strikes"""
    if not st.session_state.options_data:
        st.info("Options analysis not available")
        return
    
    options_data = st.session_state.options_data
    strategies = options_data.get('strategies', {})
    profitable_strikes = options_data.get('profitable_strikes', {})
    
    if strategies:
        st.subheader("🎯 Options Strategies Analysis")
        
        strategy_data = strategies.get('strategies', {})
        expiration = strategies.get('expiration', 'N/A')
        days_to_expiry = strategies.get('days_to_expiry', 0)
        current_iv = strategies.get('current_iv', 0)
        
        st.write(f"**Expiration:** {expiration} ({days_to_expiry} days)")
        st.write(f"**Current IV:** {current_iv:.1f}%")
        
        # Display each strategy
        for strategy_name, strategy_info in strategy_data.items():
            with st.expander(f"📋 {strategy_info.get('strategy', strategy_name)}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Strike:** ${strategy_info.get('strike', 0):.2f}")
                    st.write(f"**Breakeven:** ${strategy_info.get('breakeven', 0):.2f}")
                    st.write(f"**Max Profit:** {strategy_info.get('max_profit', 'N/A')}")
                
                with col2:
                    st.write(f"**Max Loss:** ${strategy_info.get('max_loss', 0):.2f}")
                    prob_profit = strategy_info.get('probability_profit', 0)
                    st.write(f"**Profit Probability:** {prob_profit:.1%}")
    
    # Profitable strikes analysis
    if profitable_strikes:
        st.subheader("💰 Profitable Strike Prices")
        
        for exp_date, exp_data in profitable_strikes.items():
            with st.expander(f"📅 Expiration: {exp_date}"):
                days = exp_data.get('days_to_expiry', 0)
                st.write(f"**Days to Expiry:** {days}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Profitable Calls:**")
                    calls = exp_data.get('profitable_calls', [])
                    if calls:
                        calls_df = pd.DataFrame(calls)
                        st.dataframe(calls_df, use_container_width=True)
                    else:
                        st.info("No profitable calls found")
                
                with col2:
                    st.write("**Profitable Puts:**")
                    puts = exp_data.get('profitable_puts', [])
                    if puts:
                        puts_df = pd.DataFrame(puts)
                        st.dataframe(puts_df, use_container_width=True)
                    else:
                        st.info("No profitable puts found")

def display_patterns_tab():
    """Chart patterns analysis"""
    if st.session_state.pattern_data:
        display_pattern_analysis()

def display_threshold_analysis_tab():
    """Detailed threshold and decision analysis"""
    data = st.session_state.analysis_data
    
    # Decision analysis from original code
    st.subheader("🤖 Trading Decision Analysis")
    decision_data = data['decision_data']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Decision Factors:**")
        factors = decision_data.get('factors', {})
        for factor, weight in factors.items():
            st.write(f"• {factor}: {weight:+.1f}")
    
    with col2:
        st.markdown("**Risk Assessment:**")
        st.write(f"• Volatility: {decision_data.get('risk_level', 'Unknown')}")
        st.write(f"• Trend Strength: {decision_data.get('trend_strength', 'Unknown')}")
        st.write(f"• Market Sentiment: {decision_data.get('market_sentiment', 'Unknown')}")
    
    with col3:
        st.markdown("**Support & Resistance:**")
        support_resistance = decision_data.get('support_resistance', {})
        if support_resistance:
            support = support_resistance.get('support', 0)
            resistance = support_resistance.get('resistance', 0)
            if support:
                st.write(f"• Support: ${support:.2f}")
            if resistance:
                st.write(f"• Resistance: ${resistance:.2f}")
    
    # Decision reasoning
    st.subheader("💡 Decision Reasoning")
    st.write(decision_data.get('reasoning', 'No reasoning available'))

def display_alerts_tab():
    """Smart Alerts tab for watchlist management and notifications"""
    st.subheader("🚨 Smart Alert System")
    
    # Initialize alert system
    alert_system = AlertSystem()
    
    # Current analysis data
    data = st.session_state.analysis_data
    symbol = data['symbol']
    current_price = data['current_price']
    
    # Alerts Management Section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📱 Add to Watchlist")
        st.markdown(f"**Current Stock:** {symbol} (${current_price:.2f})")
        
        # Get current sentiment for display
        enhanced_data = st.session_state.enhanced_data
        if enhanced_data and enhanced_data.get('threshold_summary'):
            current_sentiment = enhanced_data['threshold_summary'].get('overall_sentiment', 'Unknown')
            bullish_count = enhanced_data['threshold_summary'].get('bullish_count', 0)
            bearish_count = enhanced_data['threshold_summary'].get('bearish_count', 0)
            
            st.info(f"**Current Sentiment:** {current_sentiment} ({bullish_count} bullish, {bearish_count} bearish indicators)")
        
        # Alert setup form
        with st.form("add_alert_form"):
            st.markdown("**📞 Alert Notifications:**")
            
            col_phone, col_email = st.columns(2)
            with col_phone:
                user_phone = st.text_input(
                    "Phone Number (SMS alerts)",
                    placeholder="+1234567890",
                    help="Enter with country code for SMS alerts"
                )
            
            with col_email:
                user_email = st.text_input(
                    "Email Address",
                    placeholder="your@email.com",
                    help="Email for alert notifications"
                )
            
            st.markdown("**🎯 Alert Triggers:**")
            st.markdown("""
            **Automatic Alerts for:**
            - 🚀 **Bullish Reversal:** When sentiment changes from bearish/neutral to bullish
            - 🛑 **Stop Loss Hit:** When price hits calculated stop loss
            - 🎯 **Target Hit:** When price reaches profit targets
            - ⚡ **Risk Management:** Automatic stop-loss and target calculations using ATR
            """)
            
            submitted = st.form_submit_button("➕ Add to Watchlist", type="primary")
            
            if submitted:
                if not user_phone and not user_email:
                    st.error("Please provide at least a phone number or email for alerts.")
                else:
                    # Add to watchlist
                    success = alert_system.add_to_watchlist(
                        symbol=symbol,
                        user_phone=user_phone if user_phone else None,
                        user_email=user_email if user_email else None
                    )
                    
                    if success:
                        st.success(f"✅ {symbol} added to watchlist! You'll receive alerts for sentiment changes and price targets.")
                        st.rerun()
                    else:
                        st.error("Failed to add to watchlist. Please try again.")
    
    with col2:
        st.markdown("### 🔔 Alert Types")
        st.markdown("""
        **🚀 Bullish Reversal**
        - Sentiment: Bearish → Bullish
        - Min 3+ bullish indicators
        - Auto stop-loss & targets
        
        **🛑 Stop Loss**
        - ATR-based or 8% default
        - Automatic risk management
        
        **🎯 Profit Targets**
        - Target 1: +15%
        - Target 2: +30%
        - Risk/reward ratios
        """)
    
    st.divider()
    
    # Current Watchlist Section
    st.markdown("### 📋 Current Watchlist")
    
    watchlist = alert_system.get_watchlist()
    
    if watchlist:
        # Display watchlist as cards
        for watch_symbol, stock_info in watchlist.items():
            with st.container():
                st.markdown(f"#### 📈 {watch_symbol}")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Current Price",
                        f"${stock_info.get('current_price', 0):.2f}",
                        f"Entry: ${stock_info.get('current_price', 0):.2f}"
                    )
                
                with col2:
                    st.metric(
                        "Stop Loss",
                        f"${stock_info.get('stop_loss', 0):.2f}",
                        f"{((stock_info.get('stop_loss', 0) / stock_info.get('current_price', 1) - 1) * 100):+.1f}%"
                    )
                
                with col3:
                    st.metric(
                        "Target 1",
                        f"${stock_info.get('target_1', 0):.2f}",
                        f"{((stock_info.get('target_1', 0) / stock_info.get('current_price', 1) - 1) * 100):+.1f}%"
                    )
                
                with col4:
                    st.metric(
                        "Target 2",
                        f"${stock_info.get('target_2', 0):.2f}",
                        f"{((stock_info.get('target_2', 0) / stock_info.get('current_price', 1) - 1) * 100):+.1f}%"
                    )
                
                # Stock info
                col_info, col_remove = st.columns([3, 1])
                with col_info:
                    st.write(f"**Sentiment:** {stock_info.get('last_sentiment', 'Unknown')}")
                    st.write(f"**Added:** {stock_info.get('added_date', '').split('T')[0]}")
                    st.write(f"**Alerts:** {'📱 SMS' if stock_info.get('user_phone') else ''} {'📧 Email' if stock_info.get('user_email') else ''}")
                
                with col_remove:
                    if st.button(f"🗑️ Remove", key=f"remove_{watch_symbol}"):
                        if alert_system.remove_from_watchlist(watch_symbol):
                            st.success(f"Removed {watch_symbol} from watchlist")
                            st.rerun()
                
                st.divider()
    else:
        st.info("📭 No stocks in watchlist yet. Add the current stock to start receiving alerts!")
    
    # Alerts History Section
    st.markdown("### 📜 Recent Alerts History")
    
    alerts_history = alert_system.get_alerts_history()
    
    if alerts_history:
        # Show last 10 alerts
        recent_alerts = alerts_history[-10:]
        
        for alert in reversed(recent_alerts):
            alert_type = alert.get('alert_type', 'UNKNOWN')
            timestamp = alert.get('timestamp', '').split('T')
            date_part = timestamp[0] if timestamp else 'Unknown'
            time_part = timestamp[1].split('.')[0] if len(timestamp) > 1 else 'Unknown'
            
            # Color code by alert type
            if alert_type == "BULLISH_REVERSAL":
                st.success(f"🚀 **{alert['symbol']}** - Bullish Reversal Alert ({date_part} {time_part})")
            elif alert_type == "STOP_LOSS_HIT":
                st.error(f"🛑 **{alert['symbol']}** - Stop Loss Hit ({date_part} {time_part})")
            elif "TARGET" in alert_type:
                st.info(f"🎯 **{alert['symbol']}** - Target Hit ({date_part} {time_part})")
            else:
                st.write(f"📢 **{alert['symbol']}** - Alert ({date_part} {time_part})")
            
            with st.expander("View Details"):
                st.text(alert.get('message', 'No details available'))
    else:
        st.info("🔕 No alerts generated yet. Add stocks to watchlist to start monitoring!")
    
    # Manual Alert Check Section
    st.markdown("### ⚡ Manual Alert Check")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("Check all watchlist stocks for new alerts manually:")
    
    with col2:
        if st.button("🔍 Check All Alerts", type="secondary"):
            if watchlist:
                with st.spinner("Checking for new alerts..."):
                    new_alerts = alert_system.check_watchlist_alerts()
                    
                    if new_alerts:
                        st.success(f"🚨 Found {len(new_alerts)} new alert(s)!")
                        for alert in new_alerts:
                            st.info(f"**{alert['symbol']}:** {alert['alert_type']}")
                            # Send the alerts
                            alert_system.send_alert(alert)
                        st.rerun()
                    else:
                        st.info("✅ No new alerts at this time.")
            else:
                st.warning("📭 No stocks in watchlist to check.")

def display_markets_tab():
    """Markets overview tab with indices, commodities, forex, and market movers"""
    st.subheader("🌍 Global Markets Overview")
    
    # Initialize market overview
    market_overview = MarketOverview()
    
    # Create sub-tabs for different market categories
    market_tab1, market_tab2, market_tab3, market_tab4, market_tab5, market_tab6 = st.tabs([
        "📈 Indices", "🥇 Commodities", "💱 Forex", "🚀 Top Gainers", "📉 Top Losers", "🔥 Most Active"
    ])
    
    with market_tab1:
        st.markdown("### 📈 Major Stock Indices")
        
        with st.spinner("Loading indices data..."):
            indices_df = market_overview.get_major_indices()
            
            if indices_df is not None and not indices_df.empty:
                # Display indices with color coding
                for _, row in indices_df.iterrows():
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    
                    with col1:
                        st.write(f"**{row['Name']}**")
                    
                    with col2:
                        price_color = "normal"
                        if row['Change %'] > 0:
                            st.success(f"${row['Price']:.2f}")
                        elif row['Change %'] < 0:
                            st.error(f"${row['Price']:.2f}")
                        else:
                            st.write(f"${row['Price']:.2f}")
                    
                    with col3:
                        if row['Change %'] > 0:
                            st.success(f"+{row['Change %']:.2f}%")
                        elif row['Change %'] < 0:
                            st.error(f"{row['Change %']:.2f}%")
                        else:
                            st.write(f"{row['Change %']:.2f}%")
                    
                    with col4:
                        # Trend indicator
                        if 'Bullish' in row['Trend']:
                            st.success(f"📈 {row['Trend']}")
                        elif 'Bearish' in row['Trend']:
                            st.error(f"📉 {row['Trend']}")
                        else:
                            st.info(f"↔️ {row['Trend']}")
                
                # Technical summary for indices
                summary = market_overview.get_technical_summary(indices_df)
                
                st.markdown("### 📊 Indices Technical Summary")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Indices", summary.get('total_instruments', 0))
                with col2:
                    st.metric("Bullish", summary.get('bullish_count', 0), 
                             delta=f"{(summary.get('bullish_count', 0)/summary.get('total_instruments', 1)*100):.0f}%")
                with col3:
                    st.metric("Bearish", summary.get('bearish_count', 0),
                             delta=f"{(summary.get('bearish_count', 0)/summary.get('total_instruments', 1)*100):.0f}%")
                with col4:
                    st.metric("Avg Change", f"{summary.get('avg_change', 0):.2f}%")
                
            else:
                st.error("Unable to load indices data. Please check your connection or API access.")
    
    with market_tab2:
        st.markdown("### 🥇 Commodities Market")
        
        with st.spinner("Loading commodities data..."):
            commodities_df = market_overview.get_commodities()
            
            if commodities_df is not None and not commodities_df.empty:
                # Display commodities
                for _, row in commodities_df.iterrows():
                    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                    
                    with col1:
                        st.write(f"**{row['Name']}**")
                    
                    with col2:
                        st.write(f"${row['Price']:.2f}")
                    
                    with col3:
                        if row['Change %'] > 0:
                            st.success(f"+{row['Change %']:.2f}%")
                        elif row['Change %'] < 0:
                            st.error(f"{row['Change %']:.2f}%")
                        else:
                            st.write(f"{row['Change %']:.2f}%")
                    
                    with col4:
                        st.write(f"{row['From High %']:.1f}%")
                    
                    with col5:
                        if 'Bullish' in row['Trend']:
                            st.success(f"📈")
                        elif 'Bearish' in row['Trend']:
                            st.error(f"📉")
                        else:
                            st.info(f"↔️")
                
                # Commodities summary
                summary = market_overview.get_technical_summary(commodities_df)
                
                st.markdown("### 📊 Commodities Summary")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Bullish Commodities", summary.get('bullish_count', 0))
                with col2:
                    st.metric("Bearish Commodities", summary.get('bearish_count', 0))
                with col3:
                    st.metric("Average Change", f"{summary.get('avg_change', 0):.2f}%")
                
            else:
                st.error("Unable to load commodities data.")
    
    with market_tab3:
        st.markdown("### 💱 Foreign Exchange (Forex)")
        
        with st.spinner("Loading forex data..."):
            forex_df = market_overview.get_forex_pairs()
            
            if forex_df is not None and not forex_df.empty:
                # Display forex pairs
                for _, row in forex_df.iterrows():
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    
                    with col1:
                        st.write(f"**{row['Name']}**")
                    
                    with col2:
                        st.write(f"{row['Price']:.4f}")
                    
                    with col3:
                        if row['Change %'] > 0:
                            st.success(f"+{row['Change %']:.2f}%")
                        elif row['Change %'] < 0:
                            st.error(f"{row['Change %']:.2f}%")
                        else:
                            st.write(f"{row['Change %']:.2f}%")
                    
                    with col4:
                        if 'Bullish' in row['Trend']:
                            st.success(f"📈 {row['Trend']}")
                        elif 'Bearish' in row['Trend']:
                            st.error(f"📉 {row['Trend']}")
                        else:
                            st.info(f"↔️ {row['Trend']}")
                
            else:
                st.error("Unable to load forex data.")
    
    with market_tab4:
        st.markdown("### 🚀 Top Gainers")
        
        with st.spinner("Loading market movers..."):
            top_gainers, top_losers, most_active = market_overview.get_market_movers()
            
            if top_gainers is not None and not top_gainers.empty:
                st.markdown("**Top 10 Gainers Today:**")
                
                for i, (_, row) in enumerate(top_gainers.head(10).iterrows(), 1):
                    col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
                    
                    with col1:
                        st.write(f"#{i}")
                    
                    with col2:
                        st.write(f"**{row['Symbol']}**")
                    
                    with col3:
                        st.write(f"${row['Price']:.2f}")
                    
                    with col4:
                        st.success(f"+{row['Change %']:.2f}%")
                
            else:
                st.error("Unable to load top gainers data.")
    
    with market_tab5:
        st.markdown("### 📉 Top Losers")
        
        if top_losers is not None and not top_losers.empty:
            st.markdown("**Top 10 Losers Today:**")
            
            for i, (_, row) in enumerate(top_losers.head(10).iterrows(), 1):
                col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
                
                with col1:
                    st.write(f"#{i}")
                
                with col2:
                    st.write(f"**{row['Symbol']}**")
                
                with col3:
                    st.write(f"${row['Price']:.2f}")
                
                with col4:
                    st.error(f"{row['Change %']:.2f}%")
            
        else:
            st.error("Unable to load top losers data.")
    
    with market_tab6:
        st.markdown("### 🔥 Most Active (By Volume)")
        
        if most_active is not None and not most_active.empty:
            st.markdown("**Most Active Stocks Today:**")
            
            for i, (_, row) in enumerate(most_active.head(10).iterrows(), 1):
                col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 1, 1])
                
                with col1:
                    st.write(f"#{i}")
                
                with col2:
                    st.write(f"**{row['Symbol']}**")
                
                with col3:
                    st.write(f"${row['Price']:.2f}")
                
                with col4:
                    if row['Change %'] > 0:
                        st.success(f"+{row['Change %']:.2f}%")
                    elif row['Change %'] < 0:
                        st.error(f"{row['Change %']:.2f}%")
                    else:
                        st.write(f"{row['Change %']:.2f}%")
                
                with col5:
                    st.info(f"{row['Volume Ratio']:.1f}x avg")
            
        else:
            st.error("Unable to load most active stocks data.")
    
    # 52-Week Highs and Lows Section
    st.divider()
    
    st.markdown("### 📊 52-Week Extremes")
    
    col_highs, col_lows = st.columns(2)
    
    with col_highs:
        st.markdown("#### 🎯 Near 52-Week Highs")
        
        with st.spinner("Loading 52-week highs..."):
            highs_df, lows_df = market_overview.get_52_week_extremes()
            
            if highs_df is not None and not highs_df.empty:
                for _, row in highs_df.head(10).iterrows():
                    st.success(f"**{row['Symbol']}** - ${row['Current Price']:.2f} ({row['From High %']:+.1f}% from high)")
            else:
                st.info("No stocks near 52-week highs found.")
    
    with col_lows:
        st.markdown("#### 🎯 Near 52-Week Lows")
        
        if lows_df is not None and not lows_df.empty:
            for _, row in lows_df.head(10).iterrows():
                st.error(f"**{row['Symbol']}** - ${row['Current Price']:.2f} ({row['From Low %']:+.1f}% from low)")
        else:
            st.info("No stocks near 52-week lows found.")
    
    # Refresh button
    st.divider()
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Market data updates automatically. Click refresh for latest information.**")
    
    with col2:
        if st.button("🔄 Refresh Markets", type="secondary"):
            st.rerun()

def display_youtube_videos_section():
    """Display relevant YouTube videos for stock and technical indicators"""
    if not hasattr(st.session_state, 'youtube_videos'):
        return
    
    videos = st.session_state.youtube_videos
    data = st.session_state.analysis_data
    
    st.markdown("---")
    st.subheader("📺 Educational Videos")
    
    # Create tabs for different video categories
    if any(videos.values()):  # Check if any category has videos
        video_tab1, video_tab2, video_tab3 = st.tabs([
            f"📊 {data['symbol']} Analysis", 
            "📈 Technical Indicators", 
            "🎓 Trading Education"
        ])
        
        with video_tab1:
            st.markdown(f"**Videos about {data['symbol']} stock analysis:**")
            display_video_category(videos.get('stock_analysis', []), f"{data['symbol']} stock")
        
        with video_tab2:
            st.markdown("**Learn about technical indicators:**")
            display_video_category(videos.get('technical_indicators', []), "technical indicators")
        
        with video_tab3:
            st.markdown("**General trading education:**")
            display_video_category(videos.get('general_education', []), "trading education")
    else:
        st.info("Educational videos will be available once analysis is complete")

def display_video_category(video_list, category_name):
    """Display videos for a specific category"""
    if not video_list:
        st.warning(f"Educational videos require YouTube API access. Please check your API configuration to view {category_name} content.")
        return
    
    # Display videos in a grid layout
    cols = st.columns(min(len(video_list), 2))
    
    for idx, video in enumerate(video_list):
        col_idx = idx % 2
        with cols[col_idx]:
            st.markdown(f"**{video['title'][:50]}{'...' if len(video['title']) > 50 else ''}**")
            st.markdown(f"*By: {video['channel_title']}*")
            
            # Embed YouTube video
            try:
                st.video(video['embed_url'].replace('/embed/', '/watch?v='))
            except:
                # Fallback to link if embedding fails
                st.markdown(f"[Watch Video]({video['embed_url'].replace('/embed/', '/watch?v=')})")
            
            # Show description
            if video.get('description'):
                with st.expander("Video Description"):
                    st.write(video['description'])
            
            st.markdown("---")

def display_educational_sidebar():
    """Educational sidebar with embedded video tutorials"""
    st.markdown("### 📚 Learn Trading")
    st.markdown("*Interactive Video Tutorials*")
    
    # Stock Analysis Education
    with st.expander("📊 Stock Analysis", expanded=False):
        st.markdown("**Stock Analysis Fundamentals:**")
        st.components.v1.html("""
        <iframe width="280" height="157" src="https://www.youtube.com/embed/p7HKvqRI_Bo" 
        frameborder="0" allowfullscreen></iframe>
        """, height=160)
        
        st.markdown("**Chart Reading:**")
        st.components.v1.html("""
        <iframe width="280" height="157" src="https://www.youtube.com/embed/08c1Nb8j1Sw" 
        frameborder="0" allowfullscreen></iframe>
        """, height=160)
    
    # Technical Indicators Education
    with st.expander("📈 Technical Indicators", expanded=False):
        st.markdown("**RSI Indicator:**")
        st.components.v1.html("""
        <iframe width="280" height="157" src="https://www.youtube.com/embed/Wz_N7B4cCZE" 
        frameborder="0" allowfullscreen></iframe>
        """, height=160)
        
        st.markdown("**MACD Indicator:**")
        st.components.v1.html("""
        <iframe width="280" height="157" src="https://www.youtube.com/embed/MlDIm5oUJgU" 
        frameborder="0" allowfullscreen></iframe>
        """, height=160)
    
    # Swing Trading Education
    with st.expander("🔄 Swing Trading", expanded=False):
        st.markdown("**Swing Trading Basics:**")
        st.components.v1.html("""
        <iframe width="280" height="157" src="https://www.youtube.com/embed/lzYWKoNVsno" 
        frameborder="0" allowfullscreen></iframe>
        """, height=160)
        
        st.markdown("**Chart Patterns:**")
        st.components.v1.html("""
        <iframe width="280" height="157" src="https://www.youtube.com/embed/2LtggmnT3WM" 
        frameborder="0" allowfullscreen></iframe>
        """, height=160)
    
    # Financial Statements Education
    with st.expander("📋 Financial Statements", expanded=False):
        st.markdown("**Balance Sheet Analysis:**")
        st.components.v1.html("""
        <iframe width="280" height="157" src="https://www.youtube.com/embed/nIRGOz9jL5k" 
        frameborder="0" allowfullscreen></iframe>
        """, height=160)
        
        st.markdown("**Income Statement:**")
        st.components.v1.html("""
        <iframe width="280" height="157" src="https://www.youtube.com/embed/UiXKmzpPUzE" 
        frameborder="0" allowfullscreen></iframe>
        """, height=160)
    
    # Risk Management
    with st.expander("⚠️ Risk Management", expanded=False):
        st.markdown("**Stop Loss Strategy:**")
        st.components.v1.html("""
        <iframe width="280" height="157" src="https://www.youtube.com/embed/OYq2tD6psxM" 
        frameborder="0" allowfullscreen></iframe>
        """, height=160)
        
        st.markdown("**Position Sizing:**")
        st.components.v1.html("""
        <iframe width="280" height="157" src="https://www.youtube.com/embed/Pg7vGYhqfhY" 
        frameborder="0" allowfullscreen></iframe>
        """, height=160)
    
    # Quick Tips Section
    st.markdown("---")
    st.markdown("### 💡 Quick Tips")
    st.info("📌 Start with paper trading\n📌 Learn one indicator at a time\n📌 Always use stop losses\n📌 Never risk more than 2% per trade")
    
    # Platform Features Guide
    st.markdown("---")
    st.markdown("### 🔧 Platform Guide")
    st.markdown("**How to use this platform:**")
    st.markdown("🔍 **Overview**: Key metrics & charts")
    st.markdown("📈 **Technical**: Individual indicators")
    st.markdown("🏢 **Sectors**: Industry comparison")
    st.markdown("📋 **Financials**: Company fundamentals")
    st.markdown("📰 **News**: Market sentiment")
    st.markdown("🎯 **Options**: Strategy analysis")
    st.markdown("📉 **Patterns**: Chart patterns")
    st.markdown("🚨 **Alerts**: Watchlist management")
    st.markdown("💊 **Wellness**: Investment health")
    st.markdown("📺 **Videos**: Educational content")

def display_videos_tab():
    """Dedicated tab for educational YouTube videos"""
    st.subheader("📺 Educational Trading Videos")
    
    if not hasattr(st.session_state, 'youtube_videos') or not st.session_state.youtube_videos:
        st.info("Educational videos will be available after analyzing a stock")
        return
    
    videos = st.session_state.youtube_videos
    data = st.session_state.analysis_data
    
    # Display all video categories with better organization
    if videos.get('stock_analysis'):
        st.markdown(f"### 📊 {data['symbol']} Stock Analysis Videos")
        display_video_grid(videos['stock_analysis'])
        st.markdown("---")
    
    if videos.get('technical_indicators'):
        st.markdown("### 📈 Technical Indicators Education")
        display_video_grid(videos['technical_indicators'])
        st.markdown("---")
    
    if videos.get('general_education'):
        st.markdown("### 🎓 General Trading Education")
        display_video_grid(videos['general_education'])

def display_video_grid(video_list):
    """Display videos in a responsive grid layout"""
    if not video_list:
        st.info("No videos available for this category")
        return
    
    # Create columns for video grid
    num_cols = min(len(video_list), 3)
    cols = st.columns(num_cols)
    
    for idx, video in enumerate(video_list):
        col_idx = idx % num_cols
        with cols[col_idx]:
            # Video card display
            st.markdown(f"**{video['title'][:60]}{'...' if len(video['title']) > 60 else ''}**")
            st.markdown(f"*Channel: {video['channel_title']}*")
            
            # Embed video
            video_url = video['embed_url'].replace('/embed/', '/watch?v=')
            st.video(video_url)
            
            # Video description
            if video.get('description'):
                with st.expander("Show Description"):
                    st.write(video['description'])
            
            # Open in YouTube button
            st.markdown(f"[Open in YouTube]({video_url})")
            st.markdown("---")

def display_wellness_tab():
    """Financial wellness report with personalized improvement suggestions"""
    if not st.session_state.wellness_report:
        st.info("Financial wellness report not available")
        return
    
    report = st.session_state.wellness_report
    
    # Header with overall score
    st.markdown(f"## 💊 Financial Wellness Report - {report['symbol']}")
    
    # Overall wellness score display
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        score = report['overall_wellness_score']
        grade = report['wellness_grade']
        if score >= 80:
            st.success(f"**Overall Score: {score}/100**")
        elif score >= 60:
            st.warning(f"**Overall Score: {score}/100**")
        else:
            st.error(f"**Overall Score: {score}/100**")
        st.write(f"**Grade: {grade}**")
    
    with col2:
        st.metric("Current Price", f"${report['current_price']:.2f}")
    
    with col3:
        st.write(f"**Analysis Date:**")
        st.write(report['analysis_date'])
    
    with col4:
        outlook = report['investment_outlook']
        if "Strong" in outlook:
            st.success("Strong Outlook")
        elif "High-risk" in outlook:
            st.error("High Risk")
        else:
            st.info("Moderate Outlook")
    
    st.markdown("---")
    
    # Category scores breakdown
    st.markdown("### 📊 Wellness Categories")
    
    categories = report['category_scores']
    cat_col1, cat_col2, cat_col3 = st.columns(3)
    
    with cat_col1:
        st.markdown("**💰 Valuation**")
        val_score = categories['valuation']
        st.progress(val_score / 100)
        st.write(f"{val_score}/100")
        
        st.markdown("**📈 Technical**")
        tech_score = categories['technical']
        st.progress(tech_score / 100)
        st.write(f"{tech_score}/100")
    
    with cat_col2:
        st.markdown("**🏢 Fundamental**")
        fund_score = categories['fundamental']
        st.progress(fund_score / 100)
        st.write(f"{fund_score}/100")
        
        st.markdown("**🎯 Market Position**")
        market_score = categories['market_position']
        st.progress(market_score / 100)
        st.write(f"{market_score}/100")
    
    with cat_col3:
        st.markdown("**⚠️ Risk Management**")
        risk_score = categories['risk_management']
        st.progress(risk_score / 100)
        st.write(f"{risk_score}/100")
        
        st.markdown("**📰 Sentiment**")
        sent_score = categories['sentiment']
        st.progress(sent_score / 100)
        st.write(f"{sent_score}/100")
    
    st.markdown("---")
    
    # Strengths and weaknesses
    strengths_col, weakness_col = st.columns(2)
    
    with strengths_col:
        st.markdown("### ✅ Key Strengths")
        strengths = report['key_strengths']
        if strengths:
            for strength in strengths:
                st.success(f"• {strength}")
        else:
            st.info("No major strengths identified")
    
    with weakness_col:
        st.markdown("### ⚠️ Areas for Improvement")
        weaknesses = report['improvement_areas']
        if weaknesses:
            for weakness in weaknesses:
                st.error(f"• {weakness}")
        else:
            st.success("No major weaknesses identified")
    
    st.markdown("---")
    
    # Personalized suggestions
    st.markdown("### 💡 Personalized Improvement Suggestions")
    
    suggestions = report['personalized_suggestions']
    if suggestions:
        for i, suggestion in enumerate(suggestions):
            priority = suggestion['priority']
            category = suggestion['category']
            
            if priority == 'High':
                st.error(f"**🔴 High Priority - {category}**")
            elif priority == 'Medium':
                st.warning(f"**🟡 Medium Priority - {category}**")
            else:
                st.info(f"**🟢 Low Priority - {category}**")
            
            st.write(f"**Suggestion:** {suggestion['suggestion']}")
            st.write(f"**Reason:** {suggestion['reason']}")
            st.markdown("---")
    else:
        st.success("No specific improvement suggestions needed - investment looks solid!")
    
    # Action items
    st.markdown("### 📋 Recommended Action Items")
    action_items = report['action_items']
    
    for i, action in enumerate(action_items, 1):
        st.write(f"{i}. {action}")
    
    st.markdown("---")
    
    # Investment outlook and risk assessment
    outlook_col, risk_col = st.columns(2)
    
    with outlook_col:
        st.markdown("### 🔮 Investment Outlook")
        st.info(report['investment_outlook'])
    
    with risk_col:
        st.markdown("### ⚠️ Risk Assessment")
        risk_assessment = report['risk_assessment']
        if "Low risk" in risk_assessment:
            st.success(risk_assessment)
        elif "High risk" in risk_assessment:
            st.error(risk_assessment)
        else:
            st.warning(risk_assessment)

def display_help_tab():
    """Help tab with indicator explanations and trading guide"""
    st.subheader("📚 Technical Indicators Guide")
    
    st.markdown("""
    Welcome to your comprehensive guide for understanding technical indicators! 
    This section explains what each indicator means and how to use it for better trading decisions.
    """)
    
    # Indicator categories
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Trend Indicators")
        st.markdown("*These show the direction and strength of price trends*")
        
        with st.expander("📊 Simple Moving Average (SMA)", expanded=False):
            explanation = get_indicator_explanation("SMA")
            st.markdown(format_explanation_for_display("SMA", explanation))
        
        with st.expander("📈 Exponential Moving Average (EMA)", expanded=False):
            explanation = get_indicator_explanation("EMA")
            st.markdown(format_explanation_for_display("EMA", explanation))
        
        with st.expander("📉 MACD (Moving Average Convergence Divergence)", expanded=False):
            explanation = get_indicator_explanation("MACD")
            st.markdown(format_explanation_for_display("MACD", explanation))
    
    with col2:
        st.markdown("### ⚡ Momentum Indicators")
        st.markdown("*These measure the speed and strength of price movements*")
        
        with st.expander("🎯 RSI (Relative Strength Index)", expanded=False):
            explanation = get_indicator_explanation("RSI")
            st.markdown(format_explanation_for_display("RSI", explanation))
        
        with st.expander("📊 Stochastic Oscillator", expanded=False):
            explanation = get_indicator_explanation("Stochastic")
            st.markdown(format_explanation_for_display("Stochastic", explanation))
        
        with st.expander("📈 Williams %R", expanded=False):
            explanation = get_indicator_explanation("Williams %R")
            st.markdown(format_explanation_for_display("Williams %R", explanation))
    
    # Volatility and Support/Resistance
    st.markdown("### 🌪️ Volatility & Price Level Indicators")
    
    col3, col4 = st.columns(2)
    
    with col3:
        with st.expander("📏 Bollinger Bands", expanded=False):
            explanation = get_indicator_explanation("Bollinger Bands")
            st.markdown(format_explanation_for_display("Bollinger Bands", explanation))
        
        with st.expander("📊 ATR (Average True Range)", expanded=False):
            explanation = get_indicator_explanation("ATR")
            st.markdown(format_explanation_for_display("ATR", explanation))
    
    with col4:
        with st.expander("🏗️ Support & Resistance", expanded=False):
            explanation = get_indicator_explanation("Support/Resistance")
            st.markdown(format_explanation_for_display("Support/Resistance", explanation))
        
        with st.expander("📦 Volume Analysis", expanded=False):
            explanation = get_indicator_explanation("Volume")
            st.markdown(format_explanation_for_display("Volume", explanation))
    
    st.divider()
    
    # Trading Strategy Guide
    st.markdown("### 🎯 Smart Trading Strategies")
    
    col_strategy1, col_strategy2 = st.columns(2)
    
    with col_strategy1:
        st.markdown("""
        **🚀 Bullish Signal Confirmation:**
        - RSI recovering from oversold (below 30)
        - MACD crossing above signal line
        - Price breaking above resistance
        - Volume increasing on price rise
        - Multiple indicators aligning
        """)
        
        st.markdown("""
        **🛑 Risk Management:**
        - Use ATR for stop-loss placement (2x ATR)
        - Never risk more than 2% per trade
        - Set profit targets at resistance levels
        - Trail stops as profit increases
        """)
    
    with col_strategy2:
        st.markdown("""
        **🔴 Bearish Signal Warning:**
        - RSI showing overbought (above 70)
        - MACD crossing below signal line
        - Price failing at resistance
        - Volume declining on price rise
        - Divergences between price and indicators
        """)
        
        st.markdown("""
        **📊 Multi-Timeframe Analysis:**
        - Check daily charts for overall trend
        - Use hourly for entry timing
        - Align signals across timeframes
        - Higher timeframe trend takes priority
        """)
    
    st.divider()
    
    # Alert System Guide
    st.markdown("### 🚨 Smart Alert System Guide")
    
    st.markdown("""
    **Your platform includes an intelligent alert system that monitors stocks for bullish reversals:**
    
    ✅ **How Bullish Reversal Alerts Work:**
    - Monitors sentiment changes from bearish/neutral to bullish
    - Requires minimum 3 bullish indicators for confirmation
    - Automatically calculates stop-loss using ATR (safer method)
    - Sets dual profit targets (15% and 30%)
    - Sends SMS/email notifications instantly
    
    🎯 **Setting Up Your First Alert:**
    1. Analyze any stock using the platform
    2. Go to the "🚨 Alerts" tab
    3. Add your phone number for SMS alerts
    4. Click "Add to Watchlist"
    5. Platform monitors 24/7 for bullish changes
    
    📱 **Types of Alerts You'll Receive:**
    - **Bullish Reversal:** When sentiment flips to bullish with auto-calculated levels
    - **Stop Loss Hit:** When price touches your calculated stop loss
    - **Target Hit:** When price reaches your profit targets (Target 1: +15%, Target 2: +30%)
    """)
    
    st.info("""
    💡 **Pro Tip:** The platform uses ATR-based stop losses which adapt to each stock's volatility, 
    providing better protection than fixed percentage stops. This helps avoid being stopped out by normal market noise!
    """)

def display_multi_stock_analysis(symbols_list, period, sma_period, ema_period, rsi_period, bb_period, bb_std, atr_period):
    """Display comprehensive analysis for multiple stocks"""
    st.subheader(f"📊 Multi-Stock Technical Analysis: {', '.join(symbols_list)}")
    
    # Limit to 5 stocks for performance
    symbols_list = symbols_list[:5]
    
    analysis_results = {}
    comparison_data = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, symbol in enumerate(symbols_list):
        status_text.text(f"Analyzing {symbol}... ({i+1}/{len(symbols_list)})")
        progress_bar.progress((i + 1) / len(symbols_list))
        
        try:
            # Fetch data
            data_fetcher = DataFetcher()
            stock_data = data_fetcher.fetch_stock_data(symbol, period)
            
            if stock_data is None or stock_data.empty:
                st.warning(f"No data found for {symbol}")
                continue
            
            # Technical analysis
            ta = TechnicalAnalysis()
            tech_analysis = ta.calculate_all_indicators(
                stock_data,
                sma_period=sma_period,
                ema_period=ema_period,
                rsi_period=rsi_period,
                bb_period=bb_period,
                bb_std=bb_std,
                atr_period=atr_period
            )
            
            # Generate decision
            decision_engine = DecisionEngine()
            decision_data = decision_engine.generate_decision(tech_analysis)
            
            # Enhanced analysis
            enhanced_analyzer = EnhancedAnalysis()
            individual_indicators = enhanced_analyzer.analyze_individual_indicators(tech_analysis)
            threshold_summary = enhanced_analyzer.generate_threshold_summary(individual_indicators)
            
            current_price = stock_data['Close'].iloc[-1]
            price_change = ((current_price / stock_data['Close'].iloc[-2]) - 1) * 100 if len(stock_data) > 1 else 0
            
            # Store detailed results
            analysis_results[symbol] = {
                'stock_data': stock_data,
                'technical_analysis': tech_analysis,
                'analysis_data': tech_analysis,  # Include for trading levels display
                'decision_data': decision_data,
                'individual_indicators': individual_indicators,
                'threshold_summary': threshold_summary,
                'current_price': current_price,
                'price_change': price_change
            }
            
            # Prepare comparison data
            rsi_value = tech_analysis['RSI'].iloc[-1] if 'RSI' in tech_analysis.columns else 0
            macd_value = tech_analysis['MACD'].iloc[-1] if 'MACD' in tech_analysis.columns else 0
            
            comparison_data.append({
                'Symbol': symbol,
                'Price': f"${current_price:.2f}",
                'Change %': f"{price_change:+.2f}%",
                'Decision': decision_data['decision'],
                'Confidence': f"{decision_data['confidence']:.0f}%",
                'RSI': f"{rsi_value:.1f}",
                'MACD': f"{macd_value:.3f}",
                'Bullish Signals': threshold_summary.get('bullish_count', 0) if threshold_summary else 0,
                'Bearish Signals': threshold_summary.get('bearish_count', 0) if threshold_summary else 0,
                'Overall Sentiment': threshold_summary.get('overall_sentiment', 'Unknown') if threshold_summary else 'Unknown'
            })
            
        except Exception as e:
            st.warning(f"Could not analyze {symbol}: {str(e)}")
            continue
    
    progress_bar.empty()
    status_text.empty()
    
    if not comparison_data:
        st.error("Could not analyze any of the selected stocks. Please check the symbols and try again.")
        return
    
    # Display comparison table
    st.markdown("### 📋 Technical Analysis Comparison")
    
    df = pd.DataFrame(comparison_data)
    
    # Color-code decisions
    def highlight_cells(val):
        if 'Buy' in str(val):
            return 'background-color: #d4edda; color: #155724; font-weight: bold'
        elif 'Sell' in str(val):
            return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
        elif 'Hold' in str(val):
            return 'background-color: #d1ecf1; color: #0c5460; font-weight: bold'
        return ''
    
    styled_df = df.style.map(highlight_cells, subset=['Decision', 'Overall Sentiment'])
    st.dataframe(styled_df, use_container_width=True)
    
    # Portfolio summary metrics
    st.markdown("### 📈 Portfolio Analysis Summary")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        buy_count = len([d for d in comparison_data if 'Buy' in d['Decision']])
        st.metric("Buy Signals", buy_count, f"{buy_count/len(comparison_data)*100:.0f}%")
    
    with col2:
        sell_count = len([d for d in comparison_data if 'Sell' in d['Decision']])
        st.metric("Sell Signals", sell_count, f"{sell_count/len(comparison_data)*100:.0f}%")
    
    with col3:
        avg_confidence = sum([float(d['Confidence'].rstrip('%')) for d in comparison_data]) / len(comparison_data)
        st.metric("Avg Confidence", f"{avg_confidence:.0f}%")
    
    with col4:
        positive_count = len([d for d in comparison_data if '+' in d['Change %']])
        st.metric("Positive Movers", positive_count, f"{positive_count/len(comparison_data)*100:.0f}%")
    
    with col5:
        total_bullish = sum([d['Bullish Signals'] for d in comparison_data])
        total_bearish = sum([d['Bearish Signals'] for d in comparison_data])
        bullish_ratio = total_bullish / (total_bullish + total_bearish) * 100 if (total_bullish + total_bearish) > 0 else 0
        st.metric("Bullish Ratio", f"{bullish_ratio:.0f}%")
    
    # Full analysis tabs for multi-stock analysis - matching single stock tabs
    st.markdown("### 🔍 Comprehensive Multi-Stock Analysis")
    
    # Create all the detailed analysis tabs to match single-stock analysis
    mtab1, mtab2, mtab3, mtab4, mtab5, mtab6, mtab7, mtab8, mtab9, mtab10 = st.tabs([
        "📊 Overview", "📈 Technical", "🏢 Sectors", "💰 Financials", 
        "📰 News", "🎯 Options", "📉 Patterns", "🔍 Analysis", "🚨 Alerts", "📚 Help"
    ])
    
    with mtab1:
        # Overview with S&P 500 comparison and individual stock summaries
        st.markdown("#### 📊 Portfolio Overview vs S&P 500")
        
        # Create comparison chart with S&P 500
        try:
            data_fetcher = DataFetcher()
            sp500_data = data_fetcher.fetch_stock_data("^GSPC", period)
            
            if not sp500_data.empty:
                # Create comparison chart
                fig = go.Figure()
                
                # Add S&P 500 as baseline
                sp500_normalized = (sp500_data['Close'] / sp500_data['Close'].iloc[0] - 1) * 100
                fig.add_trace(go.Scatter(
                    x=sp500_data.index,
                    y=sp500_normalized,
                    mode='lines',
                    name='S&P 500',
                    line=dict(color='gray', width=2, dash='dash'),
                    opacity=0.7
                ))
                
                # Add each stock to comparison with signal indicators
                colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
                for i, (symbol, data) in enumerate(analysis_results.items()):
                    stock_data = data['stock_data']
                    if not stock_data.empty:
                        # Normalize to percentage change from start
                        normalized = (stock_data['Close'] / stock_data['Close'].iloc[0] - 1) * 100
                        
                        # Get buy/sell signals
                        buy_signals, sell_signals = count_technical_signals(data)
                        
                        # Determine line style based on performance vs S&P
                        final_perf = normalized.iloc[-1]
                        sp500_final = sp500_normalized.iloc[-1]
                        line_width = 3 if final_perf > sp500_final else 2
                        
                        # Color line based on signal dominance
                        base_color = colors[i % len(colors)]
                        if buy_signals > sell_signals:
                            line_color = base_color
                            opacity = 1.0
                        elif sell_signals > buy_signals:
                            line_color = base_color
                            opacity = 0.7
                        else:
                            line_color = base_color
                            opacity = 0.8
                        
                        fig.add_trace(go.Scatter(
                            x=stock_data.index,
                            y=normalized,
                            mode='lines',
                            name=f'{symbol} ({final_perf:+.1f}%) [B:{buy_signals}/S:{sell_signals}]',
                            line=dict(color=line_color, width=line_width),
                            opacity=opacity
                        ))
                
                fig.update_layout(
                    title=f'Portfolio Performance vs S&P 500 ({period.upper()})',
                    xaxis_title='Date',
                    yaxis_title='Return (%)',
                    height=400,
                    showlegend=True,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True, key="overview_comparison")
                
                # Performance summary table with technical indicators
                summary_data = []
                for symbol, data in analysis_results.items():
                    stock_data = data['stock_data']
                    if not stock_data.empty:
                        period_return = ((stock_data['Close'].iloc[-1] / stock_data['Close'].iloc[0]) - 1) * 100
                        sp500_return = ((sp500_data['Close'].iloc[-1] / sp500_data['Close'].iloc[0]) - 1) * 100
                        outperformance = period_return - sp500_return
                        
                        # Calculate buy/sell signals from technical indicators
                        buy_signals, sell_signals = count_technical_signals(data)
                        total_signals = buy_signals + sell_signals
                        signal_ratio = f"{buy_signals}/{sell_signals}" if total_signals > 0 else "0/0"
                        
                        summary_data.append({
                            'Symbol': symbol,
                            'Buy/Sell Signals': signal_ratio,
                            'Period Return': f'{period_return:+.2f}%',
                            'S&P 500 Return': f'{sp500_return:+.2f}%',
                            'Outperformance': f'{outperformance:+.2f}%',
                            'Current Price': f'${data["current_price"]:.2f}',
                            'Decision': data['decision_data']['decision']
                        })
                
                if summary_data:
                    df_summary = pd.DataFrame(summary_data)
                    
                    def highlight_performance(val):
                        if '+' in str(val) and 'Outperformance' in str(val):
                            return 'background-color: #d4edda; color: #155724'
                        elif '-' in str(val) and 'Outperformance' in str(val):
                            return 'background-color: #f8d7da; color: #721c24'
                        return ''
                    
                    styled_df = df_summary.style.map(highlight_performance)
                    st.dataframe(styled_df, use_container_width=True)
            
        except Exception as e:
            st.warning("Could not load S&P 500 comparison data")
        
        st.markdown("---")
        st.markdown("#### 📋 Individual Stock Analysis")
        
        if len(analysis_results) > 1:
            # Create tabs for each stock
            stock_tab_names = list(analysis_results.keys())
            stock_tabs = st.tabs(stock_tab_names)
            
            for i, (symbol, data) in enumerate(analysis_results.items()):
                with stock_tabs[i]:
                    display_individual_stock_summary(symbol, data)
        else:
            # Single stock detailed view
            symbol, data = list(analysis_results.items())[0]
            display_individual_stock_summary(symbol, data)
    
    with mtab2:
        # Technical indicators comparison across all stocks
        display_technical_indicators_comparison(analysis_results)
    
    with mtab3:
        # Sector analysis for multiple stocks
        display_multi_stock_sector_analysis(analysis_results)
    
    with mtab4:
        # Financial analysis for multiple stocks
        display_multi_stock_financials(analysis_results)
    
    with mtab5:
        # News analysis for multiple stocks
        display_multi_stock_news(analysis_results)
    
    with mtab6:
        # Options analysis for multiple stocks
        display_multi_stock_options(analysis_results)
    
    with mtab7:
        # Pattern analysis for multiple stocks
        display_multi_stock_patterns(analysis_results)
    
    with mtab8:
        # Threshold analysis across stocks
        display_multi_stock_threshold_analysis(analysis_results)
    
    with mtab9:
        # Bulk alerts management
        display_multi_stock_alerts(analysis_results, symbols_list)
    
    with mtab10:
        # Help tab (same as single stock)
        display_help_tab()

def display_individual_stock_summary(symbol, data):
    """Display individual stock analysis summary"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            f"{symbol} Price",
            f"${data['current_price']:.2f}",
            f"{data['price_change']:+.2f}%"
        )
    
    with col2:
        decision = data['decision_data']['decision']
        confidence = data['decision_data']['confidence']
        if 'Buy' in decision:
            st.success(f"📈 {decision} ({confidence:.0f}%)")
        elif 'Sell' in decision:
            st.error(f"📉 {decision} ({confidence:.0f}%)")
        else:
            st.info(f"📊 {decision} ({confidence:.0f}%)")
    
    with col3:
        if data['threshold_summary']:
            bullish = data['threshold_summary'].get('bullish_count', 0)
            bearish = data['threshold_summary'].get('bearish_count', 0)
            st.write(f"**Signals:** {bullish} Bullish, {bearish} Bearish")
        
    # Key indicators
    if data['individual_indicators']:
        st.markdown("**Key Technical Indicators:**")
        
        indicators_col1, indicators_col2 = st.columns(2)
        
        with indicators_col1:
            for indicator, analysis in list(data['individual_indicators'].items())[:3]:
                if isinstance(analysis, dict):
                    status = analysis.get('status', analysis.get('signal', 'Unknown'))
                    value = analysis.get('current_value', 0)
                    
                    if 'Bullish' in str(status) or 'Buy' in str(status):
                        st.success(f"**{indicator}:** {value:.2f} - {status}")
                    elif 'Bearish' in str(status) or 'Sell' in str(status):
                        st.error(f"**{indicator}:** {value:.2f} - {status}")
                    else:
                        st.info(f"**{indicator}:** {value:.2f} - {status}")
        
        with indicators_col2:
            remaining_indicators = list(data['individual_indicators'].items())[3:6]
            for indicator, analysis in remaining_indicators:
                if isinstance(analysis, dict):
                    status = analysis.get('status', analysis.get('signal', 'Unknown'))
                    value = analysis.get('current_value', 0)
                    
                    if 'Bullish' in str(status) or 'Buy' in str(status):
                        st.success(f"**{indicator}:** {value:.2f} - {status}")
                    elif 'Bearish' in str(status) or 'Sell' in str(status):
                        st.error(f"**{indicator}:** {value:.2f} - {status}")
                    else:
                        st.info(f"**{indicator}:** {value:.2f} - {status}")
    
    # Trading levels section
    st.markdown("**Trading Levels:**")
    if 'analysis_data' in data and not data['analysis_data'].empty:
        latest_data = data['analysis_data'].iloc[-1]
        
        levels_col1, levels_col2, levels_col3 = st.columns(3)
        
        with levels_col1:
            support = latest_data.get('Support_Level', data['current_price'] * 0.95)
            resistance = latest_data.get('Resistance_Level', data['current_price'] * 1.05)
            st.metric("Support", f"${support:.2f}", 
                     f"{((support / data['current_price']) - 1) * 100:+.1f}%")
            st.metric("Resistance", f"${resistance:.2f}", 
                     f"{((resistance / data['current_price']) - 1) * 100:+.1f}%")
        
        with levels_col2:
            stop_loss = latest_data.get('Stop_Loss', data['current_price'] * 0.92)
            short_target = latest_data.get('Short_Term_Target', data['current_price'] * 1.03)
            st.metric("Stop Loss", f"${stop_loss:.2f}", 
                     f"{((stop_loss / data['current_price']) - 1) * 100:+.1f}%")
            st.metric("Short Target", f"${short_target:.2f}", 
                     f"{((short_target / data['current_price']) - 1) * 100:+.1f}%")
        
        with levels_col3:
            long_target = latest_data.get('Long_Term_Target', data['current_price'] * 1.08)
            atr = latest_data.get('ATR', data['current_price'] * 0.02)
            st.metric("Long Target", f"${long_target:.2f}", 
                     f"{((long_target / data['current_price']) - 1) * 100:+.1f}%")
            st.metric("ATR (Volatility)", f"${atr:.2f}", 
                     f"{(atr / data['current_price']) * 100:.1f}%")
    
    # Risk/Reward Analysis
    st.markdown("**Risk/Reward Analysis:**")
    if 'analysis_data' in data and not data['analysis_data'].empty:
        latest_data = data['analysis_data'].iloc[-1]
        current_price = data['current_price']
        
        stop_loss = latest_data.get('Stop_Loss', current_price * 0.92)
        short_target = latest_data.get('Short_Term_Target', current_price * 1.03)
        long_target = latest_data.get('Long_Term_Target', current_price * 1.08)
        
        risk = current_price - stop_loss
        short_reward = short_target - current_price
        long_reward = long_target - current_price
        
        rr_col1, rr_col2 = st.columns(2)
        with rr_col1:
            if risk > 0:
                short_rr = short_reward / risk if risk > 0 else 0
                st.write(f"**Short-term R/R:** {short_rr:.2f}:1")
        with rr_col2:
            if risk > 0:
                long_rr = long_reward / risk if risk > 0 else 0
                st.write(f"**Long-term R/R:** {long_rr:.2f}:1")
    
    # Quick chart
    st.markdown("**Price Chart:**")
    chart_generator = ChartGenerator()
    fig = chart_generator.create_simple_price_chart(data['stock_data'], symbol)
    st.plotly_chart(fig, use_container_width=True, key=f"summary_chart_{symbol}")

def display_technical_indicators_comparison(analysis_results):
    """Display technical indicators comparison across multiple stocks"""
    st.markdown("#### 📈 Technical Indicators Comparison")
    
    # Create comparison table for key indicators
    indicators_data = []
    
    for symbol, data in analysis_results.items():
        tech_analysis = data['technical_analysis']
        
        if tech_analysis is not None and not tech_analysis.empty:
            latest_row = tech_analysis.iloc[-1]
            
            indicators_data.append({
                'Symbol': symbol,
                'RSI': f"{latest_row.get('RSI', 0):.1f}",
                'MACD': f"{latest_row.get('MACD', 0):.3f}",
                'SMA_20': f"${latest_row.get('SMA_20', 0):.2f}",
                'EMA_20': f"${latest_row.get('EMA_20', 0):.2f}",
                'BB_Upper': f"${latest_row.get('BB_Upper', 0):.2f}",
                'BB_Lower': f"${latest_row.get('BB_Lower', 0):.2f}",
                'ATR': f"{latest_row.get('ATR', 0):.2f}",
                'Volume': f"{latest_row.get('Volume', 0):,.0f}"
            })
    
    if indicators_data:
        df_indicators = pd.DataFrame(indicators_data)
        st.dataframe(df_indicators, use_container_width=True)
        
        # RSI comparison chart
        st.markdown("**RSI Comparison:**")
        rsi_data = {row['Symbol']: float(row['RSI']) for row in indicators_data}
        
        col1, col2, col3 = st.columns(3)
        for i, (symbol, rsi_val) in enumerate(rsi_data.items()):
            col = [col1, col2, col3][i % 3]
            with col:
                if rsi_val > 70:
                    st.error(f"{symbol}: {rsi_val:.1f} (Overbought)")
                elif rsi_val < 30:
                    st.success(f"{symbol}: {rsi_val:.1f} (Oversold)")
                else:
                    st.info(f"{symbol}: {rsi_val:.1f} (Neutral)")

def display_multi_stock_sector_analysis(analysis_results):
    """Display sector analysis for multiple stocks"""
    st.markdown("#### 🏢 Sector Analysis")
    
    # Get sector information for each stock
    sector_data = []
    
    for symbol, data in analysis_results.items():
        try:
            stock_info = yf.Ticker(symbol).info
            sector = stock_info.get('sector', 'Unknown')
            industry = stock_info.get('industry', 'Unknown')
            market_cap = stock_info.get('marketCap', 0)
            
            sector_data.append({
                'Symbol': symbol,
                'Sector': sector,
                'Industry': industry,
                'Market Cap': f"${market_cap/1e9:.1f}B" if market_cap > 0 else "N/A",
                'Decision': data['decision_data']['decision'],
                'Price': f"${data['current_price']:.2f}"
            })
        except:
            sector_data.append({
                'Symbol': symbol,
                'Sector': 'Unknown',
                'Industry': 'Unknown', 
                'Market Cap': 'N/A',
                'Decision': data['decision_data']['decision'],
                'Price': f"${data['current_price']:.2f}"
            })
    
    if sector_data:
        df_sectors = pd.DataFrame(sector_data)
        st.dataframe(df_sectors, use_container_width=True)
        
        # Sector distribution
        sector_counts = {}
        for item in sector_data:
            sector = item['Sector']
            if sector != 'Unknown':
                sector_counts[sector] = sector_counts.get(sector, 0) + 1
        
        if sector_counts:
            st.markdown("**Sector Distribution:**")
            for sector, count in sector_counts.items():
                st.write(f"• {sector}: {count} stock(s)")

def display_multi_stock_charts(analysis_results):
    """Display quick charts for all analyzed stocks"""
    st.markdown("#### 📱 Quick Price Charts")
    
    # Display charts in a grid
    if len(analysis_results) <= 2:
        cols = st.columns(len(analysis_results))
    else:
        cols = st.columns(2)
    
    chart_generator = ChartGenerator()
    
    for i, (symbol, data) in enumerate(analysis_results.items()):
        col_idx = i % len(cols)
        
        with cols[col_idx]:
            st.markdown(f"**{symbol}**")
            
            # Price and change
            price_change = data['price_change']
            if price_change > 0:
                st.success(f"${data['current_price']:.2f} (+{price_change:.2f}%)")
            elif price_change < 0:
                st.error(f"${data['current_price']:.2f} ({price_change:.2f}%)")
            else:
                st.info(f"${data['current_price']:.2f} ({price_change:.2f}%)")
            
            # Quick chart
            fig = chart_generator.create_simple_price_chart(data['stock_data'], symbol)
            st.plotly_chart(fig, use_container_width=True, key=f"chart_{symbol}_{i}")
            
            # Decision
            decision = data['decision_data']['decision']
            confidence = data['decision_data']['confidence']
            
            if 'Buy' in decision:
                st.success(f"Decision: {decision} ({confidence:.0f}%)")
            elif 'Sell' in decision:
                st.error(f"Decision: {decision} ({confidence:.0f}%)")
            else:
                st.info(f"Decision: {decision} ({confidence:.0f}%)")

def display_multi_stock_financials(analysis_results):
    """Display financial analysis for multiple stocks"""
    st.markdown("#### 💰 Financial Analysis Comparison")
    
    financial_data = []
    for symbol, data in analysis_results.items():
        try:
            ticker = yf.Ticker(symbol)
            stock_info = ticker.info
            
            # Get financial statements for more detailed data
            try:
                financials = ticker.financials
                balance_sheet = ticker.balance_sheet
                
                # Extract latest year data
                if not financials.empty and len(financials.columns) > 0:
                    latest_year = financials.columns[0]
                    prev_year = financials.columns[1] if len(financials.columns) > 1 else None
                    
                    total_revenue = financials.loc['Total Revenue', latest_year] if 'Total Revenue' in financials.index else 0
                    net_income = financials.loc['Net Income', latest_year] if 'Net Income' in financials.index else 0
                    
                    # Calculate YoY changes
                    revenue_yoy = 0
                    income_yoy = 0
                    if prev_year is not None:
                        prev_revenue = financials.loc['Total Revenue', prev_year] if 'Total Revenue' in financials.index else 0
                        prev_income = financials.loc['Net Income', prev_year] if 'Net Income' in financials.index else 0
                        
                        if prev_revenue > 0:
                            revenue_yoy = ((total_revenue / prev_revenue) - 1) * 100
                        if prev_income != 0:
                            income_yoy = ((net_income / prev_income) - 1) * 100
                else:
                    total_revenue = stock_info.get('totalRevenue', 0)
                    net_income = 0
                    revenue_yoy = stock_info.get('revenueGrowth', 0) * 100 if stock_info.get('revenueGrowth') else 0
                    income_yoy = 0
                
                # Get liabilities from balance sheet
                total_liabilities = 0
                if not balance_sheet.empty and len(balance_sheet.columns) > 0:
                    latest_bs = balance_sheet.columns[0]
                    total_liabilities = balance_sheet.loc['Total Liab', latest_bs] if 'Total Liab' in balance_sheet.index else 0
                
            except:
                # Fallback to basic info
                total_revenue = stock_info.get('totalRevenue', 0)
                net_income = 0
                revenue_yoy = stock_info.get('revenueGrowth', 0) * 100 if stock_info.get('revenueGrowth') else 0
                income_yoy = 0
                total_liabilities = 0
            
            financial_data.append({
                'Symbol': symbol,
                'Price': f"${data['current_price']:.2f}",
                'Change %': f"{data['price_change']:+.2f}%",
                'Market Cap': f"${stock_info.get('marketCap', 0)/1e9:.1f}B" if stock_info.get('marketCap') else "N/A",
                'P/E Ratio': f"{stock_info.get('trailingPE', 0):.2f}" if stock_info.get('trailingPE') else "N/A",
                'Fwd P/E': f"{stock_info.get('forwardPE', 0):.2f}" if stock_info.get('forwardPE') else "N/A",
                'Revenue': f"${total_revenue/1e9:.1f}B" if total_revenue > 0 else "N/A",
                'Revenue YoY': f"{revenue_yoy:+.1f}%" if revenue_yoy != 0 else "N/A",
                'Net Income': f"${net_income/1e9:.1f}B" if net_income > 0 else f"${net_income/1e9:.1f}B" if net_income < 0 else "N/A",
                'Income YoY': f"{income_yoy:+.1f}%" if income_yoy != 0 else "N/A",
                'Total Liabilities': f"${total_liabilities/1e9:.1f}B" if total_liabilities > 0 else "N/A"
            })
        except Exception as e:
            financial_data.append({
                'Symbol': symbol,
                'Price': f"${data['current_price']:.2f}",
                'Change %': f"{data['price_change']:+.2f}%",
                'Market Cap': "N/A",
                'P/E Ratio': "N/A",
                'Fwd P/E': "N/A", 
                'Revenue': "N/A",
                'Revenue YoY': "N/A",
                'Net Income': "N/A",
                'Income YoY': "N/A",
                'Total Liabilities': "N/A"
            })
    
    if financial_data:
        df_financial = pd.DataFrame(financial_data)
        st.dataframe(df_financial, use_container_width=True)
        
        # Add sector P/E comparison for each stock
        st.markdown("#### 🏭 Sector P/E Comparison")
        
        for symbol, data in analysis_results.items():
            try:
                from financial_data import FinancialData
                financial_data_obj = FinancialData()
                pe_comparison = financial_data_obj.get_sector_pe_comparison(symbol)
                
                if pe_comparison and pe_comparison.get('current_pe', 0) > 0:
                    with st.expander(f"{symbol} - Valuation vs Peers"):
                        pe_col1, pe_col2, pe_col3, pe_col4 = st.columns(4)
                        
                        with pe_col1:
                            current_pe = pe_comparison.get('current_pe', 0)
                            st.metric("Current P/E", f"{current_pe:.1f}")
                        
                        with pe_col2:
                            sector_pe = pe_comparison.get('sector_pe', 0)
                            sector_name = pe_comparison.get('sector', 'Sector')
                            st.metric(f"{sector_name} Avg", f"{sector_pe:.1f}")
                        
                        with pe_col3:
                            vs_sector = pe_comparison.get('pe_vs_sector_pct', 0)
                            st.metric("vs Sector", f"{vs_sector:+.1f}%", 
                                     delta_color="inverse" if vs_sector > 0 else "normal")
                        
                        with pe_col4:
                            assessment = pe_comparison.get('valuation_assessment', 'Unknown')
                            if "Overvalued" in assessment:
                                st.error(f"📈 {assessment}")
                            elif "Undervalued" in assessment:
                                st.success(f"📉 {assessment}")
                            else:
                                st.info(f"⚖️ {assessment}")
                        
                        # Industry comparison
                        industry_col1, industry_col2 = st.columns(2)
                        with industry_col1:
                            industry_name = pe_comparison.get('industry', 'Unknown')
                            st.write(f"**Industry:** {industry_name}")
                        with industry_col2:
                            vs_industry = pe_comparison.get('pe_vs_industry_pct', 0)
                            st.write(f"**vs Industry:** {vs_industry:+.1f}%")
            except:
                continue

def display_multi_stock_news(analysis_results):
    """Display news analysis for multiple stocks"""
    st.markdown("#### 📰 News & Sentiment Analysis")
    
    for symbol, data in analysis_results.items():
        with st.expander(f"📰 {symbol} News & Sentiment"):
            try:
                financial_analyzer = FinancialData()
                latest_news = financial_analyzer.get_latest_news(symbol, limit=5)
                
                if latest_news:
                    for i, news in enumerate(latest_news):
                        st.markdown(f"**{news.get('title', 'No title')}**")
                        
                        # Display publisher and publication date
                        col1, col2 = st.columns(2)
                        with col1:
                            st.caption(f"Publisher: {news.get('publisher', 'Unknown')}")
                        with col2:
                            if news.get('published'):
                                st.caption(f"Published: {news['published'].strftime('%Y-%m-%d %H:%M')}")
                            else:
                                st.caption("Published: Unknown date")
                        
                        # Display summary
                        if news.get('summary'):
                            st.write(news['summary'][:300] + "..." if len(news.get('summary', '')) > 300 else news.get('summary'))
                        else:
                            st.caption("No summary available")
                        
                        # Display link if available
                        if news.get('link'):
                            st.markdown(f"[Read full article]({news['link']})")
                        
                        if i < len(latest_news) - 1:
                            st.markdown("---")
                else:
                    st.info(f"No recent news found for {symbol}")
                    st.markdown("**Alternative News Sources:**")
                    st.markdown(f"- [Yahoo Finance {symbol}](https://finance.yahoo.com/quote/{symbol}/news)")
                    st.markdown(f"- [MarketWatch {symbol}](https://www.marketwatch.com/investing/stock/{symbol})")
                    st.markdown(f"- [Seeking Alpha {symbol}](https://seekingalpha.com/symbol/{symbol}/news)")
                    
            except Exception as e:
                st.warning(f"News data unavailable for {symbol}")
                st.markdown("**Alternative News Sources:**")
                st.markdown(f"- [Yahoo Finance {symbol}](https://finance.yahoo.com/quote/{symbol}/news)")
                st.markdown(f"- [MarketWatch {symbol}](https://www.marketwatch.com/investing/stock/{symbol})")
                st.markdown(f"- [Seeking Alpha {symbol}](https://seekingalpha.com/symbol/{symbol}/news)")

def display_multi_stock_options(analysis_results):
    """Display options analysis for multiple stocks"""
    st.markdown("#### 🎯 Options Analysis Comparison")
    
    for symbol, data in analysis_results.items():
        with st.expander(f"🎯 {symbol} Options Analysis"):
            try:
                from options_analysis import OptionsAnalysis
                options_analyzer = OptionsAnalysis()
                current_price = data['current_price']
                
                # Get volatility from technical analysis if available
                volatility = 0.25  # Default
                if 'analysis_data' in data and data['analysis_data'] is not None:
                    try:
                        if 'Volatility' in data['analysis_data'].columns:
                            volatility = data['analysis_data']['Volatility'].iloc[-1]
                    except:
                        pass
                
                # Get options strategies
                strategies = options_analyzer.analyze_option_strategies(symbol, current_price, volatility)
                profitable_strikes = options_analyzer.get_profitable_strikes(symbol, current_price, volatility)
                
                if strategies and len(strategies) > 0:
                    st.write(f"**Current Price:** ${current_price:.2f}")
                    st.write(f"**Volatility:** {volatility*100:.1f}%")
                    st.markdown("---")
                    
                    # Display strategies
                    st.markdown("**📋 Recommended Strategies:**")
                    for i, strategy in enumerate(strategies):
                        if isinstance(strategy, dict):
                            strategy_name = strategy.get('strategy', f'Strategy {i+1}')
                            strike = strategy.get('strike', 0)
                            max_profit = strategy.get('max_profit', 'N/A')
                            max_loss = strategy.get('max_loss', 'N/A')
                            breakeven = strategy.get('breakeven', 0)
                            
                            st.write(f"• **{strategy_name}** (Strike: ${strike:.2f})")
                            st.write(f"  Max Profit: {max_profit} | Max Loss: {max_loss}")
                            if breakeven > 0:
                                st.write(f"  Breakeven: ${breakeven:.2f}")
                            st.write("")
                    
                    # Display profitable strikes
                    if profitable_strikes and len(profitable_strikes) > 0:
                        st.markdown("**💰 Profitable Strike Prices:**")
                        for strike_info in profitable_strikes:
                            if isinstance(strike_info, dict):
                                strike_price = strike_info.get('strike', 0)
                                option_type = strike_info.get('type', 'Unknown')
                                profit_potential = strike_info.get('profit_potential', 'N/A')
                                probability = strike_info.get('probability', 0)
                                
                                st.write(f"• **${strike_price:.2f} {option_type}**")
                                st.write(f"  Profit Potential: {profit_potential}")
                                st.write(f"  Success Probability: {probability*100:.1f}%")
                                st.write("")
                else:
                    st.info(f"Options strategies calculation in progress for {symbol}")
                    
            except Exception as e:
                st.warning(f"Options analysis temporarily unavailable for {symbol}")
                st.write("This may be due to market hours or data availability.")

def display_multi_stock_patterns(analysis_results):
    """Display pattern analysis for multiple stocks"""
    st.markdown("#### 📉 Chart Pattern Analysis")
    
    for symbol, data in analysis_results.items():
        with st.expander(f"📉 {symbol} Pattern Analysis"):
            try:
                pattern_analyzer = PatternRecognition()
                patterns = pattern_analyzer.analyze_all_patterns(data['stock_data'])
                
                if patterns:
                    for pattern_name, pattern_data in patterns.items():
                        if isinstance(pattern_data, dict) and pattern_data.get('detected'):
                            st.success(f"✅ {pattern_name} detected")
                            st.write(f"Confidence: {pattern_data.get('confidence', 'N/A')}")
                        else:
                            st.info(f"❌ {pattern_name} not detected")
                else:
                    st.info(f"No patterns analyzed for {symbol}")
            except:
                st.warning(f"Pattern analysis unavailable for {symbol}")

def display_multi_stock_threshold_analysis(analysis_results):
    """Display threshold analysis across stocks"""
    st.markdown("#### 🔍 Threshold Analysis Summary")
    
    threshold_data = []
    for symbol, data in analysis_results.items():
        if data.get('threshold_summary'):
            threshold_summary = data['threshold_summary']
            threshold_data.append({
                'Symbol': symbol,
                'Overall Sentiment': threshold_summary.get('overall_sentiment', 'Unknown'),
                'Bullish Signals': threshold_summary.get('bullish_count', 0),
                'Bearish Signals': threshold_summary.get('bearish_count', 0),
                'Decision': data['decision_data']['decision'],
                'Confidence': f"{data['decision_data']['confidence']:.0f}%"
            })
    
    if threshold_data:
        df_threshold = pd.DataFrame(threshold_data)
        
        def highlight_sentiment(val):
            if 'Bullish' in str(val):
                return 'background-color: #d4edda; color: #155724'
            elif 'Bearish' in str(val):
                return 'background-color: #f8d7da; color: #721c24'
            else:
                return 'background-color: #d1ecf1; color: #0c5460'
        
        styled_df = df_threshold.style.map(highlight_sentiment, subset=['Overall Sentiment', 'Decision'])
        st.dataframe(styled_df, use_container_width=True)

def display_multi_stock_alerts(analysis_results, symbols_list):
    """Display bulk alerts management for multiple stocks"""
    st.markdown("#### 🚨 Bulk Alerts Management")
    
    alert_system = AlertSystem()
    
    st.markdown(f"**Add all {len(symbols_list)} stocks to watchlist:**")
    
    with st.form("bulk_alerts_form"):
        st.markdown("**Contact Information for Alerts:**")
        
        col1, col2 = st.columns(2)
        with col1:
            bulk_phone = st.text_input("Phone Number", placeholder="+1234567890")
        with col2:
            bulk_email = st.text_input("Email Address", placeholder="your@email.com")
        
        if st.form_submit_button("🚨 Add All to Watchlist", type="primary"):
            if not bulk_phone and not bulk_email:
                st.error("Please provide at least a phone number or email for alerts.")
            else:
                success_count = 0
                for symbol in symbols_list:
                    try:
                        if alert_system.add_to_watchlist(symbol, bulk_phone or None, bulk_email or None):
                            success_count += 1
                    except:
                        continue
                
                if success_count > 0:
                    st.success(f"✅ Added {success_count} stocks to watchlist!")
                else:
                    st.error("Failed to add stocks to watchlist.")
    
    # Show current watchlist
    watchlist = alert_system.get_watchlist()
    if watchlist:
        st.markdown("**Current Watchlist:**")
        for symbol in watchlist.keys():
            if symbol in symbols_list:
                st.success(f"✅ {symbol} - Already in watchlist")
            else:
                st.info(f"📊 {symbol} - In watchlist")

def count_technical_signals(data):
    """Count buy and sell signals from technical indicators"""
    try:
        analysis_data = data.get('analysis_data')
        current_price = data.get('current_price', 0)
        
        if analysis_data is None or analysis_data.empty:
            return 0, 0
        
        buy_signals = 0
        sell_signals = 0
        
        # Get latest values
        latest = analysis_data.iloc[-1]
        
        # RSI signals
        rsi = latest.get('RSI', 50)
        if rsi < 30:  # Oversold - potential buy
            buy_signals += 1
        elif rsi > 70:  # Overbought - potential sell
            sell_signals += 1
        
        # Moving Average signals
        sma_20 = latest.get('SMA_20', current_price)
        sma_50 = latest.get('SMA_50', current_price)
        ema_20 = latest.get('EMA_20', current_price)
        
        if current_price > sma_20 and current_price > sma_50:
            buy_signals += 1
        elif current_price < sma_20 and current_price < sma_50:
            sell_signals += 1
            
        if current_price > ema_20:
            buy_signals += 1
        else:
            sell_signals += 1
        
        # MACD signals
        macd = latest.get('MACD', 0)
        macd_signal = latest.get('MACD_Signal', 0)
        if macd > macd_signal:
            buy_signals += 1
        else:
            sell_signals += 1
        
        # Bollinger Bands signals
        bb_upper = latest.get('BB_Upper', current_price)
        bb_lower = latest.get('BB_Lower', current_price)
        if current_price < bb_lower:  # Below lower band - potential buy
            buy_signals += 1
        elif current_price > bb_upper:  # Above upper band - potential sell
            sell_signals += 1
        
        # Volume analysis
        volume = latest.get('Volume', 0)
        avg_volume = analysis_data['Volume'].rolling(20).mean().iloc[-1] if len(analysis_data) >= 20 else volume
        if volume > avg_volume * 1.5:  # High volume can support price moves
            if current_price > sma_20:
                buy_signals += 1
            else:
                sell_signals += 1
        
        return buy_signals, sell_signals
        
    except Exception as e:
        return 0, 0

def display_stock_comparison(symbols_list, period):
    """Display side-by-side comparison of multiple stocks"""
    display_multi_stock_analysis(symbols_list, period, 20, 20, 14, 20, 2, 14)

    # Educational Videos Section at Bottom
    st.markdown("---")
    st.markdown("### 📚 Educational Trading Videos")
    
    # Create 3x2 grid for educational videos
    col1, col2, col3 = st.columns(3)
    
    # First row
    with col1:
        st.markdown("**📊 RSI Trading Strategy**")
        st.video("https://www.youtube.com/watch?v=CFIJbOnwqz8")
    
    with col2:
        st.markdown("**📈 MACD Indicator Explained**")
        st.video("https://www.youtube.com/watch?v=MgkuzoDeQL8")
    
    with col3:
        st.markdown("**💹 Moving Averages Guide**")
        st.video("https://www.youtube.com/watch?v=YZH1dr1GCOE")
    
    # Second row
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown("**⚡ Day Trading Live**")
        st.video("https://www.youtube.com/watch?v=na7vN4SUsZk")
    
    with col5:
        st.markdown("**🎯 Swing Trading Strategies**")
        st.video("https://www.youtube.com/watch?v=_LuAa6xzIEU")
    
    with col6:
        st.markdown("**📊 Support & Resistance**")
        st.video("https://www.youtube.com/watch?v=GEhN5FuN6nc")

if __name__ == "__main__":
    main()

def display_bottom_educational_content():
    """Display educational content at the bottom of the page"""
    st.markdown("### 📚 Learn Trading & Quick Tips")
    
    # Create tabs for educational content
    edu_tab1, edu_tab2, edu_tab3 = st.columns(3)
    
    with edu_tab1:
        st.markdown("#### 🎯 Quick Tips")
        st.info("""
        **Trading Essentials:**
        • Start with paper trading
        • Learn one indicator at a time
        • Always use stop losses
        • Never risk more than 2% per trade
        • Keep a trading journal
        """)
    
    with edu_tab2:
        st.markdown("#### 📊 Platform Guide")
        st.success("""
        **Tab Features:**
        • Overview: Key metrics & charts
        • Technical: Individual indicators
        • Sectors: Industry comparison
        • Financials: Company fundamentals
        • News: Market sentiment
        • Options: Strategy analysis
        """)
    
    with edu_tab3:
        st.markdown("#### 🔗 Learning Resources")
        st.markdown("""
        **Educational Links:**
        - [Stock Analysis Basics](https://www.investopedia.com/articles/fundamental-analysis/09/five-must-have-metrics-value-investors.asp)
        - [Technical Indicators Guide](https://www.investopedia.com/articles/active-trading/102914/technical-analysis-strategies-beginners.asp)
        - [Risk Management](https://www.investopedia.com/articles/trading/09/risk-management.asp)
        - [Chart Patterns](https://www.investopedia.com/articles/technical/112601.asp)
        """)
