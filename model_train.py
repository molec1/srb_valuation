
import pandas as pd
import numpy as np

from sklearn import linear_model
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_percentage_error as mape

import pickle


def mdape(y, pred):
    return (np.sqrt(np.square(y-pred))/y).median()

def train(path):
    raw = pd.read_parquet(path+'/prepared.parquet')
    #print(raw.columns)
    df = raw[['area', 'rooms', 'floor_number', 'parking_places', 'garage_places',
              'price', 'city', 'region', 'landmark',
              'Tip', 'Lift', 'Godina izgradnje', 'street', 'link', 'Stanje',
              'Uknjiženost', 'Grejanje', 'Infrastruktura', 'floors', 'Nameštenost']].drop_duplicates().copy()
    df['ppm'] = df['price'] / df['area']
    df = df[df.area.between(20, 200)]
    df['target'] = np.log1p(df['price'] / df['area'])
    print('len df:', len(df))
    df_nonencoded = df.copy()
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

    X_train, X_test, y_train, y_test = train_test_split(df[model_cols], df['target'], test_size = 0.33, random_state = 42)

    reg = linear_model.Ridge(alpha=2, positive=True)
    reg.fit(X_train, y_train)
    #print(reg.intercept_)
    #print(dict(zip(model_cols, reg.coef_)))
    pred_train = reg.predict(X_train)
    pred_test = reg.predict(X_test)
    print('number of features: ', len(model_cols))
    print('train mape: ', mape(np.expm1(y_train), np.expm1(pred_train)))
    print('test mape: ', mape(np.expm1(y_test), np.expm1(pred_test)))
    print('train mdape: ', mdape(np.expm1(y_train), np.expm1(pred_train)))
    print('test mdape: ', mdape(np.expm1(y_test), np.expm1(pred_test)))

    pickle.dump(reg, open(path+'/model.sav', 'wb'))

    df['pred_ppm'] = np.expm1(reg.predict(df[model_cols]))
    df_nonencoded['pred_ppm'] = df['pred_ppm']
    df['err'] = (df.pred_ppm-df.ppm)/df.ppm
    df=df.sort_values(by='err')
    pd.set_option('display.max_colwidth', None)
    #print(df.head(10)[['link', 'err']])
    #print(df.head(10)[['price', 'area', 'ppm', 'pred_ppm', 'err']])
    #print(df.tail(20)[['link', 'err']])
    #print(df.tail(20)[['price', 'area', 'ppm', 'pred_ppm', 'err']])


def load_model(path):
    return pickle.load(open(path+'/model.sav', 'rb'))


def features_encode(df_):
    df = df_.copy()
    df['parking_places'] = df['parking_places'].replace({'nan': 0.5})
    df['garage_places'] = df['garage_places'].replace({'nan': 0})
    df['Stanje'] = df['Stanje'].replace({'nan': '-'}).fillna('-').apply(lambda x: x.strip().title())
    df['Uknjiženost'] = df['Uknjiženost'].replace({'nan': '-'}).fillna('-').apply(lambda x: x.strip())
    df['Grejanje'] = df['Grejanje'].replace({'nan': '-'}).fillna('-').apply(lambda x: x.strip().title())
    df['Infrastruktura'] = df['Infrastruktura'].replace({'nan': '-'}).fillna('-').apply(lambda x: x.strip().title())
    df['Tip'] = df['Tip'].replace({'nan': '-'}).fillna('-').apply(lambda x: x.strip())
    df['Lift'] = df['Lift'].replace({'nan': '-'}).fillna('-').apply(lambda x: x.strip().title())
    df['street'] = df['street'].replace({'nan': '-'}).fillna('-').apply(lambda x: x.strip().title())

    df['decade'] = df['Godina izgradnje'].apply(lambda x: int(x//10)*10 if not pd.isna(x) else 0)
    df['city_region'] = df.city + '_' + df.region
    df['city_landmark'] = df.city_region + '_' + df.landmark
    df['city_street'] = df.city_landmark + '_' + df.street
    df['anti_area'] = -np.log1p(df['area'])

    df['floors'] = df['floors'].fillna(0)
    df['floor_number'] = df['floor_number'].fillna(0)
    df['top_floor'] = ((df['floors'] - df['floor_number'])<1).apply(lambda x: 1 if x else 0)

    df['region_parking'] = df['city_region']+'_has_parking'
    df.loc[df['parking_places'].fillna(0)==0, 'region_parking'] = 'no_parking'
    df['region_garage'] = df['city_region'] + '_has_garage'
    df.loc[df['garage_places'].fillna(0)==0, 'region_garage'] = 'no_garage'

    df['lift_floor'] = df['Lift'].fillna('no_info').apply(lambda x: 'has_lift_' if 'Ima' in x else 'no_lift_') + df['floor_number'].apply(str)

    df = pd.get_dummies(data=df, columns=['rooms'])
    df = pd.get_dummies(data=df, columns=['floor_number'])
    df = pd.get_dummies(data=df, columns=['decade'])
    df = pd.get_dummies(data=df, columns=['Tip'])
    df = pd.get_dummies(data=df, columns=['Lift'])
    df = pd.get_dummies(data=df, columns=['Stanje'])
    df = pd.get_dummies(data=df, columns=['Uknjiženost'])
    df = pd.get_dummies(data=df, columns=['Grejanje'])
    df = pd.get_dummies(data=df, columns=['Infrastruktura'])
    df = pd.get_dummies(data=df, columns=['Nameštenost'])
    df = pd.get_dummies(data=df, columns=['city'])
    df = pd.get_dummies(data=df, columns=['city_region'])
    df = pd.get_dummies(data=df, columns=['city_landmark'])
    df = pd.get_dummies(data=df, columns=['city_street'])
    df = pd.get_dummies(data=df, columns=['region_parking'])
    df = pd.get_dummies(data=df, columns=['region_garage'])
    df = pd.get_dummies(data=df, columns=['lift_floor'])
    return df


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #sale
    train('4zida/apartments/sale')
    #rent
    train('4zida/apartments/rent')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
