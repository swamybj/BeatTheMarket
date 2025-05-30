import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
import yfinance as yf
from typing import Dict, List, Optional
import json
import os

class AlertSystem:
    """
    Class to monitor stocks and send alerts when sentiment changes from bearish to bullish
    with automatic stop-loss and target calculations
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.watchlist_file = "watchlist.json"
        self.alerts_file = "alerts_history.json"
        
        # Alert thresholds
        self.sentiment_change_threshold = 0.3  # Minimum change to trigger alert
        self.min_bullish_indicators = 3  # Minimum bullish signals required
        
        # Risk management parameters
        self.default_stop_loss_pct = 0.08  # 8% stop loss
        self.default_target_pct = 0.15     # 15% target
        self.atr_multiplier = 2.0          # ATR-based stop loss multiplier
        
    def add_to_watchlist(self, symbol: str, user_phone: str = None, user_email: str = None):
        """
        Add a stock to the watchlist for monitoring
        
        Args:
            symbol (str): Stock symbol to monitor
            user_phone (str): Phone number for SMS alerts
            user_email (str): Email for alerts
            
        Returns:
            bool: Success status
        """
        try:
            watchlist = self._load_watchlist()
            
            # Get current stock data for baseline
            from technical_analysis import TechnicalAnalysis
            from enhanced_analysis import EnhancedAnalysis
            from data_fetcher import DataFetcher
            
            data_fetcher = DataFetcher()
            stock_data = data_fetcher.fetch_stock_data(symbol, "3mo")
            
            if stock_data is None or stock_data.empty:
                self.logger.error(f"Cannot add {symbol} to watchlist - no data available")
                return False
            
            # Get current technical analysis
            ta = TechnicalAnalysis()
            analysis_results = ta.calculate_all_indicators(stock_data)
            
            enhanced_analyzer = EnhancedAnalysis()
            individual_indicators = enhanced_analyzer.analyze_individual_indicators(analysis_results)
            threshold_summary = enhanced_analyzer.generate_threshold_summary(individual_indicators)
            
            current_price = stock_data['Close'].iloc[-1]
            atr_value = analysis_results['ATR'].iloc[-1] if 'ATR' in analysis_results.columns else current_price * 0.02
            
            # Calculate initial stop loss and targets
            stop_loss_atr = current_price - (atr_value * self.atr_multiplier)
            stop_loss_pct = current_price * (1 - self.default_stop_loss_pct)
            stop_loss = max(stop_loss_atr, stop_loss_pct)  # Use the higher (safer) stop loss
            
            target_1 = current_price * (1 + self.default_target_pct)
            target_2 = current_price * (1 + self.default_target_pct * 2)
            
            stock_entry = {
                'symbol': symbol,
                'added_date': datetime.now().isoformat(),
                'current_price': current_price,
                'last_sentiment': threshold_summary.get('overall_sentiment', 'Unknown') if threshold_summary else 'Unknown',
                'last_bullish_count': threshold_summary.get('bullish_count', 0) if threshold_summary else 0,
                'last_bearish_count': threshold_summary.get('bearish_count', 0) if threshold_summary else 0,
                'stop_loss': stop_loss,
                'target_1': target_1,
                'target_2': target_2,
                'atr_value': atr_value,
                'user_phone': user_phone,
                'user_email': user_email,
                'alerts_enabled': True,
                'last_checked': datetime.now().isoformat()
            }
            
            watchlist[symbol] = stock_entry
            self._save_watchlist(watchlist)
            
            self.logger.info(f"Added {symbol} to watchlist with stop loss ${stop_loss:.2f} and targets ${target_1:.2f}, ${target_2:.2f}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding {symbol} to watchlist: {str(e)}")
            return False
    
    def check_watchlist_alerts(self):
        """
        Check all stocks in watchlist for sentiment changes and price alerts
        
        Returns:
            List[Dict]: List of alerts generated
        """
        try:
            watchlist = self._load_watchlist()
            alerts = []
            
            for symbol, stock_info in watchlist.items():
                if not stock_info.get('alerts_enabled', True):
                    continue
                
                alert = self._check_stock_for_alerts(symbol, stock_info)
                if alert:
                    alerts.append(alert)
                    self._log_alert(alert)
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error checking watchlist alerts: {str(e)}")
            return []
    
    def _check_stock_for_alerts(self, symbol: str, stock_info: Dict) -> Optional[Dict]:
        """
        Check individual stock for alert conditions
        
        Args:
            symbol (str): Stock symbol
            stock_info (dict): Stock information from watchlist
            
        Returns:
            dict or None: Alert information if triggered
        """
        try:
            from technical_analysis import TechnicalAnalysis
            from enhanced_analysis import EnhancedAnalysis
            from data_fetcher import DataFetcher
            
            # Get current data
            data_fetcher = DataFetcher()
            stock_data = data_fetcher.fetch_stock_data(symbol, "3mo")
            
            if stock_data is None or stock_data.empty:
                return None
            
            current_price = stock_data['Close'].iloc[-1]
            
            # Get current technical analysis
            ta = TechnicalAnalysis()
            analysis_results = ta.calculate_all_indicators(stock_data)
            
            enhanced_analyzer = EnhancedAnalysis()
            individual_indicators = enhanced_analyzer.analyze_individual_indicators(analysis_results)
            threshold_summary = enhanced_analyzer.generate_threshold_summary(individual_indicators)
            
            if not threshold_summary:
                return None
            
            current_sentiment = threshold_summary.get('overall_sentiment', 'Unknown')
            current_bullish_count = threshold_summary.get('bullish_count', 0)
            current_bearish_count = threshold_summary.get('bearish_count', 0)
            
            last_sentiment = stock_info.get('last_sentiment', 'Unknown')
            last_bullish_count = stock_info.get('last_bullish_count', 0)
            
            alert_type = None
            alert_message = ""
            
            # Check for bullish sentiment change
            if (last_sentiment in ['Bearish', 'Strong Bearish', 'Neutral'] and 
                current_sentiment in ['Bullish', 'Strong Bullish']):
                
                if current_bullish_count >= self.min_bullish_indicators:
                    alert_type = "BULLISH_REVERSAL"
                    
                    # Recalculate stop loss and targets based on current price
                    atr_value = analysis_results['ATR'].iloc[-1] if 'ATR' in analysis_results.columns else current_price * 0.02
                    
                    new_stop_loss_atr = current_price - (atr_value * self.atr_multiplier)
                    new_stop_loss_pct = current_price * (1 - self.default_stop_loss_pct)
                    new_stop_loss = max(new_stop_loss_atr, new_stop_loss_pct)
                    
                    new_target_1 = current_price * (1 + self.default_target_pct)
                    new_target_2 = current_price * (1 + self.default_target_pct * 2)
                    
                    # Update watchlist entry
                    watchlist = self._load_watchlist()
                    watchlist[symbol].update({
                        'last_sentiment': current_sentiment,
                        'last_bullish_count': current_bullish_count,
                        'last_bearish_count': current_bearish_count,
                        'current_price': current_price,
                        'stop_loss': new_stop_loss,
                        'target_1': new_target_1,
                        'target_2': new_target_2,
                        'last_checked': datetime.now().isoformat()
                    })
                    self._save_watchlist(watchlist)
                    
                    alert_message = f"""
