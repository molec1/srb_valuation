
import pandas as pd
import numpy as np

import pickle

from model_train import features_encode

def report(path):
    raw = pd.read_parquet(path+'/prepared.parquet')
    print(len(raw))
    print(raw.columns)
    df = raw[['area', 'rooms', 'floor_number', 'parking_places', 'garage_places', 'price', 'city', 'region', 'landmark',
              'Tip', 'Lift', 'Godina izgradnje', 'street']].copy()

    geo = df[['city', 'region', 'landmark', 'street']].drop_duplicates()
    template = {'floor_number': 2, 'parking_places': 1, 'garage_places': 0, 'Tip': 'Stan u zgradi', 'Lift': 'ima lift',
                'Godina izgradnje': 2023, 'Stanje': 'Novo', 'Uknjiženost': 'uknjiženo', 'Grejanje': 'Grejanje Na Gas',
                'Infrastruktura': 'Terasa', 'floors': 5}
    sizes = {'Jednosoban': 30, 'Dvosoban': 50, 'Trosoban': 70}
    for t in template:
        geo[t] = template[t]
    ret = []
    for s in sizes:
        t = geo.copy()
        t['rooms'] = s
        t['area'] = sizes[s]
        ret.append(t)
    report = pd.concat(ret)

    reg = pickle.load(open(path+'/model.sav', 'rb'))
    report_enc = features_encode(report)
    model_cols = reg.feature_names_in_
    report_enc[list(set(model_cols)-set(report_enc.columns))] = 0
    report_enc = report_enc.copy()

    report['sale_price_per_sqm'] = np.expm1(reg.predict(report_enc[model_cols]))
    report['sale_price'] = report['sale_price_per_sqm'] * report['area']

    report.to_csv(path+'/report.csv')




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #sale
    report('4zida/apartments/sale')
    #rent
    report('4zida/apartments/rent')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
