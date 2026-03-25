import pandas
import streamlit as st
import concurrent.futures
import requests

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
  
# calculates one price with one weight 
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
  
# small function for executor.map to use 
def price_from_tracking_number (tracking_number):
  weight = calculate_weight(tracking_number)
  price = calculate_price(weight)
  return price

# Using a dataframe of tracking numbers, calculate the prices and return another dataframe with the prices appended to it 
def calculate_all_prices (tracking_df):
  with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    tracking_array = tracking_df.iloc[:, 0].values
    # map returns results in the same order as input
    prices = executor.map(price_from_tracking_number, tracking_array)
    tracking_price_dict = {
      'tracking number' : tracking_array,
      'prices' : prices
    }
    tracking_price_df = pandas.DataFrame(tracking_price_dict)
    return tracking_price_df

tracking_excel = st.file_uploader("drop an excel file here")
if tracking_excel is not None:
  tracking_df = pandas.read_excel(tracking_excel)
  tracking_price_df = calculate_all_prices(tracking_df)
  st.write(tracking_price_df)

# for testing purposes. delete later
file_path = 'test.xlsx' 
# 0 = first sheet 
excel_df = pandas.read_excel(file_path, 0)
test = excel_df.head()

if st.button("test with data"):
  test_price_df = calculate_all_prices(test)
  st.write(test_price_df)

