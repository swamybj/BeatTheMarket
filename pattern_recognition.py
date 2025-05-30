import pandas as pd
import numpy as np
import logging
from scipy.signal import find_peaks
from scipy import stats

class PatternRecognition:
    """
    Class to identify chart patterns like channels, double tops/bottoms, head & shoulders
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def identify_channels(self, data, window=20, min_touches=3):
        """
        Identify upward and downward channels
        
        Args:
            data (pd.DataFrame): OHLC data
            window (int): Window for pattern detection
            min_touches (int): Minimum touches for valid channel
            
        Returns:
            dict: Channel information
        """
        try:
            highs = data['High'].values
            lows = data['Low'].values
            dates = data.index
            
            # Find peaks and valleys
            high_peaks, _ = find_peaks(highs, distance=window//2)
            low_valleys, _ = find_peaks(-lows, distance=window//2)
            
            channels = []
            
            # Check for upward channel
            if len(high_peaks) >= 2 and len(low_valleys) >= 2:
                # Get recent peaks and valleys
                recent_high_peaks = high_peaks[-min(4, len(high_peaks)):]
                recent_low_valleys = low_valleys[-min(4, len(low_valleys)):]
                
                # Fit trend lines
                if len(recent_high_peaks) >= 2:
                    high_slope, high_intercept, high_r, _, _ = stats.linregress(
                        recent_high_peaks, highs[recent_high_peaks]
                    )
                    
                if len(recent_low_valleys) >= 2:
                    low_slope, low_intercept, low_r, _, _ = stats.linregress(
                        recent_low_valleys, lows[recent_low_valleys]
                    )
                    
                    # Check if slopes are similar (parallel lines) and both positive (upward channel)
                    if (len(recent_high_peaks) >= 2 and 
                        abs(high_slope - low_slope) < 0.1 and 
                        high_slope > 0 and low_slope > 0 and
                        high_r > 0.7 and low_r > 0.7):
                        
                        channels.append({
                            'type': 'upward_channel',
                            'upper_slope': high_slope,
                            'lower_slope': low_slope,
                            'upper_intercept': high_intercept,
                            'lower_intercept': low_intercept,
                            'strength': min(abs(high_r), abs(low_r)),
                            'current_position': self._get_channel_position(data.iloc[-1], high_slope, high_intercept, low_slope, low_intercept, len(data)-1)
                        })
                    
                    # Check for downward channel
                    elif (abs(high_slope - low_slope) < 0.1 and 
                          high_slope < 0 and low_slope < 0 and
                          high_r > 0.7 and low_r > 0.7):
                        
                        channels.append({
                            'type': 'downward_channel',
                            'upper_slope': high_slope,
                            'lower_slope': low_slope,
                            'upper_intercept': high_intercept,
                            'lower_intercept': low_intercept,
                            'strength': min(abs(high_r), abs(low_r)),
                            'current_position': self._get_channel_position(data.iloc[-1], high_slope, high_intercept, low_slope, low_intercept, len(data)-1)
                        })
            
            return {
                'channels': channels,
                'high_peaks': high_peaks,
                'low_valleys': low_valleys
            }
            
        except Exception as e:
            self.logger.error(f"Error identifying channels: {str(e)}")
            return {'channels': [], 'high_peaks': [], 'low_valleys': []}
    
    def _get_channel_position(self, current_data, upper_slope, upper_intercept, lower_slope, lower_intercept, current_index):
        """Calculate current position within channel"""
        current_price = current_data['Close']
        upper_line = upper_slope * current_index + upper_intercept
        lower_line = lower_slope * current_index + lower_intercept
        
        channel_width = upper_line - lower_line
        position_in_channel = (current_price - lower_line) / channel_width
        
        return {
            'position_percent': position_in_channel * 100,
            'upper_line': upper_line,
            'lower_line': lower_line
        }
    
    def identify_double_tops_bottoms(self, data, window=20, tolerance=0.02):
        """
        Identify double top and double bottom patterns
        
        Args:
            data (pd.DataFrame): OHLC data
            window (int): Window for peak detection
            tolerance (float): Price tolerance for "double" peaks
            
        Returns:
            dict: Double top/bottom patterns
        """
        try:
            highs = data['High'].values
            lows = data['Low'].values
            
            # Find peaks and valleys
            high_peaks, peak_properties = find_peaks(highs, distance=window, prominence=highs.std())
            low_valleys, valley_properties = find_peaks(-lows, distance=window, prominence=lows.std())
            
            patterns = []
            
            # Check for double tops
            if len(high_peaks) >= 2:
                for i in range(len(high_peaks)-1):
                    peak1_idx = high_peaks[i]
                    peak1_price = highs[peak1_idx]
                    
                    for j in range(i+1, len(high_peaks)):
                        peak2_idx = high_peaks[j]
                        peak2_price = highs[peak2_idx]
                        
                        # Check if peaks are similar in height
                        if abs(peak1_price - peak2_price) / peak1_price <= tolerance:
                            # Find valley between peaks
                            valleys_between = [v for v in low_valleys if peak1_idx < v < peak2_idx]
                            if valleys_between:
                                valley_idx = valleys_between[0]
                                valley_price = lows[valley_idx]
                                
                                # Ensure valley is significantly lower
                                if (peak1_price - valley_price) / peak1_price > 0.05:
                                    patterns.append({
                                        'type': 'double_top',
                                        'peak1_idx': peak1_idx,
                                        'peak2_idx': peak2_idx,
                                        'valley_idx': valley_idx,
                                        'peak_price': (peak1_price + peak2_price) / 2,
                                        'valley_price': valley_price,
                                        'strength': 1 - abs(peak1_price - peak2_price) / peak1_price,
                                        'target_price': valley_price - (peak1_price - valley_price)
                                    })
            
            # Check for double bottoms
            if len(low_valleys) >= 2:
                for i in range(len(low_valleys)-1):
                    valley1_idx = low_valleys[i]
                    valley1_price = lows[valley1_idx]
                    
                    for j in range(i+1, len(low_valleys)):
                        valley2_idx = low_valleys[j]
                        valley2_price = lows[valley2_idx]
                        
                        # Check if valleys are similar in depth
                        if abs(valley1_price - valley2_price) / valley1_price <= tolerance:
                            # Find peak between valleys
                            peaks_between = [p for p in high_peaks if valley1_idx < p < valley2_idx]
                            if peaks_between:
                                peak_idx = peaks_between[0]
                                peak_price = highs[peak_idx]
                                
                                # Ensure peak is significantly higher
                                if (peak_price - valley1_price) / valley1_price > 0.05:
                                    patterns.append({
                                        'type': 'double_bottom',
                                        'valley1_idx': valley1_idx,
                                        'valley2_idx': valley2_idx,
                                        'peak_idx': peak_idx,
                                        'valley_price': (valley1_price + valley2_price) / 2,
                                        'peak_price': peak_price,
                                        'strength': 1 - abs(valley1_price - valley2_price) / valley1_price,
                                        'target_price': peak_price + (peak_price - valley1_price)
                                    })
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error identifying double tops/bottoms: {str(e)}")
            return []
    
    def identify_head_and_shoulders(self, data, window=15):
        """
        Identify head and shoulders patterns
        
        Args:
            data (pd.DataFrame): OHLC data
            window (int): Window for peak detection
            
        Returns:
            list: Head and shoulders patterns
        """
        try:
            highs = data['High'].values
            lows = data['Low'].values
            
            # Find peaks
            peaks, _ = find_peaks(highs, distance=window, prominence=highs.std())
            
            patterns = []
            
            # Need at least 3 peaks for head and shoulders
            if len(peaks) >= 3:
                for i in range(len(peaks)-2):
                    left_shoulder_idx = peaks[i]
                    head_idx = peaks[i+1]
                    right_shoulder_idx = peaks[i+2]
                    
                    left_shoulder_price = highs[left_shoulder_idx]
                    head_price = highs[head_idx]
                    right_shoulder_price = highs[right_shoulder_idx]
                    
                    # Check head and shoulders criteria
                    # Head should be higher than both shoulders
                    # Shoulders should be roughly equal
                    if (head_price > left_shoulder_price and 
                        head_price > right_shoulder_price and
                        abs(left_shoulder_price - right_shoulder_price) / left_shoulder_price < 0.05):
                        
                        # Find valleys between peaks for neckline
                        valley1_candidates = [v for v in range(left_shoulder_idx+1, head_idx) 
                                            if lows[v] == min(lows[left_shoulder_idx+1:head_idx])]
                        valley2_candidates = [v for v in range(head_idx+1, right_shoulder_idx) 
                                            if lows[v] == min(lows[head_idx+1:right_shoulder_idx])]
                        
                        if valley1_candidates and valley2_candidates:
                            valley1_idx = valley1_candidates[0]
                            valley2_idx = valley2_candidates[0]
                            valley1_price = lows[valley1_idx]
                            valley2_price = lows[valley2_idx]
                            
                            neckline_price = (valley1_price + valley2_price) / 2
                            target_price = neckline_price - (head_price - neckline_price)
                            
                            patterns.append({
                                'type': 'head_and_shoulders',
                                'left_shoulder_idx': left_shoulder_idx,
                                'head_idx': head_idx,
                                'right_shoulder_idx': right_shoulder_idx,
                                'valley1_idx': valley1_idx,
                                'valley2_idx': valley2_idx,
                                'left_shoulder_price': left_shoulder_price,
                                'head_price': head_price,
                                'right_shoulder_price': right_shoulder_price,
                                'neckline_price': neckline_price,
                                'target_price': target_price,
                                'strength': (head_price - neckline_price) / head_price
                            })
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error identifying head and shoulders: {str(e)}")
            return []
    
    def identify_multiple_tops_bottoms(self, data, window=20, min_peaks=3):
        """
        Identify multiple top and bottom patterns
        
        Args:
            data (pd.DataFrame): OHLC data
            window (int): Window for peak detection
            min_peaks (int): Minimum number of peaks/valleys
            
        Returns:
            dict: Multiple top/bottom patterns
        """
        try:
            highs = data['High'].values
            lows = data['Low'].values
            
            # Find peaks and valleys
            high_peaks, _ = find_peaks(highs, distance=window//2, prominence=highs.std()*0.5)
            low_valleys, _ = find_peaks(-lows, distance=window//2, prominence=lows.std()*0.5)
            
            patterns = []
            
            # Multiple tops
            if len(high_peaks) >= min_peaks:
                recent_peaks = high_peaks[-min_peaks:]
                peak_prices = highs[recent_peaks]
                
                # Check if peaks are at similar levels
                if (max(peak_prices) - min(peak_prices)) / np.mean(peak_prices) < 0.03:
                    resistance_level = np.mean(peak_prices)
                    patterns.append({
                        'type': 'multiple_tops',
                        'level': resistance_level,
                        'peak_indices': recent_peaks.tolist(),
                        'strength': len(recent_peaks) / min_peaks,
                        'touches': len(recent_peaks)
                    })
            
            # Multiple bottoms
            if len(low_valleys) >= min_peaks:
                recent_valleys = low_valleys[-min_peaks:]
                valley_prices = lows[recent_valleys]
                
                # Check if valleys are at similar levels
                if (max(valley_prices) - min(valley_prices)) / np.mean(valley_prices) < 0.03:
                    support_level = np.mean(valley_prices)
                    patterns.append({
                        'type': 'multiple_bottoms',
                        'level': support_level,
                        'valley_indices': recent_valleys.tolist(),
                        'strength': len(recent_valleys) / min_peaks,
                        'touches': len(recent_valleys)
                    })
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error identifying multiple tops/bottoms: {str(e)}")
            return []
    
    def analyze_all_patterns(self, data):
        """
        Analyze all chart patterns
        
        Args:
            data (pd.DataFrame): OHLC data
            
        Returns:
            dict: All identified patterns
        """
        try:
            patterns = {
                'channels': self.identify_channels(data),
                'double_patterns': self.identify_double_tops_bottoms(data),
                'head_shoulders': self.identify_head_and_shoulders(data),
                'multiple_patterns': self.identify_multiple_tops_bottoms(data)
            }
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error analyzing patterns: {str(e)}")
            return {
                'channels': {'channels': [], 'high_peaks': [], 'low_valleys': []},
                'double_patterns': [],
                'head_shoulders': [],
                'multiple_patterns': []
            }