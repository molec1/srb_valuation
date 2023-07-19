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
path = './4zida/apartments/sale'
df = st.cache_resource(pd.read_parquet)(path+"/valuated.parquet")
print(datetime.datetime.now(), 'sale data is loaded')
reg = complex_func(path+'/model.sav')
print(datetime.datetime.now(), 'model is loaded')

path_rent = './4zida/apartments/rent'
df_rent = st.cache_resource(pd.read_parquet)(path_rent+"/valuated.parquet")
reg_rent = complex_func(path_rent+'/model.sav')
print(datetime.datetime.now(), 'rent data and model are loaded')

property = {}
property['city'] = st.selectbox('City:', df['city'].sort_values().unique(), 4)
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
property['floor_number'] = st.number_input('Floor:', 0, 20, 2)
property['floors'] = st.number_input('Total floors:', 1, 20, 5)
property['parking_places'] = st.number_input('Parking places:', 0, 5)
property['garage_places'] = st.number_input('Garage places:', 0, 5)
property['Stanje'] = st.selectbox('Condition:', df['Stanje'].sort_values().unique(), 2)
property['Uknjiženost'] = st.selectbox('Registered:', df['Uknjiženost'].unique())
property['Grejanje'] = st.selectbox('Heating:', df['Grejanje'].sort_values().unique(), 1)
property['Infrastruktura'] = st.selectbox('Additional:', ['-']+list(df['Infrastruktura'].sort_values().unique()))
property['Tip'] = st.selectbox('Type:', df['Tip'].sort_values().unique(), 6)
property['Lift'] = st.selectbox('Lift:', df['Lift'].sort_values().unique(), 1)
property['Nameštenost'] = st.selectbox('Nameštenost:', df['Nameštenost'].sort_values().unique())

property['date_update'] = datetime.datetime.now()

st.header('Valuation (please enter the area to get it)')

# Filter dataframe
if property['area']>0:
    print(datetime.datetime.now(), 'valuation started')
    property_df = pd.DataFrame(property, index=[1])
    property_enc = features_encode(property_df)
    print(datetime.datetime.now(), 'encoding finished')
    model_cols = reg.feature_names_in_
    model_cols_rent = reg_rent.feature_names_in_
    add_sale_cols = list(set(model_cols)-set(property_enc.columns))
    add_sale_df = pd.DataFrame({key: 0 for key in add_sale_cols}, index=[1])
    property_enc = pd.concat([property_enc, add_sale_df], axis=1)
    add_rent_cols = list(set(model_cols_rent)-set(property_enc.columns))
    add_rent_df = pd.DataFrame({key: 0 for key in add_rent_cols}, index=[1])
    property_enc = pd.concat([property_enc, add_rent_df], axis=1)
    property_enc = property_enc.copy()
    print(datetime.datetime.now(), 'columns are added')

    property_df['Price per m2'] = np.expm1(reg.predict(property_enc[model_cols])).round(1)
    property_df['Price per m2'] = property_df['Price per m2'].round(3-len(str(property_df['Price per m2'].apply(int))))
    property_df['Valuated price'] = property_df['Price per m2'] * property_df['area'].round()
    print(datetime.datetime.now(), 'sale valuated')

    property_df['Rent price per m2'] = np.expm1(reg_rent.predict(property_enc[model_cols_rent])).round(1)
    property_df['Rent price per m2'] = property_df['Rent price per m2'].round(3-len(str(property_df['Rent price per m2'].apply(int))))
    property_df['Valuated rent price'] = property_df['Rent price per m2'] * property_df['area'].round()
    print(datetime.datetime.now(), 'rent valuated')
    # write dataframe to screen

    st.write(property_df[['Price per m2', 'Valuated price', 'Rent price per m2', 'Valuated rent price']])
    print(datetime.datetime.now(), 'valuation finished')

    df['Updated'] = df['date_update']
    df['Price per m2'] = df['ppm'].round(-1)

    st.header('Some sale offers')
    st.write(df.loc[
                 (df['city'] == property['city']) &
                 (df['region'] == property['region']) &
                 (df['landmark'] == property['landmark'])
             ,
             ['Updated', 'rooms', 'area', 'street', 'Price per m2', 'price',
              'Grejanje', 'Stanje', 'parking_places', 'garage_places', 'link']
             ])

    st.header('Some rent offers')
    df_rent['Updated'] = df_rent['date_update']
    df_rent['Rent price per m2'] = df_rent['ppm'].round(1)
    st.write(df_rent.loc[
                 (df_rent['city'] == property['city']) &
                 (df_rent['region'] == property['region']) &
                 (df_rent['landmark'] == property['landmark'])
             ,
             ['Updated', 'rooms', 'area', 'street', 'Rent price per m2', 'price',
              'Grejanje', 'Stanje', 'parking_places', 'garage_places', 'link']
             ])
    print(datetime.datetime.now(), 'dfs showed')


st.header('Some plots')
df['%'] = df.ppm / df.ppm.mean() * 100
def plot_str_graph(df, x):
    fig = px.scatter(df.groupby([x], as_index=False, dropna=False)['%'].mean(), x=x, y='%')
    # Plot!
    st.plotly_chart(fig)

for x in ['city', 'date_update', 'rooms', 'Grejanje', 'Stanje', 'floor_number', 'Lift', 'Tip',
          'Uknjiženost', 'parking_places', 'garage_places', 'Godina izgradnje']:
    plot_str_graph(df, x)

print(datetime.datetime.now(), 'finished')
print('----------------------------------------------------------')