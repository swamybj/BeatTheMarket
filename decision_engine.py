import pandas as pd
import numpy as np
import logging

class DecisionEngine:
    """
    Class to generate trading decisions based on technical analysis
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Weight factors for different indicators
        self.weights = {
            'trend': 0.25,
            'momentum': 0.20,
            'mean_reversion': 0.15,
            'volatility': 0.15,
            'support_resistance': 0.15,
            'volume': 0.10
        }
    
    def generate_decision(self, analysis_data):
        """
        Generate trading decision based on technical analysis
        
        Args:
            analysis_data (pd.DataFrame): DataFrame with technical indicators
            
        Returns:
            dict: Trading decision with confidence and reasoning
        """
        try:
            if analysis_data is None or analysis_data.empty:
                return self._default_decision("No data available for analysis")
            
            # Get latest values
            latest = analysis_data.iloc[-1]
            current_price = latest['Close']
            
            # Calculate individual signals
            trend_signal = self._analyze_trend(analysis_data)
            momentum_signal = self._analyze_momentum(analysis_data)
            mean_reversion_signal = self._analyze_mean_reversion(analysis_data)
            volatility_signal = self._analyze_volatility(analysis_data)
            support_resistance_signal = self._analyze_support_resistance(analysis_data)
            volume_signal = self._analyze_volume(analysis_data)
            
            # Combine signals
            signals = {
                'trend': trend_signal,
                'momentum': momentum_signal,
                'mean_reversion': mean_reversion_signal,
                'volatility': volatility_signal,
                'support_resistance': support_resistance_signal,
                'volume': volume_signal
            }
            
            # Calculate weighted score
            total_score = 0
            for signal_type, signal_value in signals.items():
                total_score += signal_value * self.weights[signal_type]
            
            # Generate decision
            decision, confidence = self._score_to_decision(total_score)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(signals, analysis_data)
            
            # Additional analysis
            risk_level = self._assess_risk(analysis_data)
            trend_strength = self._assess_trend_strength(analysis_data)
            market_sentiment = self._assess_market_sentiment(analysis_data)
            
            # Get support and resistance levels
            support_resistance = latest['support_resistance']
            
            return {
                'decision': decision,
                'confidence': confidence,
                'total_score': total_score,
                'factors': signals,
                'reasoning': reasoning,
                'risk_level': risk_level,
                'trend_strength': trend_strength,
                'market_sentiment': market_sentiment,
                'support_resistance': support_resistance
            }
            
        except Exception as e:
            self.logger.error(f"Error generating decision: {str(e)}")
            return self._default_decision(f"Error in analysis: {str(e)}")
    
    def _analyze_trend(self, data):
        """
        Analyze trend indicators (SMA, EMA, MACD)
        
        Returns:
            float: Trend signal (-1 to 1)
        """
        latest = data.iloc[-1]
        current_price = latest['Close']
        
        signals = []
        
        # SMA signal
        if not pd.isna(latest['SMA']):
            sma_signal = 1 if current_price > latest['SMA'] else -1
            signals.append(sma_signal)
        
        # EMA signal
        if not pd.isna(latest['EMA']):
            ema_signal = 1 if current_price > latest['EMA'] else -1
            signals.append(ema_signal)
        
        # MACD signal
        if not pd.isna(latest['MACD']) and not pd.isna(latest['MACD_Signal']):
            macd_signal = 1 if latest['MACD'] > latest['MACD_Signal'] else -1
            signals.append(macd_signal)
        
        # Price trend
        if len(data) >= 20:
            recent_trend = data['Close'].tail(20).pct_change().mean()
            trend_signal = np.clip(recent_trend * 100, -1, 1)
            signals.append(trend_signal)
        
        return np.mean(signals) if signals else 0
    
    def _analyze_momentum(self, data):
        """
        Analyze momentum indicators (RSI, MACD histogram)
        
        Returns:
            float: Momentum signal (-1 to 1)
        """
        latest = data.iloc[-1]
        
        signals = []
        
        # RSI signal
        if not pd.isna(latest['RSI']):
            rsi = latest['RSI']
            if rsi < 30:
                rsi_signal = 1  # Oversold, bullish
            elif rsi > 70:
                rsi_signal = -1  # Overbought, bearish
            else:
                # Normalize RSI to -1 to 1 scale
                rsi_signal = (rsi - 50) / 50
            signals.append(rsi_signal)
        
        # MACD Histogram signal
        if not pd.isna(latest['MACD_Histogram']):
            macd_hist = latest['MACD_Histogram']
            # Look at histogram trend
            if len(data) >= 3:
                hist_trend = data['MACD_Histogram'].tail(3).diff().mean()
                hist_signal = np.clip(hist_trend * 10, -1, 1)
                signals.append(hist_signal)
        
        return np.mean(signals) if signals else 0
    
    def _analyze_mean_reversion(self, data):
        """
        Analyze mean reversion indicators (Bollinger Bands)
        
        Returns:
            float: Mean reversion signal (-1 to 1)
        """
        latest = data.iloc[-1]
        current_price = latest['Close']
        
        signals = []
        
        # Bollinger Bands signal
        if not pd.isna(latest['BB_Upper']) and not pd.isna(latest['BB_Lower']):
            bb_upper = latest['BB_Upper']
            bb_lower = latest['BB_Lower']
            bb_middle = latest['BB_Middle']
            
            if current_price > bb_upper:
                bb_signal = -1  # Overbought
            elif current_price < bb_lower:
                bb_signal = 1  # Oversold
            else:
                # Position within bands
                bb_position = (current_price - bb_middle) / (bb_upper - bb_middle)
                bb_signal = -bb_position  # Reverse signal for mean reversion
            
            signals.append(bb_signal)
        
        return np.mean(signals) if signals else 0
    
    def _analyze_volatility(self, data):
        """
        Analyze volatility indicators (ATR)
        
        Returns:
            float: Volatility signal (-1 to 1)
        """
        latest = data.iloc[-1]
        
        signals = []
        
        # ATR signal
        if not pd.isna(latest['ATR']) and len(data) >= 20:
            current_atr = latest['ATR']
            avg_atr = data['ATR'].tail(20).mean()
            
            if current_atr > avg_atr * 1.5:
                atr_signal = -0.5  # High volatility, be cautious
            elif current_atr < avg_atr * 0.5:
                atr_signal = 0.5  # Low volatility, opportunity
            else:
                atr_signal = 0
            
            signals.append(atr_signal)
        
        return np.mean(signals) if signals else 0
    
    def _analyze_support_resistance(self, data):
        """
        Analyze support and resistance levels
        
        Returns:
            float: Support/resistance signal (-1 to 1)
        """
        latest = data.iloc[-1]
        current_price = latest['Close']
        support_resistance = latest['support_resistance']
        
        signals = []
        
        if support_resistance:
            resistance = support_resistance.get('resistance')
            support = support_resistance.get('support')
            
            if resistance and support:
                # Distance to support/resistance as percentage
                dist_to_resistance = (resistance - current_price) / current_price
                dist_to_support = (current_price - support) / current_price
                
                # Closer to support = bullish, closer to resistance = bearish
                if dist_to_support < 0.02:  # Within 2% of support
                    sr_signal = 1
                elif dist_to_resistance < 0.02:  # Within 2% of resistance
                    sr_signal = -1
                else:
                    # Weighted by relative position
                    total_range = resistance - support
                    position = (current_price - support) / total_range
                    sr_signal = 0.5 - position  # Bullish near support, bearish near resistance
                
                signals.append(sr_signal)
        
        return np.mean(signals) if signals else 0
    
    def _analyze_volume(self, data):
        """
        Analyze volume patterns
        
        Returns:
            float: Volume signal (-1 to 1)
        """
        if len(data) < 20:
            return 0
        
        latest = data.iloc[-1]
        recent_volume = data['Volume'].tail(5).mean()
        avg_volume = data['Volume'].tail(20).mean()
        
        # Price and volume relationship
        price_change = data['Close'].pct_change().iloc[-1]
        volume_ratio = recent_volume / avg_volume
        
        # High volume with price increase = bullish
        # High volume with price decrease = bearish
        if volume_ratio > 1.5:  # High volume
            volume_signal = 1 if price_change > 0 else -1
        else:
            volume_signal = 0
        
        return volume_signal * 0.5  # Moderate weight
    
    def _score_to_decision(self, score):
        """
        Convert numerical score to trading decision
        
        Args:
            score (float): Combined signal score
            
        Returns:
            tuple: (decision, confidence)
        """
        abs_score = abs(score)
        confidence = min(abs_score * 100, 95)  # Cap confidence at 95%
        
        if score > 0.3:
            decision = "BUY"
        elif score < -0.3:
            decision = "SELL"
        else:
            decision = "HOLD"
        
        # Minimum confidence threshold
        if confidence < 30:
            decision = "HOLD"
            confidence = max(confidence, 30)
        
        return decision, confidence
    
    def _generate_reasoning(self, signals, data):
        """
        Generate human-readable reasoning for the decision
        
        Args:
            signals (dict): Individual signal scores
            data (pd.DataFrame): Analysis data
            
        Returns:
            str: Reasoning text
        """
        reasoning_parts = []
        
        # Trend analysis
        trend_score = signals['trend']
        if trend_score > 0.3:
            reasoning_parts.append("The stock shows a strong upward trend with price above key moving averages.")
        elif trend_score < -0.3:
            reasoning_parts.append("The stock is in a downward trend with price below key moving averages.")
        else:
            reasoning_parts.append("The stock is trading sideways with mixed trend signals.")
        
        # Momentum analysis
        momentum_score = signals['momentum']
        latest = data.iloc[-1]
        rsi = latest['RSI']
        
        if not pd.isna(rsi):
            if rsi < 30:
                reasoning_parts.append(f"RSI at {rsi:.1f} indicates oversold conditions, suggesting potential upward reversal.")
            elif rsi > 70:
                reasoning_parts.append(f"RSI at {rsi:.1f} indicates overbought conditions, suggesting potential downward correction.")
            else:
                reasoning_parts.append(f"RSI at {rsi:.1f} shows neutral momentum.")
        
        # Support/Resistance analysis
        sr_score = signals['support_resistance']
        if sr_score > 0.3:
            reasoning_parts.append("Price is near support levels, providing potential buying opportunity.")
        elif sr_score < -0.3:
            reasoning_parts.append("Price is approaching resistance levels, suggesting caution.")
        
        # Volatility analysis
        vol_score = signals['volatility']
        if vol_score < -0.3:
            reasoning_parts.append("High volatility suggests increased risk and uncertainty.")
        elif vol_score > 0.3:
            reasoning_parts.append("Low volatility environment may present opportunities.")
        
        return " ".join(reasoning_parts)
    
    def _assess_risk(self, data):
        """
        Assess overall risk level
        
        Returns:
            str: Risk level description
        """
        latest = data.iloc[-1]
        
        # ATR-based volatility
        if not pd.isna(latest['ATR']) and len(data) >= 20:
            current_atr = latest['ATR']
            avg_atr = data['ATR'].tail(20).mean()
            atr_ratio = current_atr / avg_atr
            
            if atr_ratio > 1.5:
                return "High"
            elif atr_ratio < 0.7:
                return "Low"
            else:
                return "Medium"
        
        return "Medium"
    
    def _assess_trend_strength(self, data):
        """
        Assess trend strength
        
        Returns:
            str: Trend strength description
        """
        if len(data) < 20:
            return "Insufficient data"
        
        # Calculate trend consistency
        price_changes = data['Close'].tail(20).pct_change()
        positive_days = (price_changes > 0).sum()
        trend_consistency = abs(positive_days - 10) / 10
        
        if trend_consistency > 0.6:
            return "Strong"
        elif trend_consistency > 0.3:
            return "Moderate"
        else:
            return "Weak"
    
    def _assess_market_sentiment(self, data):
        """
        Assess market sentiment based on technical indicators
        
        Returns:
            str: Market sentiment description
        """
        latest = data.iloc[-1]
        bullish_signals = 0
        total_signals = 0
        
        # RSI sentiment
        if not pd.isna(latest['RSI']):
            total_signals += 1
            if latest['RSI'] > 50:
                bullish_signals += 1
        
        # MACD sentiment
        if not pd.isna(latest['MACD']) and not pd.isna(latest['MACD_Signal']):
            total_signals += 1
            if latest['MACD'] > latest['MACD_Signal']:
                bullish_signals += 1
        
        # Price vs SMA sentiment
        if not pd.isna(latest['SMA']):
            total_signals += 1
            if latest['Close'] > latest['SMA']:
                bullish_signals += 1
        
        if total_signals > 0:
            bullish_ratio = bullish_signals / total_signals
            if bullish_ratio > 0.7:
                return "Bullish"
            elif bullish_ratio < 0.3:
                return "Bearish"
            else:
                return "Neutral"
        
        return "Unknown"
    
    def _default_decision(self, reason):
        """
        Return default decision when analysis fails
        
        Args:
            reason (str): Reason for default decision
            
        Returns:
            dict: Default decision data
        """
        return {
            'decision': 'HOLD',
            'confidence': 0,
            'total_score': 0,
            'factors': {},
            'reasoning': f"Unable to generate decision: {reason}",
            'risk_level': 'Unknown',
            'trend_strength': 'Unknown',
            'market_sentiment': 'Unknown',
            'support_resistance': {}
        }
