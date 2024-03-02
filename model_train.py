
import pandas as pd
import numpy as np

from sklearn import linear_model
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_percentage_error as mape

import pickle

basic_cols = ['area', 'rooms', 'floor_number', 'parking_places', 'garage_places',
              'price', 'city', 'region', 'landmark',
              'Tip', 'Lift', 'Godina izgradnje', 'street', 'link', 'Stanje',
              'Uknjiženost', 'Grejanje', 'Infrastruktura', 'floors', 'Nameštenost',
              'date_update', 'land_area']


def mdape(y, pred):
    return (np.sqrt(np.square(y-pred))/y).median()

def train(path):
    raw = pd.read_parquet(path+'/prepared.parquet')
    #print(raw.columns)
    df = raw[basic_cols].drop_duplicates().copy()
    df['ppm'] = df['price'] / df['area']
    
    #df = df[df.city=='Beograd']
    
    df = df[df.area.between(20, 200)]
    df['target'] = np.log1p(df['price'] / df['area'])
    print('len df:', len(df), path)
    if len(df[df.land_area>1])>0:
        df = df[(df.land_area>100)&(df.land_area<2_000)]
        print('len df la shrink:', len(df))
    df_nonencoded = df.copy()
    print(df.describe().T)
    df = features_encode(df)
    model_cols = list(df.columns)
    model_cols.remove('region')
    model_cols.remove('landmark')
    model_cols.remove('price')
    model_cols.remove('target')
    model_cols.remove('area')
    model_cols.remove('street')
    model_cols.remove('link')
    model_cols.remove('ppm')
    model_cols.remove('Godina izgradnje')
    model_cols.remove('date_update')
    model_cols.remove('Infrastruktura')
    for m in model_cols:
        if len(df[df[m]!=0])<4:
            #print(m)
            model_cols.remove(m)

    X_train, X_test, y_train, y_test = train_test_split(df[model_cols], df['target'], test_size = 0.33, random_state = 42)

    n = len(X_train)
    cnts = X_train.count().to_dict()
    for c in cnts:
        if cnts[c]<n:
            print(c, cnts[c], n)
    alpha = 0.1
    if path=='4zida/apartments/sale':
        alpha = 0.1
    print('number of features: ', len(model_cols))
    reg = linear_model.Ridge(alpha=alpha, positive=True, tol=0.0000001)
    reg.fit(X_train, y_train)
    #print(reg.intercept_)
    #print(dict(zip(model_cols, reg.coef_)))
    pred_train = reg.predict(X_train)
    pred_test = reg.predict(X_test)
    print('train mape: ', mape(np.expm1(y_train), np.expm1(pred_train)))
    print('test mape: ', mape(np.expm1(y_test), np.expm1(pred_test)))
    print('train mdape: ', mdape(np.expm1(y_train), np.expm1(pred_train)))
    print('test mdape: ', mdape(np.expm1(y_test), np.expm1(pred_test)))

    pickle.dump(reg, open(path+'/model.sav', 'wb'))

    df['pred_lppm'] = reg.predict(df[model_cols])
    df['pred_ppm'] = np.expm1(df['pred_lppm'])
    df_nonencoded['pred_ppm'] = df['pred_ppm']
    df_nonencoded['pred_price'] = df_nonencoded['pred_ppm'] * df_nonencoded['area']
    df_nonencoded.to_parquet(path+'/valuated.parquet')
    
    #df_nonencoded[df_nonencoded.landmark=='Đeram'].to_csv(path+'/valuated_djeram.csv')


    df['abs_err'] = abs(df['pred_lppm']-df['target'])
    #print(df['abs_err'].describe().T)
    conf_reg = linear_model.Ridge(alpha=2)
    conf_reg.fit(df[model_cols], df['abs_err'])
    df['pred_abs_err'] = conf_reg.predict(df[model_cols])
    #print(df['pred_abs_err'].describe().T)
    pickle.dump(conf_reg, open(path+'/confidence_model.sav', 'wb'))



def load_model(path):
    return pickle.load(open(path+'/model.sav', 'rb'))


