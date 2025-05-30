import yfinance as yf
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

class EnhancedAnalysis:
    """
    Class for index/sector comparisons, individual indicator analysis, and threshold analysis
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Major market indices
        self.market_indices = {
            'S&P 500': '^GSPC',
            'Dow Jones': '^DJI', 
            'NASDAQ': '^IXIC',
            'Russell 2000': '^RUT',
            'VIX': '^VIX'
        }
        
        # Sector ETFs
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
        
        # Technical indicator thresholds
        self.indicator_thresholds = {
            'RSI': {'oversold': 30, 'overbought': 70, 'neutral_low': 40, 'neutral_high': 60},
            'MACD': {'bullish': 'MACD > Signal', 'bearish': 'MACD < Signal'},
            'BB': {'oversold': 'Price < Lower', 'overbought': 'Price > Upper', 'neutral': 'Within Bands'},
            'SMA_20': {'bullish': 'Price > SMA', 'bearish': 'Price < SMA'},
            'EMA_20': {'bullish': 'Price > EMA', 'bearish': 'Price < EMA'},
            'ATR': {'high_volatility': 'ATR > Average', 'low_volatility': 'ATR < Average'}
        }
    
    def get_index_comparison(self, symbol, period='1y'):
        """
        Compare stock performance with major indices
        
        Args:
            symbol (str): Stock symbol
            period (str): Time period for comparison
            
        Returns:
            dict: Index comparison data
        """
        try:
            # Get stock data
            stock_ticker = yf.Ticker(symbol)
            stock_data = stock_ticker.history(period=period)
            
            if stock_data.empty:
                return None
            
            comparison_data = {}
            stock_return = ((stock_data['Close'].iloc[-1] / stock_data['Close'].iloc[0]) - 1) * 100
            
            # Compare with each index
            for index_name, index_symbol in self.market_indices.items():
                try:
                    index_ticker = yf.Ticker(index_symbol)
                    index_data = index_ticker.history(period=period)
                    
                    if not index_data.empty:
                        index_return = ((index_data['Close'].iloc[-1] / index_data['Close'].iloc[0]) - 1) * 100
                        
                        comparison_data[index_name] = {
                            'symbol': index_symbol,
                            'return': index_return,
                            'vs_stock': stock_return - index_return,
                            'current_price': index_data['Close'].iloc[-1],
                            'outperforming': stock_return > index_return
                        }
                except Exception as e:
                    self.logger.warning(f"Could not get data for {index_name}: {str(e)}")
                    continue
            
            return {
                'stock_symbol': symbol,
                'stock_return': stock_return,
                'period': period,
                'indices': comparison_data
            }
            
        except Exception as e:
            self.logger.error(f"Error in index comparison: {str(e)}")
            return None
    
    def get_sector_comparison(self, symbol, sector, period='1y'):
        """
        Compare stock with sector ETF and similar stocks
        
        Args:
            symbol (str): Stock symbol
            sector (str): Stock sector
            period (str): Time period
            
        Returns:
            dict: Sector comparison data
        """
        try:
            # Get stock data
            stock_ticker = yf.Ticker(symbol)
            stock_data = stock_ticker.history(period=period)
            
            if stock_data.empty:
                return None
            
            stock_return = ((stock_data['Close'].iloc[-1] / stock_data['Close'].iloc[0]) - 1) * 100
            
            # Find matching sector ETF
            sector_etf = None
            for sector_name, etf_symbol in self.sector_etfs.items():
                if sector_name.lower() in sector.lower() or sector.lower() in sector_name.lower():
                    sector_etf = etf_symbol
                    break
            
            sector_data = {}
            if sector_etf:
                try:
                    etf_ticker = yf.Ticker(sector_etf)
                    etf_data = etf_ticker.history(period=period)
                    
                    if not etf_data.empty:
                        etf_return = ((etf_data['Close'].iloc[-1] / etf_data['Close'].iloc[0]) - 1) * 100
                        
                        sector_data = {
                            'etf_symbol': sector_etf,
                            'etf_return': etf_return,
                            'vs_stock': stock_return - etf_return,
                            'outperforming_sector': stock_return > etf_return
                        }
                except Exception as e:
                    self.logger.warning(f"Could not get sector ETF data: {str(e)}")
            
            return {
                'stock_symbol': symbol,
                'stock_return': stock_return,
                'sector': sector,
                'period': period,
                'sector_data': sector_data
            }
            
        except Exception as e:
            self.logger.error(f"Error in sector comparison: {str(e)}")
            return None
    
    def analyze_individual_indicators(self, analysis_data):
        """
        Analyze each technical indicator individually with thresholds
        
        Args:
            analysis_data (pd.DataFrame): Data with technical indicators
            
        Returns:
            dict: Individual indicator analysis with buy/sell/hold signals
        """
        try:
            if analysis_data is None or analysis_data.empty:
                return None
            
            latest = analysis_data.iloc[-1]
            current_price = latest['Close']
            
            indicators_analysis = {}
            
            # RSI Analysis
            rsi_value = latest.get('RSI', 50)
            if not pd.isna(rsi_value):
                if rsi_value < self.indicator_thresholds['RSI']['oversold']:
                    rsi_signal = 'BUY'
                    rsi_strength = 'Strong'
                elif rsi_value > self.indicator_thresholds['RSI']['overbought']:
                    rsi_signal = 'SELL'
                    rsi_strength = 'Strong'
                elif rsi_value < self.indicator_thresholds['RSI']['neutral_low']:
                    rsi_signal = 'HOLD'
                    rsi_strength = 'Weak Bearish'
                elif rsi_value > self.indicator_thresholds['RSI']['neutral_high']:
                    rsi_signal = 'HOLD'
                    rsi_strength = 'Weak Bullish'
                else:
                    rsi_signal = 'HOLD'
                    rsi_strength = 'Neutral'
                
                indicators_analysis['RSI'] = {
                    'value': rsi_value,
                    'signal': rsi_signal,
                    'strength': rsi_strength,
                    'description': f"RSI at {rsi_value:.1f} indicates {rsi_strength.lower()} conditions"
                }
            
            # MACD Analysis
            macd_value = latest.get('MACD', 0)
            macd_signal = latest.get('MACD_Signal', 0)
            if not pd.isna(macd_value) and not pd.isna(macd_signal):
                if macd_value > macd_signal:
                    macd_trend = 'BUY'
                    macd_strength = 'Bullish'
                else:
                    macd_trend = 'SELL'
                    macd_strength = 'Bearish'
                
                # Check momentum
                macd_hist = latest.get('MACD_Histogram', 0)
                if not pd.isna(macd_hist):
                    if macd_hist > 0 and macd_trend == 'BUY':
                        macd_strength = 'Strong Bullish'
                    elif macd_hist < 0 and macd_trend == 'SELL':
                        macd_strength = 'Strong Bearish'
                
                indicators_analysis['MACD'] = {
                    'macd': macd_value,
                    'signal': macd_signal,
                    'histogram': macd_hist,
                    'trend': macd_trend,
                    'strength': macd_strength,
                    'description': f"MACD shows {macd_strength.lower()} momentum"
                }
            
            # Bollinger Bands Analysis
            bb_upper = latest.get('BB_Upper', 0)
            bb_lower = latest.get('BB_Lower', 0)
            bb_middle = latest.get('BB_Middle', 0)
            
            if not pd.isna(bb_upper) and not pd.isna(bb_lower):
                if current_price > bb_upper:
                    bb_signal = 'SELL'
                    bb_strength = 'Overbought'
                elif current_price < bb_lower:
                    bb_signal = 'BUY'
                    bb_strength = 'Oversold'
                else:
                    bb_signal = 'HOLD'
                    bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
                    if bb_position > 0.7:
                        bb_strength = 'Near Upper Band'
                    elif bb_position < 0.3:
                        bb_strength = 'Near Lower Band'
                    else:
                        bb_strength = 'Within Normal Range'
                
                indicators_analysis['Bollinger_Bands'] = {
                    'upper': bb_upper,
                    'middle': bb_middle,
                    'lower': bb_lower,
                    'current_price': current_price,
                    'signal': bb_signal,
                    'strength': bb_strength,
                    'description': f"Price is {bb_strength.lower()} relative to Bollinger Bands"
                }
            
            # Moving Averages Analysis
            sma_20 = latest.get('SMA', 0)
            ema_20 = latest.get('EMA', 0)
            
            if not pd.isna(sma_20):
                sma_signal = 'BUY' if current_price > sma_20 else 'SELL'
                sma_distance = ((current_price / sma_20) - 1) * 100
                
                indicators_analysis['SMA_20'] = {
                    'value': sma_20,
                    'current_price': current_price,
                    'signal': sma_signal,
                    'distance_percent': sma_distance,
                    'description': f"Price is {abs(sma_distance):.1f}% {'above' if sma_distance > 0 else 'below'} SMA(20)"
                }
            
            if not pd.isna(ema_20):
                ema_signal = 'BUY' if current_price > ema_20 else 'SELL'
                ema_distance = ((current_price / ema_20) - 1) * 100
                
                indicators_analysis['EMA_20'] = {
                    'value': ema_20,
                    'current_price': current_price,
                    'signal': ema_signal,
                    'distance_percent': ema_distance,
                    'description': f"Price is {abs(ema_distance):.1f}% {'above' if ema_distance > 0 else 'below'} EMA(20)"
                }
            
            # ATR Analysis
            atr_value = latest.get('ATR', 0)
            if not pd.isna(atr_value) and len(analysis_data) >= 20:
                atr_average = analysis_data['ATR'].tail(20).mean()
                if atr_value > atr_average * 1.2:
                    atr_signal = 'HIGH_VOLATILITY'
                    atr_strength = 'High'
                elif atr_value < atr_average * 0.8:
                    atr_signal = 'LOW_VOLATILITY'
                    atr_strength = 'Low'
                else:
                    atr_signal = 'NORMAL_VOLATILITY'
                    atr_strength = 'Normal'
                
                indicators_analysis['ATR'] = {
                    'value': atr_value,
                    'average': atr_average,
                    'signal': atr_signal,
                    'strength': atr_strength,
                    'description': f"Current volatility is {atr_strength.lower()} compared to recent average"
                }
            
            return indicators_analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing individual indicators: {str(e)}")
            return None
    
    def generate_threshold_summary(self, indicators_analysis):
        """
        Generate summary table showing bullish/bearish signals from each indicator
        
        Args:
            indicators_analysis (dict): Individual indicator analysis
            
        Returns:
            dict: Threshold summary with overall sentiment
        """
        try:
            if not indicators_analysis:
                return None
            
            threshold_summary = []
            bullish_count = 0
            bearish_count = 0
            total_indicators = 0
            
            for indicator, data in indicators_analysis.items():
                signal = data.get('signal', 'HOLD')
                strength = data.get('strength', 'Neutral')
                
                # Determine bullish/bearish classification
                if signal == 'BUY' or (signal == 'HOLD' and 'bullish' in strength.lower()):
                    sentiment = 'Bullish'
                    bullish_count += 1
                elif signal == 'SELL' or (signal == 'HOLD' and 'bearish' in strength.lower()):
                    sentiment = 'Bearish'
                    bearish_count += 1
                else:
                    sentiment = 'Neutral'
                
                total_indicators += 1
                
                threshold_summary.append({
                    'Indicator': indicator.replace('_', ' '),
                    'Current Signal': signal,
                    'Strength': strength,
                    'Sentiment': sentiment,
                    'Description': data.get('description', 'No description available')
                })
            
            # Calculate overall sentiment
            if total_indicators > 0:
                bullish_percent = (bullish_count / total_indicators) * 100
                bearish_percent = (bearish_count / total_indicators) * 100
                
                if bullish_percent > 60:
                    overall_sentiment = 'Strong Bullish'
                elif bullish_percent > 40:
                    overall_sentiment = 'Bullish'
                elif bearish_percent > 60:
                    overall_sentiment = 'Strong Bearish'
                elif bearish_percent > 40:
                    overall_sentiment = 'Bearish'
                else:
                    overall_sentiment = 'Neutral'
            else:
                overall_sentiment = 'Unknown'
            
            return {
                'threshold_table': threshold_summary,
                'overall_sentiment': overall_sentiment,
                'bullish_count': bullish_count,
                'bearish_count': bearish_count,
                'neutral_count': total_indicators - bullish_count - bearish_count,
                'total_indicators': total_indicators,
                'bullish_percent': bullish_percent if total_indicators > 0 else 0,
                'bearish_percent': bearish_percent if total_indicators > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error generating threshold summary: {str(e)}")
            return None
    
    def get_analyst_recommendations(self, symbol):
        """
        Get analyst recommendations and target prices
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            dict: Analyst recommendations data
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Get analyst recommendations
            recommendations = ticker.recommendations
            upgrades_downgrades = ticker.upgrades_downgrades
            
            # Get analyst info from stock info
            info = ticker.info
            analyst_data = {
                'target_mean_price': info.get('targetMeanPrice', 0),
                'target_high_price': info.get('targetHighPrice', 0),
                'target_low_price': info.get('targetLowPrice', 0),
                'recommendation_mean': info.get('recommendationMean', 0),
                'number_of_analyst_opinions': info.get('numberOfAnalystOpinions', 0)
            }
            
            # Convert recommendation mean to text
            rec_mean = analyst_data.get('recommendation_mean', 0)
            if rec_mean > 0:
                if rec_mean <= 1.5:
                    rec_text = 'Strong Buy'
                elif rec_mean <= 2.5:
                    rec_text = 'Buy'
                elif rec_mean <= 3.5:
                    rec_text = 'Hold'
                elif rec_mean <= 4.5:
                    rec_text = 'Sell'
                else:
                    rec_text = 'Strong Sell'
            else:
                rec_text = 'No Rating'
            
            return {
                'recommendations': recommendations,
                'upgrades_downgrades': upgrades_downgrades,
                'analyst_data': analyst_data,
                'recommendation_text': rec_text,
                'current_price': info.get('currentPrice', 0)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting analyst recommendations: {str(e)}")
            return None