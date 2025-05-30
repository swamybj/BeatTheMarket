import yfinance as yf
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

class FinancialData:
    """
    Class to fetch financial statements, news, and comprehensive metrics
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_financial_statements(self, symbol):
        """
        Get income statement, balance sheet, and cash flow
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            dict: Financial statements data
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Get financial statements
            income_stmt = ticker.financials
            balance_sheet = ticker.balance_sheet
            cash_flow = ticker.cashflow
            
            # Get quarterly data
            quarterly_income = ticker.quarterly_financials
            quarterly_balance = ticker.quarterly_balancesheet
            quarterly_cashflow = ticker.quarterly_cashflow
            
            return {
                'income_statement': {
                    'annual': income_stmt,
                    'quarterly': quarterly_income
                },
                'balance_sheet': {
                    'annual': balance_sheet,
                    'quarterly': quarterly_balance
                },
                'cash_flow': {
                    'annual': cash_flow,
                    'quarterly': quarterly_cashflow
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching financial statements for {symbol}: {str(e)}")
            return None
    
    def get_comprehensive_metrics(self, symbol):
        """
        Get comprehensive financial metrics table
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            dict: Comprehensive metrics
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1y")
            
            # Get current price
            current_price = hist['Close'].iloc[-1] if not hist.empty else info.get('currentPrice', 0)
            
            # Calculate performance metrics
            perf_data = self._calculate_performance_metrics(hist, current_price)
            
            # Calculate technical indicators
            tech_data = self._calculate_quick_technicals(hist)
            
            # Compile comprehensive metrics
            metrics = {
                # Basic Info
                'symbol': symbol,
                'current_price': current_price,
                'previous_close': info.get('previousClose', current_price),
                'change': current_price - info.get('previousClose', current_price),
                'change_percent': ((current_price / info.get('previousClose', current_price)) - 1) * 100,
                
                # Market Data
                'market_cap': info.get('marketCap', 0),
                'shares_outstanding': info.get('sharesOutstanding', 0),
                'shares_float': info.get('floatShares', 0),
                'avg_volume': info.get('averageVolume', 0),
                'volume': hist['Volume'].iloc[-1] if not hist.empty else 0,
                
                # Valuation Ratios
                'pe_ratio': info.get('trailingPE', 0),
                'forward_pe': info.get('forwardPE', 0),
                'peg_ratio': info.get('pegRatio', 0),
                'price_to_sales': info.get('priceToSalesTrailing12Months', 0),
                'price_to_book': info.get('priceToBook', 0),
                'price_to_cash': info.get('totalCashPerShare', 0),
                'price_to_fcf': info.get('totalCashPerShare', 0),  # Approximation
                
                # Sector/Industry Comparison
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                
                # Per Share Data
                'eps_ttm': info.get('trailingEps', 0),
                'eps_forward': info.get('forwardEps', 0),
                'book_value_per_share': info.get('bookValue', 0),
                'cash_per_share': info.get('totalCashPerShare', 0),
                
                # Growth Rates
                'eps_growth_yoy': info.get('earningsGrowth', 0) * 100 if info.get('earningsGrowth') else 0,
                'revenue_growth_yoy': info.get('revenueGrowth', 0) * 100 if info.get('revenueGrowth') else 0,
                'eps_growth_next_year': 0,  # Would need additional API
                'eps_growth_next_5y': 0,    # Would need additional API
                
                # Profitability
                'gross_margin': info.get('grossMargins', 0) * 100 if info.get('grossMargins') else 0,
                'operating_margin': info.get('operatingMargins', 0) * 100 if info.get('operatingMargins') else 0,
                'profit_margin': info.get('profitMargins', 0) * 100 if info.get('profitMargins') else 0,
                'roa': info.get('returnOnAssets', 0) * 100 if info.get('returnOnAssets') else 0,
                'roe': info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0,
                'roi': 0,  # Would need calculation
                
                # Financial Health
                'current_ratio': info.get('currentRatio', 0),
                'quick_ratio': info.get('quickRatio', 0),
                'debt_to_equity': info.get('debtToEquity', 0),
                'lt_debt_to_equity': 0,  # Would need calculation
                
                # Market Performance
                'beta': info.get('beta', 0),
                'atr_14': tech_data.get('atr', 0),
                'rsi_14': tech_data.get('rsi', 0),
                'volatility_week': 0,  # Would need calculation
                'volatility_month': 0,  # Would need calculation
                
                # Price Levels
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
                'fifty_two_week_high_percent': ((current_price / info.get('fiftyTwoWeekHigh', current_price)) - 1) * 100,
                'fifty_two_week_low_percent': ((current_price / info.get('fiftyTwoWeekLow', current_price)) - 1) * 100,
                
                # Performance
                'perf_week': perf_data.get('week', 0),
                'perf_month': perf_data.get('month', 0),
                'perf_quarter': perf_data.get('quarter', 0),
                'perf_half_year': perf_data.get('half_year', 0),
                'perf_year': perf_data.get('year', 0),
                'perf_ytd': perf_data.get('ytd', 0),
                
                # Moving Averages
                'sma_20': tech_data.get('sma_20_percent', 0),
                'sma_50': tech_data.get('sma_50_percent', 0),
                'sma_200': tech_data.get('sma_200_percent', 0),
                
                # Short Interest
                'short_float': info.get('shortPercentOfFloat', 0) * 100 if info.get('shortPercentOfFloat') else 0,
                'short_ratio': info.get('shortRatio', 0),
                'short_interest': info.get('sharesShort', 0),
                
                # Ownership
                'insider_ownership': info.get('heldPercentInsiders', 0) * 100 if info.get('heldPercentInsiders') else 0,
                'institutional_ownership': info.get('heldPercentInstitutions', 0) * 100 if info.get('heldPercentInstitutions') else 0,
                
                # Analyst Data
                'target_price': info.get('targetMeanPrice', 0),
                'recommendation': info.get('recommendationMean', 0),
                
                # Dividend
                'dividend_rate': info.get('dividendRate', 0),
                'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
                'payout_ratio': info.get('payoutRatio', 0) * 100 if info.get('payoutRatio') else 0,
                
                # Other
                'employees': info.get('fullTimeEmployees', 0),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown')
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error fetching comprehensive metrics for {symbol}: {str(e)}")
            return None
    
    def _calculate_performance_metrics(self, hist, current_price):
        """Calculate performance metrics for different time periods"""
        try:
            if hist.empty:
                return {}
            
            performance = {}
            
            # Get prices for different periods
            if len(hist) >= 5:  # 1 week
                week_ago_price = hist['Close'].iloc[-5]
                performance['week'] = ((current_price / week_ago_price) - 1) * 100
            
            if len(hist) >= 22:  # 1 month
                month_ago_price = hist['Close'].iloc[-22]
                performance['month'] = ((current_price / month_ago_price) - 1) * 100
            
            if len(hist) >= 63:  # 1 quarter
                quarter_ago_price = hist['Close'].iloc[-63]
                performance['quarter'] = ((current_price / quarter_ago_price) - 1) * 100
            
            if len(hist) >= 126:  # 6 months
                half_year_ago_price = hist['Close'].iloc[-126]
                performance['half_year'] = ((current_price / half_year_ago_price) - 1) * 100
            
            if len(hist) >= 252:  # 1 year
                year_ago_price = hist['Close'].iloc[-252]
                performance['year'] = ((current_price / year_ago_price) - 1) * 100
            
            # YTD performance
            current_year = datetime.now().year
            ytd_data = hist[hist.index.year == current_year]
            if not ytd_data.empty:
                ytd_start_price = ytd_data['Close'].iloc[0]
                performance['ytd'] = ((current_price / ytd_start_price) - 1) * 100
            
            return performance
            
        except Exception as e:
            self.logger.error(f"Error calculating performance metrics: {str(e)}")
            return {}
    
    def _calculate_quick_technicals(self, hist):
        """Calculate quick technical indicators"""
        try:
            if hist.empty or len(hist) < 50:
                return {}
            
            current_price = hist['Close'].iloc[-1]
            
            # Simple Moving Averages
            sma_20 = hist['Close'].rolling(20).mean().iloc[-1] if len(hist) >= 20 else current_price
            sma_50 = hist['Close'].rolling(50).mean().iloc[-1] if len(hist) >= 50 else current_price
            sma_200 = hist['Close'].rolling(200).mean().iloc[-1] if len(hist) >= 200 else current_price
            
            # RSI calculation
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1] if not rsi.empty else 50
            
            # ATR calculation
            high_low = hist['High'] - hist['Low']
            high_close = np.abs(hist['High'] - hist['Close'].shift())
            low_close = np.abs(hist['Low'] - hist['Close'].shift())
            true_range = np.maximum(high_low, np.maximum(high_close, low_close))
            atr = true_range.rolling(14).mean().iloc[-1] if len(true_range) >= 14 else 0
            
            return {
                'sma_20_percent': ((current_price / sma_20) - 1) * 100,
                'sma_50_percent': ((current_price / sma_50) - 1) * 100,
                'sma_200_percent': ((current_price / sma_200) - 1) * 100,
                'rsi': current_rsi,
                'atr': atr
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating quick technicals: {str(e)}")
            return {}
    
    def get_latest_news(self, symbol, limit=10):
        """
        Get latest news for the stock using News API
        
        Args:
            symbol (str): Stock symbol
            limit (int): Number of news items to fetch
            
        Returns:
            list: Latest news items
        """
        try:
            import os
            import requests
            
            news_api_key = os.environ.get('NEWS_API_KEY')
            if not news_api_key:
                # Fallback to Yahoo Finance news
                return self._get_yahoo_news(symbol, limit)
            
            # Get company info for better search terms
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                company_name = info.get('longName', symbol)
            except:
                company_name = symbol
            
            # Use News API for better coverage with multiple search approaches
            url = f"https://newsapi.org/v2/everything"
            
            # Try multiple search queries for better coverage
            search_queries = [
                f'{symbol} AND (stock OR shares OR earnings OR financial OR revenue)',
                f'"{company_name}" AND (stock OR earnings OR financial)',
                f'{symbol} stock price',
                f'{company_name} quarterly results'
            ]
            
            all_articles = []
            for query in search_queries:
                params = {
                    'q': query,
                    'sortBy': 'publishedAt',
                    'language': 'en',
                    'pageSize': min(limit, 10),
                    'apiKey': news_api_key,
                    'from': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                }
                
                try:
                    response = requests.get(url, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        articles = data.get('articles', [])
                        all_articles.extend(articles)
                        if len(all_articles) >= limit:
                            break
                except:
                    continue
            
            # Process collected articles
            if all_articles:
                # Remove duplicates and filter relevant articles
                seen_titles = set()
                formatted_news = []
                
                for article in all_articles:
                    title = article.get('title', '')
                    if title and title not in seen_titles:
                        seen_titles.add(title)
                        try:
                            formatted_news.append({
                                'title': article.get('title', 'No title'),
                                'publisher': article.get('source', {}).get('name', 'Unknown'),
                                'link': article.get('url', ''),
                                'published': datetime.fromisoformat(article.get('publishedAt', '').replace('Z', '+00:00')),
                                'summary': article.get('description', 'No summary available'),
                                'content': article.get('content', '')
                            })
                        except:
                            continue
                
                return formatted_news[:limit]
            else:
                # Fallback to Yahoo Finance if News API fails
                return self._get_yahoo_news(symbol, limit)
            
        except Exception as e:
            self.logger.error(f"Error fetching news for {symbol}: {str(e)}")
            # Fallback to Yahoo Finance news
            return self._get_yahoo_news(symbol, limit)
    
    def _get_yahoo_news(self, symbol, limit=10):
        """Fallback method using Yahoo Finance news"""
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            if not news:
                return []
            
            # Format news data
            formatted_news = []
            for item in news[:limit]:
                formatted_news.append({
                    'title': item.get('title', 'No title'),
                    'publisher': item.get('publisher', 'Yahoo Finance'),
                    'link': item.get('link', ''),
                    'published': datetime.fromtimestamp(item.get('providerPublishTime', 0)),
                    'summary': item.get('summary', 'No summary available')
                })
            
            return formatted_news
            
        except Exception as e:
            self.logger.error(f"Error fetching Yahoo news for {symbol}: {str(e)}")
            return []
    
    def analyze_news_sentiment(self, news_items):
        """
        Analyze sentiment of news items
        
        Args:
            news_items (list): List of news items
            
        Returns:
            dict: Sentiment analysis
        """
        try:
            if not news_items:
                return {'sentiment': 'neutral', 'score': 0, 'analysis': 'No news available'}
            
            # Simple keyword-based sentiment analysis
            positive_keywords = ['profit', 'growth', 'increase', 'beat', 'strong', 'positive', 'up', 'gain', 'buy', 'upgrade']
            negative_keywords = ['loss', 'decline', 'decrease', 'miss', 'weak', 'negative', 'down', 'fall', 'sell', 'downgrade']
            
            positive_count = 0
            negative_count = 0
            
            for news in news_items:
                title_lower = news['title'].lower()
                summary_lower = news.get('summary', '').lower()
                text = title_lower + ' ' + summary_lower
                
                for keyword in positive_keywords:
                    positive_count += text.count(keyword)
                
                for keyword in negative_keywords:
                    negative_count += text.count(keyword)
            
            total_keywords = positive_count + negative_count
            if total_keywords == 0:
                sentiment_score = 0
                sentiment = 'neutral'
            else:
                sentiment_score = (positive_count - negative_count) / total_keywords
                if sentiment_score > 0.2:
                    sentiment = 'positive'
                elif sentiment_score < -0.2:
                    sentiment = 'negative'
                else:
                    sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'score': sentiment_score,
                'positive_mentions': positive_count,
                'negative_mentions': negative_count,
                'total_news': len(news_items)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing news sentiment: {str(e)}")
            return {'sentiment': 'neutral', 'score': 0, 'analysis': 'Error analyzing sentiment'}
    
    def get_sector_pe_comparison(self, symbol):
        """Get sector and industry P/E comparison for valuation analysis"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            current_pe = info.get('trailingPE', 0)
            sector = info.get('sector', '')
            industry = info.get('industry', '')
            
            # Average P/E ratios by sector (based on historical market data)
            sector_pe_averages = {
                'Technology': 28.5,
                'Healthcare': 24.3,
                'Financial Services': 12.8,
                'Consumer Cyclical': 18.2,
                'Communication Services': 22.1,
                'Consumer Defensive': 19.7,
                'Industrials': 21.4,
                'Energy': 15.8,
                'Utilities': 17.2,
                'Real Estate': 19.8,
                'Materials': 16.3,
                'Basic Materials': 16.3
            }
            
            # Industry-specific P/E averages (subset of common industries)
            industry_pe_averages = {
                'Software—Application': 32.1,
                'Software—Infrastructure': 29.8,
                'Semiconductors': 25.4,
                'Drug Manufacturers—Major': 22.7,
                'Biotechnology': 28.9,
                'Banks—Regional': 11.2,
                'Banks—Major': 10.8,
                'Auto Manufacturers': 14.6,
                'Retail—Apparel': 19.3,
                'Oil & Gas E&P': 18.2,
                'Electric Utilities': 16.8,
                'REITs—Retail': 22.1,
                'Food Processing': 18.5,
                'Aerospace & Defense': 23.2,
                'Medical Devices': 25.8
            }
            
            sector_pe = sector_pe_averages.get(sector, 20.0)  # Market average fallback
            industry_pe = industry_pe_averages.get(industry, sector_pe)
            
            # Calculate relative valuation
            pe_vs_sector = ((current_pe / sector_pe) - 1) * 100 if sector_pe > 0 else 0
            pe_vs_industry = ((current_pe / industry_pe) - 1) * 100 if industry_pe > 0 else 0
            
            return {
                'current_pe': current_pe,
                'sector': sector,
                'sector_pe': sector_pe,
                'industry': industry,
                'industry_pe': industry_pe,
                'pe_vs_sector_pct': pe_vs_sector,
                'pe_vs_industry_pct': pe_vs_industry,
                'valuation_assessment': self._assess_valuation(pe_vs_sector, pe_vs_industry)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting sector P/E comparison for {symbol}: {str(e)}")
            return None
    
    def _assess_valuation(self, sector_diff, industry_diff):
        """Assess if stock is overvalued or undervalued compared to peers"""
        avg_diff = (sector_diff + industry_diff) / 2
        
        if avg_diff > 30:
            return "Significantly Overvalued"
        elif avg_diff > 15:
            return "Overvalued"
        elif avg_diff > -15:
            return "Fairly Valued"
        elif avg_diff > -30:
            return "Undervalued"
        else:
            return "Significantly Undervalued"