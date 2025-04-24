import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.market_data import (
    fetch_stock_data, fetch_metal_prices, fetch_historical_data, fetch_sector_performance,
    fetch_top_stocks, fetch_currency_rates, calculate_technical_indicators, INDICES
)

def render_market_insights():
    """
    Render the enhanced Fingyan Market Insights dashboard with professional styling,
    advanced graphs, and data-driven financial advice.
    """
    # Professional Header
    st.markdown("""
        <h1 style='text-align: center; color: #003366; font-family: "Roboto", sans-serif;'>🇮🇳 Fingyan Market Insights</h1>
        <p style='text-align: center; font-size: 20px; color: #666666;'>India's Premier Financial Intelligence Hub</p>
        """, unsafe_allow_html=True)

    # Sidebar - Market Pulse
    with st.sidebar:
        st.markdown("<h2 style='color: #333333;'>Market Pulse</h2>", unsafe_allow_html=True)
        st.info("**NSE Hours:** 9:15 AM - 3:30 PM IST")
        st.markdown(f"**Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.markdown("**Source:** Yahoo Finance (yfinance)")

    # Section 1: Market Snapshot with error handling
    st.subheader("Market Snapshot")
    cols = st.columns(3)
    
    # Fixed index data in case API fails
    fallback_data = {
        'price': 22000.0,
        'change': 150.0,
        'change_percent': 0.68
    }
    
    for i, (name, symbol) in enumerate(INDICES.items()):
        with cols[i % 3]:
            try:
                data = fetch_stock_data(symbol)
                # Add error handling for None data
                if data is None or 'change' not in data:
                    data = fallback_data
                    st.warning(f"Using fallback data for {name}")
                
                color = "#00FF00" if data['change'] >= 0 else "#FF4500"
                st.markdown(
                    f"<h4>{name}</h4><p style='color: {color};'>₹{data['price']:,.2f} ({data['change_percent']:+.2f}%)</p>",
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.error(f"Error loading {name} data: {str(e)}")
                # Use fallback data on error
                color = "#00FF00" if fallback_data['change'] >= 0 else "#FF4500"
                st.markdown(
                    f"<h4>{name}</h4><p style='color: {color};'>₹{fallback_data['price']:,.2f} ({fallback_data['change_percent']:+.2f}%)</p>",
                    unsafe_allow_html=True
                )

    # Section 2: Metals & Forex with error handling
    st.subheader("Metals & Forex")
    col1, col2, col3, col4 = st.columns(4)
    
    # Fallback data for metals and currencies
    fallback_metals = {
        'gold': {'price': 6500.0, 'last_updated': 'Fallback data'},
        'silver': {'price': 75.0, 'last_updated': 'Fallback data'}
    }
    
    fallback_currencies = {
        'USD/INR': 82.50,
        'EUR/INR': 89.75
    }
    
    try:
        metals = fetch_metal_prices()
        if metals is None:
            metals = fallback_metals
            st.warning("Using fallback metal price data")
    except Exception as e:
        st.error(f"Error fetching metal prices: {str(e)}")
        metals = fallback_metals
        
    try:
        currencies = fetch_currency_rates()
        if currencies is None:
            currencies = fallback_currencies
            st.warning("Using fallback currency data")
    except Exception as e:
        st.error(f"Error fetching currency rates: {str(e)}")
        currencies = fallback_currencies
    
    with col1:
        st.metric("Gold (₹/gram)", f"{metals['gold']['price']:,.2f}", metals['gold']['last_updated'])
    with col2:
        st.metric("Silver (₹/gram)", f"{metals['silver']['price']:,.2f}", metals['silver']['last_updated'])
    with col3:
        st.metric("USD/INR", f"₹{currencies['USD/INR']:.2f}", "Live")
    with col4:
        st.metric("EUR/INR", f"₹{currencies['EUR/INR']:.2f}", "Live")

    # Section 3: Sector Performance Heatmap with error handling
    st.subheader("Sector Performance")
    try:
        sector_data = fetch_sector_performance()
        if sector_data and len(sector_data) > 0:
            sector_df = pd.DataFrame.from_dict(sector_data, orient='index')
            fig_sector = go.Figure(data=go.Heatmap(
                z=sector_df['change_percent'],
                x=sector_df.index,
                y=['Change %'],
                colorscale='RdYlGn',
                zmin=-5, zmax=5,
                text=sector_df['change_percent'].apply(lambda x: f"{x:.2f}%"),
                texttemplate="%{text}",
                hoverinfo="x+z"
            ))
            fig_sector.update_layout(title="Sector Daily Change (%)", height=300, template="plotly_dark")
            st.plotly_chart(fig_sector, use_container_width=True)
        else:
            # Fallback sector data
            st.warning("Unable to fetch sector data. Displaying fallback visualization.")
            sectors = ['IT', 'Banking', 'Pharma', 'Auto', 'FMCG', 'Energy', 'Realty']
            changes = [1.2, -0.8, 0.5, 1.5, -0.3, 2.1, -1.2]
            
            sector_df = pd.DataFrame({
                'sector': sectors,
                'change_percent': changes
            }).set_index('sector')
            
            fig_sector = go.Figure(data=go.Heatmap(
                z=sector_df['change_percent'],
                x=sector_df.index,
                y=['Change %'],
                colorscale='RdYlGn',
                zmin=-5, zmax=5,
                text=sector_df['change_percent'].apply(lambda x: f"{x:.2f}%"),
                texttemplate="%{text}",
                hoverinfo="x+z"
            ))
            fig_sector.update_layout(title="Sector Daily Change (%) - Demo Data", height=300, template="plotly_dark")
            st.plotly_chart(fig_sector, use_container_width=True)
    except Exception as e:
        st.error(f"Error rendering sector performance: {str(e)}")
        st.info("Please try refreshing the page or check data connectivity.")

    # Section 4: Top Indian Stocks with error handling
    st.subheader("Top Indian Stocks")
    try:
        stock_data = fetch_top_stocks()
        if stock_data is None or len(stock_data) == 0:
            # Fallback stock data
            stock_data = {
                'TCS': {'price': 3850.75, 'change': 45.50, 'change_percent': 1.2},
                'HDFC Bank': {'price': 1625.30, 'change': -12.25, 'change_percent': -0.75},
                'Reliance': {'price': 2540.80, 'change': 65.30, 'change_percent': 2.64},
                'Infosys': {'price': 1450.25, 'change': 22.40, 'change_percent': 1.57}
            }
            st.warning("Using demo stock data (unable to fetch live data)")
            
        cols = st.columns(4)
        for i, (name, data) in enumerate(stock_data.items()):
            with cols[i % 4]:
                color = "#00FF00" if data['change'] >= 0 else "#FF4500"
                st.markdown(
                    f"<p><b>{name}</b>: ₹{data['price']:,.2f} <span style='color: {color}'>({data['change_percent']:+.2f}%)</span></p>",
                    unsafe_allow_html=True
                )
    except Exception as e:
        st.error(f"Error loading top stocks: {str(e)}")

    # Section 5: Technical Analysis & Insights with robust error handling
    st.subheader("Technical Analysis & Insights")
    selected_index = st.selectbox("Select Index", list(INDICES.keys()), index=0)
    selected_symbol = INDICES[selected_index]
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=180))
    with col2:
        end_date = st.date_input("End Date", datetime.now())

    has_data = True
    with st.spinner("Analyzing Market Trends..."):
        try:
            df = fetch_historical_data(selected_symbol, start_date, end_date)
            if df is None or df.empty:
                has_data = False
                st.warning("No data available for the selected period. Try adjusting the date range.")
                # Generate demo data for visualization
                date_range = pd.date_range(start=start_date, end=end_date)
                df = pd.DataFrame(index=date_range)
                df['Close'] = np.linspace(20000, 22000, len(date_range)) + np.random.normal(0, 200, len(date_range))
                df['Open'] = df['Close'].shift(1) * (1 + np.random.normal(0, 0.005, len(date_range)))
                df['High'] = df[['Open', 'Close']].max(axis=1) * (1 + abs(np.random.normal(0, 0.003, len(date_range))))
                df['Low'] = df[['Open', 'Close']].min(axis=1) * (1 - abs(np.random.normal(0, 0.003, len(date_range))))
                df['Volume'] = np.random.randint(100000, 1000000, len(date_range))
                df = df.iloc[1:] # Remove first row with NaN
                st.info("Displaying demo data for visualization purposes")
            
            df = calculate_technical_indicators(df)
        except Exception as e:
            has_data = False
            st.error(f"Error processing data: {str(e)}")
            st.warning("Proceeding with demo data for visualization")
            # Generate synthetic data for demonstration
            date_range = pd.date_range(start=start_date, end=end_date)
            df = pd.DataFrame(index=date_range)
            df['Close'] = np.linspace(20000, 22000, len(date_range)) + np.random.normal(0, 200, len(date_range))
            df['Open'] = df['Close'].shift(1) * (1 + np.random.normal(0, 0.005, len(date_range)))
            df['High'] = df[['Open', 'Close']].max(axis=1) * (1 + abs(np.random.normal(0, 0.003, len(date_range))))
            df['Low'] = df[['Open', 'Close']].min(axis=1) * (1 - abs(np.random.normal(0, 0.003, len(date_range))))
            df['Volume'] = np.random.randint(100000, 1000000, len(date_range))
            df = df.iloc[1:] # Remove first row with NaN
            
            # Calculate basic indicators for demo data
            df['MA20'] = df['Close'].rolling(window=20).mean()
            df['MA50'] = df['Close'].rolling(window=50).mean()
            df['RSI'] = 50 + np.random.normal(0, 10, len(df))
            df['MACD'] = np.random.normal(0, 50, len(df))
            df['MACD_Signal'] = df['MACD'] + np.random.normal(0, 20, len(df))
            df['Volatility'] = 0.15 + np.random.normal(0, 0.03, len(df))
            std = df['Close'].rolling(window=20).std()
            df['BB_Upper'] = df['MA20'] + (std * 2)
            df['BB_Lower'] = df['MA20'] - (std * 2)

    if not df.empty:
        try:
            # Advanced Multi-Panel Chart
            fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                                subplot_titles=(f"{selected_index} Price", "Volume", "MACD"),
                                row_heights=[0.5, 0.2, 0.3])
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
            
            # Only add indicators if they exist
            if 'MA20' in df.columns and not df['MA20'].isna().all():
                fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name="MA20", line=dict(color='#FFA500')), row=1, col=1)
            
            if 'MA50' in df.columns and not df['MA50'].isna().all():
                fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], name="MA50", line=dict(color='#FF4500')), row=1, col=1)
            
            if 'BB_Upper' in df.columns and not df['BB_Upper'].isna().all():
                fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], name="BB Upper", line=dict(color='#888', dash='dash')), row=1, col=1)
            
            if 'BB_Lower' in df.columns and not df['BB_Lower'].isna().all():
                fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], name="BB Lower", line=dict(color='#888', dash='dash')), row=1, col=1)
            
            fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Volume", marker_color='#666'), row=2, col=1)
            
            if 'MACD' in df.columns and 'MACD_Signal' in df.columns:
                if not (df['MACD'].isna().all() or df['MACD_Signal'].isna().all()):
                    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name="MACD", line=dict(color='#FF4500')), row=3, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], name="Signal", line=dict(color='#00FF00')), row=3, col=1)
            
            fig.update_layout(
                title=f"{selected_index} Analysis" + (" (Demo Data)" if not has_data else ""),
                yaxis_title="Price (₹)",
                yaxis2_title="Volume",
                yaxis3_title="MACD",
                height=800,
                template="plotly_dark",
                xaxis_rangeslider_visible=False,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        except Exception as e:
            st.error(f"Error rendering chart: {str(e)}")
            st.info("Unable to display chart. Please check data connectivity.")

        # Enhanced Financial Advice with robust error handling
        st.subheader("Data-Driven Financial Advice")
        try:
            last_idx = -1
            price = df['Close'].iloc[last_idx] if 'Close' in df.columns and len(df) > 0 else None
            ma50 = df['MA50'].iloc[last_idx] if 'MA50' in df.columns and len(df) > 0 and not pd.isna(df['MA50'].iloc[last_idx]) else None
            rsi = df['RSI'].iloc[last_idx] if 'RSI' in df.columns and len(df) > 0 and not pd.isna(df['RSI'].iloc[last_idx]) else None
            macd = df['MACD'].iloc[last_idx] if 'MACD' in df.columns and len(df) > 0 and not pd.isna(df['MACD'].iloc[last_idx]) else None
            signal = df['MACD_Signal'].iloc[last_idx] if 'MACD_Signal' in df.columns and len(df) > 0 and not pd.isna(df['MACD_Signal'].iloc[last_idx]) else None
            bb_upper = df['BB_Upper'].iloc[last_idx] if 'BB_Upper' in df.columns and len(df) > 0 and not pd.isna(df['BB_Upper'].iloc[last_idx]) else None
            bb_lower = df['BB_Lower'].iloc[last_idx] if 'BB_Lower' in df.columns and len(df) > 0 and not pd.isna(df['BB_Lower'].iloc[last_idx]) else None
            volatility = df['Volatility'].iloc[last_idx] if 'Volatility' in df.columns and len(df) > 0 and not pd.isna(df['Volatility'].iloc[last_idx]) else None

            # Make sure values are floats, not numpy types (which can cause serialization issues)
            if price is not None: price = float(price)
            if ma50 is not None: ma50 = float(ma50)
            if rsi is not None: rsi = float(rsi)
            if macd is not None: macd = float(macd)
            if signal is not None: signal = float(signal)
            if bb_upper is not None: bb_upper = float(bb_upper)
            if bb_lower is not None: bb_lower = float(bb_lower)
            if volatility is not None: volatility = float(volatility)
            
        except Exception as e:
            st.error(f"Error extracting indicator data: {str(e)}")
            price, ma50, rsi, macd, signal, bb_upper, bb_lower, volatility = None, None, None, None, None, None, None, None

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Market Signals")
            if rsi is not None:
                if rsi > 70:
                    st.error(f"RSI: {rsi:.2f} - Overbought. Consider selling or taking profits.")
                elif rsi < 30:
                    st.success(f"RSI: {rsi:.2f} - Oversold. Potential buying opportunity.")
                else:
                    st.info(f"RSI: {rsi:.2f} - Neutral. Monitor for changes.")
            else:
                st.info("RSI not available (insufficient data).")

            if macd is not None and signal is not None:
                if macd > signal:
                    st.success("MACD: Bullish crossover. Favor buying or holding.")
                else:
                    st.warning("MACD: Bearish crossover. Consider selling or hedging.")
            else:
                st.info("MACD not available (insufficient data).")

            if bb_upper is not None and bb_lower is not None and price is not None:
                if price > bb_upper:
                    st.warning("Above BB Upper: Price may revert to mean. Caution advised.")
                elif price < bb_lower:
                    st.success("Below BB Lower: Potential undervaluation. Consider buying.")
                else:
                    st.info("Within BB: Price is within normal range.")
            else:
                st.info("Bollinger Bands not available (insufficient data).")

            if volatility is not None:
                st.info(f"Volatility: {volatility:.2%} (Annualized)")
            else:
                st.info("Volatility not available (insufficient data).")

        with col2:
            st.markdown("### Investment Insights")
            advice = []
            if price is not None and ma50 is not None:
                if price > ma50:
                    advice.append("Price above MA50: Indicates an uptrend. Consider holding or buying.")
                else:
                    advice.append("Price below MA50: Indicates a downtrend. Consider selling or hedging.")
            if volatility is not None:
                if volatility > 0.3:
                    advice.append("High volatility: Market is volatile. Consider hedging or reducing exposure.")
                else:
                    advice.append("Low volatility: Market is stable. Suitable for long-term investments.")
            
            # Add fallback metal prices if needed
            try:
                gold_price = metals['gold']['price']
            except (KeyError, TypeError):
                gold_price = 6500.0
                
            advice.append(f"Portfolio Suggestion: 50% {selected_index}, 30% Midcap, 20% Gold (₹{gold_price:.2f}/gram). Adjust based on risk tolerance.")
            
            if advice:
                st.markdown("\n".join([f"- {item}" for item in advice]))
            else:
                st.info("Investment insights not available due to insufficient data.")
    else:
        st.warning("No data available for the selected period. Try adjusting the date range.")

    # Section 6: Economic Outlook
    st.subheader("Economic Outlook")
    st.markdown("""
    - **RBI Repo Rate**: 6.5% (Stable, Mar 2025)
    - **CPI Inflation**: ~5.5% (Monitor for shifts)
    - **GDP Growth**: 7.2% FY25—Bullish for equities
    """)

    # Footer
    st.markdown("""
        <hr style='border: 1px solid #FFFFFF;'>
        <p style='text-align: center; font-size: 14px; color: #888;'>
        <b>Disclaimer:</b> Informational only. Consult a SEBI-registered advisor.
        Data by Yahoo Finance (yfinance). © 2025 Fingyan.
        </p>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    render_market_insights()