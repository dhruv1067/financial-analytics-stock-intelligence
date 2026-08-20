import streamlit as st
import pandas as pd
import capm_functions_advance
import yfinance as yf
import datetime

st.set_page_config(page_title="Beta Calculations", layout='wide')
st.title("📈 Beta Calculations")

# --- 1. GETTING INPUT FROM USER ---

col1, col2 = st.columns([1,1])
with col1:
    stocks_list = st.multiselect("Choose Stocks", ('TSLA', 'AAPL','NFLX', 'MSFT', 'MGM', 'AMZN','NVDA', 'GOOGL'),['TSLA', 'AAPL', 'AMZN', 'GOOGL'] )
with col2:
    year = st.number_input("Number of years",1,10,1)

# Stop execution if no stocks are selected
if not stocks_list:
    st.warning("Please select at least one stock to proceed.")
    st.stop()

# --- 2. PERFORM CALCULATION ON THIS PAGE ---
try:
    with st.spinner("Downloading Data and Calculating Beta..."):
        # --- Download Data ---
        end = datetime.date.today()
        start = datetime.date.today() - datetime.timedelta(days=year * 365)
        
        # Add S&P 500 ticker
        all_tickers = stocks_list + ['^GSPC']
        data = yf.download(all_tickers, start=start, end=end)['Close']
        
        # --- ROBUSTNESS CHECK ---
        if data.empty:
            st.error("Could not download data. Check tickers or date range.")
            st.stop()
            
        data.reset_index(inplace=True)
        
        # Rename market column to 'sp500' to match capm_functions
        data.rename(columns={'^GSPC': 'sp500'}, inplace=True)
        
        # Drop rows with any missing data
        full_df = data.dropna()
        
        # --- Run Calculations ---
        # Pass the full df (including 'sp500') to daily_return
        stocks_daily_return = capm_functions_advance.daily_return(full_df)
        
        beta = {}
        alpha = {}
        # Calculate beta/alpha for each selected stock
        for stock in stocks_list:
            # The capm_functions.calculate_beta expects 'sp500' to be in the df
            b, a = capm_functions_advance.calculate_beta(stocks_daily_return, stock)
            beta[stock] = b
            alpha[stock] = a
            
    # --- 3. DISPLAY RESULTS ---
    st.markdown("### Calculated Beta & Alpha Values")
    st.write("""
    **Beta (β)** measures a stock's volatility relative to the market (S&P 500).
    - $\\beta > 1$: More volatile than the market.
    - $\\beta = 1$: Moves with the market.
    - $\\beta < 1$: Less volatile than the market.
    
    **Alpha (α)** represents the stock's excess return when the market return is zero. A positive alpha suggests the stock has outperformed.
    """)
    
    # Create Beta DataFrame
    beta_df = pd.DataFrame({
        'Stock': beta.keys(),
        'Beta (β)': [round(b, 2) for b in beta.values()],
        'Alpha (α)': [f"{a:.2f}%" for a in alpha.values()] # Show as percentage
    })
    
    st.dataframe(beta_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    
    st.markdown("### Beta Visualization (Stock vs. Market)")
    st.write("Select a stock to see its daily returns plotted against the S&P 500.")
    
    # Dropdown to select which stock to visualize
    selected_stock = st.selectbox("Select a stock to visualize", stocks_list)
    
    if selected_stock:
        # Get the beta and alpha for the selected stock
        beta_val = beta[selected_stock]
        alpha_val = alpha[selected_stock]
        
        # The capm_functions.beta_regression_plot also expects 'sp500'
        fig = capm_functions_advance.beta_regression_plot(stocks_daily_return, selected_stock, beta_val, alpha_val)
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"An error occurred during calculation: {e}")
    st.error("This can happen if YFinance fails to download data or if the 'Date' column is missing. Please check your stock tickers or try again.")

