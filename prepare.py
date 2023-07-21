import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def prepare(path):
    t = []
    for f in os.listdir(path+'/scraped'):
        t.append(pd.read_csv(path+'/scraped/' + f))
    df = pd.concat(t)
    del t
    df = df[pd.isna(df['Površina'])==False]
    df['area'] = df['Površina'].apply(lambda x: int(str(x).split(' ')[0]))
    df['rooms'] = df['title'].apply(lambda x: x.split(' ')[0])
    df['bedrooms'] = df['Broj soba'].apply(lambda x: float(str(x).split(' ')[0]) if str(x)[0]!='n' else 0)

    if 'Spratnost' not in df.columns:
        df['Spratnost'] = np.nan
    underground_markers = ['potkrovlje', 'nan', 'visoko prizemlje', 'suteren', 'prizemlje', 'nisko prizemlje', 'podrum']
    df['floor_number'] = df['Spratnost'].apply(lambda x: str(x).replace(' sprat ', '').replace('.', '').split('/')[0] if str(x).strip() not in underground_markers else 0 if str(x)=='visoko prizemlje' else -1)
    df['floor_number'] = df['floor_number'].apply(lambda x: 0 if x in underground_markers else int(x))
    df['floors'] = df['Spratnost'].apply(lambda x: str(x).strip().split('/')[1].replace(' spratova', '').replace(' sprata', '').replace(' sprat', '') if len(str(x).strip().split('/'))>1 else '')
    df['floors'] = df['floors'].apply(lambda x: int(x) if len(x)>1 else 0)

    df['landmark'] = df['address'].apply(lambda x: str(x).split(', ')[0])
    df = df.loc[df['address'].apply(lambda x: len(str(x).split(', ')))>2]
    df['region'] = df['address'].apply(lambda x: str(x).split(', ')[-2] if str(x).split(', ')[-2]!='Gradske lokacije' else str(x).split(', ')[-3] if len(str(x).split(', '))>2 else '')
    df['city'] = df['address'].apply(lambda x: str(x).split(', ')[-1])
    df.loc[df.city=='', 'city'] = df['region']
    df.loc[df.city==df.region, 'region'] = df['landmark']

    df['parking_places'] = df['Parking'].apply(lambda x: int(str(x).split(' ')[0]) if str(x)!='nan' else 0)
    df['garage_places'] = df['Garaža'].apply(lambda x: int(str(x).split(' ')[0]) if str(x)!='nan' else 0)
    df.loc[df['garage_places']>20, 'garage_places'] = 1
    df.loc[df['garage_places']>4, 'garage_places'] = 5

    df['delay_days'] = df['Oglas ažuriran'].apply(lambda x: int(str(x).split(' ')[1]) if len(str(x).split(' '))>1 else 0)
    df.loc[df['Oglas ažuriran'].apply(lambda x: len(str(x).split(' ')))<3, 'Oglas ažuriran'] = '   '
    df.loc[df['Oglas ažuriran'].apply(lambda x: str(x).split(' ')[2]).isin(['sat', 'sati', 'sata', 'minut', 'minuta']), 'delay_days'] = 0
    df.loc[df['Oglas ažuriran'].apply(lambda x: str(x).split(' ')[2]).isin(['mesec', 'meseca', 'meseci']), 'delay_days'] = \
        df.loc[df['Oglas ažuriran'].apply(lambda x: str(x).split(' ')[2]).isin(['mesec', 'meseca', 'meseci']), 'delay_days']*30
    df['date_update'] = pd.to_datetime(df['end_date']) .dt.date - df['delay_days'].apply(lambda x: timedelta(days=x))
    df['date_update'] = pd.to_datetime(df['date_update'])
    df['Stanje'] = df['Stanje'].apply(lambda  x: str(x).strip())
    df['Grejanje'] = df['Grejanje'].apply(lambda  x: str(x).strip())
    if 'Lift' not in df.columns:
        df['Lift'] = np.nan
    df['Lift'] = df['Lift'].apply(lambda  x: str(x).strip())
    df['Tip'] = df['Tip'].apply(lambda  x: str(x).strip())
    df['street'] = df['street'].apply(lambda  x: str(x).strip().title())
    df['Infrastruktura'] = df['Infrastruktura'].apply(lambda  x: str(x).strip().title())
    df['house_number'] = df['street'].apply(lambda  x: x.split(' ')[-1] if x.split(' ')[-1][0].isnumeric() else '')
    df['street'] = df['street'].apply(lambda  x: ' '.join(x.split(' ')[:-1]) if x.split(' ')[-1][0].isnumeric() else x)
    df['Nameštenost'] = df['Nameštenost'].apply(lambda  x: str(x).strip())
    df['Uknjiženost'] = df['Uknjiženost'].apply(lambda  x: str(x).strip())
    df['Režije'] = '-'
    if 'plac' in df.columns:
        df['land_area'] = df['plac'].apply(lambda x: 4047*float(str(x).split('a ')[0]))
    else:
        df['land_area'] = 0

    df['lower_description'] = df['description'].fillna('').str.lower()

    df.loc[df['lower_description'].str.contains('lux stan'), 'Stanje'] = 'luksuzno'
    df.loc[df['lower_description'].str.contains('luksuzan'), 'Stanje'] = 'luksuzno'
    df.loc[df['lower_description'].str.contains('luxuzan'), 'Stanje'] = 'luksuzno'
    df.loc[df['lower_description'].str.contains('luksuzno'), 'Stanje'] = 'luksuzno'
    df.loc[df['lower_description'].str.contains('luxuzno'), 'Stanje'] = 'luksuzno'
    df.loc[df['lower_description'].str.contains('luks,'), 'Stanje'] = 'luksuzno'
    df.loc[df['lower_description'].str.contains('novogradnja'), 'Stanje'] = 'novo'
    df.loc[df['lower_description'].str.contains('nov stan'), 'Stanje'] = 'novo'
    df.loc[df['lower_description'].str.contains('novoizgra'), 'Stanje'] = 'novo'
    df.loc[df['lower_description'].str.contains('u izvornom stanju'), 'Stanje'] = 'potrebno renoviranje'

    df.loc[df['lower_description'].str.contains('stan u kući'), 'Tip'] = 'Stan u kući'
    df.loc[df['lower_description'].str.contains('dupleks'), 'Tip'] = 'Dupleks'
    df.loc[df['lower_description'].str.contains('salonac'), 'Tip'] = 'Salonac'

    df.loc[df['lower_description'].str.contains('slobodan park'), 'parking_places'] = 3
    df.loc[df['lower_description'].str.contains('parking mesto'), 'parking_places'] = 1
    df.loc[df['lower_description'].str.contains('garaža'), 'garage_places'] = 1

    df.loc[df['lower_description'].str.contains('centralno grejanje'), 'Grejanje'] = 'centralno grejanje'

    df.loc[df['lower_description'].str.contains(' ima lift'), 'Lift'] = 'ima lift'
    df.loc[df['lower_description'].str.contains('sa liftom'), 'Lift'] = 'ima lift'
    df.loc[df['lower_description'].str.contains('bez lifta'), 'Lift'] = 'bez lifta'

    df.loc[df['lower_description'].str.contains('kompletno namešten'), 'Nameštenost'] = 'namešteno'

    #df.loc[df['lower_description'].str.contains('nije uknjiženo'), 'Uknjiženost'] = 'nije uknjiženo'
    print(df.loc[df['lower_description'].str.contains('uknjižen'), 'description'])
    df.loc[df['lower_description'].str.contains('u procesu uknjiževanja'), 'Uknjiženost'] = 'u procesu uknjiževanja'
    df.loc[df['lower_description'].str.contains('delimično uknjiženo'), 'Uknjiženost'] = 'delimično uknjiženo'

    if 'Tramvajske linije' in df.columns:
        del df['Tramvajske linije']
    if 'Trolejbuske linije' in df.columns:
        del df['Trolejbuske linije']
    del df['Šifra oglasa']
    if 'Autobuske linije' in df.columns:
        del df['Autobuske linije']
    del df['Režije']
    if 'Useljivo' in df.columns:
        del df['Useljivo']
    if 'Useljivo od' in df.columns:
        del df['Useljivo od']

    df = df.loc[df['price'] != 1.]
    if 'sale' in path:
        df['price'] = df['price'].apply(lambda x: float(x.replace('.', '')) if type(x)==str else x)
        df.loc[df['price']<500, 'price'] = df.loc[df['price']<500, 'price']*1000
    else:
        df['price'] = df['price'].apply(lambda x: float(x.replace('.', '')) if type(x)==str else x*1000 if x<10 else x)
    df = df[df.price.between(df.price.median()/4, df.price.median()*4)]
    df['ppm'] = df.price / df.area
    print(df.describe(include='all').T[['count', 'top']])
    print(df.columns)
    df = df.sort_values('date_update').drop_duplicates(subset=['link'], keep='last')
    df.to_parquet(path+'/prepared.parquet')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #sale
    path = '4zida/apartments/sale'
    prepare(path)
    #rent
    path = '4zida/apartments/rent'
    prepare(path)
    #sale
    path = '4zida/houses/sale'
    prepare(path)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