🚀 BULLISH REVERSAL ALERT: {symbol}

📈 Sentiment Change: {last_sentiment} → {current_sentiment}
💰 Current Price: ${current_price:.2f}
📊 Bullish Indicators: {current_bullish_count}/{current_bullish_count + current_bearish_count}

🎯 Trading Setup:
• Entry: ${current_price:.2f}
• Stop Loss: ${new_stop_loss:.2f} ({((new_stop_loss/current_price-1)*100):+.1f}%)
• Target 1: ${new_target_1:.2f} ({((new_target_1/current_price-1)*100):+.1f}%)
• Target 2: ${new_target_2:.2f} ({((new_target_2/current_price-1)*100):+.1f}%)

⚡ Risk/Reward Ratio: 1:{((new_target_1-current_price)/(current_price-new_stop_loss)):.1f}
                    """
            
            # Check for stop loss hit
            elif current_price <= stock_info.get('stop_loss', 0):
                alert_type = "STOP_LOSS_HIT"
                loss_pct = ((current_price / stock_info.get('current_price', current_price)) - 1) * 100
                
                alert_message = f"""
🛑 STOP LOSS HIT: {symbol}

💔 Current Price: ${current_price:.2f}
📉 Stop Loss: ${stock_info.get('stop_loss', 0):.2f}
📊 Loss: {loss_pct:.1f}%

