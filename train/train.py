import pandas as pd
from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import metrics, cross_validation
from sklearn.cross_validation import cross_val_score
from nltk import ConfusionMatrix

train = []
Data = pd.read_csv("all1.csv")

feature_cols = ["coeff"]

X = Data[feature_cols]
y = Data["y"]


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=0)

logreg = LogisticRegression(tol=0.356)
y_score = logreg.fit(X_train, y_train).predict_proba(X_test)

predicted = cross_validation.cross_val_predict(logreg, X, y, cv=10)
# print metrics.accuracy_score(y, predicted)
# print metrics.classification_report(y, predicted)

accuracy = cross_val_score(logreg, X, y, cv=10, scoring='accuracy')
# print (accuracy)
# print (cross_val_score(logreg, X, y, cv=10, scoring='accuracy').mean())

test = logreg.predict(X_test)
print(X_test["coeff"])
print(test)
print(y_score)
# Compute ROC curve and ROC area for each class
fpr = dict()
tpr = dict()
roc_auc = dict()
print(y_score)
fpr, tpr, thresholds = roc_curve(y_test, y_score[:,1])
print(thresholds)
print(fpr)
print(tpr)
coeffs=zip(fpr,tpr)
coeffs = map(lambda x: 1-x[0]+x[1], coeffs)
print(coeffs)
roc_auc = auc(fpr, tpr)
plt.plot(fpr, tpr, label='%s LR (area = %0.2f)' % ('LR', roc_auc))
plt.plot([0, 1], [0, 1], 'k--')
plt.xlim([-0.01, 1.0])
plt.ylim([0.0, 1.01])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.legend(loc=0, fontsize='small')
plt.show()

