import pandas as pd
from sklearn import svm
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn import svm
from sklearn import metrics
import matplotlib.pyplot as plt
import numpy as np

# load dataset
df = pd.read_csv('titanic_dataset.csv')

# drop useless columns
df.drop(columns=['Cabin','Name','Ticket'], inplace = True)
df.dropna(inplace=True)

# TEST SAMPLE
# USE THIS SAMPLE ONLY FOR TESTING
test_df = df.sample(n=100, random_state=42)
# KEEP ONLY THOSE WHO ARE NOT IN THE TEST SET
df = df[~df.PassengerId.isin(test_df.PassengerId.tolist())]

# FIT THE FIRST MODEL ONLY ON THE DATAFRAME START_DF
start_df = df.sample(n=100, random_state=42)
# DROP OBS FROM START_DF FROM DF
df = df[~df.PassengerId.isin(start_df.PassengerId.tolist())]

# Preprocessing of data
# DROP NA
start_df.dropna(inplace=True)
test_df.dropna(inplace=True)

# for categorical data
ohe = OneHotEncoder()

def encoder(model,data, columns, fit=False):
    if fit:  
        encoded = model.fit_transform(data.loc[:,columns]).toarray()
    else:
        encoded = model.transform(data.loc[:,columns]).toarray()
    encoded = pd.DataFrame(encoded, index = data.index, columns=[ohe.get_feature_names(columns)])
    return pd.merge(data.PassengerId,encoded,left_index=True,right_index=True,how='left')

encoded_train = encoder(ohe,start_df,['Sex','Embarked'],fit=True)
encoded_test = encoder(ohe,test_df,['Sex','Embarked'])

sc = StandardScaler()

def scaler(model, data, columns, fit=False):
    if fit:
        scaled = pd.DataFrame(model.fit_transform(data.loc[:,columns]),index = data.index,columns=columns)
    else:
        scaled = pd.DataFrame(model.transform(data.loc[:,columns]),index = data.index,columns=columns)
    return pd.merge(data.PassengerId,scaled,left_index=True,right_index=True,how='left')

scaled_train = scaler(sc,start_df,['Pclass', 'Age', 'SibSp', 'Parch'],fit=True)
scaled_test = scaler(sc,test_df,['Pclass', 'Age', 'SibSp', 'Parch'])

X = pd.merge(scaled_train.drop(columns=['PassengerId']),encoded_train.drop(columns=['PassengerId']),left_index=True,right_index=True)
X_test = pd.merge(scaled_test.drop(columns=['PassengerId']),encoded_test.drop(columns=['PassengerId']),left_index=True,right_index=True)
y = start_df.Survived
y_test = test_df.Survived


# evluation metrics history
acc_hist=[]
pre_hist=[]
rec_hist=[]
iteration_nb=[]
i = 0 # iteration_nb
# SVM classifier
X_i = X
y_i = y
while len(df)>0:
    # fit model to current data
    clf = svm.SVC()
    clf.fit(X_i,y_i)

    acc_hist.append(metrics.accuracy_score(y_test,clf.predict(X_test)))
    pre_hist.append(metrics.precision_score(y_test,clf.predict(X_test)))
    rec_hist.append(metrics.recall_score(y_test,clf.predict(X_test)))
    i += 1
    iteration_nb.append(i)
    
    # next 10 observations
    next_df = df.sample(n=min([10,len(df)]),random_state=42)
    
    print(i,len(df),len(next_df))
    next_df.dropna(inplace=True)
    if len(next_df)>0:
        encoded_next = encoder(ohe,next_df,['Sex','Embarked'])
        scaled_next = scaler(sc,next_df,['Pclass', 'Age', 'SibSp', 'Parch'])

        X_next = pd.merge(scaled_next.drop(columns=['PassengerId']),encoded_next.drop(columns=['PassengerId']),left_index=True,right_index=True)
        y_next = next_df.Survived

        #if len(X_next)>2:
        if 0:
            decision = np.abs(list(clf.decision_function(X_next))) 
            ind = np.argpartition(decision, 2)
            indy_to_drop = X_next.iloc[ind[0:2]].index
        else:
            indy_to_drop = X_next.index
            print(indy_to_drop)
        
        X_i = pd.concat([X_i,X_next.loc[indy_to_drop]],ignore_index=True)
        y_i = pd.concat([y_i,y_next.loc[indy_to_drop]],ignore_index=True)

    # drop observations from global df
    df = df[~df.index.isin(indy_to_drop)]
    
plt.plot(iteration_nb,acc_hist)
plt.plot(iteration_nb,pre_hist)
plt.plot(iteration_nb,rec_hist)
plt.show()
plt.savefig('random_sampling.png')