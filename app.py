import pandas as pd
import plotly.express as px

from datetime import datetime
from faicons import icon_svg
from pathlib import Path

from shiny import reactive
from shiny.express import input, render, ui
from shinywidgets import render_plotly

# ignore PerformanceWarning (it pops up SO MANY times)
from warnings import simplefilter
simplefilter(action="ignore", category=pd.errors.PerformanceWarning)


# ---------------------------------------------------------------------
# Read in Files
# ---------------------------------------------------------------------

median_listing_price_df = pd.read_csv(Path(__file__).parent / 'data/Metro_mlp_uc_sfrcondo_sm_month.csv')
for_sale_inventory_df = pd.read_csv(Path(__file__).parent / 'data/Metro_invt_fs_uc_sfrcondo_sm_month.csv')
new_listings_df = pd.read_csv(Path(__file__).parent / 'data/Metro_new_listings_uc_sfrcondo_sm_month.csv')


# ---------------------------------------------------------------------
# Helper functions - converting to DateTime
# ---------------------------------------------------------------------

def string_to_date(date_str: str) -> datetime.date:
    date_format = "%Y-%m-%d"
    return datetime.strptime(date_str, date_format).date()

def filter_by_date(df: pd.DataFrame, date_range: tuple):
    sorted_range = sorted(date_range)
    dates = pd.to_datetime(df['Date'], format='%Y-%m-%d').dt.date
    return df[(dates >= sorted_range[0]) & (dates <= sorted_range[1])]


# ---------------------------------------------------------------------
# Visualizations
# ---------------------------------------------------------------------

# set page level title
ui.page_opts(title='US Housing App')

# for state selection via 'input select'
state_choices = new_listings_df['StateName'].dropna().drop_duplicates().sort_values().tolist()
state_choices = ['United States'] + state_choices

# for date range selection via 'input slider'
date_columns = new_listings_df.columns[5:]
min_date, max_date = string_to_date(date_columns[0]), string_to_date(date_columns[-1])

# sidebar
with ui.sidebar():
    # ui 'input select' for selecting state
    ui.input_select('state', 'Filter by State', choices=state_choices)

    # ui 'input slider' for selecting date range
    ui.input_slider(
        'date_range', 
        'Filter by Date Range',
        min=min_date,
        max=max_date,
        value=[min_date, max_date]
    )

    # toggle dark mode
    ui.input_dark_mode()


with ui.navset_card_underline(title='Median List Price'):

    with ui.nav_panel(title='Plot', icon=icon_svg('chart-line')):

        # Plotly visualization of median home price per state
        @render_plotly
        def list_price_plot():
            # group by state name and specify the date columns
            price_grouped = median_listing_price_df.groupby('StateName').mean(numeric_only=True)
            date_columns = median_listing_price_df.columns[5:]
            price_grouped_dates = price_grouped[date_columns].reset_index()   
            price_df_for_viz = price_grouped_dates.melt(id_vars=['StateName'], var_name='Date', value_name='Value')

            # input select
            if input.state() == 'United States':
                df = price_df_for_viz
            else:
                df = price_df_for_viz[price_df_for_viz['StateName'] == input.state()]

            # input slider
            df = filter_by_date(df, input.date_range())    

            # create visualization using Plotly
            fig = px.line(df, x='Date', y='Value', color='StateName')
            fig.update_xaxes(title_text='')
            fig.update_yaxes(title_text='')
            
            return fig

    with ui.nav_panel(title='Data', icon=icon_svg('table')):

        @render.data_frame
        def list_price_data():
            if input.state() == 'United States':
                df = median_listing_price_df
            else:
                df = median_listing_price_df[median_listing_price_df['StateName'] == input.state()]

            return render.DataGrid(df)


with ui.navset_card_underline(title='Home Inventory'):

    with ui.nav_panel(title='Plot', icon=icon_svg('chart-line')):

        # Plotly visualization of homes for sale per state
        @render_plotly
        def for_sale_plot():
            # group by state name and specify the date columns
            df2_grouped = for_sale_inventory_df.groupby('StateName').sum(numeric_only=True)
            date_columns = for_sale_inventory_df.columns[5:]
            df2_grouped_dates = df2_grouped[date_columns].reset_index()
            df2_melted = df2_grouped_dates.melt(id_vars=['StateName'], var_name='Date', value_name='Value')

            # input select
            if input.state() == 'United States':
                df = df2_melted
            else:
                df = df2_melted[df2_melted['StateName'] == input.state()]

            # input slider
            df = filter_by_date(df, input.date_range())  

            # create visualization using Plotly
            fig = px.line(df, x='Date', y='Value', color='StateName')
            fig.update_xaxes(title_text='')
            fig.update_yaxes(title_text='')

            return fig

    with ui.nav_panel(title='Data', icon=icon_svg('table')):

        @render.data_frame
        def for_sale_data():
            if input.state() == 'United States':
                df = for_sale_inventory_df
            else:
                df = for_sale_inventory_df[for_sale_inventory_df['StateName'] == input.state()]

            return render.DataGrid(df)


with ui.navset_card_underline(title='New Listings'):

    with ui.nav_panel('Plot', icon=icon_svg('chart-line')):

        # Plotly visualization of listings per state
        @render_plotly
        def listings_plot():
            # group by state name and specify the date columns
            df3_grouped = new_listings_df.groupby('StateName').sum(numeric_only=True)
            date_columns = new_listings_df.columns[5:]
            df3_grouped_dates = df3_grouped[date_columns].reset_index()
            df3_melted = df3_grouped_dates.melt(id_vars=['StateName'], var_name='Date', value_name='Value')

            # input select
            if input.state() == 'United States':
                df = df3_melted
            else:
                df = df3_melted[df3_melted['StateName'] == input.state()]

            # input slider
            df = filter_by_date(df, input.date_range())  

            # create visualization using Plotly
            fig = px.line(df, x='Date', y='Value', color='StateName')
            fig.update_xaxes(title_text='')
            fig.update_yaxes(title_text='')
            
            return fig

    with ui.nav_panel(title='Data', icon=icon_svg('table')):

        @render.data_frame
        def listings_data():
            if input.state() == 'United States':
                df = new_listings_df
            else:
                df = new_listings_df[new_listings_df['StateName'] == input.state()]

            return render.DataGrid(df)
