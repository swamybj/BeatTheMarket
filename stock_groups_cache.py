import yfinance as yf
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List
import logging

class StockGroupsCache:
    """
    Cache system for stock groups with 1-day expiration
    Fetches real stock data for each category and caches it
    """
    
    def __init__(self, cache_file="stock_groups_cache.json"):
        self.cache_file = cache_file
        self.logger = logging.getLogger(__name__)
        
        # Define stock groups with real tickers
        self.stock_groups = {
            "FAANG": ["META", "AAPL", "AMZN", "NFLX", "GOOGL"],
            "Tech Giants": ["MSFT", "NVDA", "ORCL", "CRM", "ADBE"],
            "Finance": ["JPM", "BAC", "GS", "MS", "WFC"],
            "Healthcare": ["JNJ", "UNH", "PFE", "ABT", "MRK"],
            "Semiconductors": ["NVDA", "AMD", "INTC", "TSM", "QCOM"],
            "REITs": ["AMT", "PLD", "CCI", "EQIX", "SPG"],
            "Consumer Discretionary": ["AMZN", "TSLA", "HD", "MCD", "NKE"],
            "Consumer Staples": ["PG", "KO", "PEP", "WMT", "COST"],
            "Top 5 Large Cap": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"],
            "Top 5 Mid Cap": ["CRWD", "SNOW", "ZM", "DDOG", "NET"],
            "Top 5 Small Cap": ["SMCI", "IONQ", "MARA", "RIOT", "COIN"]
        }
    
    def _is_cache_valid(self) -> bool:
        """Check if cache exists and is less than 1 day old"""
        if not os.path.exists(self.cache_file):
            return False
        
        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
            
            cache_time = datetime.fromisoformat(cache_data.get('timestamp', ''))
            return datetime.now() - cache_time < timedelta(days=1)
        except (json.JSONDecodeError, ValueError, KeyError):
            return False
    
    def _fetch_stock_data(self, symbols: List[str]) -> Dict:
        """Fetch current stock data for given symbols"""
        stock_data = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="5d")
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                    change_pct = ((current_price - prev_price) / prev_price) * 100
                    
                    stock_data[symbol] = {
                        'name': info.get('longName', symbol),
                        'sector': info.get('sector', 'Unknown'),
                        'industry': info.get('industry', 'Unknown'),
                        'market_cap': info.get('marketCap', 0),
                        'current_price': float(current_price),
                        'change_percent': float(change_pct),
                        'volume': int(hist['Volume'].iloc[-1]) if 'Volume' in hist else 0,
                        'pe_ratio': info.get('forwardPE', info.get('trailingPE', 0))
                    }
                else:
                    # Fallback for symbols without historical data
                    stock_data[symbol] = {
                        'name': symbol,
                        'sector': 'Unknown',
                        'industry': 'Unknown', 
                        'market_cap': 0,
                        'current_price': 0,
                        'change_percent': 0,
                        'volume': 0,
                        'pe_ratio': 0
                    }
                    
            except Exception as e:
                self.logger.warning(f"Failed to fetch data for {symbol}: {str(e)}")
                # Add minimal data for failed symbols
                stock_data[symbol] = {
                    'name': symbol,
                    'sector': 'Unknown',
                    'industry': 'Unknown',
                    'market_cap': 0,
                    'current_price': 0,
                    'change_percent': 0,
                    'volume': 0,
                    'pe_ratio': 0
                }
        
        return stock_data
    
    def _save_cache(self, data: Dict):
        """Save data to cache file with timestamp"""
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save cache: {str(e)}")
    
    def _load_cache(self) -> Dict:
        """Load data from cache file"""
        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
            return cache_data.get('data', {})
        except Exception as e:
            self.logger.error(f"Failed to load cache: {str(e)}")
            return {}
    
    def get_stock_groups_data(self) -> Dict:
        """Get stock groups data from cache or fetch if expired"""
        if self._is_cache_valid():
            self.logger.info("Loading stock groups from cache")
            return self._load_cache()
        
        self.logger.info("Cache expired or missing, fetching fresh stock data")
        
        # Fetch fresh data for all groups
        all_data = {}
        for group_name, symbols in self.stock_groups.items():
            self.logger.info(f"Fetching data for {group_name}")
            group_data = self._fetch_stock_data(symbols)
            all_data[group_name] = group_data
        
        # Save to cache
        self._save_cache(all_data)
        
        return all_data
    
    def get_group_symbols(self, group_name: str) -> List[str]:
        """Get symbol list for a specific group"""
        return self.stock_groups.get(group_name, [])
    
    def get_group_data(self, group_name: str) -> Dict:
        """Get cached data for a specific group"""
        all_data = self.get_stock_groups_data()
        return all_data.get(group_name, {})
    
    def refresh_cache(self):
        """Force refresh the cache"""
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        self.get_stock_groups_data()
    
    def get_cache_info(self) -> Dict:
        """Get cache information"""
        if not os.path.exists(self.cache_file):
            return {'exists': False}
        
        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
            
            timestamp = datetime.fromisoformat(cache_data.get('timestamp', ''))
            age = datetime.now() - timestamp
            
            return {
                'exists': True,
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'age_hours': round(age.total_seconds() / 3600, 1),
                'valid': age < timedelta(days=1),
                'groups_count': len(cache_data.get('data', {}))
            }
        except Exception as e:
            return {'exists': True, 'error': str(e)}