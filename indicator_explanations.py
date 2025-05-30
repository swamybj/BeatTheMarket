"""
Technical Indicator Explanations for Stock Analysis Platform
"""

INDICATOR_EXPLANATIONS = {
    "RSI": {
        "name": "Relative Strength Index (RSI)",
        "description": "Measures momentum to identify overbought and oversold conditions",
        "signals": {
            "bullish": "RSI below 30 (oversold) suggests potential buying opportunity",
            "bearish": "RSI above 70 (overbought) suggests potential selling pressure",
            "neutral": "RSI between 30-70 indicates balanced momentum"
        },
        "interpretation": "RSI oscillates between 0-100. Values below 30 indicate oversold conditions where price might bounce up. Values above 70 indicate overbought conditions where price might pull back.",
        "trading_tips": "Look for RSI divergences - when price makes new highs but RSI doesn't, it can signal weakness."
    },
    
    "MACD": {
        "name": "Moving Average Convergence Divergence",
        "description": "Shows relationship between two moving averages to identify trend changes",
        "signals": {
            "bullish": "MACD line crosses above signal line (bullish crossover)",
            "bearish": "MACD line crosses below signal line (bearish crossover)",
            "neutral": "MACD and signal lines moving sideways"
        },
        "interpretation": "MACD histogram shows momentum strength. Positive histogram indicates upward momentum, negative shows downward momentum.",
        "trading_tips": "Best used in trending markets. Look for crossovers above/below zero line for stronger signals."
    },
    
    "Bollinger Bands": {
        "name": "Bollinger Bands",
        "description": "Shows volatility and potential support/resistance levels",
        "signals": {
            "bullish": "Price touching lower band may indicate oversold condition",
            "bearish": "Price touching upper band may indicate overbought condition",
            "neutral": "Price trading within the bands shows normal volatility"
        },
        "interpretation": "Bands expand during high volatility and contract during low volatility. Price tends to bounce between the bands.",
        "trading_tips": "Use with other indicators. Band squeezes often precede significant price moves."
    },
    
    "SMA": {
        "name": "Simple Moving Average",
        "description": "Average price over a specific number of periods, smooths out price action",
        "signals": {
            "bullish": "Price above SMA indicates upward trend",
            "bearish": "Price below SMA indicates downward trend",
            "neutral": "Price crossing SMA shows potential trend change"
        },
        "interpretation": "Longer period SMAs show long-term trend, shorter periods show short-term trend.",
        "trading_tips": "Golden cross (50 SMA above 200 SMA) is a strong bullish signal. Death cross is bearish."
    },
    
    "EMA": {
        "name": "Exponential Moving Average",
        "description": "Gives more weight to recent prices, more responsive than SMA",
        "signals": {
            "bullish": "Price above EMA with EMA sloping upward",
            "bearish": "Price below EMA with EMA sloping downward",
            "neutral": "Price oscillating around flat EMA"
        },
        "interpretation": "Reacts faster to price changes than SMA. Good for identifying trend direction and momentum.",
        "trading_tips": "Use multiple EMAs (9, 21, 50) to confirm trend strength and find entry points."
    },
    
    "ATR": {
        "name": "Average True Range",
        "description": "Measures market volatility, doesn't indicate direction",
        "signals": {
            "high": "High ATR indicates increased volatility and larger price swings",
            "low": "Low ATR indicates decreased volatility and smaller price movements",
            "normal": "Average ATR shows typical volatility for the stock"
        },
        "interpretation": "Higher ATR values suggest more volatile periods. Useful for setting stop-losses and position sizing.",
        "trading_tips": "Use ATR multiples (2x ATR) for stop-loss placement to avoid being stopped out by normal volatility."
    },
    
    "Stochastic": {
        "name": "Stochastic Oscillator",
        "description": "Compares closing price to price range over time",
        "signals": {
            "bullish": "%K below 20 (oversold) and crossing above %D",
            "bearish": "%K above 80 (overbought) and crossing below %D",
            "neutral": "%K and %D between 20-80"
        },
        "interpretation": "Oscillates between 0-100. Shows momentum and potential reversal points.",
        "trading_tips": "Wait for confirmation - look for price action to confirm stochastic signals."
    },
    
    "Williams %R": {
        "name": "Williams Percent Range",
        "description": "Momentum oscillator similar to stochastic but inverted",
        "signals": {
            "bullish": "Reading above -20 (overbought) may signal selling opportunity",
            "bearish": "Reading below -80 (oversold) may signal buying opportunity",
            "neutral": "Reading between -20 and -80"
        },
        "interpretation": "Oscillates between -100 and 0. More negative values indicate oversold conditions.",
        "trading_tips": "Look for divergences between Williams %R and price for early reversal signals."
    },
    
    "Support/Resistance": {
        "name": "Support and Resistance Levels",
        "description": "Price levels where buying or selling pressure is concentrated",
        "signals": {
            "bullish": "Price bouncing off support level shows buying interest",
            "bearish": "Price rejected at resistance shows selling pressure",
            "breakout": "Price breaking through levels signals potential trend continuation"
        },
        "interpretation": "Support acts as floor, resistance as ceiling. Multiple touches make levels stronger.",
        "trading_tips": "Wait for confirmation of breaks. False breakouts are common - use volume for confirmation."
    },
    
    "Volume": {
        "name": "Trading Volume",
        "description": "Number of shares traded, confirms price movements",
        "signals": {
            "bullish": "Rising prices with increasing volume shows strong buying",
            "bearish": "Falling prices with increasing volume shows strong selling",
            "weak": "Price moves without volume often fail"
        },
        "interpretation": "Volume validates price movements. High volume suggests institutional interest.",
        "trading_tips": "Volume spikes often occur at trend reversals. Use volume to confirm breakouts."
    }
}

def get_indicator_explanation(indicator_name):
    """Get explanation for a specific indicator"""
    return INDICATOR_EXPLANATIONS.get(indicator_name, {
        "name": indicator_name,
        "description": "Technical indicator explanation not available",
        "signals": {"info": "Check indicator value and compare to historical levels"},
        "interpretation": "Consult trading resources for detailed explanation",
        "trading_tips": "Always use multiple indicators for confirmation"
    })

def get_all_explanations():
    """Get all indicator explanations"""
    return INDICATOR_EXPLANATIONS

def format_explanation_for_display(indicator_name, explanation):
    """Format explanation for Streamlit display"""
    return f"""
    **{explanation['name']}**
    
    📖 **What it measures:** {explanation['description']}
    
    📊 **Trading Signals:**
    • 🟢 Bullish: {explanation['signals'].get('bullish', 'N/A')}
    • 🔴 Bearish: {explanation['signals'].get('bearish', 'N/A')}
    • ⚪ Neutral: {explanation['signals'].get('neutral', 'N/A')}
    
    💡 **How to read it:** {explanation['interpretation']}
    
    🎯 **Trading Tips:** {explanation['trading_tips']}
    """