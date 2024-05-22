# Necessary dependencies
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder, StandardScaler

def import_data(path_to_file):
    
    # Input dataframe
    input_df = pd.read_csv(path_to_file)

    return input_df

# Preprocessing function
def run_preprocessing(input_df):

    # Column types
    target_feature = 'binary_target'
    cols_to_delete = ['client_id', 'mrg_', 'зона_1', 'зона_2']

    # Dropping unnecessary columns
    input_df.drop(cols_to_delete, axis=1, inplace=True)

    categorial_features = input_df.select_dtypes('object').columns
    numerical_features = list(set(input_df.columns) - set(categorial_features))

    # Filling missing values
    for col_name in categorial_features:
        input_df[col_name] = input_df[col_name].fillna('Not defined')

    for col_name in numerical_features:
        input_df[col_name] = input_df[col_name].fillna(-9999999)

    # Feature engineering
    input_df['эффективность_использования'] = input_df['доход'] / (input_df['сумма'] + 1e-4)
    input_df['среднее_пополнение'] = input_df['сумма'] / (input_df['частота_пополнения'] + 1e-4)
    input_df['средний_доход_на_операцию'] = input_df['доход'] / (input_df['частота_пополнения'] + 1e-4)
    input_df['сегмент_arpu_месячный'] = input_df['сегмент_arpu'] / 3
    input_df['скор_уможить_доход'] = input_df['секретный_скор'] * input_df['доход']
    input_df['скор_делить_сумма'] = input_df['секретный_скор'] / (input_df['сумма'] + 1e-4)
    input_df['скор_умножить_объем'] = input_df['секретный_скор'] * input_df['объем_данных']

    # Transforming categorical features into numerical
    ordinal_encoder = OrdinalEncoder()
    input_df[categorial_features] = ordinal_encoder.fit_transform(input_df[categorial_features])

    # Standardization of data
    standard_scaler = StandardScaler()
    col_names_for_scaler = list(set(input_df.columns) - set([target_feature]))
    input_df[col_names_for_scaler] = standard_scaler.fit_transform(input_df[col_names_for_scaler])
    
    output_df = input_df.copy()

    return output_df