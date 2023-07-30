import pickle
import plotly_express as px
import datetime

import numpy as np
import pandas as pd
import streamlit as st


print(datetime.datetime.now(), 'start')
path = '4zida/apartments/sale'
df = st.cache_resource(pd.read_parquet)(path+"/valuated.parquet")
print(datetime.datetime.now(), 'sale data is loaded')

path_rent = '4zida/apartments/rent'
df_rent = st.cache_resource(pd.read_parquet)(path_rent+"/valuated.parquet")
print(datetime.datetime.now(), 'rent data and model are loaded')

property = {}
property['city'] = st.selectbox('City:', ['-']+list(df['city'].sort_values().unique()))
property['region'] = st.selectbox('Region:', ['-']+list(df.loc[df['city'] == property['city'], 'region'].sort_values().unique()))
property['landmark'] = st.selectbox('Landmark:', ['-']+list(df.loc[(df['city'] == property['city'])&
                                                        (df['region'] == property['region']), \
    'landmark'].sort_values().unique()))
property['street'] = st.selectbox('Street:', ['-']+list(df.loc[(df['city'] == property['city'])&
                                                    (df['region'] == property['region'])&
                                                    (df['landmark'] == property['landmark']), \
    'street'].sort_values().unique()))
property['rooms'] = st.selectbox('Rooms:', ['-']+list(df['rooms'].sort_values().unique()))
property['Stanje'] = st.selectbox('Condition:', ['-']+list(df['Stanje'].sort_values().unique()))
property['Uknjiženost'] = st.selectbox('Registered:', ['-']+list(df['Uknjiženost'].unique()))
property['Grejanje'] = st.selectbox('Heating:', ['-']+list(df['Grejanje'].sort_values().unique()))
property['Infrastruktura'] = st.selectbox('Additional:', ['-']+list(df['Infrastruktura'].sort_values().unique()))
property['Tip'] = st.selectbox('Type:', ['-']+list(df['Tip'].sort_values().unique()))
property['Lift'] = st.selectbox('Lift:', ['-']+list(df['Lift'].sort_values().unique()))
property['Nameštenost'] = st.selectbox('Nameštenost:', ['-']+list(df['Nameštenost'].sort_values().unique()))

df['%'] = df.ppm / df.ppm.mean() * 100

temp_df = df.copy()
for prop in property:
    if property[prop]!='-':
        temp_df = temp_df[temp_df[prop]==property[prop]]

temp_rent_df = df_rent.copy()
for prop in property:
    if property[prop]!='-':
        temp_rent_df = temp_rent_df[temp_rent_df[prop]==property[prop]]

def plot_str_graph(df, x):
    fig = px.scatter(df.groupby([x], as_index=False, dropna=False)['%'].mean(), x=x, y='%')
    # Plot!
    st.plotly_chart(fig)

st.header('Sale')
for x in ['city', 'date_update', 'rooms', 'Grejanje', 'Stanje', 'floor_number', 'Lift', 'Tip',
          'Uknjiženost', 'parking_places', 'garage_places', 'Godina izgradnje']:
    plot_str_graph(temp_df, x)

st.header('Rent')
for x in ['city', 'date_update', 'rooms', 'Grejanje', 'Stanje', 'floor_number', 'Lift', 'Tip',
          'Uknjiženost', 'parking_places', 'garage_places', 'Godina izgradnje']:
    plot_str_graph(temp_rent_df, x)

print(datetime.datetime.now(), 'finished')
print('----------------------------------------------------------')