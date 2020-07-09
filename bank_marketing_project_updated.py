# -*- coding: utf-8 -*-
"""Bank Marketing Project_New.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1y4_5molJ8nrlnzlX5oPxURKXY5TNWRyr
"""

import pandas as pd
import numpy as np
import scipy.stats as stats
import os, re, fnmatch
import pathlib, itertools, time
import matplotlib.pyplot as plt

from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from sklearn.model_selection import cross_val_score, cross_val_predict
from sklearn.metrics import explained_variance_score
from sklearn.externals import joblib

from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OrdinalEncoder
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.feature_selection import mutual_info_classif


from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn import svm
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectFromModel
from sklearn.feature_selection import RFE
from sklearn.model_selection import train_test_split

from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC 
from sklearn.ensemble import RandomForestClassifier
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense
from keras.utils import to_categorical
from keras.layers import Dropout

from sklearn import datasets
import xgboost as xgb
import numpy as np
from sklearn.metrics import precision_score, recall_score, accuracy_score, f1_score

##Upload  data file 
from google.colab import files 
uploaded = files.upload()

import tensorflow as tf 
tf.test.gpu_device_name()

#Read data file data into a dataframe

import io 
Bank_data = pd.read_csv(io.BytesIO(uploaded['bank-additional-full.csv']),sep=';')
#Bank_data =pd.read_csv("C:/Users/meera/Projects/Bank Marketing/bank-additional/bank-additional/bank-additional-full.csv",sep=';')

Bank_data.head()

## Check for missing values

Bank_data.isnull().sum()
Bank_data.isna().sum(), Bank_data['y'].value_counts()

## Function to plot piplot
def piplot(data):
    labels = data.astype('category').cat.categories.tolist()
    counts = data.value_counts()
    sizes = [counts[i] for i in labels]
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True) 
    ax1.axis('equal')
    plt.show()

piplot(Bank_data['job'])

piplot(Bank_data['education'])

piplot(Bank_data['loan'])

piplot(Bank_data['age']>25)

piplot(Bank_data['housing'])

piplot(Bank_data['marital'])

Bank_data.groupby(['campaign','y']).size().to_frame().unstack().plot(kind='bar',stacked=True,legend=True)
plt.xlim(0,16)
plt.show()

Bank_data.groupby(['education','y']).size().to_frame().unstack().plot(kind='bar',stacked=True,legend=True)
plt.xlim(0,16)
plt.show()

Bank_data.groupby(['job','y']).size().to_frame().unstack().plot(kind='bar',stacked=True,legend=True)
plt.xlim(0,16)
plt.show()

Bank_data.groupby(['loan','y']).size().to_frame().unstack().plot(kind='bar',stacked=True,legend=True)
plt.xlim(0,16)
plt.show()

Bank_data.groupby(['housing','y']).size().to_frame().unstack().plot(kind='bar',stacked=True,legend=True)
plt.xlim(0,16)
plt.show()

Bank_data.groupby(['marital','y']).size().to_frame().unstack().plot(kind='bar',stacked=True,legend=True)
plt.xlim(0,16)
plt.show()

## Convert features to categorical type

Bank_data['job'] = Bank_data['job'].astype('category')
Bank_data['marital'] = Bank_data['marital'].astype('category')
Bank_data['education'] = Bank_data['education'].astype('category')
Bank_data['default'] = Bank_data['default'].astype('category')
Bank_data['housing'] = Bank_data['housing'].astype('category')
Bank_data['loan'] = Bank_data['loan'].astype('category')
Bank_data['contact'] = Bank_data['contact'].astype('category')
Bank_data['month'] = Bank_data['month'].astype('category')
Bank_data['day_of_week'] = Bank_data['day_of_week'].astype('category')
Bank_data['poutcome'] = Bank_data['poutcome'].astype('category')
Bank_data['y'] = Bank_data['y'].astype('category')

Bank_data.dtypes

##Function for label encoding
def getlabels(cat_val):
    le = LabelEncoder()
    le.fit(cat_val)
    y_train_enc = le.transform(cat_val)
    mappings = {index: label for index, label in 
                  enumerate(le.classes_)}
    return y_train_enc

####### Label Encoding

Bank_data['job_new'] = getlabels(Bank_data['job'])
Bank_data['marital_new'] = getlabels(Bank_data['marital'])
Bank_data['education'] = getlabels(Bank_data['education'])
Bank_data['default_new'] = getlabels(Bank_data['default'])
Bank_data['housing_new'] = getlabels(Bank_data['housing'])
Bank_data['loan_new'] = getlabels(Bank_data['loan'])
Bank_data['contact_new'] = getlabels(Bank_data['contact'])
Bank_data['month_new'] = getlabels(Bank_data['month'])
Bank_data['day_of_week_new'] = getlabels(Bank_data['day_of_week'])
Bank_data['poutcome_new'] = getlabels(Bank_data['poutcome'])
Bank_data['y_new'] = getlabels(Bank_data['y'])
Bank_data.head(10)

