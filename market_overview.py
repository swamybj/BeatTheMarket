import pandas as pd
import yfinance as yf
import requests
import os
from datetime import datetime, timedelta
import logging

class MarketOverview:
    """
    Class to fetch market overview data including indices, commodities, forex, and futures
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.alpha_vantage_api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    
    def get_major_indices(self):
        """Get major stock indices data"""
        indices = {
            "S&P 500": "^GSPC",
            "Dow Jones": "^DJI", 
            "NASDAQ": "^IXIC",
            "Russell 2000": "^RUT",
            "VIX": "^VIX",
            "FTSE 100": "^FTSE",
            "DAX": "^GDAXI",
            "Nikkei 225": "^N225",
            "Hang Seng": "^HSI",
            "Shanghai": "000001.SS"
        }
        
        return self._fetch_multiple_symbols(indices, "Index")
    
    def get_commodities(self):
        """Get major commodities data"""
        commodities = {
            "Gold": "GC=F",
            "Silver": "SI=F", 
            "Crude Oil": "CL=F",
            "Natural Gas": "NG=F",
            "Copper": "HG=F",
            "Platinum": "PL=F",
            "Corn": "ZC=F",
            "Wheat": "ZW=F",
            "Soybeans": "ZS=F",
            "Coffee": "KC=F"
        }
        
        return self._fetch_multiple_symbols(commodities, "Commodity")
    
    def get_forex_pairs(self):
        """Get major forex pairs"""
        forex = {
            "EUR/USD": "EURUSD=X",
            "GBP/USD": "GBPUSD=X",
            "USD/JPY": "USDJPY=X", 
            "USD/CHF": "USDCHF=X",
            "AUD/USD": "AUDUSD=X",
            "USD/CAD": "USDCAD=X",
            "NZD/USD": "NZDUSD=X",
            "EUR/GBP": "EURGBP=X",
            "EUR/JPY": "EURJPY=X",
            "GBP/JPY": "GBPJPY=X"
        }
        
        return self._fetch_multiple_symbols(forex, "Forex")
    
    def get_crypto_currencies(self):
        """Get major cryptocurrencies"""
        crypto = {
            "Bitcoin": "BTC-USD",
            "Ethereum": "ETH-USD",
            "Binance Coin": "BNB-USD",
            "Cardano": "ADA-USD",
            "Solana": "SOL-USD",
            "XRP": "XRP-USD",
            "Polkadot": "DOT-USD",
            "Dogecoin": "DOGE-USD",
            "Avalanche": "AVAX-USD",
            "Chainlink": "LINK-USD"
        }
        
        return self._fetch_multiple_symbols(crypto, "Crypto")
    
    def _fetch_multiple_symbols(self, symbols_dict, category):
        """Fetch data for multiple symbols"""
        results = []
        
        for name, symbol in symbols_dict.items():
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="1y")
                
                if hist.empty:
                    continue
                    
                current_price = hist['Close'].iloc[-1]
                prev_close = info.get('previousClose', hist['Close'].iloc[-2] if len(hist) > 1 else current_price)
                
                # Calculate changes
                change = current_price - prev_close
                change_pct = (change / prev_close) * 100 if prev_close != 0 else 0
                
                # Calculate 52-week high/low
                high_52w = hist['High'].max()
                low_52w = hist['Low'].min()
                
                # Calculate distance from 52w high/low
                dist_from_high = ((current_price - high_52w) / high_52w) * 100
                dist_from_low = ((current_price - low_52w) / low_52w) * 100
                
                # Simple technical analysis
                sma_20 = hist['Close'].rolling(20).mean().iloc[-1]
                sma_50 = hist['Close'].rolling(50).mean().iloc[-1]
                
                # Determine trend
                if current_price > sma_20 > sma_50:
                    trend = "Strong Bullish"
                elif current_price > sma_20:
                    trend = "Bullish"
                elif current_price < sma_20 < sma_50:
                    trend = "Strong Bearish"
                elif current_price < sma_20:
                    trend = "Bearish"
                else:
                    trend = "Sideways"
                
                # Volume analysis (if available)
                volume = hist['Volume'].iloc[-1] if 'Volume' in hist.columns else 0
                avg_volume = hist['Volume'].rolling(20).mean().iloc[-1] if 'Volume' in hist.columns else 0
                volume_ratio = volume / avg_volume if avg_volume > 0 else 1
                
                results.append({
                    'Name': name,
                    'Symbol': symbol,
                    'Category': category,
                    'Price': current_price,
                    'Change': change,
                    'Change %': change_pct,
                    '52W High': high_52w,
                    '52W Low': low_52w,
                    'From High %': dist_from_high,
                    'From Low %': dist_from_low,
                    'Trend': trend,
                    'Volume Ratio': volume_ratio,
                    'SMA 20': sma_20,
                    'SMA 50': sma_50
                })
                
            except Exception as e:
                self.logger.error(f"Error fetching data for {name} ({symbol}): {str(e)}")
                continue
        
        return pd.DataFrame(results)
    
    def get_market_movers(self):
        """Get top market movers"""
        try:
            # Get S&P 500 components (simplified list)
            sp500_symbols = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'BRK-B', 'NVDA', 'JPM', 'JNJ',
                'V', 'PG', 'UNH', 'HD', 'MA', 'DIS', 'PYPL', 'BAC', 'NFLX', 'ADBE',
                'CRM', 'TMO', 'COST', 'PFE', 'XOM', 'ABT', 'VZ', 'KO', 'WMT', 'PEP',
                'CSCO', 'ACN', 'DHR', 'TXN', 'BMY', 'LIN', 'T', 'MRK', 'HON', 'NKE'
            ]
            
            movers_data = []
            
            for symbol in sp500_symbols[:30]:  # Limit to avoid rate limits
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="5d")
                    
                    if len(hist) < 2:
                        continue
                        
                    current_price = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2]
                    change_pct = ((current_price - prev_close) / prev_close) * 100
                    
                    volume = hist['Volume'].iloc[-1]
                    avg_volume = hist['Volume'].mean()
                    
                    movers_data.append({
                        'Symbol': symbol,
                        'Price': current_price,
                        'Change %': change_pct,
                        'Volume': volume,
                        'Avg Volume': avg_volume,
                        'Volume Ratio': volume / avg_volume if avg_volume > 0 else 1
                    })
                    
                except Exception as e:
                    continue
            
            df = pd.DataFrame(movers_data)
            
            if df.empty:
                return None, None, None
            
            # Get top gainers, losers, and most active
            top_gainers = df.nlargest(10, 'Change %')
            top_losers = df.nsmallest(10, 'Change %')
            most_active = df.nlargest(10, 'Volume Ratio')
            
            return top_gainers, top_losers, most_active
            
        except Exception as e:
            self.logger.error(f"Error getting market movers: {str(e)}")
            return None, None, None
    
    def get_52_week_extremes(self):
        """Get stocks at 52-week highs and lows"""
        try:
            # Use a subset of popular stocks
            symbols = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'JNJ', 'V',
                'PG', 'UNH', 'HD', 'MA', 'DIS', 'BAC', 'NFLX', 'ADBE', 'CRM', 'TMO',
                'COST', 'PFE', 'XOM', 'ABT', 'VZ', 'KO', 'WMT', 'PEP', 'CSCO', 'ACN'
            ]
            
            highs_data = []
            lows_data = []
            
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="1y")
                    
                    if hist.empty:
                        continue
                    
                    current_price = hist['Close'].iloc[-1]
                    high_52w = hist['High'].max()
                    low_52w = hist['Low'].min()
                    
                    # Check if near 52-week high (within 5%)
                    if current_price >= high_52w * 0.95:
                        dist_from_high = ((current_price - high_52w) / high_52w) * 100
                        highs_data.append({
                            'Symbol': symbol,
                            'Current Price': current_price,
                            '52W High': high_52w,
                            'From High %': dist_from_high
                        })
                    
                    # Check if near 52-week low (within 5%)
                    if current_price <= low_52w * 1.05:
                        dist_from_low = ((current_price - low_52w) / low_52w) * 100
                        lows_data.append({
                            'Symbol': symbol,
                            'Current Price': current_price,
                            '52W Low': low_52w,
                            'From Low %': dist_from_low
                        })
                        
                except Exception as e:
                    continue
            
            highs_df = pd.DataFrame(highs_data)
            lows_df = pd.DataFrame(lows_data)
            
            return highs_df, lows_df
            
        except Exception as e:
            self.logger.error(f"Error getting 52-week extremes: {str(e)}")
            return None, None
    
    def get_technical_summary(self, df):
        """Generate technical analysis summary for a dataframe"""
        if df is None or df.empty:
            return {}
        
        summary = {
            'total_instruments': len(df),
            'bullish_count': len(df[df['Trend'].str.contains('Bullish', na=False)]),
            'bearish_count': len(df[df['Trend'].str.contains('Bearish', na=False)]),
            'sideways_count': len(df[df['Trend'] == 'Sideways']),
            'avg_change': df['Change %'].mean(),
            'top_performer': df.loc[df['Change %'].idxmax()] if not df.empty else None,
            'worst_performer': df.loc[df['Change %'].idxmin()] if not df.empty else None
        }
        
        return summary