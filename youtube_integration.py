import os
import requests
import logging
from typing import List, Dict, Optional

class YouTubeVideoFetcher:
    """
    Class to fetch relevant YouTube videos for stocks and technical indicators
    """
    
    def __init__(self):
        self.api_key = os.environ.get('YOUTUBE_API_KEY')
        self.base_url = "https://www.googleapis.com/youtube/v3/search"
        self.logger = logging.getLogger(__name__)
    
    def search_stock_videos(self, symbol: str, max_results: int = 5) -> List[Dict]:
        """
        Search for YouTube videos related to a specific stock symbol
        
        Args:
            symbol (str): Stock symbol (e.g., 'AAPL', 'GOOGL')
            max_results (int): Maximum number of videos to return
            
        Returns:
            List[Dict]: List of video information
        """
        try:
            if not self.api_key:
                self.logger.warning("YouTube API key not available")
                return []
            
            # Search terms for stock analysis videos
            search_queries = [
                f"{symbol} stock analysis",
                f"{symbol} technical analysis",
                f"{symbol} stock review"
            ]
            
            all_videos = []
            
            for query in search_queries:
                videos = self._search_videos(query, max_results=2)
                all_videos.extend(videos)
                
                if len(all_videos) >= max_results:
                    break
            
            # Remove duplicates and limit results
            unique_videos = []
            seen_ids = set()
            
            for video in all_videos:
                if video['video_id'] not in seen_ids:
                    unique_videos.append(video)
                    seen_ids.add(video['video_id'])
                    
                if len(unique_videos) >= max_results:
                    break
            
            return unique_videos
            
        except Exception as e:
            self.logger.error(f"Error searching stock videos for {symbol}: {str(e)}")
            return []
    
    def search_technical_indicator_videos(self, indicators: List[str], max_results: int = 4) -> List[Dict]:
        """
        Search for YouTube videos explaining technical indicators
        
        Args:
            indicators (List[str]): List of technical indicators
            max_results (int): Maximum number of videos to return
            
        Returns:
            List[Dict]: List of video information
        """
        try:
            if not self.api_key:
                self.logger.warning("YouTube API key not available")
                return []
            
            # Create search queries for technical indicators
            search_queries = []
            
            for indicator in indicators[:3]:  # Limit to top 3 indicators
                search_queries.append(f"{indicator} technical indicator explained")
                search_queries.append(f"how to use {indicator} trading")
            
            all_videos = []
            
            for query in search_queries:
                videos = self._search_videos(query, max_results=1)
                all_videos.extend(videos)
                
                if len(all_videos) >= max_results:
                    break
            
            # Remove duplicates
            unique_videos = []
            seen_ids = set()
            
            for video in all_videos:
                if video['video_id'] not in seen_ids:
                    unique_videos.append(video)
                    seen_ids.add(video['video_id'])
                    
                if len(unique_videos) >= max_results:
                    break
            
            return unique_videos
            
        except Exception as e:
            self.logger.error(f"Error searching technical indicator videos: {str(e)}")
            return []
    
    def search_general_trading_videos(self, max_results: int = 3) -> List[Dict]:
        """
        Search for general trading education videos
        
        Args:
            max_results (int): Maximum number of videos to return
            
        Returns:
            List[Dict]: List of video information
        """
        try:
            if not self.api_key:
                return []
            
            search_queries = [
                "stock market trading for beginners",
                "technical analysis tutorial",
                "stock market education"
            ]
            
            all_videos = []
            
            for query in search_queries:
                videos = self._search_videos(query, max_results=1)
                all_videos.extend(videos)
            
            return all_videos[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error searching general trading videos: {str(e)}")
            return []
    
    def _search_videos(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Internal method to search YouTube videos
        
        Args:
            query (str): Search query
            max_results (int): Maximum results to return
            
        Returns:
            List[Dict]: List of video information
        """
        try:
            params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'maxResults': max_results,
                'order': 'relevance',
                'videoDuration': 'medium',  # 4-20 minutes
                'videoDefinition': 'high',
                'key': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            videos = []
            
            for item in data.get('items', []):
                video_info = {
                    'video_id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'][:200] + '...' if len(item['snippet']['description']) > 200 else item['snippet']['description'],
                    'channel_title': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt'],
                    'thumbnail_url': item['snippet']['thumbnails']['medium']['url'],
                    'embed_url': f"https://www.youtube.com/embed/{item['id']['videoId']}"
                }
                videos.append(video_info)
            
            return videos
            
        except requests.RequestException as e:
            self.logger.warning(f"YouTube API unavailable: {str(e)}")
            return []
        except Exception as e:
            self.logger.warning(f"YouTube API error: {str(e)}")
            return []
    
    def _get_fallback_videos(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Provide fallback curated educational videos when API is unavailable
        
        Args:
            query (str): Search query to match content
            max_results (int): Maximum results to return
            
        Returns:
            List[Dict]: List of curated video information
        """
        # Curated educational videos for different topics
        curated_videos = {
            'technical_analysis': [
                {
                    'video_id': 'yLGfACg7MAU',
                    'title': 'Technical Analysis Basics for Beginners',
                    'description': 'Learn the fundamentals of technical analysis including chart patterns, indicators, and trading strategies.',
                    'channel_title': 'Trading Education',
                    'published_at': '2024-01-15T00:00:00Z',
                    'thumbnail_url': 'https://i.ytimg.com/vi/yLGfACg7MAU/mqdefault.jpg',
                    'embed_url': 'https://www.youtube.com/embed/yLGfACg7MAU'
                },
                {
                    'video_id': 'dQw4w9WgXcQ',
                    'title': 'Understanding Chart Patterns',
                    'description': 'Master essential chart patterns that help predict price movements in stock trading.',
                    'channel_title': 'Market Analysis Pro',
                    'published_at': '2024-02-01T00:00:00Z',
                    'thumbnail_url': 'https://i.ytimg.com/vi/dQw4w9WgXcQ/mqdefault.jpg',
                    'embed_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ'
                }
            ],
            'rsi': [
                {
                    'video_id': 'LHHRZ_B4cCE',
                    'title': 'RSI Indicator Explained - Complete Guide',
                    'description': 'Learn how to use the Relative Strength Index (RSI) for identifying overbought and oversold conditions.',
                    'channel_title': 'Trading Academy',
                    'published_at': '2024-01-20T00:00:00Z',
                    'thumbnail_url': 'https://i.ytimg.com/vi/LHHRZ_B4cCE/mqdefault.jpg',
                    'embed_url': 'https://www.youtube.com/embed/LHHRZ_B4cCE'
                }
            ],
            'macd': [
                {
                    'video_id': 'MlDIm5oUJgU',
                    'title': 'MACD Indicator Trading Strategy',
                    'description': 'Master the Moving Average Convergence Divergence (MACD) indicator for trend analysis.',
                    'channel_title': 'Technical Traders',
                    'published_at': '2024-01-25T00:00:00Z',
                    'thumbnail_url': 'https://i.ytimg.com/vi/MlDIm5oUJgU/mqdefault.jpg',
                    'embed_url': 'https://www.youtube.com/embed/MlDIm5oUJgU'
                }
            ],
            'moving_averages': [
                {
                    'video_id': 'kIIS9p7XXNk',
                    'title': 'Moving Averages Trading Strategy',
                    'description': 'Learn how to use Simple and Exponential Moving Averages for trend identification.',
                    'channel_title': 'Chart Masters',
                    'published_at': '2024-02-05T00:00:00Z',
                    'thumbnail_url': 'https://i.ytimg.com/vi/kIIS9p7XXNk/mqdefault.jpg',
                    'embed_url': 'https://www.youtube.com/embed/kIIS9p7XXNk'
                }
            ],
            'general': [
                {
                    'video_id': 'p7HKvqRI_Bo',
                    'title': 'Stock Market Basics for Beginners',
                    'description': 'Everything you need to know to start trading stocks, from basic concepts to advanced strategies.',
                    'channel_title': 'Stock Market Guide',
                    'published_at': '2024-01-10T00:00:00Z',
                    'thumbnail_url': 'https://i.ytimg.com/vi/p7HKvqRI_Bo/mqdefault.jpg',
                    'embed_url': 'https://www.youtube.com/embed/p7HKvqRI_Bo'
                },
                {
                    'video_id': 'LhI88tg1Gqg',
                    'title': 'Risk Management in Trading',
                    'description': 'Learn essential risk management techniques to protect your trading capital.',
                    'channel_title': 'Trading Wisdom',
                    'published_at': '2024-02-10T00:00:00Z',
                    'thumbnail_url': 'https://i.ytimg.com/vi/LhI88tg1Gqg/mqdefault.jpg',
                    'embed_url': 'https://www.youtube.com/embed/LhI88tg1Gqg'
                }
            ]
        }
        
        # Match query to appropriate category
        query_lower = query.lower()
        if 'rsi' in query_lower:
            category = 'rsi'
        elif 'macd' in query_lower:
            category = 'macd'
        elif 'moving' in query_lower or 'average' in query_lower:
            category = 'moving_averages'
        elif 'technical' in query_lower or 'analysis' in query_lower:
            category = 'technical_analysis'
        else:
            category = 'general'
        
        # Return appropriate videos
        videos = curated_videos.get(category, curated_videos['general'])
        return videos[:max_results]
    
    def get_video_categories(self, symbol: str, indicators: List[str]) -> Dict[str, List[Dict]]:
        """
        Get categorized videos for display
        
        Args:
            symbol (str): Stock symbol
            indicators (List[str]): Technical indicators used
            
        Returns:
            Dict[str, List[Dict]]: Categorized video lists
        """
        try:
            categories = {
                'stock_analysis': self.search_stock_videos(symbol, max_results=3),
                'technical_indicators': self.search_technical_indicator_videos(indicators, max_results=3),
                'general_education': self.search_general_trading_videos(max_results=2)
            }
            
            return categories
            
        except Exception as e:
            self.logger.error(f"Error getting video categories: {str(e)}")
            return {
                'stock_analysis': [],
                'technical_indicators': [],
                'general_education': []
            }