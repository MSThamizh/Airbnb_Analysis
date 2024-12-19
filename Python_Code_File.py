import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import plotly.express as px
from pymongo import MongoClient

# MongoDB Connection
connection = MongoClient("mongodb+srv://thamizhvanan2000:8dRl4X258bBAnMN6@cluster0.pculefa.mongodb.net/")
db=connection['Airbnb']
col = db['Airbnb_Data']

# Getting Data
df = pd.read_csv('airbnb.csv')

# Streamlit Part
st.set_page_config(layout="wide")

col1, col2 = st.columns(2)
with col1:
    st.image("D:\Guvi\Projects\Airbnb Analysis\Data\Header Image.png", width=450, use_column_width=True)
    st.title("Airbnb Analysis")
with col2:
    st.write('''***This project aims to analyze Airbnb data for extracting meaningful insights into pricing 
             trends, availability patterns, and host performance. Using a rich dataset of Airbnb listings, 
             the analysis is focused on geospatial and statistical aspects to help users, property managers,
             and potential investors make informed decisions.***''') 
    st.markdown('''
    - **MongoDB**: For Data Storage and Complex Queries.
    - **Streamlit**: For Building Interactive Web Applications.
    - **Plotly**: For Generating Dynamic Visualizations.
    - **Tableau/Power BI**: For Comprehensive Data Dashboards.
    ''')

selected_tab = option_menu(menu_title='',options=['Geospatial Visualization', 'Price Analysis', 
                                                  'Availability Analysis', 'Location-Based Insights'],
                                                  icons=['globe-americas', 'currency-dollar', 'buildings',
                                                         'pin-map', 'clipboard-data-fill'], 
                                                  menu_icon="menu-button-wide-fill",
                                                  default_index=0,orientation="horizontal")

# Geospatial Visualization
if selected_tab == 'Geospatial Visualization':
    st.header("Listings Map")

    price_range = st.slider('Select Price Range', int(df['Price'].min()), int(df['Price'].max()), 
                            (int(df['Price'].min()), int(df['Price'].max())))
    df_map = df[(df['Price'] >= price_range[0]) & (df['Price'] <= price_range[1])]

    map_fig = px.scatter_mapbox(df_map, lat="Latitude", lon="Longitude", 
                            hover_name="Name", hover_data=["Price", "Review Scores Rating", "Property Type",
                                                           "Accommodates", "Bedrooms", "Beds", 
                                                           "Bathrooms"],
                            color="Price", size="Accommodates", mapbox_style="carto-positron", 
                            color_continuous_scale=px.colors.sequential.Rainbow, size_max=10, zoom=2)
    st.plotly_chart(map_fig)

# Price Analysis
elif selected_tab == 'Price Analysis':
    st.header("Price Analysis")   
    col1, col2 = st.columns(2)

    with col1:
        # Price Trend Over Time by Room Type
        room_type = st.radio("**Select the Room Type**", sorted(df['Room Type'].unique()), horizontal=True)
        df_price = df.groupby(['Room Type','Last Scraped'])['Price'].mean().reset_index()
        df_price = df_price[df_price['Room Type'] == room_type]
        fig_room_line = px.line(df_price, x='Last Scraped', y='Price',
                        title="Price Trend Over Time by Room Type",
                        labels={'Price':'Average Price ($)', 'Last Scraped':'Date'})
        st.plotly_chart(fig_room_line)

    with col2:
        # Price Distriibution by Country
        country = st.selectbox('**Select the Country**', sorted(df['Country'].unique()))  
        df_country = df[df['Country'] == country]
        fig_country_hist = px.histogram(df_country, x='Price', nbins=50, 
                                        title="Price Distribution by Country",
                        labels={'Price':'Price ($)'})
        st.plotly_chart(fig_country_hist)  
    
    # Country Wise Price Distriibution by Property Type
    property = st.multiselect("**Select the Property**", sorted(df_country['Property Type'].unique()), 
                              default=df_country['Property Type'].unique()[0])
    df_property = df_country[df_country['Property Type'].isin(property)]
    fig_property_box = px.box(df_property, x='Property Type', y='Price', color='Property Type', 
                          title="Country-wise Price Distribution by Property Type", 
                          labels={'Price': 'Price ($)'})
    st.plotly_chart(fig_property_box)  

    # Correlation Heatmap
    corr_rel = df_property[['Price', 'Accommodates', 'Bedrooms', 'Beds','Bathrooms', 'Number Of Reviews', 
                   'Review Scores Rating', 'Availability 365', 'Guests Included']].corr()
    fig_heatmap = px.imshow(corr_rel, text_auto=True, title="Correlation Heatmap", 
                            height=950, width=1200, color_continuous_scale='Peach')
    st.plotly_chart(fig_heatmap) 

