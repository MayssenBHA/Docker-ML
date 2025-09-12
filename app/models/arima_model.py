import pickle
import pandas as pd
import numpy as np
import os
from typing import List, Dict, Any
import io
import base64
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Pour éviter les problèmes d'affichage

class ARIMAModel:
    """
    Classe pour gérer le modèle ARIMA pré-entraîné
    """
    
    def __init__(self):
        self.model = None
        self.data = None
        self.model_path = os.path.join(os.path.dirname(__file__), 'trained_model.pkl')
        self.data_path = os.path.join(os.path.dirname(__file__), 'processed_data.pkl')
        self.load_model()
    
    def load_model(self):
        """Charge le modèle pré-entraîné"""
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            with open(self.data_path, 'rb') as f:
                self.data = pickle.load(f)
            
            print("Modèle chargé avec succès")
        except FileNotFoundError:
            print("Modèle non trouvé. Veuillez d'abord exécuter scripts/train_model.py")
            self.model = None
            self.data = None
        except Exception as e:
            print(f"Erreur lors du chargement du modèle: {e}")
            self.model = None
            self.data = None
    
    def predict(self, steps: int = 12) -> Dict[str, Any]:
        """
        Fait des prédictions pour les prochains mois
        
        Args:
            steps: Nombre de mois à prédire
            
        Returns:
            Dictionnaire avec les prédictions et intervalles de confiance
        """
        if self.model is None:
            raise ValueError("Modèle non chargé")
        
        # Générer les prédictions
        forecast = self.model.forecast(steps=steps)
        forecast_ci = self.model.get_forecast(steps=steps).conf_int()
        
        # Créer les dates futures
        last_date = self.data.index[-1]
        future_dates = pd.date_range(
            start=last_date + pd.DateOffset(months=1), 
            periods=steps, 
            freq='MS'
        )
        
        # Conversion sécurisée en liste
        if hasattr(forecast, 'tolist'):
            forecast_values = forecast.tolist()
        elif hasattr(forecast, 'values'):
            forecast_values = forecast.values.tolist()
        else:
            forecast_values = list(forecast)
        
        # Préparer les résultats
        predictions = {
            'dates': [date.strftime('%Y-%m') for date in future_dates],
            'values': forecast_values,
            'lower_ci': forecast_ci.iloc[:, 0].tolist(),
            'upper_ci': forecast_ci.iloc[:, 1].tolist()
        }
        
        return predictions
    
    def get_historical_data(self) -> Dict[str, Any]:
        """
        Retourne les données historiques
        """
        if self.data is None:
            raise ValueError("Données non chargées")
        
        return {
            'dates': [date.strftime('%Y-%m') for date in self.data.index],
            'values': self.data['Passengers'].tolist()
        }
    
    def generate_plot(self, predictions: Dict[str, Any]) -> str:
        """
        Génère un graphique des prédictions et retourne l'image en base64
        """
        if self.data is None:
            raise ValueError("Données non chargées")
        
        plt.figure(figsize=(12, 6))
        
        # Données historiques
        plt.plot(self.data.index, self.data['Passengers'], 
                label='Données historiques', color='blue', linewidth=2)
        
        # Prédictions
        future_dates = pd.to_datetime(predictions['dates'])
        plt.plot(future_dates, predictions['values'], 
                label='Prédictions', color='red', linewidth=2, linestyle='--')
        
        # Intervalles de confiance
        plt.fill_between(future_dates, 
                        predictions['lower_ci'], 
                        predictions['upper_ci'], 
                        alpha=0.3, color='red', label='Intervalle de confiance 95%')
        
        plt.title('Prédiction du nombre de passagers aériens', fontsize=16)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Nombre de passagers', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Convertir en base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        img_string = base64.b64encode(img_buffer.read()).decode()
        plt.close()
        
        return img_string
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Retourne les informations sur le modèle
        """
        if self.model is None:
            return {"error": "Modèle non chargé"}
        
        return {
            "model_type": "SARIMAX",
            "order": "(1, 1, 1)",
            "seasonal_order": "(1, 1, 1, 12)",
            "data_points": len(self.data) if self.data is not None else 0,
            "last_date": self.data.index[-1].strftime('%Y-%m') if self.data is not None else None
        }
