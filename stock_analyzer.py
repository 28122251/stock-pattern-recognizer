import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ta
import warnings
warnings.filterwarnings('ignore')

class StockPatternRecognizer:
    def __init__(self):
        self.patterns_detected = []
        
    def fetch_stock_data(self, symbol, period='1y'):
        try:
            symbol = symbol.strip().upper()
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)
            return data if not data.empty else None
        except:
            return None
    
    def calculate_technical_indicators(self, data):
        data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()
        macd = ta.trend.MACD(data['Close'])
        data['MACD'] = macd.macd()
        data['MACD_signal'] = macd.macd_signal()
        data['MACD_histogram'] = macd.macd_diff()
        data['SMA_20'] = ta.trend.SMAIndicator(data['Close'], window=20).sma_indicator()
        data['EMA_20'] = ta.trend.EMAIndicator(data['Close'], window=20).ema_indicator()
        data['SMA_50'] = ta.trend.SMAIndicator(data['Close'], window=50).sma_indicator()
        return data
    
    def detect_head_shoulders(self, data, window=20):
        patterns = []
        for i in range(window, len(data) - window):
            left_shoulder = data['High'].iloc[i-window:i].max()
            head = data['High'].iloc[i-window:i+window].max()
            right_shoulder = data['High'].iloc[i:i+window].max()
            if (head > left_shoulder and head > right_shoulder and 
                abs(left_shoulder - right_shoulder) / head < 0.05):
                patterns.append({
                    'pattern': 'Head and Shoulders',
                    'type': 'Bearish',
                    'confidence': 'Medium',
                    'description': 'Reversal pattern indicating potential downtrend'
                })
                break
        return patterns
    
    def detect_double_top_bottom(self, data, window=30):
        patterns = []
        for i in range(window, len(data) - window):
            top1 = data['High'].iloc[i-window:i].max()
            top2 = data['High'].iloc[i:i+window].max()
            if (abs(top1 - top2) / top1 < 0.02 and
                data['Close'].iloc[i] < min(top1, top2) * 0.98):
                patterns.append({
                    'pattern': 'Double Top',
                    'type': 'Bearish',
                    'confidence': 'Medium',
                    'description': 'Reversal pattern indicating potential downtrend'
                })
                break
            bottom1 = data['Low'].iloc[i-window:i].min()
            bottom2 = data['Low'].iloc[i:i+window].min()
            if (abs(bottom1 - bottom2) / bottom1 < 0.02 and
                data['Close'].iloc[i] > max(bottom1, bottom2) * 1.02):
                patterns.append({
                    'pattern': 'Double Bottom',
                    'type': 'Bullish',
                    'confidence': 'Medium',
                    'description': 'Reversal pattern indicating potential uptrend'
                })
                break
        return patterns
    
    def generate_signals(self, data):
        if len(data) < 2:
            return ["Insufficient data for analysis"]
        latest_rsi = data['RSI'].iloc[-1]
        latest_macd = data['MACD'].iloc[-1]
        latest_macd_signal = data['MACD_signal'].iloc[-1]
        signals = []
        if pd.notna(latest_rsi):
            if latest_rsi < 30:
                signals.append("RSI indicates OVERSOLD - Potential BUY")
            elif latest_rsi > 70:
                signals.append("RSI indicates OVERBOUGHT - Potential SELL")
            else:
                signals.append("RSI in NEUTRAL zone")
        if pd.notna(latest_macd) and pd.notna(latest_macd_signal):
            if latest_macd > latest_macd_signal:
                signals.append("MACD Bullish Crossover - BUY Signal")
            else:
                signals.append("MACD Bearish Crossover - SELL Signal")
        if (pd.notna(data['Close'].iloc[-1]) and 
            pd.notna(data['SMA_20'].iloc[-1]) and 
            pd.notna(data['SMA_50'].iloc[-1])):
            if data['Close'].iloc[-1] > data['SMA_20'].iloc[-1] > data['SMA_50'].iloc[-1]:
                signals.append("Price above SMAs - Uptrend confirmed")
            elif data['Close'].iloc[-1] < data['SMA_20'].iloc[-1] < data['SMA_50'].iloc[-1]:
                signals.append("Price below SMAs - Downtrend confirmed")
            else:
                signals.append("Mixed signals from Moving Averages")
        return signals
    
    def analyze_stock(self, symbol, period='1y'):
        data = self.fetch_stock_data(symbol, period)
        if data is None or data.empty:
            return None, [], ["Failed to fetch data for this symbol"]
        data = self.calculate_technical_indicators(data)
        patterns = []
        patterns.extend(self.detect_head_shoulders(data))
        patterns.extend(self.detect_double_top_bottom(data))
        signals = self.generate_signals(data)
        return data, patterns, signals
    
    def create_dashboard(self, data, patterns, signals, symbol):
        if data is None:
            return None
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=(
                f'{symbol} Price Chart with Moving Averages',
                'Volume',
                'RSI (Relative Strength Index)',
                'MACD (Moving Average Convergence Divergence)'
            ),
            row_heights=[0.4, 0.15, 0.2, 0.25]
        )
        fig.add_trace(go.Candlestick(
            x=data.index, open=data['Open'], high=data['High'], 
            low=data['Low'], close=data['Close'], name='Price'
        ), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA_20'], line=dict(color='orange', width=1), name='SMA 20'), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA_50'], line=dict(color='red', width=1), name='SMA 50'), row=1, col=1)
        colors = ['red' if data['Close'].iloc[i] < data['Open'].iloc[i] else 'green' for i in range(len(data))]
        fig.add_trace(go.Bar(x=data.index, y=data['Volume'], marker_color=colors, name='Volume'), row=2, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], line=dict(color='purple', width=1), name='RSI'), row=3, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['MACD'], line=dict(color='blue', width=1), name='MACD'), row=4, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['MACD_signal'], line=dict(color='red', width=1), name='Signal'), row=4, col=1)
        fig.update_layout(height=1000, title_text=f"Technical Analysis Dashboard - {symbol}", xaxis_rangeslider_visible=False)
        return fig