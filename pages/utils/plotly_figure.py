import plotly.graph_objects as go
import pandas as pd
import dateutil
import datetime
import pandas_ta as pta

def plotly_table(dataframe: pd.DataFrame):    
    header_values = []
    
    # Check if columns are a MultiIndex
    if isinstance(dataframe.columns, pd.MultiIndex):
        header_values = dataframe.columns.get_level_values(0)
    else:
        header_values = dataframe.columns
    
    # create the bolded header values
    final_header_values = ["<b>" + str(col) + "<b>" for col in header_values]
    
    # Add the Index header
    header_name = dataframe.index.name if dataframe.index.name else "Index"
    final_header_values.insert(0, "<b>" + header_name + "<b>")
    
    # Create cell values
    cell_values = [["<b>" + str(i) + "<b>" for i in dataframe.index]]
    cell_values.extend([dataframe[col] for col in dataframe.columns])
    
    # Row Colors
    rowOddColor = 'white'
    rowEvenColor = 'lightgray'

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=final_header_values,
            fill_color='#0078ff',
            align='left',
            font=dict(color="black", size=16),
            line_color='darkslategray'
        ),
        cells=dict(
            values=cell_values,
            # Alternating colors for rows
            fill_color=[[rowOddColor, rowEvenColor] * (len(dataframe) // 2 + 1)],
            align='left',
            font=dict(color="black", size=15),
            line_color='darkslategray'
        )
    )])
    
    fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=10) # Tighten the layout
    )
    return fig

def filter_data(dataframe, num_period):
    if num_period == '5d':
        date = dataframe.index[-1] + dateutil.relativedelta.relativedelta(days=-5)
    elif num_period == '1mo':
        date = dataframe.index[-1] + dateutil.relativedelta.relativedelta(months=-1)
    elif num_period == '6mo':
        date = dataframe.index[-1] + dateutil.relativedelta.relativedelta(months=-6)
    elif num_period == '1y':
        date = dataframe.index[-1] + dateutil.relativedelta.relativedelta(years=-1)
    elif num_period == '5y':
        date = dataframe.index[-1] + dateutil.relativedelta.relativedelta(years=-5)
    elif num_period == 'ytd':
        date = datetime.datetime(dataframe.index[-1].year,1,1).strftime('%Y-%m-%d')
    else:
        date = dataframe.index[0]
        
    return dataframe.reset_index()[dataframe.reset_index()['Date']>date]

def close_chart(dataframe, num_period =False):
    if num_period:
        dataframe = filter_data(dataframe, num_period)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x= dataframe['Date'], y=dataframe['Open'], mode='lines', name='Open', line=dict(width=2,color='#5ab7ff')))
    fig.add_trace(go.Scatter(x= dataframe['Date'], y=dataframe['Close'], mode='lines', name='Close', line=dict(width=2,color='black')))
    fig.add_trace(go.Scatter(x= dataframe['Date'], y=dataframe['High'], mode='lines', name='High', line=dict(width=2,color='#0078ff')))
    fig.add_trace(go.Scatter(x= dataframe['Date'], y=dataframe['Low'], mode='lines', name='Low', line=dict(width=2,color='red')))
    fig.update_xaxes(rangeslider_visible=True)
    fig.update_layout(height=500, margin=dict(l=0, r=20, t=20, b=0), plot_bgcolor='white',paper_bgcolor='#e1efff', legend=dict(yanchor="top", xanchor="right"))
    return fig
    
