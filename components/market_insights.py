import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
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
        <p style='text-align: center; font-size: 20px; color: #666666;'>India’s Premier Financial Intelligence Hub</p>
        """, unsafe_allow_html=True)

    # Sidebar - Market Pulse
    with st.sidebar:
        st.markdown("<h2 style='color: #333333;'>Market Pulse</h2>", unsafe_allow_html=True)
        st.info("**NSE Hours:** 9:15 AM - 3:30 PM IST")
        st.markdown(f"**Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.markdown("**Source:** Yahoo Finance (yfinance)")

    # Section 1: Market Snapshot
    st.subheader("Market Snapshot")
    cols = st.columns(3)
    for i, (name, symbol) in enumerate(INDICES.items()):
        with cols[i % 3]:
            data = fetch_stock_data(symbol)
            color = "#00FF00" if data['change'] >= 0 else "#FF4500"
            st.markdown(
                f"<h4>{name}</h4><p style='color: {color};'>₹{data['price']:,.2f} ({data['change_percent']:+.2f}%)</p>",
                unsafe_allow_html=True
            )

    # Section 2: Metals & Forex
    st.subheader("Metals & Forex")
    col1, col2, col3, col4 = st.columns(4)
    metals = fetch_metal_prices()
    currencies = fetch_currency_rates()
    with col1:
        st.metric("Gold (₹/gram)", f"{metals['gold']['price']:,.2f}", metals['gold']['last_updated'])
    with col2:
        st.metric("Silver (₹/gram)", f"{metals['silver']['price']:,.2f}", metals['silver']['last_updated'])
    with col3:
        st.metric("USD/INR", f"₹{currencies['USD/INR']:.2f}", "Live")
    with col4:
        st.metric("EUR/INR", f"₹{currencies['EUR/INR']:.2f}", "Live")

    # Section 3: Sector Performance Heatmap
    st.subheader("Sector Performance")
    sector_data = fetch_sector_performance()
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

    # Section 4: Top Indian Stocks
    st.subheader("Top Indian Stocks")
    stock_data = fetch_top_stocks()
    cols = st.columns(4)
    for i, (name, data) in enumerate(stock_data.items()):
        with cols[i % 4]:
            color = "#00FF00" if data['change'] >= 0 else "#FF4500"
            st.markdown(
                f"<p><b>{name}</b>: ₹{data['price']:,.2f} <span style='color: {color}'>({data['change_percent']:+.2f}%)</span></p>",
                unsafe_allow_html=True
            )

    # Section 5: Technical Analysis & Insights
    st.subheader("Technical Analysis & Insights")
    selected_index = st.selectbox("Select Index", list(INDICES.keys()), index=0)
    selected_symbol = INDICES[selected_index]
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=180))
    with col2:
        end_date = st.date_input("End Date", datetime.now())

    with st.spinner("Analyzing Market Trends..."):
        df = fetch_historical_data(selected_symbol, start_date, end_date)
        if not df.empty:
            df = calculate_technical_indicators(df)

    if not df.empty:
        # Advanced Multi-Panel Chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                            subplot_titles=(f"{selected_index} Price", "Volume", "MACD"),
                            row_heights=[0.5, 0.2, 0.3])
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name="MA20", line=dict(color='#FFA500')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], name="MA50", line=dict(color='#FF4500')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], name="BB Upper", line=dict(color='#888', dash='dash')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], name="BB Lower", line=dict(color='#888', dash='dash')), row=1, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Volume", marker_color='#666'), row=2, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name="MACD", line=dict(color='#FF4500')), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], name="Signal", line=dict(color='#00FF00')), row=3, col=1)
        fig.update_layout(
            title=f"{selected_index} Analysis",
            yaxis_title="Price (₹)",
            yaxis2_title="Volume",
            yaxis3_title="MACD",
            height=800,
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Enhanced Financial Advice
        st.subheader("Data-Driven Financial Advice")
        try:
            price = df['Close'].iloc[-1].item()
            ma50 = df['MA50'].iloc[-1].item() if not pd.isna(df['MA50'].iloc[-1]) else None
            rsi = df['RSI'].iloc[-1].item() if not pd.isna(df['RSI'].iloc[-1]) else None
            macd = df['MACD'].iloc[-1].item() if not pd.isna(df['MACD'].iloc[-1]) else None
            signal = df['MACD_Signal'].iloc[-1].item() if not pd.isna(df['MACD_Signal'].iloc[-1]) else None
            bb_upper = df['BB_Upper'].iloc[-1].item() if not pd.isna(df['BB_Upper'].iloc[-1]) else None
            bb_lower = df['BB_Lower'].iloc[-1].item() if not pd.isna(df['BB_Lower'].iloc[-1]) else None
            volatility = df['Volatility'].iloc[-1].item() if not pd.isna(df['Volatility'].iloc[-1]) else None
        except Exception as e:
            st.error(f"Error extracting data: {e}")
            return

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

            if bb_upper is not None and bb_lower is not None:
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
            if ma50 is not None:
                if price > ma50:
                    advice.append("Price above MA50: Indicates an uptrend. Consider holding or buying.")
                else:
                    advice.append("Price below MA50: Indicates a downtrend. Consider selling or hedging.")
            if volatility is not None:
                if volatility > 0.3:
                    advice.append("High volatility: Market is volatile. Consider hedging or reducing exposure.")
                else:
                    advice.append("Low volatility: Market is stable. Suitable for long-term investments.")
            advice.append(f"Portfolio Suggestion: 50% {selected_index}, 30% Midcap, 20% Gold (₹{metals['gold']['price']:.2f}/gram). Adjust based on risk tolerance.")
            st.markdown("\n".join([f"- {item}" for item in advice]))

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