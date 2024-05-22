import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

# В соревновании использовал мета-классификатор VotingClassifier
# Здесь для предсказания будет использован CatBoost, т.к. он более легковесный
from catboost import CatBoostClassifier

matplotlib.use('agg')
plt.style.use('seaborn-v0_8-darkgrid')

# Function for predictions
def make_pred(dt, path_to_file):

    print('Importing pretrained model...')
    # Model import
    model = CatBoostClassifier()
    model.load_model('./models/cat_model.cbm')

    # Optimal threshold
    model_threshold = 0.33

    # Submission dataframe
    submission = pd.DataFrame({
        'client_id':  pd.read_csv(path_to_file)['client_id'],
        'preds': (model.predict_proba(dt)[:, 1] > model_threshold).astype(int)
    })
    print('Prediction complete!')

    # Return proba for positive class
    return submission

# Function to return the top 5 model features
def get_feature_importances():
    # Import model
    model = CatBoostClassifier()
    model.load_model('./models/cat_model.cbm')

    # Getting the features and their importance
    features = model.feature_names_
    feature_importances = model.get_feature_importance()
    
    feature_importances_dict = dict(zip(features, feature_importances))

    # Sorting and selecting the top 5 important features
    sorted_feature_importances_dict = dict(sorted(feature_importances_dict.items(),
                                                  key=lambda item: item[1], reverse=True)[:5])
    return sorted_feature_importances_dict

# Function that saves a density plot to a file
def save_density_plot(preds, path_to_file):
    plt.figure(figsize=(15, 6))
    sns.kdeplot(preds, alpha=0.7, color='purple')
    plt.title('Плотность распределения предсказанных скоров')
    plt.xlabel('Предсказания')
    plt.ylabel('Плотность')
    plt.savefig(path_to_file, format='png')
    plt.close()