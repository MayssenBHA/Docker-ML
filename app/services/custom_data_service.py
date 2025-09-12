import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from typing import Dict, Any, Optional
import io
import base64
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import warnings
warnings.filterwarnings('ignore')

class CustomDataForecastService:
    """
    Service pour traiter les données uploadées par l'utilisateur et générer des prédictions
    """
    
    def __init__(self):
        self.data = None
        self.model = None
        self.model_info = {}
    
    def validate_and_process_csv(self, csv_content: bytes) -> Dict[str, Any]:
        """
        Valide et traite le fichier CSV uploadé
        
        Args:
            csv_content: Contenu du fichier CSV en bytes
            
        Returns:
            Dictionnaire avec le statut de validation et les données
        """
        try:
            # Lire le CSV
            csv_string = csv_content.decode('utf-8')
            data = pd.read_csv(io.StringIO(csv_string))
            
            # Validation basique
            if data.shape[1] < 2:
                return {
                    "success": False,
                    "error": "Le fichier CSV doit contenir au moins 2 colonnes (Date, Valeur)"
                }
            
            if data.shape[0] < 10:
                return {
                    "success": False,
                    "error": "Le fichier CSV doit contenir au moins 10 lignes de données"
                }
            
            # Identifier les colonnes automatiquement
            date_col = None
            value_col = None
            
            for col in data.columns:
                # Chercher la colonne de date
                if any(keyword in col.lower() for keyword in ['date', 'time', 'month', 'year', 'day']):
                    date_col = col
                # Chercher la colonne de valeur (numérique)
                elif pd.api.types.is_numeric_dtype(data[col]):
                    if value_col is None:  # Prendre la première colonne numérique
                        value_col = col
            
            # Si pas trouvé automatiquement, utiliser les deux premières colonnes
            if date_col is None:
                date_col = data.columns[0]
            if value_col is None:
                value_col = data.columns[1]
            
            # Préprocessing
            try:
                data['Date'] = pd.to_datetime(data[date_col])
            except:
                return {
                    "success": False,
                    "error": f"Impossible de convertir la colonne '{date_col}' en date"
                }
            
            try:
                data['Value'] = pd.to_numeric(data[value_col])
            except:
                return {
                    "success": False,
                    "error": f"Impossible de convertir la colonne '{value_col}' en valeurs numériques"
                }
            
            # Nettoyer et préparer les données
            data = data[['Date', 'Value']].dropna()
            data = data.set_index('Date').sort_index()
            
            # Vérifier s'il y a assez de données après nettoyage
            if len(data) < 10:
                return {
                    "success": False,
                    "error": "Pas assez de données valides après nettoyage (minimum 10 points)"
                }
            
            self.data = data
            self.model_info = {
                "data_points": len(data),
                "date_range": f"{data.index.min().strftime('%Y-%m-%d')} à {data.index.max().strftime('%Y-%m-%d')}",
                "date_column": date_col,
                "value_column": value_col,
                "mean_value": float(data['Value'].mean()),
                "std_value": float(data['Value'].std())
            }
            
            return {
                "success": True,
                "data_info": self.model_info,
                "message": f"Données chargées avec succès: {len(data)} points"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur lors du traitement du fichier: {str(e)}"
            }
    
    def train_model_and_predict(self, steps: int = 12) -> Dict[str, Any]:
        """
        Entraîne un modèle SARIMAX sur les données uploadées et génère des prédictions
        
        Args:
            steps: Nombre de périodes à prédire
            
        Returns:
            Dictionnaire avec les prédictions et métadonnées
        """
        if self.data is None:
            return {
                "success": False,
                "error": "Aucune donnée chargée. Veuillez d'abord uploader un fichier CSV."
            }
        
        try:
            # Déterminer la fréquence automatiquement
            freq = pd.infer_freq(self.data.index)
            if freq is None:
                # Essayer de deviner la fréquence basée sur l'écart médian
                time_diffs = self.data.index.to_series().diff().dropna()
                median_diff = time_diffs.median()
                
                if median_diff.days <= 1:
                    freq = 'D'  # Daily
                elif median_diff.days <= 7:
                    freq = 'W'  # Weekly
                elif median_diff.days <= 31:
                    freq = 'MS'  # Monthly
                else:
                    freq = 'YS'  # Yearly
            
            # Réindexer avec la fréquence détectée
            self.data = self.data.asfreq(freq, method='ffill')
            
            # Entraîner le modèle SARIMAX avec des paramètres adaptatifs
            try:
                # Essayer d'abord un modèle saisonnier si on a assez de données
                if len(self.data) >= 24:
                    seasonal_periods = min(12, len(self.data) // 2)
                    model = SARIMAX(self.data['Value'], 
                                  order=(1, 1, 1), 
                                  seasonal_order=(1, 1, 1, seasonal_periods))
                else:
                    # Modèle non saisonnier pour peu de données
                    model = SARIMAX(self.data['Value'], order=(1, 1, 1))
                
                model_fit = model.fit(disp=False)
                self.model = model_fit
                
                # Générer les prédictions
                forecast = model_fit.forecast(steps=steps)
                forecast_ci = model_fit.get_forecast(steps=steps).conf_int()
                
                # Créer les dates futures
                last_date = self.data.index[-1]
                if freq == 'D':
                    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=steps, freq=freq)
                elif freq == 'W':
                    future_dates = pd.date_range(start=last_date + pd.Timedelta(weeks=1), periods=steps, freq=freq)
                elif freq == 'MS':
                    future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=steps, freq=freq)
                else:
                    future_dates = pd.date_range(start=last_date + pd.DateOffset(years=1), periods=steps, freq=freq)
                
                # Préparer les résultats
                predictions = {
                    'dates': [date.strftime('%Y-%m-%d') for date in future_dates],
                    'values': forecast.tolist(),
                    'lower_ci': forecast_ci.iloc[:, 0].tolist(),
                    'upper_ci': forecast_ci.iloc[:, 1].tolist()
                }
                
                # Données historiques
                historical_data = {
                    'dates': [date.strftime('%Y-%m-%d') for date in self.data.index],
                    'values': self.data['Value'].tolist()
                }
                
                # Informations du modèle
                model_info = {
                    "model_type": "SARIMAX (Données personnalisées)",
                    "data_points": len(self.data),
                    "frequency": freq,
                    "last_date": self.data.index[-1].strftime('%Y-%m-%d'),
                    "value_column": self.model_info.get("value_column", "Value")
                }
                
                return {
                    "success": True,
                    "predictions": predictions,
                    "historical_data": historical_data,
                    "model_info": model_info,
                    "steps": steps
                }
                
            except Exception as model_error:
                return {
                    "success": False,
                    "error": f"Erreur lors de l'entraînement du modèle: {str(model_error)}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur lors de la prédiction: {str(e)}"
            }
    
    def generate_plot(self, predictions: Dict[str, Any], historical_data: Dict[str, Any]) -> str:
        """
        Génère un graphique des prédictions et retourne l'image en base64
        """
        try:
            plt.figure(figsize=(12, 6))
            
            # Données historiques
            hist_dates = pd.to_datetime(historical_data['dates'])
            plt.plot(hist_dates, historical_data['values'], 
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
            
            plt.title('Prédiction de vos données temporelles', fontsize=16)
            plt.xlabel('Date', fontsize=12)
            plt.ylabel('Valeur', fontsize=12)
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
            
        except Exception as e:
            print(f"Erreur lors de la génération du graphique: {e}")
            return ""
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Retourne les informations du modèle entrainé
        """
        return self.model_info.copy() if self.model_info else {}
