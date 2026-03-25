# parse excel file into an array 
import pandas
import streamlit as st
import concurrent.futures
import requests

file_path = 'test.xlsx' 

# 0 = first sheet 
excel_df = pandas.read_excel(file_path, 0)
test = excel_df.head()
st.write(test) 

@st.cache_data
# Given a tracking number, ask the beans API for the package details
def get_package_details (tracking_number):
  API_URL_TEMPLATE = "https://isp.beans.ai/enterprise/v1/lists/status_logs?tracking_id={tracking_id}&readable=true&include_item=true"
  url = API_URL_TEMPLATE.format(tracking_id=tracking_number)
  api_key = st.secrets.API_TOKEN
  headers = {"Accept": "application/json",
            "Authorization": api_key}
  response = requests.get(url, headers=headers)
  return response

# Given a tracking number, return the weight
def calculate_weight (tracking_number):
  response = get_package_details(tracking_number)
  response_data = response.json() 
  logs = response_data.get("listItemReadableStatusLogs")
  if logs is None:
    return 0
  else: 
    return int(logs[0]["item"]["dimensions"]["dims"][2]["v"])
  
def calculate_price (weight):
  if weight == 0: 
    return 0
  elif weight < 31:
    return 8
  elif weight < 41:
    return 9
  elif weight < 51:
    return 10 
  elif weight < 61: 
    return 11
  elif weight < 71:
    return 12
  elif weight < 81:
    return 13
  elif weight < 91: 
    return 14
  elif weight < 101: 
    return 15
  elif weight < 111:
    return 17
  elif weight < 121:
    return 19
  elif weight < 131:
    return 21
  elif weight < 141: 
    return 23
  else: 
    return 26 
  
def price_from_tracking_number (tracking_number):
  weight = calculate_weight(tracking_number)
  price = calculate_price(weight)
  return price

if st.button("calculate prices"):
  counter_placeholder = st.empty()
  # Use ThreadPoolExecutor to run multiple API calls in parallel
  with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    numbers_array = test.iloc[:, 0].values
    # map returns results in the same order as input
    prices = executor.map(price_from_tracking_number, numbers_array)
    tracking_price_dict = {
      'tracking number' : numbers_array,
      'prices' : prices
    }
    tracking_price_df = pandas.DataFrame(tracking_price_dict)
    
    st.write(tracking_price_df)

