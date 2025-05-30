import yfinance as yf
import pandas as pd
import streamlit as st
import requests
import os
from datetime import datetime, timedelta
import logging

class DataFetcher:
    """
    Class to fetch stock data from Yahoo Finance using yfinance library
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.alpha_vantage_api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    
    def fetch_stock_data(self, symbol, period="1y"):
        """
        Fetch historical stock data for a given symbol
        
        Args:
            symbol (str): Stock symbol (e.g., 'AAPL', 'GOOGL')
            period (str): Time period for data ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
        
        Returns:
            pandas.DataFrame: Historical stock data with OHLCV columns
        """
        try:
            # Create ticker object
            ticker = yf.Ticker(symbol)
            
            # Fetch historical data
            hist_data = ticker.history(period=period)
            
            if hist_data.empty:
                self.logger.error(f"No data found for symbol: {symbol}")
                return None
            
            # Clean and prepare data
            hist_data = hist_data.reset_index()
            
            # Ensure we have the required columns
            required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in hist_data.columns for col in required_columns):
                self.logger.error(f"Missing required columns in data for {symbol}")
                return None
            
            # Set date as index
            hist_data.set_index('Date', inplace=True)
            
            # Sort by date
            hist_data.sort_index(inplace=True)
            
            # Remove any rows with NaN values
            hist_data.dropna(inplace=True)
            
            self.logger.info(f"Successfully fetched {len(hist_data)} data points for {symbol}")
            return hist_data
            
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def get_current_price(self, symbol):
        """
        Get the current/latest price for a stock symbol
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            float: Current stock price
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Try different price fields in order of preference
            price_fields = ['currentPrice', 'regularMarketPrice', 'previousClose']
            
            for field in price_fields:
                if field in info and info[field] is not None:
                    return float(info[field])
            
            # Fallback to latest close price from history
            hist = ticker.history(period="1d")
            if not hist.empty:
                return float(hist['Close'].iloc[-1])
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting current price for {symbol}: {str(e)}")
            return None
    
    def get_stock_info(self, symbol):
        """
        Get additional stock information
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            dict: Stock information
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Extract relevant information
            stock_info = {
                'symbol': symbol,
                'company_name': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'dividend_yield': info.get('dividendYield', 'N/A'),
                'beta': info.get('beta', 'N/A'),
                '52_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
                '52_week_low': info.get('fiftyTwoWeekLow', 'N/A'),
                'avg_volume': info.get('averageVolume', 'N/A')
            }
            
            return stock_info
            
        except Exception as e:
            self.logger.error(f"Error getting stock info for {symbol}: {str(e)}")
            return {}
    
    def validate_symbol(self, symbol):
        """
        Validate if a stock symbol exists and has data
        
        Args:
            symbol (str): Stock symbol to validate
            
        Returns:
            bool: True if symbol is valid, False otherwise
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            return not hist.empty
            
        except Exception as e:
            self.logger.error(f"Error validating symbol {symbol}: {str(e)}")
            return False
    
    def get_multiple_stocks(self, symbols, period="1y"):
        """
        Fetch data for multiple stock symbols
        
        Args:
            symbols (list): List of stock symbols
            period (str): Time period for data
            
        Returns:
            dict: Dictionary with symbol as key and DataFrame as value
        """
        stock_data = {}
        
        for symbol in symbols:
            data = self.fetch_stock_data(symbol, period)
            if data is not None:
                stock_data[symbol] = data
                
        return stock_data
    
    def get_market_data(self):
        """
        Get general market data (major indices)
        
        Returns:
            dict: Market data for major indices
        """
        indices = {
            'S&P 500': '^GSPC',
            'Dow Jones': '^DJI',
            'NASDAQ': '^IXIC',
            'VIX': '^VIX'
        }
        
        market_data = {}
        
        for name, symbol in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d")
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    previous_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                    change = current_price - previous_price
                    change_percent = (change / previous_price) * 100
                    
                    market_data[name] = {
                        'price': current_price,
                        'change': change,
                        'change_percent': change_percent
                    }
                    
            except Exception as e:
                self.logger.error(f"Error fetching market data for {name}: {str(e)}")
                continue
                
        return market_data
