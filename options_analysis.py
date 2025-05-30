import yfinance as yf
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from scipy.stats import norm
import math

class OptionsAnalysis:
    """
    Class to analyze options strategies and calculate profitable strike prices
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_options_data(self, symbol):
        """
        Get options data for a given symbol
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            dict: Options data with calls and puts
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Get available expiration dates
            expiration_dates = ticker.options
            
            if not expiration_dates:
                return None
            
            options_data = {}
            
            # Get options for the next 3 expiration dates
            for exp_date in expiration_dates[:3]:
                try:
                    option_chain = ticker.option_chain(exp_date)
                    options_data[exp_date] = {
                        'calls': option_chain.calls,
                        'puts': option_chain.puts
                    }
                except Exception as e:
                    self.logger.warning(f"Could not get options for {exp_date}: {str(e)}")
                    continue
            
            return options_data
            
        except Exception as e:
            self.logger.error(f"Error getting options data for {symbol}: {str(e)}")
            return None
    
    def calculate_black_scholes(self, spot_price, strike_price, time_to_expiry, risk_free_rate, volatility, option_type='call'):
        """
        Calculate Black-Scholes option price
        
        Args:
            spot_price (float): Current stock price
            strike_price (float): Strike price
            time_to_expiry (float): Time to expiry in years
            risk_free_rate (float): Risk-free rate
            volatility (float): Implied volatility
            option_type (str): 'call' or 'put'
            
        Returns:
            float: Option price
        """
        try:
            if time_to_expiry <= 0:
                if option_type == 'call':
                    return max(spot_price - strike_price, 0)
                else:
                    return max(strike_price - spot_price, 0)
            
            d1 = (math.log(spot_price / strike_price) + (risk_free_rate + 0.5 * volatility**2) * time_to_expiry) / (volatility * math.sqrt(time_to_expiry))
            d2 = d1 - volatility * math.sqrt(time_to_expiry)
            
            if option_type == 'call':
                price = spot_price * norm.cdf(d1) - strike_price * math.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2)
            else:
                price = strike_price * math.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2) - spot_price * norm.cdf(-d1)
            
            return price
            
        except Exception as e:
            self.logger.error(f"Error calculating Black-Scholes price: {str(e)}")
            return 0
    
    def calculate_greeks(self, spot_price, strike_price, time_to_expiry, risk_free_rate, volatility, option_type='call'):
        """
        Calculate option Greeks (Delta, Gamma, Theta, Vega)
        """
        try:
            if time_to_expiry <= 0:
                return {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0}
            
            d1 = (math.log(spot_price / strike_price) + (risk_free_rate + 0.5 * volatility**2) * time_to_expiry) / (volatility * math.sqrt(time_to_expiry))
            d2 = d1 - volatility * math.sqrt(time_to_expiry)
            
            # Delta
            if option_type == 'call':
                delta = norm.cdf(d1)
            else:
                delta = norm.cdf(d1) - 1
            
            # Gamma
            gamma = norm.pdf(d1) / (spot_price * volatility * math.sqrt(time_to_expiry))
            
            # Theta
            if option_type == 'call':
                theta = (-spot_price * norm.pdf(d1) * volatility / (2 * math.sqrt(time_to_expiry)) 
                        - risk_free_rate * strike_price * math.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2)) / 365
            else:
                theta = (-spot_price * norm.pdf(d1) * volatility / (2 * math.sqrt(time_to_expiry)) 
                        + risk_free_rate * strike_price * math.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2)) / 365
            
            # Vega
            vega = spot_price * norm.pdf(d1) * math.sqrt(time_to_expiry) / 100
            
            return {
                'delta': delta,
                'gamma': gamma,
                'theta': theta,
                'vega': vega
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating Greeks: {str(e)}")
            return {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0}
    
    def analyze_option_strategies(self, symbol, current_price, volatility):
        """
        Analyze various option strategies and their profitability
        
        Args:
            symbol (str): Stock symbol
            current_price (float): Current stock price
            volatility (float): Implied volatility
            
        Returns:
            dict: Analysis of different option strategies
        """
        try:
            options_data = self.get_options_data(symbol)
            
            if not options_data:
                return None
            
            risk_free_rate = 0.05  # Assume 5% risk-free rate
            strategies = {}
            
            # Analyze for the nearest expiration
            nearest_exp = list(options_data.keys())[0]
            exp_date = datetime.strptime(nearest_exp, '%Y-%m-%d')
            days_to_exp = (exp_date - datetime.now()).days
            time_to_expiry = days_to_exp / 365.0
            
            calls = options_data[nearest_exp]['calls']
            puts = options_data[nearest_exp]['puts']
            
            if calls.empty or puts.empty:
                return None
            
            # Find ATM options
            atm_call = calls.iloc[(calls['strike'] - current_price).abs().argsort()[:1]]
            atm_put = puts.iloc[(puts['strike'] - current_price).abs().argsort()[:1]]
            
            if not atm_call.empty and not atm_put.empty:
                atm_strike = atm_call['strike'].iloc[0]
                call_price = atm_call['lastPrice'].iloc[0]
                put_price = atm_put['lastPrice'].iloc[0]
                
                # Long Call Strategy
                strategies['long_call'] = {
                    'strategy': 'Long Call',
                    'strike': atm_strike,
                    'premium': call_price,
                    'breakeven': atm_strike + call_price,
                    'max_profit': 'Unlimited',
                    'max_loss': call_price,
                    'probability_profit': self._calculate_probability_above(current_price, atm_strike + call_price, volatility, time_to_expiry)
                }
                
                # Long Put Strategy
                strategies['long_put'] = {
                    'strategy': 'Long Put',
                    'strike': atm_strike,
                    'premium': put_price,
                    'breakeven': atm_strike - put_price,
                    'max_profit': atm_strike - put_price,
                    'max_loss': put_price,
                    'probability_profit': self._calculate_probability_below(current_price, atm_strike - put_price, volatility, time_to_expiry)
                }
                
                # Covered Call Strategy (if you own the stock)
                strategies['covered_call'] = {
                    'strategy': 'Covered Call',
                    'strike': atm_strike,
                    'premium_received': call_price,
                    'breakeven': current_price - call_price,
                    'max_profit': (atm_strike - current_price) + call_price,
                    'max_loss': current_price - call_price,
                    'probability_profit': self._calculate_probability_below(current_price, atm_strike, volatility, time_to_expiry)
                }
                
                # Protective Put Strategy (if you own the stock)
                strategies['protective_put'] = {
                    'strategy': 'Protective Put',
                    'strike': atm_strike,
                    'premium_paid': put_price,
                    'breakeven': current_price + put_price,
                    'max_profit': 'Unlimited',
                    'max_loss': current_price - atm_strike + put_price,
                    'probability_profit': self._calculate_probability_above(current_price, current_price + put_price, volatility, time_to_expiry)
                }
                
                # Straddle Strategy
                straddle_cost = call_price + put_price
                strategies['long_straddle'] = {
                    'strategy': 'Long Straddle',
                    'strike': atm_strike,
                    'premium_paid': straddle_cost,
                    'breakeven_upper': atm_strike + straddle_cost,
                    'breakeven_lower': atm_strike - straddle_cost,
                    'max_profit': 'Unlimited',
                    'max_loss': straddle_cost,
                    'probability_profit': 1 - self._calculate_probability_between(current_price, atm_strike - straddle_cost, atm_strike + straddle_cost, volatility, time_to_expiry)
                }
            
            return {
                'expiration': nearest_exp,
                'days_to_expiry': days_to_exp,
                'strategies': strategies,
                'current_iv': volatility * 100
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing option strategies: {str(e)}")
            return None
    
    def _calculate_probability_above(self, current_price, target_price, volatility, time_to_expiry):
        """Calculate probability that stock price will be above target at expiration"""
        try:
            if time_to_expiry <= 0:
                return 1.0 if current_price > target_price else 0.0
            
            d = (math.log(target_price / current_price)) / (volatility * math.sqrt(time_to_expiry))
            return 1 - norm.cdf(d)
            
        except:
            return 0.5
    
    def _calculate_probability_below(self, current_price, target_price, volatility, time_to_expiry):
        """Calculate probability that stock price will be below target at expiration"""
        return 1 - self._calculate_probability_above(current_price, target_price, volatility, time_to_expiry)
    
    def _calculate_probability_between(self, current_price, lower_target, upper_target, volatility, time_to_expiry):
        """Calculate probability that stock price will be between two targets at expiration"""
        prob_above_lower = self._calculate_probability_above(current_price, lower_target, volatility, time_to_expiry)
        prob_above_upper = self._calculate_probability_above(current_price, upper_target, volatility, time_to_expiry)
        return prob_above_lower - prob_above_upper
    
    def get_profitable_strikes(self, symbol, current_price, volatility, target_profit=0.2):
        """
        Find strike prices that could be profitable based on target profit
        
        Args:
            symbol (str): Stock symbol
            current_price (float): Current stock price
            volatility (float): Stock volatility
            target_profit (float): Target profit percentage
            
        Returns:
            dict: Profitable strike analysis
        """
        try:
            options_data = self.get_options_data(symbol)
            
            if not options_data:
                return None
            
            profitable_analysis = {}
            
            for exp_date, data in list(options_data.items())[:2]:  # Analyze first 2 expirations
                exp_datetime = datetime.strptime(exp_date, '%Y-%m-%d')
                days_to_exp = (exp_datetime - datetime.now()).days
                time_to_expiry = days_to_exp / 365.0
                
                calls = data['calls']
                puts = data['puts']
                
                profitable_calls = []
                profitable_puts = []
                
                # Analyze calls
                for _, call in calls.iterrows():
                    strike = call['strike']
                    premium = call.get('lastPrice', 0)
                    
                    if premium > 0:
                        breakeven = strike + premium
                        profit_target_price = current_price * (1 + target_profit)
                        
                        if profit_target_price > breakeven:
                            probability = self._calculate_probability_above(current_price, breakeven, volatility, time_to_expiry)
                            
                            profitable_calls.append({
                                'strike': strike,
                                'premium': premium,
                                'breakeven': breakeven,
                                'probability_profit': probability,
                                'potential_profit': 'Unlimited',
                                'risk_reward': 'High Risk/High Reward'
                            })
                
                # Analyze puts
                for _, put in puts.iterrows():
                    strike = put['strike']
                    premium = put.get('lastPrice', 0)
                    
                    if premium > 0:
                        breakeven = strike - premium
                        profit_target_price = current_price * (1 - target_profit)
                        
                        if profit_target_price < breakeven:
                            probability = self._calculate_probability_below(current_price, breakeven, volatility, time_to_expiry)
                            
                            profitable_puts.append({
                                'strike': strike,
                                'premium': premium,
                                'breakeven': breakeven,
                                'probability_profit': probability,
                                'potential_profit': breakeven,
                                'risk_reward': 'High Risk/High Reward'
                            })
                
                profitable_analysis[exp_date] = {
                    'days_to_expiry': days_to_exp,
                    'profitable_calls': sorted(profitable_calls, key=lambda x: x['probability_profit'], reverse=True)[:5],
                    'profitable_puts': sorted(profitable_puts, key=lambda x: x['probability_profit'], reverse=True)[:5]
                }
            
            return profitable_analysis
            
        except Exception as e:
            self.logger.error(f"Error finding profitable strikes: {str(e)}")
            return None