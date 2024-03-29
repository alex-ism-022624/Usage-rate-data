# Imported libraries
import pandas as pd
pd.set_option("display.max_rows", 100000,"display.max_columns", 100)
import gspread
import requests
import json

# Collect data from metabase by calling API

metabase_header1 = {'X-Metabase-Session': 'caf8be61-25ff-4e08-9d54-9831fbdb473e', 'Content-Type': 'application/x-www-form-urlencoded'}
url1 = 'https://metabase.aloninja.com/api/card/163/query/json'
_r1 = requests.post(url=url1, headers=metabase_header1)
usage1 = pd.DataFrame.from_dict(_r1.json())

metabase_header2 = {'X-Metabase-Session': '1b43e9b5-b2a9-4d6a-a7e1-089abd1542de', 'Content-Type': 'application/x-www-form-urlencoded'}
url2 = 'https://metabase.ninjavan.co/api/card/45838/query/json'
_r2 = requests.post(url=url2, headers=metabase_header2)
usage2 = pd.DataFrame.from_dict(_r2.json())


metabase_header3 = {'X-Metabase-Session': '1b43e9b5-b2a9-4d6a-a7e1-089abd1542de', 'Content-Type': 'application/x-www-form-urlencoded'}
url3 = 'https://metabase.ninjavan.co/api/card/48884/query/json'
_r3 = requests.post(url=url3, headers=metabase_header3)
usage3 = pd.DataFrame.from_dict(_r3.json())

 
# Transforming data

## Collect data from a googlesheet
## Turning data into a dataframe by using pandas library, also execute some transformation practice such as rename columns, merge tables, drop columns, replace values, and summarize data.

whitelisted_rider = gc.open_by_key ('1SW0VPEhJ_FVw-ryiTx1pSYT7-VfV4xjI5-zsc7hjbMI')

whitelisted_rider_data = pd.DataFrame(whitelisted_rider.worksheet('Usage').get('A2:G'))

whitelisted_rider_data.columns = ['STT','Note','last_digits_contact','rider_name','rider_id','hub_name','region']

whitelisted_rider_data['last_digits_contact'] = whitelisted_rider_data['last_digits_contact'].str.extract(r'(\d{8}$)')

adoption1 = pd.merge(whitelisted_rider_data, usage1, how = "left", on = ["last_digits_contact"])

adoption2 = pd.merge(whitelisted_rider_data, usage1, how = "inner", on = ["last_digits_contact"])

adoption2['use_app_check'] = 1

adoption2 = adoption2[['last_digits_contact','use_app_check']]

adoption3 = pd.merge(adoption1, adoption2, how = "left", on = ["last_digits_contact"])

adoption3['use_app_check'] = adoption3['use_app_check'].fillna(0)

adoption3 = adoption3.drop(['attempt_with_app','attempt_date'], axis=1)

adoption3.fillna('', inplace=True)

adoption3.drop_duplicates(inplace=True)

adoption4 = adoption3.groupby(['region','hub_name','rider_name'], as_index = False).agg({'rider_id': 'count','use_app_check' : 'sum'})


usage_combine = pd.merge(usage2, usage1, how = "left", on = ["last_digits_contact", "attempt_date"])

usage_combine_final = pd.merge(usage_combine, usage3, how = "left", on = ["last_digits_contact", "attempt_date"])

usage_combine_final['total_attempted_order'] = usage_combine_final['delivery_attempted_order'] + usage_combine_final['pickup_attempted_order']

usage_combine_final.fillna('', inplace=True)


# Export data into google sheet

raw_data_sheet = gc.open_by_key('1QHRRcMeCE33TXT7jmtXZR48vsolm5zAA74RTitlxWTs')

raw_data_output = raw_data_sheet.sheet1

raw_data_output.update('M1',[adoption4.columns.tolist()] + adoption4.values.tolist())

raw_data_output.update('A1',[usage_combine_final.columns.tolist()] + usage_combine_final.values.tolist())
