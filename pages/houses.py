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
path = '4zida/houses/sale'
df = st.cache_resource(pd.read_parquet)(path+"/valuated.parquet")
df['Plac'] = df['land_area']/100
print(datetime.datetime.now(), 'sale data is loaded')
reg = complex_func(path+'/model.sav')
conf_reg = complex_func(path+'/confidence_model.sav')
print(datetime.datetime.now(), 'model is loaded')

property = {}
property['city'] = st.selectbox('City:', df['city'].sort_values().unique(), 13)
property['region'] = st.selectbox('Region:', df.loc[df['city'] == property['city'], 'region'].sort_values().unique())
property['landmark'] = st.selectbox('Landmark:', df.loc[(df['city'] == property['city'])&
                                                        (df['region'] == property['region']), \
    'landmark'].sort_values().unique())
property['street'] = st.selectbox('Street:', df.loc[(df['city'] == property['city'])&
                                                    (df['region'] == property['region'])&
                                                    (df['landmark'] == property['landmark']), \
    'street'].sort_values().unique())
property['rooms'] = st.selectbox('Rooms:', df['rooms'].sort_values().unique())
property['area'] = st.number_input('Area:', 0, 200)
property['Godina izgradnje'] = st.number_input('Building year:', 1850, 2040, 2010, 5)
property['floor_number'] = 0
property['Plac'] = st.number_input('Plac, a:', 0, 20)
property['land_area'] = property['Plac']*100
property['floors'] = st.number_input('Total floors:', 1, 5, 2)
property['parking_places'] = st.number_input('Parking places:', 0, 5)
property['garage_places'] = st.number_input('Garage places:', 0, 5)
property['Stanje'] = st.selectbox('Condition:', df['Stanje'].sort_values().unique(), 2)
property['Uknjiženost'] = st.selectbox('Registered:', df['Uknjiženost'].unique())
property['Grejanje'] = st.selectbox('Heating:', df['Grejanje'].sort_values().unique(), 1)
infr_options = df['Infrastruktura'].unique()
infr_options = [x.split(', ') for x in infr_options]
infr_options = [j for i in infr_options for j in i]
infr_options = list(set(infr_options))
infr_options.sort()
property['Infrastruktura'] = st.multiselect('Additional:', infr_options)
property['Tip'] = st.selectbox('Type:', df['Tip'].sort_values().unique(), 6)
property['Lift'] = st.selectbox('Lift:', df['Lift'].sort_values().unique(), 1)
property['Nameštenost'] = st.selectbox('Nameštenost:', df['Nameštenost'].sort_values().unique())

property['date_update'] = datetime.datetime.now()

st.header('Valuation (please enter the area to get it)')

# Filter dataframe
if property['area']>0:
    property['Infrastruktura'] = ', '.join(property['Infrastruktura'])
    print(datetime.datetime.now(), 'valuation started')
    property_df = pd.DataFrame(property, index=[1])
    property_enc = features_encode(property_df)
    print(datetime.datetime.now(), 'encoding finished')
    model_cols = reg.feature_names_in_
    add_sale_cols = list(set(model_cols)-set(property_enc.columns))
    add_sale_df = pd.DataFrame({key: 0 for key in add_sale_cols}, index=[1])
    property_enc = pd.concat([property_enc, add_sale_df], axis=1)
    property_enc = property_enc.copy()
    print(datetime.datetime.now(), 'columns are added')

    property_df['Price per m2'] = np.expm1(reg.predict(property_enc[model_cols])).round(-1)
    property_df['conf_coeff'] = np.exp(conf_reg.predict(property_enc[model_cols]))
    property_df['Valuated price'] = property_df['Price per m2'] * property_df['area'].round()
    property_df['Low'] = (property_df['Valuated price']/property_df['conf_coeff'] ).round(-2)
    property_df['High'] = (property_df['Valuated price']*property_df['conf_coeff'] ).round(-2)
    print(datetime.datetime.now(), 'sale valuated')
    # write dataframe to screen

    st.write(property_df[['Price per m2', 'Valuated price', 'Low', 'High']])
    print(datetime.datetime.now(), 'valuation finished')

    df['Updated'] = df['date_update']
    df['Price per m2'] = df['ppm'].round(-1)

    st.header('Some sale offers')
    st.write(df.loc[
                 (df['city'] == property['city']) &
                 (df['region'] == property['region']) &
                 (df['landmark'] == property['landmark'])
             ,
             ['Updated', 'rooms', 'area', 'Plac', 'street', 'Price per m2', 'price',
              'Grejanje', 'Stanje', 'garage_places', 'link']
             ])

    print(datetime.datetime.now(), 'dfs showed')
    
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
    trend_df_enc = trend_df_enc.fillna(0).copy()
    trend_df['Sale price'] = (np.expm1(reg.predict(trend_df_enc[model_cols]))*trend_df['area']).round(-3)
    fig = px.scatter(trend_df.groupby(['date_update'], as_index=False, dropna=False)['Sale price'].mean(), x='date_update', y='Sale price')
    # Plot!
    st.plotly_chart(fig)


st.header('Some plots')
df['%'] = df.ppm / df.ppm.mean() * 100
def plot_str_graph(df, x):
    fig = px.scatter(df.groupby([x], as_index=False, dropna=False)['%'].mean(), x=x, y='%')
    # Plot!
    st.plotly_chart(fig)

for x in ['city', 'date_update', 'rooms', 'area', 'Plac', 'Grejanje', 'Stanje', 'floor_number', 
          'Lift', 'Tip', 'Uknjiženost', 'parking_places', 'garage_places', 'Godina izgradnje']:
    plot_str_graph(df, x)

print(datetime.datetime.now(), 'finished')
print('----------------------------------------------------------')
