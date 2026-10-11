import pandas as pd
import plotly.express as px

from datetime import datetime
from faicons import icon_svg
from pathlib import Path

#from shiny import reactive
from shiny.express import input, render, ui
from shinywidgets import render_plotly

# ignore PerformanceWarning (it pops up SO MANY times)
from warnings import simplefilter
simplefilter(action="ignore", category=pd.errors.PerformanceWarning)


# -------------------------------------------------------------------------
# Read in Files
# -------------------------------------------------------------------------

# the directory containing this file
app_dir = Path(__file__).parent

# read files
median_listing_price_df = pd.read_csv(app_dir / 'data/Metro_mlp_uc_sfrcondo_sm_month.csv')
for_sale_inventory_df = pd.read_csv(app_dir / 'data/Metro_invt_fs_uc_sfrcondo_sm_month.csv')
new_listings_df = pd.read_csv(app_dir / 'data/Metro_new_listings_uc_sfrcondo_sm_month.csv')


# -------------------------------------------------------------------------
# Data Transformation
# -------------------------------------------------------------------------

# the date columns (maybe make all date columns into datetime)
date_columns = new_listings_df.columns[5:]

# Group by state name

# median list price
median_listing_price_df['StateName'] = median_listing_price_df['StateName'].fillna(median_listing_price_df['RegionName'])
price_grouped = median_listing_price_df.groupby('StateName').mean(numeric_only=True)
price_grouped_dates = price_grouped[date_columns].reset_index()   
price_df_for_viz = price_grouped_dates.melt(id_vars=['StateName'], var_name='Date', value_name='Value')

# home inventory
for_sale_inventory_df['StateName'] = for_sale_inventory_df['StateName'].fillna(for_sale_inventory_df['RegionName'])
inventory_grouped = for_sale_inventory_df.groupby('StateName').sum(numeric_only=True)
inventory_grouped_dates = inventory_grouped[date_columns].reset_index()
inventory_df_for_viz = inventory_grouped_dates.melt(id_vars=['StateName'], var_name='Date', value_name='Value')

# new listings
new_listings_df['StateName'] = new_listings_df['StateName'].fillna(new_listings_df['RegionName'])
listings_grouped = new_listings_df.groupby('StateName').sum(numeric_only=True)
listings_grouped_dates = listings_grouped[date_columns].reset_index()
listings_df_for_viz = listings_grouped_dates.melt(id_vars=['StateName'], var_name='Date', value_name='Value')


# -------------------------------------------------------------------------
# Helper functions - converting to DateTime
# -------------------------------------------------------------------------

def string_to_date(date_str: str) -> datetime.date:
    date_format = "%Y-%m-%d"
    return datetime.strptime(date_str, date_format).date()

def filter_by_date(df: pd.DataFrame, date_range: tuple):
    sorted_range = sorted(date_range)
    dates = pd.to_datetime(df['Date'], format='%Y-%m-%d').dt.date
    return df[(dates >= sorted_range[0]) & (dates <= sorted_range[1])]


# -------------------------------------------------------------------------
# Visualizations
# -------------------------------------------------------------------------

# set page level title
ui.page_opts(title='US Housing App')

# varibles for state selection
state_choices = ['United States'] + new_listings_df['StateName'].dropna().drop_duplicates().sort_values().tolist()

# variables for date selection
date_columns = new_listings_df.columns[5:]
min_date, max_date = string_to_date(date_columns[0]), string_to_date(date_columns[-1])

# sidebar
with ui.sidebar():
    # ui input select for selecting state
    ui.input_select('state', 'Filter by State', choices=state_choices)

    # ui input slider for selecting date range
    ui.input_slider(
        'date_range', 
        'Filter by Date Range',
        min=min_date,
        max=max_date,
        value=[min_date, max_date]
    )

    # toggle dark mode
    ui.input_dark_mode()