## Create dummy variables from categorical features
Bank_dummy=Bank_data[['job','marital','education','default','housing','loan','contact','month', 'day_of_week','poutcome']]
Bank_dummy=pd.get_dummies(Bank_dummy, columns=['job','marital','education','default','housing','loan','contact','month', 'day_of_week','poutcome'])
Bank_data=Bank_data.drop(['job','marital','education','default','housing','loan','contact','month', 'day_of_week','poutcome'], axis=1)
Bank_data=pd.concat([Bank_data,Bank_dummy], axis=1)
Bank_data.head()

#Correlation plot before dummy variable creation
import seaborn as sns
corrmat = Bank_data.corr()
top_corr_features = corrmat.index
plt.figure(figsize=(20,20))

g=sns.heatmap(Bank_data[top_corr_features].corr(),annot=True,cmap="RdYlGn")

##Function to get train test data

def get_traintestset(Bank_data, test_size, random_state):
    X=Bank_data.drop('y', axis=1)
    y=Bank_data['y']

    ######## Split data into train and test subsets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
    #len(X_train), len(X_test), len(y_train), len(y_test)
    return X_train, X_test, y_train, y_test

# feature selection/ Feature importance
def select_features1(X_train, y_train, X_test):
    fs = SelectKBest(score_func=mutual_info_classif, k='all')
    fs.fit(X_train, y_train)
    X_train_fs = fs.transform(X_train)
    X_test_fs = fs.transform(X_test)
    return X_train_fs, X_test_fs, fs

# Plot for feature importance

def feature_select(X_train, y_train, X_test):
    X_train_fs, X_test_fs, fs = select_features1(X_train, y_train, X_test)

    # scores for the features
    for i in range(len(fs.scores_)):
        print('Feature %d: %f' % (i, fs.scores_[i]))
    # plot the scores
    plt.bar([i for i in range(len(fs.scores_))], fs.scores_)
    plt.show(), X_train.columns

##Logistic Regression
def logisticReg(X_train, y_train, X_test, y_test):
    model = LogisticRegression().fit(X_train, y_train)
    Y_Pred=model.predict(X_test)

    model.score(X_test, y_test)

    #confusion_matrix = confusion_matrix(y_test, Y_Pred,labels=[0,1])
    
    print(classification_report(y_test, Y_Pred))
    print(model.score(X_test, y_test))
    print(pd.crosstab(y_test, Y_Pred))
    
    return model

##XgBoost model
def XgBoost(X_train, y_train, X_test, y_test, D_train, D_test,param,steps):
    ## Train model
    model = xgb.train(param, D_train, steps)

    preds = model.predict(D_test)
    best_preds = np.asarray([np.argmax(line) for line in preds])
    print("Precision = {}".format(precision_score(y_test, best_preds, average='macro')))
    print("Recall = {}".format(recall_score(y_test, best_preds, average='macro')))
    print("Accuracy = {}".format(accuracy_score(y_test, best_preds)))
    print(pd.crosstab(y_test, best_preds))
    print(classification_report(y_test, best_preds))
    
    return model

##XgBoost with GridsearchCV model

parameters = {"eta"    : [0.05, 0.10, 0.15, 0.20, 0.25, 0.30 ] ,"max_depth" : [ 3, 4, 5, 6, 8, 10, 12, 15],
     "min_child_weight" : [ 1, 3, 5, 7 ], "gamma" : [ 0.0, 0.1, 0.2 , 0.3, 0.4 ], "colsample_bytree" : [ 0.3, 0.4, 0.5 , 0.7 ]}
cv=4

def XgBoost_Gridserach(X_train, y_train, X_test, y_test,cv,parameters):
    classifier = xgb.XGBClassifier()

    Grid_search = GridSearchCV(classifier,parameters, n_jobs=4, scoring="neg_log_loss", cv=cv)

    Grid_search.fit(X_train, y_train)
    print(Grid_search.best_params_)
    y_true, y_pred = y_test, Grid_search.predict(X_test)
    print(pd.crosstab(y_test, y_pred))
    print(classification_report(y_test, y_pred))
    
    return Grid_search, Grid_search.best_params_

##SVM Classifier
def svm_classifier(X_train, y_train, X_test, y_test):
    svm_model_linear = SVC(kernel = 'linear', C = 1,probability=True).fit(X_train, y_train) 
    Y_Pred = svm_model_linear.predict(X_test) 

    print(pd.crosstab(y_test, Y_Pred))
    print(classification_report(y_test, Y_Pred))
    
    return svm_model_linear

## SVM with GridsearchCV

def svc_gridsearch(X_train, y_train, X_test, y_test,param_grid):
    grid_SVC = GridSearchCV(SVC(),param_grid,refit=True,verbose=2)
    grid_SVC.fit(X_train,y_train)
    print(grid_SVC.best_params_)
    y_true, y_pred = y_test, grid_SVC.predict(X_test)
    print(pd.crosstab(y_test, y_pred))
    print(classification_report(y_test, y_pred))
    
    return grid_SVC, grid_SVC.best_params_

##RandomForest Classifier

RSEED = 50
ns=10