Consider reviewing position and market conditions.
                """
            
            # Check for target hit
            elif current_price >= stock_info.get('target_1', 0):
                if current_price >= stock_info.get('target_2', 0):
                    alert_type = "TARGET_2_HIT"
                    target_level = "Target 2"
                    target_price = stock_info.get('target_2', 0)
                else:
                    alert_type = "TARGET_1_HIT"
                    target_level = "Target 1"
                    target_price = stock_info.get('target_1', 0)
                
                profit_pct = ((current_price / stock_info.get('current_price', current_price)) - 1) * 100
                
                alert_message = f"""
🎯 {target_level.upper()} HIT: {symbol}

💰 Current Price: ${current_price:.2f}
🎯 {target_level}: ${target_price:.2f}
📈 Profit: +{profit_pct:.1f}%

Consider taking partial profits or trailing stop loss.
                """
            
            # Update last checked time
            else:
                watchlist = self._load_watchlist()
                watchlist[symbol].update({
                    'last_sentiment': current_sentiment,
                    'last_bullish_count': current_bullish_count,
                    'last_bearish_count': current_bearish_count,
                    'current_price': current_price,
                    'last_checked': datetime.now().isoformat()
                })
                self._save_watchlist(watchlist)
            
            if alert_type:
                return {
                    'symbol': symbol,
                    'alert_type': alert_type,
                    'message': alert_message.strip(),
                    'current_price': current_price,
                    'timestamp': datetime.now().isoformat(),
                    'user_phone': stock_info.get('user_phone'),
                    'user_email': stock_info.get('user_email')
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error checking {symbol} for alerts: {str(e)}")
            return None
    
    def send_alert(self, alert: Dict) -> bool:
        """
        Send alert via SMS and/or email
        
        Args:
            alert (dict): Alert information
            
        Returns:
            bool: Success status
        """
        try:
            # SMS Alert (if phone number provided)
            if alert.get('user_phone'):
                sms_sent = self._send_sms_alert(alert)
                
            # Email Alert (if email provided)
            if alert.get('user_email'):
                email_sent = self._send_email_alert(alert)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending alert: {str(e)}")
            return False
    
    def _send_sms_alert(self, alert: Dict) -> bool:
        """Send SMS alert using Twilio"""
        try:
            # Import Twilio sending function
            from send_message import send_twilio_message
            
            phone = alert.get('user_phone')
            message = f"Stock Alert: {alert['symbol']}\n{alert['message'][:150]}..."
            
            send_twilio_message(phone, message)
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending SMS alert: {str(e)}")
            return False
    
    def _send_email_alert(self, alert: Dict) -> bool:
        """Send email alert (placeholder for email service integration)"""
        try:
            # This would integrate with an email service like SendGrid, SES, etc.
            # For now, we'll log the email content
            self.logger.info(f"Email alert for {alert['symbol']}: {alert['message']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending email alert: {str(e)}")
            return False
    
    def get_watchlist(self) -> Dict:
        """Get current watchlist"""
        return self._load_watchlist()
    
    def remove_from_watchlist(self, symbol: str) -> bool:
        """Remove stock from watchlist"""
        try:
            watchlist = self._load_watchlist()
            if symbol in watchlist:
                del watchlist[symbol]
                self._save_watchlist(watchlist)
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error removing {symbol} from watchlist: {str(e)}")
            return False
    
    def get_alerts_history(self) -> List[Dict]:
        """Get history of all alerts"""
        try:
            if os.path.exists(self.alerts_file):
                with open(self.alerts_file, 'r') as f:
                    return json.load(f)
            return []
            
        except Exception as e:
            self.logger.error(f"Error loading alerts history: {str(e)}")
            return []
    
    def _load_watchlist(self) -> Dict:
        """Load watchlist from file"""
        try:
            if os.path.exists(self.watchlist_file):
                with open(self.watchlist_file, 'r') as f:
                    return json.load(f)
            return {}
            
        except Exception as e:
            self.logger.error(f"Error loading watchlist: {str(e)}")
            return {}
    
    def _save_watchlist(self, watchlist: Dict):
        """Save watchlist to file"""
        try:
            with open(self.watchlist_file, 'w') as f:
                json.dump(watchlist, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving watchlist: {str(e)}")
    
    def _log_alert(self, alert: Dict):
        """Log alert to history"""
        try:
            alerts_history = self.get_alerts_history()
            alerts_history.append(alert)
            
            # Keep only last 1000 alerts
            if len(alerts_history) > 1000:
                alerts_history = alerts_history[-1000:]
            
            with open(self.alerts_file, 'w') as f:
                json.dump(alerts_history, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error logging alert: {str(e)}")