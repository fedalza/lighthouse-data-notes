import pandas as pd
import numpy as np

from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer

from sklearn.pipeline import Pipeline

df = pd.read_csv("data.csv") 


total_income = np.log(df.ApplicantIncome+df.CoapplicantIncome)
max(total_income)
max_bin = int(max(total_income))+1
min_bin = int(min(total_income))-1
n = max_bin-min_bin+1
bins = np.linspace(min_bin,max_bin,n,dtype=int)
labels = np.linspace(1,n-1,n-1,dtype=int)
df['log_total_Income_binned'] = pd.cut(total_income, bins=bins, labels=labels)


frequent_impute = SimpleImputer(missing_values=np.nan, strategy='most_frequent',copy=True)
constant_impute = SimpleImputer(fill_value='Unknown', strategy='constant')
null_impute = SimpleImputer(fill_value=0, strategy='constant')

ct = ColumnTransformer(transformers=[("imputer1", frequent_impute, [2,5,9]),("imputer2", constant_impute, [1]),('imputer3',null_impute,[10])],remainder='passthrough')


from sklearn.preprocessing import FunctionTransformer

class loan_amountNA():
    def transform(self,X,y=None,**transform_params):
        naLoanAmount_idx = X[X.LoanAmount.isna()].index
        mean_loans = X.groupby('log_total_Income_binned')['LoanAmount'].mean()
        X.loc[naLoanAmount_idx,'LoanAmount'] = X.loc[naLoanAmount_idx,'log_total_Income_binned'].apply(lambda x: mean_loans[x])
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
        X.loc[:,X.shape[1]] = (X.loc[:,8]+X.loc[:,9])/(X.loc[:,6]+1)
        return X

    def fit(self,X,y=None,**fit_params):
        return self

    def fit_transform(self,X,y=None):
        self.fit(X)
        return self.transform(X)


preprocessing = Pipeline([('Log_Income', loan_amountNA()),('column_transforms',ct),('deps',oneDependent())])

X = df.drop(columns=['Loan_Status'])
y = df.Loan_Status
X_cols = X.columns.tolist()

X1 = preprocessing.fit_transform(X)
X_cols.append('total_income_p_dependent')
col_order = [2,5,9,1,10,0,3,4,6,7,8,11,12,13]
X1.columns = [X_cols[i] for i in col_order]

X1 = X1.astype({'LoanAmount': 'float', 'log_total_Income_binned':'int32','Loan_Amount_Term':'int32','ApplicantIncome':'int32','CoapplicantIncome':'int32','Credit_History': 'int32','Dependents': 'int32'})