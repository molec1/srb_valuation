import pickle
import plotly_express as px

import numpy as np
import pandas as pd
import streamlit as st

from model_train import features_encode

path = './4zida/apartments/sale'
df = st.cache_resource(pd.read_parquet)(path+"/prepared.parquet")
@st.cache_resource
def complex_func(f):
    return pickle.load(open(f, 'rb'))
# Won't run again and again.
reg = complex_func(path+'/model.sav')


property = {}
property['city'] = st.selectbox('City:', df['city'].unique())
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
property['Stanje'] = st.selectbox('Condition:', df['Stanje'].sort_values().unique(), 1)
property['Uknjiženost'] = st.selectbox('Registered:', df['Uknjiženost'].unique())
property['Grejanje'] = st.selectbox('Heating:', df['Grejanje'].sort_values().unique(), 1)
property['Infrastruktura'] = st.selectbox('Additional:', df['Infrastruktura'].unique())
property['Tip'] = st.selectbox('Type:', df['Tip'].sort_values().unique(), 6)
property['Lift'] = st.selectbox('Lift:', df['Lift'].unique())

# Filter dataframe
if property['area']>0:
    property_df = pd.DataFrame(property, index=[1])
    property_enc = features_encode(property_df)
    model_cols = reg.feature_names_in_
    property_enc[list(set(model_cols)-set(property_enc.columns))] = 0
    property_enc = property_enc.copy()

    property_df['Price per m2'] = np.expm1(reg.predict(property_enc[model_cols])).round(1)
    property_df['Price per m2'] = property_df['Price per m2'].round(len(str(int(property_df['Price per m2'])))-3)
    property_df['Valuated price'] = property_df['Price per m2'] * property_df['area'].round()
    # write dataframe to screen
    st.write(property_df[['Price per m2', 'Valuated price']])

    df['Updated'] = df['date_update']
    df['Price per m2'] = df['ppm'].round(-1)
    st.write(df.loc[
                 (df['city'] == property['city']) &
                 (df['region'] == property['region']) &
                 (df['landmark'] == property['landmark'])
             ,
             ['Updated', 'rooms', 'area', 'street', 'Price per m2', 'price',
              'Grejanje', 'Stanje', 'parking_places', 'garage_places', 'link']
             ])

def plot_str_graph(x):
    fig = px.scatter(df.groupby([x], as_index=False, dropna=False).ppm.mean(), x =x, y='ppm')
    # Plot!
    st.plotly_chart(fig)

for x in ['city', 'date_update', 'rooms', 'Grejanje', 'Stanje', 'floor_number', 'Lift', 'Tip',
          'Uknjiženost', 'parking_places', 'garage_places', 'Godina izgradnje']:
    plot_str_graph(x)