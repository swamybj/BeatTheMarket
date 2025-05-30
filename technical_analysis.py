import pandas as pd
import numpy as np
from scipy import stats
import logging

class TechnicalAnalysis:
    """
    Class to calculate various technical analysis indicators
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_sma(self, data, period=20):
        """
        Calculate Simple Moving Average
        
        Args:
            data (pd.Series): Price data (typically Close prices)
            period (int): Period for SMA calculation
            
        Returns:
            pd.Series: SMA values
        """
        return data.rolling(window=period).mean()
    
    def calculate_ema(self, data, period=20):
        """
        Calculate Exponential Moving Average
        
        Args:
            data (pd.Series): Price data
            period (int): Period for EMA calculation
            
        Returns:
            pd.Series: EMA values
        """
        return data.ewm(span=period).mean()
    
    def calculate_rsi(self, data, period=14):
        """
        Calculate Relative Strength Index
        
        Args:
            data (pd.Series): Price data
            period (int): Period for RSI calculation
            
        Returns:
            pd.Series: RSI values
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_macd(self, data, fast_period=12, slow_period=26, signal_period=9):
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            data (pd.Series): Price data
            fast_period (int): Fast EMA period
            slow_period (int): Slow EMA period
            signal_period (int): Signal line EMA period
            
        Returns:
            tuple: (MACD line, Signal line, Histogram)
        """
        ema_fast = self.calculate_ema(data, fast_period)
        ema_slow = self.calculate_ema(data, slow_period)
        
        macd_line = ema_fast - ema_slow
        signal_line = self.calculate_ema(macd_line, signal_period)
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def calculate_bollinger_bands(self, data, period=20, std_dev=2):
        """
        Calculate Bollinger Bands
        
        Args:
            data (pd.Series): Price data
            period (int): Period for moving average
            std_dev (float): Standard deviation multiplier
            
        Returns:
            tuple: (Upper band, Middle band, Lower band)
        """
        middle_band = self.calculate_sma(data, period)
        std = data.rolling(window=period).std()
        
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)
        
        return upper_band, middle_band, lower_band
    
    def calculate_atr(self, high, low, close, period=14):
        """
        Calculate Average True Range
        
        Args:
            high (pd.Series): High prices
            low (pd.Series): Low prices
            close (pd.Series): Close prices
            period (int): Period for ATR calculation
            
        Returns:
            pd.Series: ATR values
        """
        # Calculate True Range
        tr1 = high - low
        tr2 = np.abs(high - close.shift(1))
        tr3 = np.abs(low - close.shift(1))
        
        true_range = np.maximum(tr1, np.maximum(tr2, tr3))
        
        # Calculate ATR as moving average of True Range
        atr = true_range.rolling(window=period).mean()
        
        return atr
    
    def calculate_fibonacci_retracement(self, high_price, low_price):
        """
        Calculate Fibonacci retracement levels
        
        Args:
            high_price (float): High price for the period
            low_price (float): Low price for the period
            
        Returns:
            dict: Fibonacci retracement levels
        """
        difference = high_price - low_price
        
        levels = {
            '0%': high_price,
            '23.6%': high_price - (0.236 * difference),
            '38.2%': high_price - (0.382 * difference),
            '50%': high_price - (0.5 * difference),
            '61.8%': high_price - (0.618 * difference),
            '78.6%': high_price - (0.786 * difference),
            '100%': low_price
        }
        
        return levels
    
    def identify_support_resistance(self, data, window=20, min_touches=2):
        """
        Identify support and resistance levels
        
        Args:
            data (pd.DataFrame): OHLC data
            window (int): Window for local minima/maxima
            min_touches (int): Minimum touches for a valid level
            
        Returns:
            dict: Support and resistance levels
        """
        highs = data['High']
        lows = data['Low']
        
        # Find local minima and maxima
        local_minima = []
        local_maxima = []
        
        for i in range(window, len(data) - window):
            # Local minimum
            if lows.iloc[i] == lows.iloc[i-window:i+window+1].min():
                local_minima.append((data.index[i], lows.iloc[i]))
            
            # Local maximum
            if highs.iloc[i] == highs.iloc[i-window:i+window+1].max():
                local_maxima.append((data.index[i], highs.iloc[i]))
        
        # Group similar levels
        support_levels = self._group_levels([price for _, price in local_minima])
        resistance_levels = self._group_levels([price for _, price in local_maxima])
        
        # Get current price for context
        current_price = data['Close'].iloc[-1]
        
        # Find closest support and resistance
        support_below = [level for level in support_levels if level < current_price]
        resistance_above = [level for level in resistance_levels if level > current_price]
        
        return {
            'support': max(support_below) if support_below else min(support_levels) if support_levels else None,
            'resistance': min(resistance_above) if resistance_above else max(resistance_levels) if resistance_levels else None,
            'strong_support': min(support_levels) if support_levels else None,
            'strong_resistance': max(resistance_levels) if resistance_levels else None,
            'all_support_levels': support_levels,
            'all_resistance_levels': resistance_levels
        }
    
    def _group_levels(self, levels, tolerance=0.02):
        """
        Group similar price levels together
        
        Args:
            levels (list): List of price levels
            tolerance (float): Tolerance for grouping (as percentage)
            
        Returns:
            list: Grouped levels
        """
        if not levels:
            return []
        
        levels = sorted(levels)
        grouped = []
        current_group = [levels[0]]
        
        for level in levels[1:]:
            if abs(level - current_group[-1]) / current_group[-1] <= tolerance:
                current_group.append(level)
            else:
                grouped.append(np.mean(current_group))
                current_group = [level]
        
        grouped.append(np.mean(current_group))
        
        return grouped
    
    def calculate_all_indicators(self, data, sma_period=20, ema_period=20, rsi_period=14,
                                bb_period=20, bb_std=2, atr_period=14):
        """
        Calculate all technical indicators for the given data
        
        Args:
            data (pd.DataFrame): OHLC stock data
            sma_period (int): SMA period
            ema_period (int): EMA period
            rsi_period (int): RSI period
            bb_period (int): Bollinger Bands period
            bb_std (float): Bollinger Bands standard deviation
            atr_period (int): ATR period
            
        Returns:
            pd.DataFrame: DataFrame with all indicators
        """
        try:
            result = data.copy()
            
            # Moving Averages with period-specific names
            result['SMA'] = self.calculate_sma(data['Close'], sma_period)
            result[f'SMA_{sma_period}'] = self.calculate_sma(data['Close'], sma_period)
            result['SMA_50'] = self.calculate_sma(data['Close'], 50)
            result['EMA'] = self.calculate_ema(data['Close'], ema_period)
            result[f'EMA_{ema_period}'] = self.calculate_ema(data['Close'], ema_period)
            
            # RSI
            result['RSI'] = self.calculate_rsi(data['Close'], rsi_period)
            
            # MACD
            macd, signal, histogram = self.calculate_macd(data['Close'])
            result['MACD'] = macd
            result['MACD_Signal'] = signal
            result['MACD_Histogram'] = histogram
            
            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(
                data['Close'], bb_period, bb_std
            )
            result['BB_Upper'] = bb_upper
            result['BB_Middle'] = bb_middle
            result['BB_Lower'] = bb_lower
            
            # ATR
            result['ATR'] = self.calculate_atr(data['High'], data['Low'], data['Close'], atr_period)
            
            # Support and Resistance
            support_resistance = self.identify_support_resistance(data)
            
            # Fibonacci Retracement (using recent high/low)
            recent_data = data.tail(100)  # Last 100 days
            high_price = recent_data['High'].max()
            low_price = recent_data['Low'].min()
            fibonacci_levels = self.calculate_fibonacci_retracement(high_price, low_price)
            
            # Add additional computed fields
            result['support_resistance'] = pd.Series([support_resistance] * len(result), index=result.index)
            result['fibonacci_levels'] = pd.Series([fibonacci_levels] * len(result), index=result.index)
            
            # Calculate trend direction
            result['Trend'] = self._calculate_trend(result)
            
            # Calculate volatility
            result['Volatility'] = self._calculate_volatility(data['Close'])
            
            # Calculate trading levels based on technical indicators
            result['Support_Level'] = self._calculate_support_level(data)
            result['Resistance_Level'] = self._calculate_resistance_level(data)
            result['Stop_Loss'] = self._calculate_stop_loss(data, result)
            result['Short_Term_Target'] = self._calculate_short_term_target(data, result)
            result['Long_Term_Target'] = self._calculate_long_term_target(data, result)
            
            self.logger.info("Successfully calculated all technical indicators")
            return result
            
        except Exception as e:
            self.logger.error(f"Error calculating technical indicators: {str(e)}")
            return None
    
    def _calculate_support_level(self, data, lookback=20):
        """Calculate dynamic support level based on recent lows and moving averages"""
        try:
            # Use rolling minimum of lows over lookback period
            support_from_lows = data['Low'].rolling(window=lookback).min()
            
            # Use lower Bollinger Band as additional support reference
            sma_20 = data['Close'].rolling(window=20).mean()
            std_20 = data['Close'].rolling(window=20).std()
            bb_lower = sma_20 - (2 * std_20)
            
            # Take the higher of the two for conservative support
            support_level = np.maximum(support_from_lows, bb_lower * 0.98)
            
            return support_level
        except:
            return data['Close'] * 0.95
    
    def _calculate_resistance_level(self, data, lookback=20):
        """Calculate dynamic resistance level based on recent highs and moving averages"""
        try:
            # Use rolling maximum of highs over lookback period
            resistance_from_highs = data['High'].rolling(window=lookback).max()
            
            # Use upper Bollinger Band as additional resistance reference
            sma_20 = data['Close'].rolling(window=20).mean()
            std_20 = data['Close'].rolling(window=20).std()
            bb_upper = sma_20 + (2 * std_20)
            
            # Take the lower of the two for conservative resistance
            resistance_level = np.minimum(resistance_from_highs, bb_upper * 1.02)
            
            return resistance_level
        except:
            return data['Close'] * 1.05
    
    def _calculate_stop_loss(self, data, indicators):
        """Calculate stop loss based on ATR and support levels"""
        try:
            current_price = data['Close']
            atr = indicators.get('ATR', current_price * 0.02)
            support = indicators.get('Support_Level', current_price * 0.95)
            
            # Stop loss = lower of (support level or current price - 2*ATR)
            atr_stop = current_price - (2 * atr)
            stop_loss = np.minimum(support * 0.98, atr_stop)
            
            return stop_loss
        except:
            return data['Close'] * 0.92
    
    def _calculate_short_term_target(self, data, indicators):
        """Calculate short-term target based on resistance and ATR"""
        try:
            current_price = data['Close']
            atr = indicators.get('ATR', current_price * 0.02)
            resistance = indicators.get('Resistance_Level', current_price * 1.05)
            
            # Short-term target = lower of (resistance level or current price + 1.5*ATR)
            atr_target = current_price + (1.5 * atr)
            short_target = np.minimum(resistance * 0.98, atr_target)
            
            return short_target
        except:
            return data['Close'] * 1.03
    
    def _calculate_long_term_target(self, data, indicators):
        """Calculate long-term target based on trend and Fibonacci levels"""
        try:
            current_price = data['Close']
            
            # Use 50-day high-low range for long-term projection
            period_high = data['High'].rolling(window=50).max()
            period_low = data['Low'].rolling(window=50).min()
            price_range = period_high - period_low
            
            # Long-term target based on Fibonacci extension (1.618 level)
            long_target = current_price + (price_range * 0.618)
            
            # Cap at reasonable level (20% above current price)
            max_target = current_price * 1.20
            long_target = np.minimum(long_target, max_target)
            
            return long_target
        except:
            return data['Close'] * 1.08
    
    def _calculate_trend(self, data, period=20):
        """
        Calculate trend direction using linear regression
        
        Args:
            data (pd.DataFrame): Data with technical indicators
            period (int): Period for trend calculation
            
        Returns:
            pd.Series: Trend direction (1 for uptrend, -1 for downtrend, 0 for sideways)
        """
        def trend_direction(prices):
            if len(prices) < period:
                return 0
            
            x = np.arange(len(prices))
            slope, _, r_value, _, _ = stats.linregress(x, prices)
            
            # Consider trend strength (R-squared)
            if r_value ** 2 > 0.5:  # Strong correlation
                return 1 if slope > 0 else -1
            else:
                return 0  # Sideways trend
        
        trend = data['Close'].rolling(window=period).apply(trend_direction, raw=False)
        return trend
    
    def _calculate_volatility(self, prices, period=20):
        """
        Calculate rolling volatility
        
        Args:
            prices (pd.Series): Price data
            period (int): Period for volatility calculation
            
        Returns:
            pd.Series: Volatility values
        """
        returns = prices.pct_change()
        volatility = returns.rolling(window=period).std() * np.sqrt(252)  # Annualized
        return volatility
