import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report

# Loading the data from CSV file
data_path = 'influxdata_2024-04-10T16_16_12Z.csv'
df = pd.read_csv(data_path)

df = df.fillna(0)

# Preprocessing
# Converting 'crash' from boolean to integer
df['crash'] = df['crash'].fillna(0).astype(int)

# Selecting relevant features and target
X = df[['accelerometer-x', 'accelerometer-y', 'accelerometer-z']]
y = df['crash']

# Splitting the dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initializing the Decision Tree Classifier
clf = DecisionTreeClassifier(random_state=42)

# Training the model
clf.fit(X_train, y_train)

# Making predictions
y_pred = clf.predict(X_test)

# Evaluating the model
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)

print(f"Accuracy: {accuracy}")
print(f"Classification Report: \n{report}")


import pickle

model_pickle_path = 'my_model.pkl'
with open(model_pickle_path, 'wb') as file:
    pickle.dump(clf, file)

print(f"Model pickled to '{model_pickle_path}'")