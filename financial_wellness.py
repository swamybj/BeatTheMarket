import pandas as pd
import numpy as np
from datetime import datetime
import logging

class FinancialWellnessAnalyzer:
    """
    Comprehensive financial wellness analyzer that evaluates stock investments
    and provides personalized improvement suggestions
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_wellness_report(self, symbol, stock_data, analysis_data, decision_data, 
                               financial_data, sector_data, options_data, news_data):
        """
        Generate comprehensive financial wellness report with improvement suggestions
        
        Args:
            symbol (str): Stock symbol
            stock_data (pd.DataFrame): Historical price data
            analysis_data (pd.DataFrame): Technical analysis data
            decision_data (dict): Trading decision data
            financial_data (dict): Financial metrics
            sector_data (dict): Sector comparison data
            options_data (dict): Options analysis data
            news_data (dict): News and sentiment data
            
        Returns:
            dict: Comprehensive wellness report
        """
        try:
            current_price = stock_data['Close'].iloc[-1]
            
            # Calculate individual wellness scores
            valuation_score = self._assess_valuation_health(financial_data, current_price)
            technical_score = self._assess_technical_health(analysis_data, decision_data)
            fundamental_score = self._assess_fundamental_health(financial_data)
            market_position_score = self._assess_market_position(sector_data, financial_data)
            risk_score = self._assess_risk_profile(analysis_data, options_data)
            sentiment_score = self._assess_sentiment_health(news_data, decision_data)
            
            # Calculate overall wellness score
            overall_score = self._calculate_overall_score([
                valuation_score, technical_score, fundamental_score,
                market_position_score, risk_score, sentiment_score
            ])
            
            # Generate personalized suggestions
            suggestions = self._generate_improvement_suggestions(
                symbol, valuation_score, technical_score, fundamental_score,
                market_position_score, risk_score, sentiment_score,
                analysis_data, financial_data, decision_data
            )
            
            # Create comprehensive report
            report = {
                'symbol': symbol,
                'current_price': current_price,
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'overall_wellness_score': overall_score,
                'wellness_grade': self._score_to_grade(overall_score),
                'category_scores': {
                    'valuation': valuation_score,
                    'technical': technical_score,
                    'fundamental': fundamental_score,
                    'market_position': market_position_score,
                    'risk_management': risk_score,
                    'sentiment': sentiment_score
                },
                'key_strengths': self._identify_strengths(
                    valuation_score, technical_score, fundamental_score,
                    market_position_score, risk_score, sentiment_score
                ),
                'improvement_areas': self._identify_weaknesses(
                    valuation_score, technical_score, fundamental_score,
                    market_position_score, risk_score, sentiment_score
                ),
                'personalized_suggestions': suggestions,
                'action_items': self._generate_action_items(suggestions),
                'investment_outlook': self._generate_outlook(overall_score, decision_data),
                'risk_assessment': self._generate_risk_assessment(risk_score, analysis_data)
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating wellness report for {symbol}: {str(e)}")
            return None
    
    def _assess_valuation_health(self, financial_data, current_price):
        """Assess valuation health based on P/E ratios and price metrics"""
        try:
            score = 50  # Base score
            
            if financial_data and 'metrics' in financial_data:
                metrics = financial_data['metrics']
                
                # P/E ratio assessment
                pe_ratio = metrics.get('pe_ratio', 0)
                if pe_ratio > 0:
                    if pe_ratio < 15:
                        score += 20  # Undervalued
                    elif pe_ratio < 25:
                        score += 10  # Fair value
                    elif pe_ratio > 40:
                        score -= 20  # Overvalued
                
                # Price to book assessment
                pb_ratio = metrics.get('price_to_book', 0)
                if pb_ratio > 0:
                    if pb_ratio < 1.5:
                        score += 10
                    elif pb_ratio > 5:
                        score -= 10
                
                # Revenue growth
                revenue_growth = metrics.get('revenue_growth_yoy', 0)
                if revenue_growth > 15:
                    score += 15
                elif revenue_growth < -5:
                    score -= 15
            
            return max(0, min(100, score))
            
        except:
            return 50
    
    def _assess_technical_health(self, analysis_data, decision_data):
        """Assess technical analysis health"""
        try:
            score = 50  # Base score
            
            if analysis_data is not None and not analysis_data.empty:
                latest = analysis_data.iloc[-1]
                
                # RSI assessment
                rsi = latest.get('RSI', 50)
                if 30 <= rsi <= 70:
                    score += 15  # Healthy range
                elif rsi < 20 or rsi > 80:
                    score -= 10  # Extreme levels
                
                # MACD assessment
                macd = latest.get('MACD', 0)
                macd_signal = latest.get('MACD_Signal', 0)
                if macd > macd_signal:
                    score += 10  # Bullish signal
                else:
                    score -= 5
                
                # Moving average alignment
                sma_20 = latest.get('SMA_20', 0)
                sma_50 = latest.get('SMA_50', 0)
                current_price = latest.get('Close', 0)
                
                if current_price > sma_20 > sma_50:
                    score += 15  # Bullish alignment
                elif current_price < sma_20 < sma_50:
                    score -= 10  # Bearish alignment
            
            # Decision confidence
            if decision_data:
                confidence = decision_data.get('confidence', 50)
                decision = decision_data.get('decision', '')
                
                if 'Buy' in decision and confidence > 75:
                    score += 10
                elif 'Sell' in decision:
                    score -= 10
            
            return max(0, min(100, score))
            
        except:
            return 50
    
    def _assess_fundamental_health(self, financial_data):
        """Assess fundamental financial health"""
        try:
            score = 50  # Base score
            
            if financial_data and 'metrics' in financial_data:
                metrics = financial_data['metrics']
                
                # Profitability
                profit_margin = metrics.get('profit_margin', 0)
                if profit_margin > 15:
                    score += 20
                elif profit_margin < 5:
                    score -= 15
                
                # ROE assessment
                roe = metrics.get('roe', 0)
                if roe > 15:
                    score += 15
                elif roe < 5:
                    score -= 10
                
                # Debt to equity
                debt_equity = metrics.get('debt_to_equity', 0)
                if debt_equity < 0.3:
                    score += 10
                elif debt_equity > 2:
                    score -= 15
                
                # Current ratio
                current_ratio = metrics.get('current_ratio', 0)
                if current_ratio > 1.5:
                    score += 10
                elif current_ratio < 1:
                    score -= 15
            
            return max(0, min(100, score))
            
        except:
            return 50
    
    def _assess_market_position(self, sector_data, financial_data):
        """Assess market position relative to peers"""
        try:
            score = 50  # Base score
            
            # Market cap assessment
            if financial_data and 'metrics' in financial_data:
                market_cap = financial_data['metrics'].get('market_cap', 0)
                if market_cap > 10e9:  # Large cap
                    score += 15
                elif market_cap > 2e9:  # Mid cap
                    score += 5
                
            # Sector comparison
            if sector_data:
                sector_performance = sector_data.get('performance_vs_sector', 0)
                if sector_performance > 5:
                    score += 20
                elif sector_performance < -10:
                    score -= 15
            
            return max(0, min(100, score))
            
        except:
            return 50
    
    def _assess_risk_profile(self, analysis_data, options_data):
        """Assess risk profile based on volatility and other factors"""
        try:
            score = 50  # Base score
            
            if analysis_data is not None and not analysis_data.empty:
                latest = analysis_data.iloc[-1]
                
                # Volatility assessment
                volatility = latest.get('Volatility', 0.02)
                if volatility < 0.15:
                    score += 15  # Low volatility
                elif volatility > 0.4:
                    score -= 20  # High volatility
                
                # ATR assessment
                atr = latest.get('ATR', 0)
                current_price = latest.get('Close', 100)
                if atr > 0 and current_price > 0:
                    atr_percent = (atr / current_price) * 100
                    if atr_percent < 2:
                        score += 10
                    elif atr_percent > 5:
                        score -= 15
            
            return max(0, min(100, score))
            
        except:
            return 50
    
    def _assess_sentiment_health(self, news_data, decision_data):
        """Assess sentiment and market perception"""
        try:
            score = 50  # Base score
            
            if news_data:
                sentiment_data = news_data.get('sentiment', {})
                sentiment = sentiment_data.get('sentiment', 'neutral')
                
                if sentiment == 'positive':
                    score += 20
                elif sentiment == 'negative':
                    score -= 20
                
                # News volume
                news_count = sentiment_data.get('total_news', 0)
                if news_count > 5:
                    score += 5  # Good coverage
            
            return max(0, min(100, score))
            
        except:
            return 50
    
    def _calculate_overall_score(self, scores):
        """Calculate weighted overall wellness score"""
        weights = [0.2, 0.2, 0.25, 0.15, 0.1, 0.1]  # Weights for each category
        weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
        return round(weighted_sum, 1)
    
    def _score_to_grade(self, score):
        """Convert numerical score to letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _identify_strengths(self, valuation, technical, fundamental, market, risk, sentiment):
        """Identify key strengths based on scores"""
        strengths = []
        scores = {
            'Valuation': valuation,
            'Technical Analysis': technical,
            'Fundamental Health': fundamental,
            'Market Position': market,
            'Risk Management': risk,
            'Market Sentiment': sentiment
        }
        
        for category, score in scores.items():
            if score >= 75:
                strengths.append(category)
        
        return strengths
    
    def _identify_weaknesses(self, valuation, technical, fundamental, market, risk, sentiment):
        """Identify areas needing improvement"""
        weaknesses = []
        scores = {
            'Valuation': valuation,
            'Technical Analysis': technical,
            'Fundamental Health': fundamental,
            'Market Position': market,
            'Risk Management': risk,
            'Market Sentiment': sentiment
        }
        
        for category, score in scores.items():
            if score < 60:
                weaknesses.append(category)
        
        return weaknesses
    
    def _generate_improvement_suggestions(self, symbol, valuation, technical, fundamental, 
                                        market, risk, sentiment, analysis_data, financial_data, decision_data):
        """Generate personalized improvement suggestions"""
        suggestions = []
        
        # Valuation suggestions
        if valuation < 60:
            suggestions.append({
                'category': 'Valuation',
                'priority': 'High',
                'suggestion': 'Consider waiting for better entry point or dollar-cost averaging',
                'reason': 'Current valuation metrics suggest the stock may be overpriced'
            })
        
        # Technical suggestions
        if technical < 60:
            suggestions.append({
                'category': 'Technical',
                'priority': 'Medium',
                'suggestion': 'Monitor key support levels and wait for technical confirmation',
                'reason': 'Technical indicators show mixed or bearish signals'
            })
        
        # Fundamental suggestions
        if fundamental < 60:
            suggestions.append({
                'category': 'Fundamental',
                'priority': 'High',
                'suggestion': 'Review financial statements for debt levels and profitability trends',
                'reason': 'Fundamental metrics indicate potential financial health concerns'
            })
        
        # Risk management suggestions
        if risk < 60:
            suggestions.append({
                'category': 'Risk Management',
                'priority': 'High',
                'suggestion': 'Consider position sizing and stop-loss strategies due to high volatility',
                'reason': 'High volatility indicates elevated risk levels'
            })
        
        # Add positive suggestions for strong areas
        if valuation >= 80:
            suggestions.append({
                'category': 'Valuation',
                'priority': 'Low',
                'suggestion': 'Good entry point - consider accumulating on weakness',
                'reason': 'Attractive valuation metrics suggest good value opportunity'
            })
        
        return suggestions
    
    def _generate_action_items(self, suggestions):
        """Generate specific action items from suggestions"""
        actions = []
        
        high_priority = [s for s in suggestions if s['priority'] == 'High']
        
        if high_priority:
            actions.append("Address high-priority concerns before investing")
        
        actions.append("Set up price alerts for key technical levels")
        actions.append("Monitor quarterly earnings for fundamental changes")
        actions.append("Review portfolio allocation and risk management")
        
        return actions
    
    def _generate_outlook(self, overall_score, decision_data):
        """Generate investment outlook based on wellness score"""
        if overall_score >= 80:
            return "Strong investment candidate with good risk-adjusted potential"
        elif overall_score >= 70:
            return "Solid investment option with some areas to monitor"
        elif overall_score >= 60:
            return "Moderate investment potential with notable concerns"
        else:
            return "High-risk investment requiring careful consideration"
    
    def _generate_risk_assessment(self, risk_score, analysis_data):
        """Generate detailed risk assessment"""
        if risk_score >= 80:
            return "Low risk profile suitable for conservative investors"
        elif risk_score >= 60:
            return "Moderate risk with balanced volatility characteristics"
        else:
            return "High risk investment requiring active monitoring"