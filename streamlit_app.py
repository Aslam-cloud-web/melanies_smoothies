# Import Python packages
import streamlit as st
import os
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# Display the app title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

st.write("Choose the fruits you want in your custom smoothie!")

# Get the customer's name
name_on_order = st.text_input("Name on smoothie:")
st.write("The name of your smoothie will be", name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Get available fruits from Snowflake (Update this line to include SEARCH_ON)
my_dataframe = (
    session.table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)
# Convert the Snowpark DataFrame to a Pandas DataFrame so we can use it
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)
st.stop()  


# Let the customer select up to 5 fruits
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df,
    max_selections=5
)

# Get nutrition information for each selected fruit
if ingredients_list:
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "
        
        # Add these two lines to get the search value
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')
        
        # Display a heading for the selected fruit
        st.subheader(fruit_chosen + " Nutrition Information")
        
        # Call the SmoothieFroot API using 'search_on' instead of 'fruit_chosen'
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)

        # Display the returned data as a table
        if smoothiefroot_response.ok:
            sf_df = st.dataframe(
                data=smoothiefroot_response.json(),
                use_container_width=True
            )
        else:
            st.error(
                f"Could not retrieve data for {fruit_chosen}. "
                f"Status code: {smoothiefroot_response.status_code}"
            )

    st.write("Selected ingredients:", ingredients_string)

# Prepare the SQL insert statement
my_insert_stmt = f"""
INSERT INTO smoothies.public.orders
(ingredients, name_on_order)
VALUES ('{ingredients_string}', '{name_on_order}')
"""

st.write(my_insert_stmt)

# Submit the smoothie order
time_to_insert = st.button("Submit order")

if time_to_insert:
    session.sql(my_insert_stmt).collect()
    st.success("Your Smoothie is ordered!", icon="✅")
