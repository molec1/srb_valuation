import os
import pandas as pd
from datetime import datetime, timedelta

def prepare(path):
    t = []
    for f in os.listdir(path+'/scraped'):
        t.append(pd.read_csv(path+'/scraped/' + f))
    df = pd.concat(t)
    del t
    df['area'] = df['Površina'].apply(lambda x: int(str(x).split(' ')[0]))
    df['rooms'] = df['title'].apply(lambda x: x.split(' ')[0])
    df['bedrooms'] = df['Broj soba'].apply(lambda x: float(str(x).split(' ')[0]) if str(x)[0]!='n' else 0)
    df['floor_number'] = df['Spratnost'].apply(lambda x: int(str(x)) if str(x).strip() not in ['potkrovlje', 'nan', 'visoko prizemlje', 'suteren', 'prizemlje', 'nisko prizemlje', 'podrum'] else 0 if str(x)=='visoko prizemlje' else -1)
    df['floors'] = df['Spratnost'].apply(lambda x: int(str(x).split('/')[1]) if len(str(x).split('/'))>1 else 0)
    df['landmark'] = df['address'].apply(lambda x: str(x).split(', ')[0])
    df['region'] = df['address'].apply(lambda x: str(x).split(', ')[-2] if str(x).split(', ')[-2]!='Gradske lokacije' else str(x).split(', ')[-3] if len(str(x).split(', '))>2 else '')
    df['city'] = df['address'].apply(lambda x: str(x).split(', ')[-1])
    df.loc[df.city=='', 'city'] = df['region']
    df.loc[df.city==df.region, 'region'] = df['landmark']
    df['parking_places'] = df['Parking'].apply(lambda x: str(x).split(' ')[0])
    df['garage_places'] = df['Garaža'].apply(lambda x: str(x).split(' ')[0])

    df['delay_days'] = df['Oglas ažuriran'].apply(lambda x: int(str(x).split(' ')[1]))
    df.loc[df['Oglas ažuriran'].apply(lambda x: str(x).split(' ')[2]).isin(['sat', 'sati', 'sata', 'minut', 'minuta']), 'delay_days'] = 0
    df.loc[df['Oglas ažuriran'].apply(lambda x: str(x).split(' ')[2]).isin(['mesec', 'meseca', 'meseci']), 'delay_days'] = \
        df.loc[df['Oglas ažuriran'].apply(lambda x: str(x).split(' ')[2]).isin(['mesec', 'meseca', 'meseci']), 'delay_days']*30
    df['date_update'] = pd.to_datetime(df['end_date']) .dt.date - df['delay_days'].apply(lambda x: timedelta(days=x))
    df['date_update'] = pd.to_datetime(df['date_update'])

    del df['Tramvajske linije']
    del df['Trolejbuske linije']
    del df['Šifra oglasa']
    del df['Autobuske linije']
    if 'sale' in path:
        df['price'] = df['price'].apply(lambda x: float(x.replace('.', '')) if type(x)==str else x*1000)
    else:
        df['price'] = df['price'].apply(lambda x: float(x.replace('.', '')) if type(x)==str else x*1000 if x<10 else x)
    df = df[df.price.between(df.price.median()/10, df.price.median()*10)]
    df['ppm'] = df.price / df.area
    print(df.describe(include='all').T[['count', 'top']])
    df.to_parquet(path+'/prepared.parquet')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #sale
    path = '4zida/apartments/sale'
    prepare(path)
    #rent
    path = '4zida/apartments/rent'
    prepare(path)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
