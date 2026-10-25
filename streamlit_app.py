# Import python packages
import streamlit as st
import os
import requests
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

st.write(
    """choose the fruits you want in your custom smoothie!"""
) 


name_on_order = st.text_input('Name on smoothie:')
st.write("The name of your smoothie will be ", name_on_order)


cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
# st.dataframe(data=my_dataframe, use_container_width=True)

# Convert the Snowpark dataframe to a Pandas dataframe so we can get a list of fruits
ice_cream_pd = my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    ice_cream_pd
    ,max_selections=5
)
# 1. Define it first with an empty value

# 1. Define it first with an empty value right here:
ingredients_string = ''

if ingredients_list:
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
    st.write(ingredients_string)

# 2. THEN, use it right after in your insert statement
my_insert_stmt = f"""insert into smoothies.public.orders(ingredients, name_on_order) values ('{ingredients_string}', '{name_on_order}')"""
st.write(my_insert_stmt)

time_to_insert = st.button('submit order')

if time_to_insert:
    session.sql(my_insert_stmt).collect()
    st.success('Your Smoothie is ordered!', icon="✅")


smoothiefroot_response = requests.get("[https://my.smoothiefroot.com/api/fruit/watermelon](https://my.smoothiefroot.com/api/fruit/watermelon)")  
st.text(smoothiefroot_response)
