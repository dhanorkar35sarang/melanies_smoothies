# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Step 1: Set up the app title and description
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Step 2: Add a text input for the smoothie name
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Step 3: Connect to Snowflake and retrieve fruit options
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.sql("SELECT FRUIT_NAME FROM smoothies.public.fruit_options").collect()
st.dataframe(data=my_dataframe, use_container_width=True)

# Step 4: Add a multiselect for choosing smoothie ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    ['Dragon Fruit', 'Guava', 'Jackfruit', 'Elderberries', 'Kiwi'],
    max_selections=5
)

# Step 5: Process the selected ingredients and generate the SQL insert statement
if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
    
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""
    
    # Step 6: Add a button to submit the order
    time_to_insert = st.button('Submit Order')
    
    # Step 7: Execute the SQL insert statement and display a success message
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your smoothie is ordered, {name_on_order}!', icon="✅")

import requests
fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
st.text(fruityvice_response)

