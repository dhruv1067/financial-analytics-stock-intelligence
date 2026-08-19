import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def interactive_plot(df):
    """
    Creates an interactive Plotly line chart using 'melt' for efficiency.
    This is much faster than adding traces in a loop.
    """
    # 'Melt' the DataFrame from wide format to long format
    # This is the standard way to use Plotly Express
    df_melted = pd.melt(df, id_vars='Date', var_name='Stock', value_name='Price')
    
    # Plotly Express can now plot everything in one call
    fig = px.line(df_melted, x='Date', y='Price', color='Stock')
    
    # Your layout settings
    fig.update_layout(
        width=450,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    return fig

def normalize(df):
    """
    Normalizes prices using vectorized division (no loops).
    """
    df_norm = df.copy()
    
    # Get all columns *except* 'Date'
    price_cols = [col for col in df.columns if col != 'Date']
    
    # Divide all price columns by their first row's value (.iloc[0]) at once.
    # This is vectorized and extremely fast.
    if not df_norm.empty and price_cols:
        df_norm[price_cols] = df_norm[price_cols] / df_norm[price_cols].iloc[0]
    
    return df_norm

def daily_return(df):
    """
    Calculates daily returns using the built-in '.pct_change()' method.
    This replaces your nested loops and is thousands of times faster.
    """
    df_returns = df.copy()
    
    # Set 'Date' as the index so that .pct_change() only
    # applies to the numeric (price) columns.
    if 'Date' in df_returns.columns:
        df_returns = df_returns.set_index('Date')
    
    # .pct_change() calculates (new_price - old_price) / old_price
    # We multiply by 100 to get the percentage.
    df_daily_return = df_returns.pct_change() * 100
    
    # The first row will be 'NaN' (since there's no previous day)
    # We replace NaN with 0 to match your original function's logic.
    df_daily_return = df_daily_return.fillna(0)
    
    # Reset the index to turn 'Date' back into a column
    return df_daily_return.reset_index()

def calculate_beta(stocks_daily_return, stock):
    """
    Calculates beta and alpha using numpy.polyfit.
    """
    # 'sp500' is the independent variable (x)
    # 'stock' is the dependent variable (y)
    # np.polyfit(x, y, 1) fits a 1st-degree polynomial (a line)
    # and returns [slope, intercept]
    
    b, a = np.polyfit(stocks_daily_return['sp500'], stocks_daily_return[stock], 1)
    
    # b = slope = Beta
    # a = intercept = Alpha
    return b, a

def beta_regression_plot(returns_df, stock_ticker, beta, alpha):
    """
    Creates a scatter plot of stock returns vs. market returns
    and adds the regression line (beta).
    """
    # Create the scatter plot
    fig = px.scatter(
        returns_df,
        x='sp500',
        y=stock_ticker,
        title=f'{stock_ticker} vs. S&P 500 (Beta: {beta:.2f})',
        labels={'sp500': 'S&P 500 Daily Return (%)', stock_ticker: f'{stock_ticker} Daily Return (%)'}
    )
    
    # Add the regression line
    # Create x-values for the line
    x_line = np.array([returns_df['sp500'].min(), returns_df['sp500'].max()])

    # Calculate corresponding y-values
    y_line = x_line * beta + alpha
    
    # Add the line to the figure
    fig.add_trace(go.Scatter(
        x=x_line,
        y=y_line,
        mode='lines',
        name='Regression Line (Beta)',
        line=dict(color='red', dash='dash')
    ))
    
    return fig

