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
        
        # Check if the search_on value is valid
        if search_on and isinstance(search_on, str) and search_on.strip():
            st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')
            
            fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
            
            if fruityvice_response.status_code == 200:
                fv_df = pd.DataFrame(fruityvice_response.json())
                st.dataframe(data=fv_df, use_container_width=True)
            else:
                st.write(f"Could not fetch data for {fruit_chosen}.")
        else:
            st.write(f"Invalid search value for {fruit_chosen}. Please update the SEARCH_ON column.")
    
    my_insert_stmt = f"""INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                        VALUES ('{ingredients_string.strip()}', '{name_on_order}')"""
    
    # Step 6: Add a button to submit the order
    time_to_insert = st.button('Submit Order')
    
    # Step 7: Execute the SQL insert statement and display a success message
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your smoothie is ordered, {name_on_order}!', icon="✅")