def RF_Classifier(X_train, y_train, X_test, y_test,RSEED,ns):
    model_rf = RandomForestClassifier(n_estimators=ns, random_state=RSEED, max_features = 'sqrt', n_jobs=-1, verbose = 1)
    model_rf.fit(X_train, y_train)
    Y_Pred=model_rf.predict(X_test)

    print(pd.crosstab(y_test, Y_Pred))
    print(classification_report(y_test, Y_Pred))
    
    return model_rf

##RandomForest GrisearchCV
def RFC_Gridserach(X_train, y_train, X_test, y_test,param_grid):
    rfc = RandomForestClassifier(n_jobs=-1,max_features= 'sqrt' ,n_estimators=50, oob_score = True) 


    CV_rfc = GridSearchCV(estimator=rfc, param_grid=param_grid, cv= 5)
    CV_rfc.fit(X_train, y_train)
    print(CV_rfc.best_params_)
    Y_Pred=CV_rfc.predict(X_test)

    print(pd.crosstab(y_test, Y_Pred))
    print(classification_report(y_test, Y_Pred))
    
    return CV_rfc, CV_rfc.best_params_

## Neural Network

def neuralnetwork(X_train, y_train, X_test, y_test):
    y_train = to_categorical(y_train)
    
    ## keras model
    model = Sequential()
    model.add(Dense(30, input_dim=63, activation='relu'))
    model.add(Dense(30, activation='relu'))
    model.add(Dense(20, activation='relu'))
    model.add(Dense(2, activation='sigmoid'))

    ## compile the keras model
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    ## fit the keras model on the dataset
    model.fit(X_train, y_train, epochs=100, batch_size=10, verbose=0)

    ## make class predictions with the model
    predictions = model.predict_classes(X_test)
    print(pd.crosstab(y_test, predictions))
    print(classification_report(y_test, predictions))
    
    return model

#Function to get results from models
def get_modelresults(model,X_test, y_test):
    preds = model.predict(X_test)
    print(pd.crosstab(y_test, preds))
    #print(classification_report(y_test, preds))
    print("Precision = {}".format(precision_score(y_test, preds, average='macro')))
    print("Recall = {}".format(recall_score(y_test, preds, average='macro')))
    print("Accuracy = {}".format(accuracy_score(y_test, preds)))
    #print("F1_score = {}".format(f1_score(y_test, y_pred)))

##Function to get ROC curve
def get_roc(model, X_train, y_train, X_test, y_test):
    ytest_probas = model.predict_proba(X_test) # predicted probabilities generated by sklearn classifier
    ytrain_probas = model.predict_proba(X_train)
    #best_preds = np.asarray([np.argmax(line) for line in y_probas])
    print("ROC Curve for Test set")
    skplt.metrics.plot_roc_curve(y_test, ytest_probas)
    plt.show()
    print("\n \n ROC Curev for train set")
    skplt.metrics.plot_roc_curve(y_train, ytrain_probas)
    plt.show()

from sklearn.calibration import calibration_curve

##Function to get calibrated curve
def get_Calibrated_curve(y_test, Y_Pred):
    fop, mpv = calibration_curve(y_test, Y_Pred, n_bins=10,  normalize=True)
    plt.plot([0, 1], [0, 1], linestyle='--')
    plt.plot(mpv, fop, marker='.')
    plt.show()

##Get data
X_train, X_test, y_train,y_test = get_traintestset(Bank_data,0.2,40)
y_train=getlabels(y_train)
y_test=getlabels(y_test)
 
log_model=logisticReg(X_train, y_train, X_test, y_test)

from sklearn import preprocessing

##Prepare data for XGBoost

D_train = xgb.DMatrix(X_train, label=y_train)
D_test = xgb.DMatrix(X_test, label=y_test)
param = {'eta': 0.3, 'max_depth': 5, 'objective': 'binary:logistic'}   
steps = 50  # The number of training iterations


xgbmodel=XgBoost(X_train, y_train, X_test, y_test, D_train, D_test,param,steps)

xgbmodel_GCV, bets_param=XgBoost_Gridserach(X_train, y_train, X_test, y_test,cv,parameters)

svmmodel=svm_classifier(X_train, y_train, X_test, y_test)

param_grid ={'kernel': ['linear'], 'C': [1, 10, 100, 1000]}
svcmodel_GC, bestsv_param=svc_gridsearch(X_train, y_train, X_test, y_test,param_grid)

RSEED=40
ns=45
rfmodel=RF_Classifier(X_train, y_train, X_test, y_test,RSEED,ns)

param_grid = {
    'n_estimators': [10,20,50,200, 700],
    'max_features': ['auto', 'sqrt', 'log2']
}
rf_gcmodel, rf_gcbest_param=RFC_Gridserach(X_train, y_train, X_test, y_test,param_grid)

nn_model=neuralnetwork(X_train, y_train, X_test, y_test)


import scikitplot as skplt
get_roc(nn_model, X_train, y_train, X_test, y_test)

get_roc(log_model, X_train, y_train, X_test, y_test)

