import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from stock_analyzer import StockPatternRecognizer

def main():
    st.set_page_config(
        page_title="Universal Stock Pattern Recognizer",
        page_icon="📈",
        layout="wide"
    )
    
    st.title("🎯 Universal Stock Pattern Recognizer")
    st.markdown("Analyze **ANY** stock from **ANY** market in real-time!")
    st.markdown("---")
    
    st.sidebar.header("🔍 Stock Analysis Parameters")
    symbol = st.sidebar.text_input("Enter Stock Symbol:", "RELIANCE.NS")
    period = st.sidebar.selectbox("Select Time Period:", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("💡 Quick Examples")
    st.sidebar.markdown("**Indian Stocks:**")
    st.sidebar.markdown("- RELIANCE.NS, TCS.NS")
    st.sidebar.markdown("- INFY.NS, HDFCBANK.NS")
    st.sidebar.markdown("- CUMMINSIND.NS, HAL.NS")
    st.sidebar.markdown("**US Stocks:**")
    st.sidebar.markdown("- AAPL, TSLA, GOOGL")
    st.sidebar.markdown("- MSFT, AMZN, NFLX")
    
    if st.sidebar.button("🚀 Analyze Stock") or symbol:
        with st.spinner(f"🔍 Analyzing {symbol}... Please wait"):
            analyzer = StockPatternRecognizer()
            data, patterns, signals = analyzer.analyze_stock(symbol, period)
            
            if data is None:
                st.error(f"❌ Could not fetch data for '{symbol}'. Please check the symbol.")
                return
            
            st.subheader(f"📊 Stock Analysis: {symbol}")
            col1, col2, col3, col4 = st.columns(4)
            current_price = data['Close'].iloc[-1]
            price_change = current_price - data['Close'].iloc[0]
            percent_change = (price_change / data['Close'].iloc[0]) * 100
            
            with col1:
                st.metric("Current Price", f"${current_price:.2f}" if '.' not in symbol else f"₹{current_price:.2f}")
            with col2:
                st.metric("Price Change", f"${price_change:.2f}" if '.' not in symbol else f"₹{price_change:.2f}")
            with col3:
                st.metric("Percentage Change", f"{percent_change:+.2f}%")
            with col4:
                st.metric("Volume", f"{data['Volume'].iloc[-1]:,}")
            
            st.markdown("---")
            st.subheader("📈 Technical Charts")
            fig = analyzer.create_dashboard(data, patterns, signals, symbol)
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("🎯 Detected Chart Patterns")
            if patterns:
                for pattern in patterns:
                    if pattern['type'] == 'Bullish':
                        st.success(f"🟢 **{pattern['pattern']}** ({pattern['type']})")
                    else:
                        st.error(f"🔴 **{pattern['pattern']}** ({pattern['type']})")
                    st.write(f"**Confidence:** {pattern['confidence']}")
                    st.write(f"**Description:** {pattern['description']}")
                    st.write("---")
            else:
                st.info("ℹ️ No strong chart patterns detected in the selected timeframe.")
            
            st.subheader("💡 Trading Signals")
            cols = st.columns(2)
            for i, signal in enumerate(signals):
                col = cols[i % 2]
                if "BUY" in signal:
                    col.success(f"✅ {signal}")
                elif "SELL" in signal:
                    col.error(f"❌ {signal}")
                else:
                    col.info(f"ℹ️ {signal}")

if __name__ == "__main__":
    main()