def features_encode(df_):
    df = df_.copy()
    for b in basic_cols:
        if b not in df.columns:
            df[b] = '-'
    df['parking_places'] = df['parking_places'].replace({'nan': 0.5, '-': 0.})
    df['garage_places'] = df['garage_places'].replace({'nan': 0, '-': 0.})
    df['Stanje'] = df['Stanje'].replace({'nan': '-'}).fillna('-').apply(lambda x: x.strip().title())
    df['Uknjiženost'] = df['Uknjiženost'].replace({'nan': '-'}).fillna('-').apply(lambda x: x.strip())
    df['Grejanje'] = df['Grejanje'].replace({'nan': '-'}).fillna('-').apply(lambda x: x.strip().title())
    df['Infrastruktura'] = df['Infrastruktura'].replace({'nan': '-'}).fillna('-').apply(lambda x: x.strip().title())
    df['Tip'] = df['Tip'].replace({'nan': '-'}).fillna('-').apply(lambda x: x.strip())
    df['Lift'] = df['Lift'].replace({'nan': '-'}).fillna('-').apply(lambda x: x.strip().title())
    df['street'] = df['street'].replace({'nan': '-'}).fillna('-').apply(lambda x: x.strip().title())

    df['trend'] = (df['date_update'] - pd.to_datetime('2022-06-01')).apply(lambda x: x.days)
    df['trend_month'] = df['trend']//30

    if len(df['Godina izgradnje'].unique())>1:
        df['decade'] = df['Godina izgradnje'].apply(lambda x: int(x//10)*10 if not pd.isna(x) else 2020)
    else:
        df['decade'] = 2020
    df['city_region'] = df.city + '_' + df.region
    df['city_landmark'] = df.city_region + '_' + df.landmark
    df['city_street'] = df.city_landmark + '_' + df.street
    df['city_trend_month'] = df['city'] + '_' + df['trend_month'].apply(str)
    df['city_region_trend_month'] = df['city_region'] + '_' + df['trend_month'].apply(str)
    #df['city_landmark_trend_month'] = df['city_landmark'] + '_' + df['trend_month'].apply(str)
    df['anti_area'] = -np.log1p(df['area'])

    df['floors'] = df['floors'].fillna(1).replace({'-': 1})
    df['floor_number'] = df['floor_number'].fillna(0).replace({'-': 0})
    df['top_floor'] = ((df['floors'] - df['floor_number'])<1).apply(lambda x: 1 if x else 0)

    infr_options = df['Infrastruktura'].unique()
    infr_options = [x.split(', ') for x in infr_options]
    infr_options = [j for i in infr_options for j in i]
    infr_options = list(set(infr_options))
    infr_options = ['infr_'+x for x in infr_options]

    df['infr_arr'] = df['Infrastruktura'].apply(lambda x: x.split(', '))
    df[infr_options] = 0
    for infr in infr_options:
        df.loc[df['infr_arr'].apply(lambda x: infr[5:] in x), infr] = 1
    del df['infr_arr']

    #df['region_parking'] = df['city_region']+'_has_parking'
    #df.loc[df['parking_places'].fillna(0)==0, 'region_parking'] = 'no_parking'
    #df['region_garage'] = df['city_region'] + '_has_garage'
    #df.loc[df['garage_places'].fillna(0)==0, 'region_garage'] = 'no_garage'

    df['lift_floor'] = df['Lift'].fillna('no_info').apply(lambda x: 'has_lift_' if 'Ima' in x else 'no_lift_') + df['floor_number'].apply(str)

    df = pd.get_dummies(data=df, columns=['rooms'])
    df = pd.get_dummies(data=df, columns=['floor_number'])
    df = pd.get_dummies(data=df, columns=['decade'])
    df = pd.get_dummies(data=df, columns=['Tip'])
    df = pd.get_dummies(data=df, columns=['Lift'])
    df = pd.get_dummies(data=df, columns=['Stanje'])
    df = pd.get_dummies(data=df, columns=['Uknjiženost'])
    df = pd.get_dummies(data=df, columns=['Grejanje'])
    #df = pd.get_dummies(data=df, columns=['Infrastruktura'])
    df = pd.get_dummies(data=df, columns=['Nameštenost'])
    if len(df[df.land_area.replace({'-': 0})>1])>0:
        df['city_house'] = df['city'].copy()
    df = pd.get_dummies(data=df, columns=['city'])
    df = pd.get_dummies(data=df, columns=['city_region'])
    df = pd.get_dummies(data=df, columns=['city_landmark'])
    df = pd.get_dummies(data=df, columns=['city_street'])
    #df = pd.get_dummies(data=df, columns=['region_parking'])
    #df = pd.get_dummies(data=df, columns=['region_garage'])
    df = pd.get_dummies(data=df, columns=['lift_floor'])
    df = pd.get_dummies(data=df, columns=['trend_month'])
    df = pd.get_dummies(data=df, columns=['city_trend_month'])
    df = pd.get_dummies(data=df, columns=['city_region_trend_month'])
    #df = pd.get_dummies(data=df, columns=['city_landmark_trend_month'])

    if len(df[df.land_area.replace({'-': 0})>1])>0:
        df = pd.get_dummies(data=df, columns=['city_house'], prefix='dummy_city_house')
        df['log_land_area'] = np.log1p(df['land_area'])
        for c in [x for x in df.columns if x.startswith('city_')]:
            df[c] = df[c] * df['log_land_area']
        df = pd.get_dummies(data=df, columns=['floors'])
    return df


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    #land
    train('4zida/land/sale')
    #sale
    train('4zida/apartments/sale')
    #rent
    train('4zida/apartments/rent')
    #sale

    train('4zida/houses/sale')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
