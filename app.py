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
  
# calculates one price with one weight based off of the fimile rate card 
def calculate_price (weight):
  base_price = 0
  if weight == 0: 
    base_price = 0
  elif weight < 31:
    base_price = 8
  elif weight < 41:
    base_price = 9
  elif weight < 51:
    base_price = 10 
  elif weight < 61: 
    base_price = 11
  elif weight < 71:
    base_price = 12
  elif weight < 81:
    base_price = 13
  elif weight < 91: 
    base_price = 14
  elif weight < 101: 
    base_price = 15
  elif weight < 111:
    base_price = 17
  elif weight < 121:
    base_price =  19
  elif weight < 131:
    base_price = 21
  elif weight < 141: 
    base_price = 23
  else: 
    base_price = 26 
  return base_price + 2
  
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
  st.download_button(
    label="Download excel",
    data=tracking_price_df,
    file_name="tracking_and_prices.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    icon=":material/download:",
)

# for testing purposes. delete later
file_path = 'test.xlsx' 
# 0 = first sheet 
excel_df = pandas.read_excel(file_path, 0)
test = excel_df.head()

if st.button("test with data"):
  test_price_df = calculate_all_prices(test)
  st.write(test_price_df)

