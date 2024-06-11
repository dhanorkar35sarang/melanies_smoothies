# Import python packages
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

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)

# Step 4: Add a multiselect for choosing smoothie ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:', 
    pd_df['FRUIT_NAME'],
    max_selections=5
)

# Step 5: Process the selected ingredients and generate the SQL insert statement
if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
        st.write(fruityvice_response.json())
    
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    # Step 6: Add a button to submit the order
    time_to_insert = st.button('Submit Order')
    
    # Step 7: Execute the SQL insert statement and display a success message
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your smoothie is ordered, {name_on_order}!', icon="✅")
