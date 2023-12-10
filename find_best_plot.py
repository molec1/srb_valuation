import pickle
import datetime

import numpy as np
import pandas as pd

from model_train import features_encode

def complex_func(f):
    return pickle.load(open(f, 'rb'))

data_path = '4zida/land/sale'
df = pd.read_parquet(data_path+"/prepared.parquet")
print(datetime.datetime.now(), 'sale data is loaded')
model_path = '4zida/apartments/sale'
reg = complex_func(model_path+'/model.sav')
conf_reg = complex_func(model_path+'/confidence_model.sav')
print(datetime.datetime.now(), 'model is loaded')

property = pd.read_csv('banjska.csv')
print(property)

property['Plac'] = '0'
property['land_area'] = 0
property['date_update'] = datetime.datetime.now()

beograd_plots = df[(df.city=='Beograd')&(df.area>3)]  # &(df.date_update>'2023-12-01')
#print(beograd_plots[['city', 'region', 'landmark', 'street', 'price', 'area']])

beograd_plots['one'] = 1
property['one'] = 1
property_df = pd.merge(property, beograd_plots[['city', 'region', 'landmark', 'street', 'one', 'price', 'link']], on='one')
property_enc = features_encode(property_df)
print(datetime.datetime.now(), 'encoding finished')

model_cols = reg.feature_names_in_
add_sale_cols = list(set(model_cols) - set(property_enc.columns))
add_sale_df = pd.DataFrame({key: 0 for key in add_sale_cols}, index=[1])
add_sale_df['one'] = 1
property_enc = pd.merge(property_enc, add_sale_df, on='one')
print(datetime.datetime.now(), 'columns are added')

property_enc['Price per m2'] = np.expm1(reg.predict(property_enc[model_cols])).round(0)
property_df['Price per m2'] = property_enc['Price per m2']
property_df['valuation'] = property_df['Price per m2'] * property_df['area'].round()
property_df.to_csv('test.csv')
res = property_df.groupby('link').agg({'valuation': sum, 'price': max, 'region': max, 'landmark': max, 'street': max})
res['profit'] = res['valuation'] - res['price']
res.to_csv('res.csv')
print(res)
print(datetime.datetime.now(), 'sale valuated')

