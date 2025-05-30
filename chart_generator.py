import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import logging

class ChartGenerator:
    """
    Class to generate interactive charts for technical analysis
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Color scheme
        self.colors = {
            'price': '#1f77b4',
            'sma': '#ff7f0e',
            'ema': '#2ca02c',
            'bb_upper': '#d62728',
            'bb_lower': '#d62728',
            'bb_fill': 'rgba(214, 39, 40, 0.1)',
            'volume': '#9467bd',
            'rsi': '#8c564b',
            'macd': '#e377c2',
            'macd_signal': '#7f7f7f',
            'macd_histogram': '#bcbd22',
            'support': '#2ca02c',
            'resistance': '#d62728',
            'fibonacci': '#ff7f0e'
        }
    
    def create_comprehensive_chart(self, stock_data, analysis_data, symbol):
        """
        Create a comprehensive chart with price, volume, and technical indicators
        
        Args:
            stock_data (pd.DataFrame): Original OHLC data
            analysis_data (pd.DataFrame): Data with technical indicators
            symbol (str): Stock symbol
            
        Returns:
            plotly.graph_objects.Figure: Comprehensive chart
        """
        try:
            # Create subplots
            fig = make_subplots(
                rows=4, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                subplot_titles=(
                    f'{symbol} - Price & Technical Indicators',
                    'Volume',
                    'RSI (14)',
                    'MACD'
                ),
                row_heights=[0.5, 0.2, 0.15, 0.15]
            )
            
            # Main price chart with candlesticks
            fig.add_trace(
                go.Candlestick(
                    x=analysis_data.index,
                    open=analysis_data['Open'],
                    high=analysis_data['High'],
                    low=analysis_data['Low'],
                    close=analysis_data['Close'],
                    name='Price',
                    increasing_line_color='#00ff00',
                    decreasing_line_color='#ff0000'
                ),
                row=1, col=1
            )
            
            # Add moving averages
            if 'SMA' in analysis_data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=analysis_data.index,
                        y=analysis_data['SMA'],
                        mode='lines',
                        name='SMA (20)',
                        line=dict(color=self.colors['sma'], width=2)
                    ),
                    row=1, col=1
                )
            
            if 'EMA' in analysis_data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=analysis_data.index,
                        y=analysis_data['EMA'],
                        mode='lines',
                        name='EMA (20)',
                        line=dict(color=self.colors['ema'], width=2)
                    ),
                    row=1, col=1
                )
            
            # Add Bollinger Bands
            if all(col in analysis_data.columns for col in ['BB_Upper', 'BB_Lower', 'BB_Middle']):
                # Upper band
                fig.add_trace(
                    go.Scatter(
                        x=analysis_data.index,
                        y=analysis_data['BB_Upper'],
                        mode='lines',
                        name='BB Upper',
                        line=dict(color=self.colors['bb_upper'], width=1, dash='dash'),
                        showlegend=False
                    ),
                    row=1, col=1
                )
                
                # Lower band
                fig.add_trace(
                    go.Scatter(
                        x=analysis_data.index,
                        y=analysis_data['BB_Lower'],
                        mode='lines',
                        name='BB Lower',
                        line=dict(color=self.colors['bb_lower'], width=1, dash='dash'),
                        fill='tonexty',
                        fillcolor=self.colors['bb_fill']
                    ),
                    row=1, col=1
                )
                
                # Middle band
                fig.add_trace(
                    go.Scatter(
                        x=analysis_data.index,
                        y=analysis_data['BB_Middle'],
                        mode='lines',
                        name='BB Middle',
                        line=dict(color='gray', width=1, dash='dot'),
                        showlegend=False
                    ),
                    row=1, col=1
                )
            
            # Add support and resistance levels
            self._add_support_resistance_levels(fig, analysis_data)
            
            # Add Fibonacci levels
            self._add_fibonacci_levels(fig, analysis_data)
            
            # Volume chart
            colors = ['red' if close < open else 'green' 
                     for close, open in zip(analysis_data['Close'], analysis_data['Open'])]
            
            fig.add_trace(
                go.Bar(
                    x=analysis_data.index,
                    y=analysis_data['Volume'],
                    name='Volume',
                    marker_color=colors,
                    opacity=0.7
                ),
                row=2, col=1
            )
            
            # RSI chart
            if 'RSI' in analysis_data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=analysis_data.index,
                        y=analysis_data['RSI'],
                        mode='lines',
                        name='RSI',
                        line=dict(color=self.colors['rsi'], width=2)
                    ),
                    row=3, col=1
                )
                
                # RSI overbought/oversold lines
                fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=3, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=3, col=1)
                fig.add_hline(y=50, line_dash="dot", line_color="gray", opacity=0.3, row=3, col=1)
            
            # MACD chart
            if all(col in analysis_data.columns for col in ['MACD', 'MACD_Signal', 'MACD_Histogram']):
                # MACD line
                fig.add_trace(
                    go.Scatter(
                        x=analysis_data.index,
                        y=analysis_data['MACD'],
                        mode='lines',
                        name='MACD',
                        line=dict(color=self.colors['macd'], width=2)
                    ),
                    row=4, col=1
                )
                
                # Signal line
                fig.add_trace(
                    go.Scatter(
                        x=analysis_data.index,
                        y=analysis_data['MACD_Signal'],
                        mode='lines',
                        name='Signal',
                        line=dict(color=self.colors['macd_signal'], width=2)
                    ),
                    row=4, col=1
                )
                
                # Histogram
                colors = ['green' if val >= 0 else 'red' for val in analysis_data['MACD_Histogram']]
                fig.add_trace(
                    go.Bar(
                        x=analysis_data.index,
                        y=analysis_data['MACD_Histogram'],
                        name='Histogram',
                        marker_color=colors,
                        opacity=0.7
                    ),
                    row=4, col=1
                )
                
                # Zero line
                fig.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.5, row=4, col=1)
            
            # Update layout
            fig.update_layout(
                title=f'{symbol} - Technical Analysis Dashboard',
                xaxis_rangeslider_visible=False,
                height=800,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                margin=dict(l=50, r=50, t=100, b=50)
            )
            
            # Update y-axis labels
            fig.update_yaxes(title_text="Price ($)", row=1, col=1)
            fig.update_yaxes(title_text="Volume", row=2, col=1)
            fig.update_yaxes(title_text="RSI", row=3, col=1, range=[0, 100])
            fig.update_yaxes(title_text="MACD", row=4, col=1)
            
            # Update x-axis
            fig.update_xaxes(title_text="Date", row=4, col=1)
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating comprehensive chart: {str(e)}")
            return self._create_error_chart(str(e))
    
    def _add_support_resistance_levels(self, fig, data):
        """
        Add support and resistance levels to the chart
        
        Args:
            fig: Plotly figure object
            data: Analysis data with support/resistance info
        """
        try:
            if 'support_resistance' in data.columns:
                latest_sr = data['support_resistance'].iloc[-1]
                
                if latest_sr and isinstance(latest_sr, dict):
                    # Support level
                    support = latest_sr.get('support')
                    if support:
                        fig.add_hline(
                            y=support,
                            line_dash="dash",
                            line_color=self.colors['support'],
                            opacity=0.7,
                            annotation_text=f"Support: ${support:.2f}",
                            annotation_position="bottom right",
                            row=1, col=1
                        )
                    
                    # Resistance level
                    resistance = latest_sr.get('resistance')
                    if resistance:
                        fig.add_hline(
                            y=resistance,
                            line_dash="dash",
                            line_color=self.colors['resistance'],
                            opacity=0.7,
                            annotation_text=f"Resistance: ${resistance:.2f}",
                            annotation_position="top right",
                            row=1, col=1
                        )
        
        except Exception as e:
            self.logger.warning(f"Could not add support/resistance levels: {str(e)}")
    
    def _add_fibonacci_levels(self, fig, data):
        """
        Add Fibonacci retracement levels to the chart
        
        Args:
            fig: Plotly figure object
            data: Analysis data with Fibonacci levels
        """
        try:
            if 'fibonacci_levels' in data.columns:
                latest_fib = data['fibonacci_levels'].iloc[-1]
                
                if latest_fib and isinstance(latest_fib, dict):
                    # Add key Fibonacci levels
                    key_levels = ['23.6%', '38.2%', '50%', '61.8%']
                    
                    for level_name in key_levels:
                        if level_name in latest_fib:
                            level_price = latest_fib[level_name]
                            fig.add_hline(
                                y=level_price,
                                line_dash="dot",
                                line_color=self.colors['fibonacci'],
                                opacity=0.5,
                                annotation_text=f"Fib {level_name}: ${level_price:.2f}",
                                annotation_position="bottom left",
                                row=1, col=1
                            )
        
        except Exception as e:
            self.logger.warning(f"Could not add Fibonacci levels: {str(e)}")
    
    def create_simple_price_chart(self, data, symbol):
        """
        Create a simple price chart for quick viewing
        
        Args:
            data (pd.DataFrame): Stock data
            symbol (str): Stock symbol
            
        Returns:
            plotly.graph_objects.Figure: Simple price chart
        """
        try:
            fig = go.Figure()
            
            # Add candlestick chart
            fig.add_trace(
                go.Candlestick(
                    x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name=symbol
                )
            )
            
            fig.update_layout(
                title=f'{symbol} - Price Chart',
                xaxis_title='Date',
                yaxis_title='Price ($)',
                xaxis_rangeslider_visible=False,
                height=400
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating simple price chart: {str(e)}")
            return self._create_error_chart(str(e))
    
    def create_indicator_chart(self, data, indicator_name, symbol):
        """
        Create a chart for a specific technical indicator
        
        Args:
            data (pd.DataFrame): Data with indicators
            indicator_name (str): Name of the indicator to chart
            symbol (str): Stock symbol
            
        Returns:
            plotly.graph_objects.Figure: Indicator chart
        """
        try:
            fig = go.Figure()
            
            if indicator_name in data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data[indicator_name],
                        mode='lines',
                        name=indicator_name,
                        line=dict(width=2)
                    )
                )
                
                # Add reference lines for specific indicators
                if indicator_name == 'RSI':
                    fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5)
                    fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5)
                    fig.add_hline(y=50, line_dash="dot", line_color="gray", opacity=0.3)
                    fig.update_yaxes(range=[0, 100])
                
                fig.update_layout(
                    title=f'{symbol} - {indicator_name}',
                    xaxis_title='Date',
                    yaxis_title=indicator_name,
                    height=300
                )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating indicator chart: {str(e)}")
            return self._create_error_chart(str(e))
    
    def _create_error_chart(self, error_message):
        """
        Create an error chart when chart generation fails
        
        Args:
            error_message (str): Error message to display
            
        Returns:
            plotly.graph_objects.Figure: Error chart
        """
        fig = go.Figure()
        
        fig.add_annotation(
            text=f"Chart Error: {error_message}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="red")
        )
        
        fig.update_layout(
            title="Chart Generation Error",
            height=400,
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False)
        )
        
        return fig