# Availability Analysis
elif selected_tab == 'Availability Analysis':
    st.header("Availability Analysis")
    col1, col2 = st.columns(2)

    with col1:
        # Occupancy Rate
        df['Occupancy Rate'] = (365 - df['Availability 365']) * 100 / 365
        df_occupancy = df.groupby('Last Scraped')['Occupancy Rate'].mean().reset_index()
        fig_occupancy_rate_line = px.line(df_occupancy, x='Last Scraped', y='Occupancy Rate',
                                    title="Occupancy Rate Over Time",
                                    labels={'Last Scraped': 'Date', 'Occupancy Rate': 'Occupancy Rate (%)'})
        st.plotly_chart(fig_occupancy_rate_line)

    with col2:
    # Demand Fluctuations
        df_demand = df.groupby('Last Scraped').agg({
            'Availability 30': 'mean',
            'Availability 60': 'mean',
            'Availability 90': 'mean',
            'Availability 365': 'mean'
        }).reset_index()
        fig_demand_fluctuation_line = px.line(df_demand, x='Last Scraped', 
                                        y=['Availability 30', 'Availability 60', 'Availability 90', 
                                           'Availability 365'],
                                        title=" Demand Fluctuations Over Time",
                                        labels={'Last Scraped': 'Date', 'value': 'Availability (Days)'},
                                        color_discrete_map={
                                            'Availability 30': 'blue', 
                                            'Availability 60': 'green',
                                            'Availability 90': 'red',
                                            'Availability 365': 'violet'})
        st.plotly_chart(fig_demand_fluctuation_line)
    
    # Availabilty Info
    col1, col2 = st.columns(2)
    with col1:
        country = st.selectbox('**Select the Country**', sorted(df['Country'].unique()))
    with col2:
        availability = st.selectbox('**Select the Availability Days**', 
                                    ['30 Days','60 Days','90 Days','365 Days']) 
    if availability == '30 Days':
        df_avg_avail = df[df['Country'] == country]
        df_avg_avail = df_avg_avail.groupby(['Room Type','Property Type'])['Availability 30'].mean().reset_index()

        fig_avg_avail_bar = px.bar(df_avg_avail, x='Property Type', y='Availability 30',
                                    title="Average Availability by Property Type", color='Room Type',
                                    labels={'Availability 30': 'Average Availability (30 Days)'})
        st.plotly_chart(fig_avg_avail_bar)

    elif availability == '60 Days':
        df_avg_avail = df[df['Country'] == country]
        df_avg_avail = df_avg_avail.groupby(['Room Type','Property Type'])['Availability 60'].mean().reset_index()

        fig_avg_avail_bar = px.bar(df_avg_avail, x='Property Type', y='Availability 60',
                                    title="Average Availability by Property Type", color='Room Type',
                                    labels={'Availability 60': 'Average Availability (60 Days)'})
        st.plotly_chart(fig_avg_avail_bar)

    elif availability == '90 Days':
        df_avg_avail = df[df['Country'] == country]
        df_avg_avail = df_avg_avail.groupby(['Room Type','Property Type'])['Availability 90'].mean().reset_index()

        fig_avg_avail_bar = px.bar(df_avg_avail, x='Property Type', y='Availability 90',
                                    title="Average Availability by Property Type", color='Room Type',
                                    labels={'Availability 90': 'Average Availability (90 Days)'})
        st.plotly_chart(fig_avg_avail_bar)

    elif availability == '365 Days':
        df_avg_avail = df[df['Country'] == country]
        df_avg_avail = df_avg_avail.groupby(['Room Type','Property Type'])['Availability 365'].mean().reset_index()

        fig_avg_avail_bar = px.bar(df_avg_avail, x='Property Type', y='Availability 365',
                                    title="Average Availability by Property Type", color='Room Type',
                                    labels={'Availability 365': 'Average Availability (365 Days)'})
        st.plotly_chart(fig_avg_avail_bar)