# value boxes
with ui.layout_column_wrap():

    with ui.value_box(showcase=icon_svg('dollar-sign')):
        'Current Median List Price'
        @render.ui
        def price():
            df = price_df_for_viz[price_df_for_viz['StateName'] == input.state()]
            last_value = df.iloc[-1, -1]

            return f'${last_value / 1000:.0f}K'

    with ui.value_box(showcase=icon_svg('house')):
        'Latest Home Inventory Change'
        @render.ui
        def change():
            df = inventory_df_for_viz[inventory_df_for_viz['StateName'] == input.state()]
            last_value = df.iloc[-1, -1]
            second_last_value = df.iloc[-2, -1]
            percentage_change = (last_value - second_last_value) / second_last_value * 100
            sign = '+' if percentage_change > 0 else ''

            return f'{sign}{percentage_change:.2f} %'

# navset for 'Median List Price'
with ui.navset_card_underline(title='Median List Price'):

    # add spacer
    ui.nav_spacer()

    # nav panel with plot
    with ui.nav_panel(title='Plot', icon=icon_svg('chart-line')):

        # Plotly visualization of median home price per state
        @render_plotly
        def list_price_plot():
            # input select
            df = price_df_for_viz[price_df_for_viz['StateName'] == input.state()]

            # input slider
            df = filter_by_date(df, input.date_range())    

            # create visualization using Plotly
            fig = px.line(df, x='Date', y='Value', color='StateName')
            fig.update_xaxes(title_text='')
            fig.update_yaxes(title_text='')
            fig.update_layout(showlegend=False)
            
            return fig

    # nav panel with data
    with ui.nav_panel(title='Data', icon=icon_svg('table')):

        @render.data_frame
        def list_price_data():
            df = median_listing_price_df[median_listing_price_df['StateName'] == input.state()]
            df = df.drop(columns=['RegionType', 'StateName', 'RegionID', 'SizeRank'])
            df = df.sort_values('RegionName')
            return render.DataGrid(df)

# navset for 'Home Inventory'
with ui.navset_card_underline(title='Home Inventory'):

    # add spacer
    ui.nav_spacer()

    # nav panel with plot
    with ui.nav_panel(title='Plot', icon=icon_svg('chart-line')):

        # Plotly visualization of homes for sale per state
        @render_plotly
        def for_sale_plot():
            # input select
            df = inventory_df_for_viz[inventory_df_for_viz['StateName'] == input.state()]

            # input slider
            df = filter_by_date(df, input.date_range())  

            # create visualization using Plotly
            fig = px.line(df, x='Date', y='Value', color='StateName')
            fig.update_xaxes(title_text='')
            fig.update_yaxes(title_text='')
            fig.update_layout(showlegend=False)

            return fig

    # nav panel with data
    with ui.nav_panel(title='Data', icon=icon_svg('table')):

        @render.data_frame
        def for_sale_data():
            df = for_sale_inventory_df[for_sale_inventory_df['StateName'] == input.state()]
            df = df.drop(columns=['RegionType', 'StateName', 'RegionID', 'SizeRank'])
            df = df.sort_values('RegionName')
            return render.DataGrid(df)

# navset for 'New Listings'
with ui.navset_card_underline(title='New Listings'):

    # add spacer
    ui.nav_spacer()

    # nav panel with plot
    with ui.nav_panel('Plot', icon=icon_svg('chart-line')):

        # Plotly visualization of listings per state
        @render_plotly
        def listings_plot():
            # input select
            df = listings_df_for_viz[listings_df_for_viz['StateName'] == input.state()]

            # input slider
            df = filter_by_date(df, input.date_range())  

            # create visualization using Plotly
            fig = px.line(df, x='Date', y='Value', color='StateName')
            fig.update_xaxes(title_text='')
            fig.update_yaxes(title_text='')
            fig.update_layout(showlegend=False)
            
            return fig

    # nav panel with data
    with ui.nav_panel(title='Data', icon=icon_svg('table')):

        @render.data_frame
        def listings_data():
            df = new_listings_df[new_listings_df['StateName'] == input.state()]
            df = df.drop(columns=['RegionType', 'StateName', 'RegionID', 'SizeRank'])
            df = df.sort_values('RegionName')
            return render.DataGrid(df)
