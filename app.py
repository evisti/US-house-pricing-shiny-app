import pandas as pd
import plotly.express as px

from datetime import datetime
from pathlib import Path

from shiny import reactive
from shiny.express import input, render, ui
from shinywidgets import render_plotly


# ---------------------------------------------------------------------
# Reading in Files
# ---------------------------------------------------------------------

median_listing_price_df = pd.read_csv(Path(__file__).parent / 'data/Metro_mlp_uc_sfrcondo_sm_month.csv')
for_sale_inventory_df = pd.read_csv(Path(__file__).parent / 'data/Metro_invt_fs_uc_sfrcondo_sm_month.csv')
new_listings_df = pd.read_csv(Path(__file__).parent / 'data/Metro_new_listings_uc_sfrcondo_sm_month.csv')


# ---------------------------------------------------------------------
# Helper functions - converting to DateTime
# ---------------------------------------------------------------------

def string_to_date(date_string: str) -> datetime.date:
    return datetime.strptime(date_string, format='%Y-%m-%d').date()

def filter_by_date(df: pd.DataFrame, date_range: tuple):
    rng = sorted(date_range)
    dates = pd.to_datetime(df['Date'], format='%Y-%m-%d').dt.date
    return df[(dates >= rng[0]) & (dates <= rng[1])]


# ---------------------------------------------------------------------
# Visualizations
# ---------------------------------------------------------------------

state_choices = new_listings_df['StateName'].dropna().drop_duplicates().sort_values().tolist()
state_choices = ['United States'] + state_choices

ui.input_select('state', 'Filter by State', choices=state_choices)

# Plotly visualization of Median Home Price Per State
@render_plotly
def list_price_plot():
    # Grouping by State Name and specifying the Date Columns
    price_grouped = median_listing_price_df.groupby('StateName').mean(numeric_only=True)     
    date_columns = median_listing_price_df.columns[5:]
    price_grouped_dates = price_grouped[date_columns].reset_index()   
    price_df_for_viz = price_grouped_dates.melt(id_vars=['StateName'], var_name='Date', value_name='Value')

    if input.state() == 'United States':
        df = price_df_for_viz
    else:
        df = price_df_for_viz[price_df_for_viz['StateName'] == input.state()]

    # Creating Visualization using Plotly
    fig = px.line(df, x='Date', y='Value', color='StateName')
    fig.update_xaxes(title_text='')
    fig.update_yaxes(title_text='')
    
    return fig

@render.data_frame
def list_price_data():
    if input.state() == 'United States':
        df = median_listing_price_df
    else:
        df = median_listing_price_df[median_listing_price_df['StateName'] == input.state()]

    return render.DataGrid(df)


# Plotly visualization of Homes For Sale Per State
@render_plotly
def for_sale_plot():
    # Grouping by State Name and specifying the Date Columns
    df2_grouped = for_sale_inventory_df.groupby('StateName').sum(numeric_only=True)
    date_columns = for_sale_inventory_df.columns[5:]
    df2_grouped_dates = df2_grouped[date_columns].reset_index()
    df2_melted = df2_grouped_dates.melt(id_vars=['StateName'], var_name='Date', value_name='Value')

    if input.state() == 'United States':
        df = df2_melted
    else:
        df = df2_melted[df2_melted['StateName'] == input.state()]

    # Creating Visualization using Plotly
    fig = px.line(df, x='Date', y='Value', color='StateName')
    fig.update_xaxes(title_text='')
    fig.update_yaxes(title_text='')

    return fig

@render.data_frame
def for_sale_data():
    if input.state() == 'United States':
        df = for_sale_inventory_df
    else:
        df = for_sale_inventory_df[for_sale_inventory_df['StateName'] == input.state()]

    return render.DataGrid(df)


# Plotly visualization of Listings Per State
@render_plotly
def listings_plot():
    # Grouping by State Name and specifying the Date Columns
    df3_grouped = new_listings_df.groupby('StateName').sum(numeric_only=True)
    date_columns = new_listings_df.columns[5:]
    df3_grouped_dates = df3_grouped[date_columns].reset_index()
    df3_melted = df3_grouped_dates.melt(id_vars=['StateName'], var_name='Date', value_name='Value')

    if input.state() == 'United States':
        df = df3_melted
    else:
        df = df3_melted[df3_melted['StateName'] == input.state()]

    # Creating Visualization using Plotly
    fig = px.line(df, x='Date', y='Value', color='StateName')
    fig.update_xaxes(title_text='')
    fig.update_yaxes(title_text='')
    
    return fig

@render.data_frame
def listings_data():
    if input.state() == 'United States':
        df = new_listings_df
    else:
        df = new_listings_df[new_listings_df['StateName'] == input.state()]

    return render.DataGrid(df)
