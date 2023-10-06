from fastapi import FastAPI
from pydantic import BaseModel

import datetime
import numpy as np
import pandas as pd
import pickle

from model_train import features_encode

app = FastAPI()

class input_(BaseModel):
    property_type: str
    deal_type: str
    city: str
    region: str
    landmark: str
    street: str
    area: float
    Plac: float
    rooms: str
    building_year: float
    Stanje: str
    floor_number: int
    Uknjiženost: str
    Grejanje: str
    Tip: str
    Nameštenost: str

@app.post("/valuate")
def valuate(o: input_):
    path = '4zida/'+o.property_type+'/'+o.deal_type
    reg = pickle.load(open(path+'/model.sav', 'rb'))
    conf_reg = pickle.load(open(path+'/confidence_model.sav', 'rb'))

    property = dict(o)
    property = pd.DataFrame([property])
    property['date_update'] = datetime.datetime.now()
    property["Godina izgradnje"] = property['building_year']
    property_enc = features_encode(property)
    model_cols = reg.feature_names_in_
    add_sale_cols = list(set(model_cols)-set(property_enc.columns))
    add_sale_df = pd.DataFrame({key: 0 for key in add_sale_cols}, index=[0])
    property_enc = pd.concat([property_enc, add_sale_df], axis=1)
    property_enc = property_enc.fillna(0).copy()

    property_enc['Price per m2'] = np.expm1(reg.predict(property_enc[model_cols])).round(-1)
    property_enc['conf_coeff'] = np.exp(conf_reg.predict(property_enc[model_cols]))
    property_enc['Valuated price'] = property_enc['Price per m2'] * property_enc['area'].round()
    property_enc['Low'] = (property_enc['Valuated price']/property_enc['conf_coeff'] ).round(-2)
    property_enc['High'] = (property_enc['Valuated price']*property_enc['conf_coeff'] ).round(-2)
    print(property_enc[['Price per m2', 'Valuated price', 'Low', 'High']])
    return property_enc[['Price per m2', 'Valuated price', 'Low', 'High']].T.to_dict()
