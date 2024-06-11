import streamlit as st
import pandas as pd
from snowflake.snowpark.functions import col
import requests

# Step 1: Set up the app title and description
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Step 2: Add a text input for the smoothie name
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Step 3: Connect to Snowflake and retrieve fruit options
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.sql("SELECT FRUIT_NAME, SEARCH_ON FROM smoothies.public.fruit_options").collect()

# Convert Snowpark DataFrame to Pandas DataFrame
pd_df = pd.DataFrame(my_dataframe)
st.dataframe(data=pd_df, use_container_width=True)

# Step 4: Add a multiselect for choosing smoothie ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# Step 5: Process the selected ingredients and generate the SQL insert statement
if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen + ' Nutrition Information')
        
        # Get the "Search On" value
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')

        # Ensure the search_on variable is a string
        if isinstance(search_on, str) and search_on:
            fruityvice_response = requests
