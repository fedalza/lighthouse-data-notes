from flask import Flask, jsonify, request
from flask_restful import Resource, Api, reqparse

import pandas as pd 
import numpy as np 
import pickle
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

app = Flask(__name__)
api = Api(app)

# Using own function in Pipeline
def numFeat(data):
    return data[num_feats]

def catFeat(data):
    return data[cat_feats]

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

class loan_amountNA():
    def transform(self,X,y=None,**transform_params):
        
        X_loan_train = X[~X.LoanAmount.isna()][['ApplicantIncome','CoapplicantIncome']]
        y_loan_train = X[~X.LoanAmount.isna()]['LoanAmount']
        X_loan_test = X[X.LoanAmount.isna()][['ApplicantIncome','CoapplicantIncome']]
        #y_loan_test = X[X.LoanAmount.isna()]['LoanAmount']

        model_loan = LinearDiscriminantAnalysis()
        #kfold = KFold(n_splits=5)
        #result = cross_val_score(model_loan,X_loan_train,y_loan_train, cv=kfold,scoring='accuracy')
        model_loan.fit(X_loan_train,y_loan_train)
        X.loc[X[X.LoanAmount.isna()].index,'LoanAmount'] = model_loan.predict(X_loan_test)
        return X

    def fit(self,X,y=None,**fit_params):
        return self

    def fit_transform(self,X,y=None):
        self.fit(X)
        return self.transform(X)

class oneDependent():
    def transform(self,X,y=None,**transform_params):
        X = pd.DataFrame(X)
        naDepWCo = X[(X.loc[:,6].isna()) & (X.loc[:,9]>0)].index
        X.loc[naDepWCo,6] = 1
        naDepWOCo = X[(X.loc[:,6].isna()) & (X.loc[:,9]==0)].index
        X.loc[naDepWOCo,6] = 0
        dep3 = X[X.loc[:,6]=='3+'].index
        X.loc[dep3,6] = 3
        X = X.astype({6:'int32',8:'int32',9:'int32'})
        X.loc[:,X.shape[1]] = np.log(X.loc[:,8]+X.loc[:,9])
        #print(X.loc[:,13],X.loc[:,9],X.loc[:,10])
        return X

    def fit(self,X,y=None,**fit_params):
        return self

    def fit_transform(self,X,y=None):
        self.fit(X)
        return self.transform(X)

# create an endpoint where we can communicate with out ML model
# POST request
model = pickle.load(open('tuned_xgb.sav','rb'))

class Prediction(Resource):
    def post(self):
        json_data = request.get_json()
        df = pd.DataFrame(json_data.values(),index=json_data.keys()).transpose()

        # getting prediction from our model
        res = model.predict(df)

        # we cannot send numpy array as result
        return res.tolist()

# assign endpoint to API
api.add_resource(Prediction, '/prediction')

if __name__ == '__main__':
    app.run(debut=True)
