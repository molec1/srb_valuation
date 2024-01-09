import pickle
import datetime

import numpy as np
import pandas as pd

from model_train import features_encode

def complex_func(f):
    return pickle.load(open(f, 'rb'))

print(datetime.datetime.now(), 'sale data is loaded')
model_path = '4zida/apartments/sale'
reg = complex_func(model_path+'/model.sav')

property = pd.read_csv('banjska.csv')
property = property.loc[property.broj=='22']

property['city'] = 'Beograd'
property['region'] = 'Zvezdara opština'
property['landmark'] = 'Đeram'
property['street'] = 'Banjska'

property['Plac'] = '0'
property['land_area'] = 0

val_date = datetime.datetime.now()
property['date_update'] = val_date

print(property.T)

property_enc = features_encode(property)
print(datetime.datetime.now(), 'encoding finished')

model_cols = reg.feature_names_in_
add_sale_cols = list(set(model_cols) - set(property_enc.columns))
add_sale_df = pd.DataFrame({key: 0 for key in add_sale_cols}, index=[1])
property_enc['one'] = 1
add_sale_df['one'] = 1
property_enc = pd.merge(property_enc, add_sale_df, on='one')
print(datetime.datetime.now(), 'columns are added')
property.T.to_csv('test.csv')

property_enc['Price per m2'] = np.expm1(reg.predict(property_enc[model_cols])).round(0)
property['Price per m2'] = property_enc['Price per m2']
property['valuation'] = property['Price per m2'] * property['area'].round()

print(np.expm1(reg.predict(property_enc[model_cols])).round(0))
print(datetime.datetime.now(), 'sale valuated')

