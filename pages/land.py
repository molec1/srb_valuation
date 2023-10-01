import pickle
import plotly_express as px
import datetime

import numpy as np
import pandas as pd
import streamlit as st

from model_train import features_encode
@st.cache_resource
def complex_func(f):
    return pickle.load(open(f, 'rb'))

print(datetime.datetime.now(), 'start')
path = '4zida/land/sale'
df = st.cache_resource(pd.read_parquet)(path+"/valuated.parquet")
print(datetime.datetime.now(), 'sale data is loaded')
reg = complex_func(path+'/model.sav')
conf_reg = complex_func(path+'/confidence_model.sav')
print(datetime.datetime.now(), 'model is loaded')

property = {}
property['city'] = st.selectbox('City:', df['city'].sort_values().unique(), 5)
property['region'] = st.selectbox('Region:', df.loc[df['city'] == property['city'], 'region'].sort_values().unique())
property['landmark'] = st.selectbox('Landmark:', df.loc[(df['city'] == property['city'])&
                                                        (df['region'] == property['region']), \
    'landmark'].sort_values().unique())
property['street'] = st.selectbox('Street:', df.loc[(df['city'] == property['city'])&
                                                    (df['region'] == property['region'])&
                                                    (df['landmark'] == property['landmark']), \
    'street'].sort_values().unique())
property['area'] = st.number_input('Area (a):', 0, 200)
property['date_update'] = datetime.datetime.now()

st.header('Valuation (please enter the area to get it)')

# Filter dataframe
if property['area']>0:
    print(datetime.datetime.now(), 'valuation started')
    property_df = pd.DataFrame(property, index=[1])
    property_enc = features_encode(property_df)
    print(datetime.datetime.now(), 'encoding finished')
    model_cols = reg.feature_names_in_
    add_sale_cols = list(set(model_cols)-set(property_enc.columns))
    add_sale_df = pd.DataFrame({key: 0 for key in add_sale_cols}, index=[1])
    property_enc = pd.concat([property_enc, add_sale_df], axis=1)
    property_enc = property_enc.replace({'-': 0})
    property_enc = property_enc.copy()
    print(datetime.datetime.now(), 'columns are added')

    pred = reg.predict(property_enc[model_cols])
    property_df['Price per a'] = np.expm1(pred).round(-2)
    property_df['conf_coeff'] = np.exp(conf_reg.predict(property_enc[model_cols]))
    property_df['Valuated price'] = property_df['Price per a'] * property_df['area'].round()
    property_df['Low'] = (property_df['Valuated price']/property_df['conf_coeff'] ).round(-2)
    property_df['High'] = (property_df['Valuated price']*property_df['conf_coeff'] ).round(-2)
    print(datetime.datetime.now(), 'sale valuated')

    # write dataframe to screen

    st.write(property_df[['Price per a', 'Valuated price', 'Low', 'High']])
    print(datetime.datetime.now(), 'valuation finished')

    df['Updated'] = df['date_update']
    df['Price per a'] = df['ppm'].round(-1)

    st.header('Some sale offers')
    st.write(df.loc[
                 (df['city'] == property['city']) &
                 (df['region'] == property['region']) &
                 (df['landmark'] == property['landmark'])
             ,
             ['Updated', 'area', 'street', 'Price per a', 'price',
              'link']
             ])
    
    st.header('Price evolution')
    min_date = datetime.datetime(2022,9,1)
    max_date = datetime.datetime.now()
    
    dates = [min_date + (max_date-min_date)/10*x for x in range(11)]
    df_dates = pd.DataFrame({'date_update': dates})
    trend_df = property_df.drop(columns=['date_update']).merge(df_dates, how='cross')
    trend_df_enc = features_encode(trend_df)
    model_cols = reg.feature_names_in_
    add_sale_cols = list(set(model_cols)-set(trend_df_enc.columns))
    add_sale_df = pd.DataFrame({key: 0 for key in add_sale_cols}, index=[1])
    trend_df_enc = pd.concat([trend_df_enc, add_sale_df], axis=1)
    trend_df_enc = trend_df_enc.replace({'-': 0}).fillna(0).copy()
    trend_df['Sale price'] = (np.expm1(reg.predict(trend_df_enc[model_cols]))*trend_df['area']).round(-3)
    fig = px.scatter(trend_df.groupby(['date_update'], as_index=False, dropna=False)['Sale price'].mean(), x='date_update', y='Sale price')
    # Plot!
    st.plotly_chart(fig)



print(datetime.datetime.now(), 'finished')
print('----------------------------------------------------------')
