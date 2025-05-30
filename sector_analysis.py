import yfinance as yf
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
import streamlit as st

class SectorAnalysis:
    """
    Class to perform sector-level analysis and find similar performing stocks
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Major sector ETFs and their typical holdings
        self.sector_etfs = {
            'Technology': 'XLK',
            'Healthcare': 'XLV',
            'Financial': 'XLF',
            'Energy': 'XLE',
            'Consumer Discretionary': 'XLY',
            'Consumer Staples': 'XLP',
            'Industrials': 'XLI',
            'Materials': 'XLB',
            'Utilities': 'XLU',
            'Real Estate': 'XLRE',
            'Communication Services': 'XLC'
        }
        
        # Popular stocks by sector for comparison
        self.sector_stocks = {
            'Technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'NFLX', 'ADBE', 'CRM'],
            'Healthcare': ['JNJ', 'UNH', 'PFE', 'ABT', 'TMO', 'MRK', 'DHR', 'BMY', 'ABBV', 'MDT'],
            'Financial': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP', 'BLK', 'SCHW', 'USB'],
            'Energy': ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'MPC', 'PSX', 'VLO', 'OXY', 'HAL'],
            'Consumer Discretionary': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'TJX', 'LOW', 'TGT', 'F'],
            'Consumer Staples': ['PG', 'KO', 'PEP', 'WMT', 'COST', 'CL', 'KMB', 'GIS', 'K', 'HSY'],
            'Industrials': ['BA', 'CAT', 'GE', 'MMM', 'HON', 'UPS', 'LMT', 'RTX', 'DE', 'UNP'],
            'Materials': ['LIN', 'APD', 'SHW', 'FCX', 'NEM', 'DOW', 'DD', 'PPG', 'ECL', 'IFF'],
            'Utilities': ['NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'XEL', 'SRE', 'PEG', 'ED'],
            'Real Estate': ['AMT', 'PLD', 'CCI', 'EQIX', 'PSA', 'WELL', 'SPG', 'EXR', 'AVB', 'EQR'],
            'Communication Services': ['GOOGL', 'META', 'NFLX', 'DIS', 'CMCSA', 'VZ', 'T', 'CHTR', 'TMUS', 'ATVI']
        }
    
    def get_stock_sector(self, symbol):
        """
        Get the sector of a given stock symbol
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            str: Sector name or None if not found
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            sector = info.get('sector', None)
            return sector
            
        except Exception as e:
            self.logger.error(f"Error getting sector for {symbol}: {str(e)}")
            return None
    
    def get_sector_top_companies(self, sector, limit=5):
        """
        Get top companies in a given sector
        
        Args:
            sector (str): Sector name
            limit (int): Number of companies to return
            
        Returns:
            list: List of top company symbols in the sector
        """
        try:
            # Map common sector names to our predefined lists
            sector_mapping = {
                'Technology': 'Technology',
                'Information Technology': 'Technology',
                'Healthcare': 'Healthcare',
                'Financial Services': 'Financial',
                'Financials': 'Financial',
                'Energy': 'Energy',
                'Consumer Cyclical': 'Consumer Discretionary',
                'Consumer Defensive': 'Consumer Staples',
                'Industrials': 'Industrials',
                'Basic Materials': 'Materials',
                'Materials': 'Materials',
                'Utilities': 'Utilities',
                'Real Estate': 'Real Estate',
                'Communication Services': 'Communication Services',
                'Telecommunications': 'Communication Services'
            }
            
            mapped_sector = sector_mapping.get(sector, sector)
            
            if mapped_sector in self.sector_stocks:
                return self.sector_stocks[mapped_sector][:limit]
            else:
                # Fallback to some major stocks if sector not found
                return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA'][:limit]
                
        except Exception as e:
            self.logger.error(f"Error getting top companies for sector {sector}: {str(e)}")
            return []
    
    def calculate_performance_metrics(self, symbol, period="1y"):
        """
        Calculate performance metrics for a stock
        
        Args:
            symbol (str): Stock symbol
            period (str): Time period
            
        Returns:
            dict: Performance metrics
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return None
            
            # Calculate metrics
            start_price = hist['Close'].iloc[0]
            end_price = hist['Close'].iloc[-1]
            total_return = (end_price - start_price) / start_price * 100
            
            # Volatility (annualized)
            returns = hist['Close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252) * 100
            
            # Sharpe ratio (assuming 2% risk-free rate)
            risk_free_rate = 2.0
            avg_return = returns.mean() * 252 * 100
            sharpe_ratio = (avg_return - risk_free_rate) / volatility if volatility > 0 else 0
            
            # Maximum drawdown
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min() * 100
            
            # Current price info
            current_price = end_price
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'total_return': total_return,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'avg_volume': hist['Volume'].mean()
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating performance for {symbol}: {str(e)}")
            return None
    
    def find_similar_performers(self, target_symbol, period="1y", similarity_threshold=0.15):
        """
        Find stocks with similar performance to the target stock
        
        Args:
            target_symbol (str): Target stock symbol
            period (str): Time period for comparison
            similarity_threshold (float): Threshold for similarity (lower = more similar)
            
        Returns:
            list: List of similar performing stocks with their metrics
        """
        try:
            # Get target stock performance
            target_metrics = self.calculate_performance_metrics(target_symbol, period)
            if not target_metrics:
                return []
            
            # Get target stock sector
            target_sector = self.get_stock_sector(target_symbol)
            
            # Create a broader list of stocks to compare
            comparison_stocks = set()
            
            # Add stocks from the same sector
            if target_sector:
                sector_stocks = self.get_sector_top_companies(target_sector, 10)
                comparison_stocks.update(sector_stocks)
            
            # Add stocks from all sectors for broader comparison
            for sector_list in self.sector_stocks.values():
                comparison_stocks.update(sector_list[:5])  # Top 5 from each sector
            
            # Remove the target stock itself
            comparison_stocks.discard(target_symbol)
            
            similar_stocks = []
            
            for stock in list(comparison_stocks)[:50]:  # Limit to 50 for performance
                metrics = self.calculate_performance_metrics(stock, period)
                if not metrics:
                    continue
                
                # Calculate similarity score based on multiple metrics
                return_diff = abs(metrics['total_return'] - target_metrics['total_return']) / 100
                vol_diff = abs(metrics['volatility'] - target_metrics['volatility']) / 100
                sharpe_diff = abs(metrics['sharpe_ratio'] - target_metrics['sharpe_ratio']) / 10
                
                # Weighted similarity score
                similarity_score = (return_diff * 0.5 + vol_diff * 0.3 + sharpe_diff * 0.2)
                
                if similarity_score <= similarity_threshold:
                    metrics['similarity_score'] = similarity_score
                    similar_stocks.append(metrics)
            
            # Sort by similarity (lower score = more similar)
            similar_stocks.sort(key=lambda x: x['similarity_score'])
            
            return similar_stocks[:10]  # Return top 10 most similar
            
        except Exception as e:
            self.logger.error(f"Error finding similar performers: {str(e)}")
            return []
    
    def get_sector_comparison_data(self, target_symbol, period="1y"):
        """
        Get comprehensive sector comparison data
        
        Args:
            target_symbol (str): Target stock symbol
            period (str): Time period for analysis
            
        Returns:
            dict: Comprehensive sector analysis data
        """
        try:
            # Get target stock info
            target_sector = self.get_stock_sector(target_symbol)
            target_metrics = self.calculate_performance_metrics(target_symbol, period)
            
            if not target_metrics:
                return None
            
            # Get sector peers
            sector_peers = []
            if target_sector:
                peer_symbols = self.get_sector_top_companies(target_sector, 5)
                for symbol in peer_symbols:
                    if symbol != target_symbol:
                        peer_metrics = self.calculate_performance_metrics(symbol, period)
                        if peer_metrics:
                            sector_peers.append(peer_metrics)
            
            # Get similar performers
            similar_performers = self.find_similar_performers(target_symbol, period)
            
            # Calculate sector averages
            sector_avg_return = np.mean([p['total_return'] for p in sector_peers]) if sector_peers else 0
            sector_avg_volatility = np.mean([p['volatility'] for p in sector_peers]) if sector_peers else 0
            
            return {
                'target_symbol': target_symbol,
                'target_sector': target_sector,
                'target_metrics': target_metrics,
                'sector_peers': sector_peers,
                'similar_performers': similar_performers,
                'sector_averages': {
                    'avg_return': sector_avg_return,
                    'avg_volatility': sector_avg_volatility
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting sector comparison data: {str(e)}")
            return None
    
    def get_sector_etf_performance(self, sector, period="1y"):
        """
        Get sector ETF performance for benchmarking
        
        Args:
            sector (str): Sector name
            period (str): Time period
            
        Returns:
            dict: Sector ETF performance metrics
        """
        try:
            # Map sector to ETF
            sector_mapping = {
                'Technology': 'XLK',
                'Information Technology': 'XLK',
                'Healthcare': 'XLV',
                'Financial Services': 'XLF',
                'Financials': 'XLF',
                'Energy': 'XLE',
                'Consumer Cyclical': 'XLY',
                'Consumer Defensive': 'XLP',
                'Industrials': 'XLI',
                'Basic Materials': 'XLB',
                'Materials': 'XLB',
                'Utilities': 'XLU',
                'Real Estate': 'XLRE',
                'Communication Services': 'XLC',
                'Telecommunications': 'XLC'
            }
            
            etf_symbol = sector_mapping.get(sector)
            if etf_symbol:
                return self.calculate_performance_metrics(etf_symbol, period)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting sector ETF performance: {str(e)}")
            return None