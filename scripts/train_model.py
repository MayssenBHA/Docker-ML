import pandas as pd
import numpy as np
import pickle
import os
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_squared_error
import warnings
warnings.filterwarnings('ignore')

def train_and_save_model():
    """
    Entraîne le modèle ARIMA et le sauvegarde en format pickle
    """
    # Charger les données
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'AirPassengers.csv')
    data = pd.read_csv(data_path)
    
    # Préprocessing
    data['Date'] = pd.to_datetime(data['Month'])
    data = data.drop(columns='Month')
    data = data.set_index('Date')
    data = data.rename(columns={'#Passengers': 'Passengers'})
    
    print(f"Données chargées: {data.shape}")
    print(f"Période: {data.index.min()} à {data.index.max()}")
    
    # Division train/test
    train_size = int(len(data) * 0.8)
    train = data['Passengers'][:train_size]
    test = data['Passengers'][train_size:]
    
    print(f"Taille train: {len(train)}, Taille test: {len(test)}")
    
    # Entraînement du modèle SARIMAX
    print("Entraînement du modèle SARIMAX...")
    model = SARIMAX(train, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
    model_fit = model.fit(disp=False)
    
    # Évaluation sur les données de test
    forecast = model_fit.forecast(steps=len(test))
    rmse = np.sqrt(mean_squared_error(test, forecast))
    print(f"RMSE sur les données de test: {rmse:.4f}")
    
    # Réentraîner sur toutes les données pour la production
    print("Réentraînement sur toutes les données...")
    final_model = SARIMAX(data['Passengers'], order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
    final_model_fit = final_model.fit(disp=False)
    
    # Sauvegarder le modèle
    model_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'models', 'trained_model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(final_model_fit, f)
    
    # Sauvegarder aussi les données pour référence
    data_processed_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'models', 'processed_data.pkl')
    with open(data_processed_path, 'wb') as f:
        pickle.dump(data, f)
    
    print(f"Modèle sauvegardé dans: {model_path}")
    print(f"Données sauvegardées dans: {data_processed_path}")
    
    return final_model_fit, data

if __name__ == "__main__":
    model, data = train_and_save_model()
    print("Entraînement terminé avec succès!")