# Location-Based Insights
elif selected_tab == 'Location-Based Insights':
    st.header("Location-Based Insights")

    cols1,cols2,cols3 = st.columns(3)
    with cols1:
        country = st.selectbox('Select a Country',sorted(df['Country'].unique()))
        df1 = df[(df['Country'] == country)]
    with cols2:
        df1['Market'] = df1['Market'].fillna("Not Specified") 
        city = st.selectbox('Select a City',sorted(df1['Market'].unique()))
        df1 = df1[(df1['Market'] == city)]
    with cols3:
        room = st.selectbox('Select a Room Type',sorted(df1['Room Type'].unique()))
        df1 = df1[(df1['Room Type'] == room)]
    
    col1,col2 = st.columns(2)
    with col1:
        # Top 10 Hosts by Lowest Price in the selected city 
        try:
            agg_result_low = col.aggregate(
                [
                    {
                        "$match": {
                            "address.country": country,
                            "address.market": city,
                            "room_type": room
                        }
                    },
                    {
                        "$project": {
                            "host.host_name": 1,
                            "price": 1
                        }
                    },
                    {
                        "$group": {
                            "_id": "$host.host_name",
                            "price": {"$avg": "$price"},
                        }
                    },
                    {
                        "$sort": {
                            "price": 1
                        }
                    },
                    {
                        "$limit": 10
                    }
                ]
            )
            data_low = []
            for i in agg_result_low:
                data_low.append(i)
            top_hosts_rating_city_low = pd.DataFrame(data_low)
            top_hosts_rating_city_low = top_hosts_rating_city_low.sort_values('price',ascending=False)

            fig_top_rating_city_low = px.bar(top_hosts_rating_city_low, 
                                            x='price', 
                                            y='_id', 
                                            title=f"Top 10 Hosts by Lowest Price in {city}", 
                                            color='price', 
                                            color_continuous_scale='Peach',
                                            labels={'_id':'Host','price':'Price ($)'},
                                            height=350, width=550)
            st.plotly_chart(fig_top_rating_city_low)
        except:
            st.error('Data Not Available')
        
    with col2:
        # Top 10 Hosts by Highest Price in the selected city 
        try:   
            agg_result_high = col.aggregate(
                [
                    {
                        "$match": {
                            "address.country": country,
                            "address.market": city,
                            "room_type": room
                        }
                    },
                    {
                        "$project": {
                            "host.host_name": 1,
                            "price": 1
                        }
                    },
                    {
                        "$group": {
                            "_id": "$host.host_name",
                            "price": {"$avg": "$price"},
                        }
                    },
                    {
                        "$sort": {
                            "price": -1
                        }
                    },
                    {
                        "$limit": 10
                    }
                ]
            )
            data_high = []
            for i in agg_result_high:
                data_high.append(i)
            top_hosts_rating_city_high = pd.DataFrame(data_high)
            top_hosts_rating_city_high = top_hosts_rating_city_high.sort_values('price',ascending=True)

            fig_top_rating_city_high = px.bar(top_hosts_rating_city_high, 
                                            x='price', 
                                            y='_id', 
                                            title=f"Top 10 Hosts by Highest Price in {city}", 
                                            color='price', 
                                            color_continuous_scale='Peach',
                                            labels={'_id':'Host','price':'Price ($)'},
                                            height=350, width=550)
            st.plotly_chart(fig_top_rating_city_high)
        except:
            st.error('Data Not Available')

    # Top 20 Hosts by Review Scores Rating in the selected city
    try:   
        top_hosts_rating_city = df1.groupby(['Host Name'])[['Review Scores Rating']].mean().reset_index()
        top_hosts_rating_city = top_hosts_rating_city.sort_values('Review Scores Rating', ascending=False).head(20)

        fig_top_rating_city = px.bar(top_hosts_rating_city, 
                                    x='Review Scores Rating', 
                                    y='Host Name', 
                                    title=f"Top 20 Hosts by Review Scores Rating in {city}", 
                                    color='Review Scores Rating', 
                                    color_continuous_scale='Peach',
                                    height=500, width=900)
        st.plotly_chart(fig_top_rating_city)
    except:
        st.error('Data Not Available')