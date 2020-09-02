from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse

import pandas as pd 
import numpy as np 
import pickle

app = Flask(__name__)
api = Api(app)

model = pickle.load(open('model.p','rb'))

# We need to create the same customized class we used in the modeling step.
class RawFeats:
    def __init__(self,feats):
        self.feats = feats
    
    def fit(self,X,y=None):
        pass

    def transform(self,X,y=None):
        return X[self.feats]

    def fit_transform(self,X,y=None):
        self.fit(X)
        return self.transform(X)

# create an endpoint where we can communicate with out ML model
# POST request

class Scoring(Resource):
    def post(self):
        json_data = request.get_json()
        df = pd.DataFrame(json_data.values(),index=json_data.keys()).transpose()

        # getting prediction from our model
        res = model.predict_proba(df)

        # we cannot send numpy array as result
        return res.tolist()

# assign endpoint to API
api.add_resource(Scoring, '/scoring')

if __name__ == '__main__':
    app.run(debut=True)
