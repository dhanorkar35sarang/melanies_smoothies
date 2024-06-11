import streamlit as st
import pandas as pd
import requests

# Set up the app title and description
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Add a text input for the smoothie name
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Connect to Snowflake and retrieve fruit options
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.sql("SELECT FRUIT_NAME, SEARCH_ON FROM smoothies.public.fruit_options").collect()

# Convert Snowpark DataFrame to Pandas DataFrame and rename columns
pd_df = pd.DataFrame(my_dataframe, columns=['FRUIT_NAME', 'SEARCH_ON'])

# Add the new SEARCH_ON column to the DataFrame
pd_df['SEARCH_ON'] = pd_df['SEARCH_ON'].apply(lambda x: fruit_name_mapping.get(x, x))

st.dataframe(data=pd_df, use_container_width=True)

# Add a multiselect for choosing smoothie ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# Process the selected ingredients and generate the SQL insert statement
if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen + ' Nutrition Information')
        
        # Get the "Search On" value
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')
        
        try:
            fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
            fruityvice_response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
            
            fv_df = pd.DataFrame([fruityvice_response.json()])
            st.dataframe(data=fv_df, use_container_width=True)
        except requests.exceptions.HTTPError as http_err:
            st.write(f"HTTP error occurred for {fruit_chosen}: {http_err}")
        except Exception as err:
            st.write(f"Other error occurred for {fruit_chosen}: {err}")
    
    my_insert_stmt = f"""INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                        VALUES ('{ingredients_string.strip()}', '{name_on_order}')"""
    
    # Add a button to submit the order
    time_to_insert = st.button('Submit Order')
    
    # Execute the SQL insert statement and display a success message
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your smoothie is ordered, {name_on_order}!', icon="✅")
