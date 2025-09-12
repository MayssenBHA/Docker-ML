from app.models.arima_model import ARIMAModel
from typing import Dict, Any

class ForecastService:
    """
    Service pour gérer les prédictions de séries temporelles
    """
    
    def __init__(self):
        self.model = ARIMAModel()
    
    def get_forecast(self, steps: int = 12) -> Dict[str, Any]:
        """
        Obtient les prédictions pour les prochains mois
        
        Args:
            steps: Nombre de mois à prédire (par défaut: 12)
            
        Returns:
            Dictionnaire avec les prédictions et métadonnées
        """
        try:
            predictions = self.model.predict(steps=steps)
            historical_data = self.model.get_historical_data()
            model_info = self.model.get_model_info()
            
            return {
                "success": True,
                "predictions": predictions,
                "historical_data": historical_data,
                "model_info": model_info,
                "steps": steps
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "predictions": None,
                "historical_data": None,
                "model_info": None
            }
    
    def get_forecast_with_plot(self, steps: int = 12) -> Dict[str, Any]:
        """
        Obtient les prédictions avec un graphique
        
        Args:
            steps: Nombre de mois à prédire
            
        Returns:
            Dictionnaire avec prédictions et graphique en base64
        """
        try:
            result = self.get_forecast(steps)
            
            if result["success"]:
                # Générer le graphique
                plot_base64 = self.model.generate_plot(result["predictions"])
                result["plot"] = plot_base64
            
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "plot": None
            }
    
    def get_model_status(self) -> Dict[str, Any]:
        """
        Vérifie le statut du modèle
        """
        try:
            model_info = self.model.get_model_info()
            is_loaded = self.model.model is not None
            
            return {
                "success": True,
                "model_loaded": is_loaded,
                "model_info": model_info
            }
        except Exception as e:
            return {
                "success": False,
                "model_loaded": False,
                "error": str(e)
            }
