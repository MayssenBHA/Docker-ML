from fastapi import FastAPI, Request, Form, HTTPException, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from app.services.forecast_service import ForecastService
from app.services.custom_data_service import CustomDataForecastService
import os
from typing import Optional

# Créer l'application FastAPI
app = FastAPI(
    title="Time Series Forecasting API",
    description="API de prédiction de séries temporelles avec ARIMA",
    version="1.0.0"
)

# Configuration des templates et fichiers statiques
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)

templates = Jinja2Templates(directory=os.path.join(project_dir, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")

# Initialiser les services
forecast_service = ForecastService()
custom_data_service = CustomDataForecastService()

@app.on_event("startup")
async def startup_event():
    """Vérifier le modèle au démarrage"""
    status = forecast_service.get_model_status()
    if not status["model_loaded"]:
        print("⚠️  Attention: Modèle non chargé!")
        print("📝 Veuillez exécuter: python scripts/train_model.py")
    else:
        print("✅ Modèle chargé avec succès!")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Page d'accueil"""
    status = forecast_service.get_model_status()
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request,
            "model_loaded": status["model_loaded"],
            "model_info": status.get("model_info", {})
        }
    )

@app.get("/api/status")
async def get_status():
    """API pour vérifier le statut du modèle"""
    return forecast_service.get_model_status()

@app.post("/api/forecast")
async def create_forecast(steps: int = Form(12)):
    """API pour créer des prédictions"""
    if steps < 1 or steps > 60:
        raise HTTPException(status_code=400, detail="Le nombre de mois doit être entre 1 et 60")
    
    result = forecast_service.get_forecast_with_plot(steps)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Erreur inconnue"))
    
    return result

@app.get("/api/forecast/{steps}")
async def get_forecast(steps: int):
    """API GET pour les prédictions"""
    if steps < 1 or steps > 60:
        raise HTTPException(status_code=400, detail="Le nombre de mois doit être entre 1 et 60")
    
    result = forecast_service.get_forecast(steps)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Erreur inconnue"))
    
    return result

@app.post("/forecast", response_class=HTMLResponse)
async def forecast_form(request: Request, steps: int = Form(12)):
    """Formulaire de prédiction"""
    result = forecast_service.get_forecast_with_plot(steps)
    
    status = forecast_service.get_model_status()
    
    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "result": result,
            "steps": steps,
            "model_info": status.get("model_info", {})
        }
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "time-series-forecasting"}

@app.post("/upload-csv", response_class=HTMLResponse)
async def upload_csv(request: Request, csv_file: UploadFile = File(...)):
    """Upload et analyse d'un fichier CSV personnalisé"""
    try:
        # Validation du fichier
        if not csv_file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Le fichier doit être au format CSV")
        
        if csv_file.size > 5 * 1024 * 1024:  # 5MB max
            raise HTTPException(status_code=400, detail="Le fichier est trop volumineux (max 5MB)")
        
        # Lire le contenu du fichier
        csv_content = await csv_file.read()
        
        # Valider et traiter les données
        validation_result = custom_data_service.validate_and_process_csv(csv_content)
        
        if not validation_result["success"]:
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "model_loaded": True,
                    "model_info": {},
                    "upload_error": validation_result["error"]
                }
            )
        
        # Rediriger vers la page de prédiction personnalisée
        return templates.TemplateResponse(
            "custom_data_analysis.html",
            {
                "request": request,
                "data_info": validation_result["data_info"],
                "upload_success": True,
                "filename": csv_file.filename
            }
        )
        
    except Exception as e:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "model_loaded": True,
                "model_info": {},
                "upload_error": f"Erreur lors du traitement: {str(e)}"
            }
        )

@app.post("/predict-custom-data", response_class=HTMLResponse)
async def predict_custom_data(request: Request, steps: int = Form(12)):
    """Génère des prédictions pour les données uploadées"""
    try:
        if steps < 1 or steps > 100:
            raise HTTPException(status_code=400, detail="Le nombre de périodes doit être entre 1 et 100")
        
        # Générer les prédictions
        result = custom_data_service.train_model_and_predict(steps)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Erreur inconnue"))
        
        # Générer le graphique
        plot_base64 = custom_data_service.generate_plot(
            result["predictions"], 
            result["historical_data"]
        )
        result["plot"] = plot_base64
        
        return templates.TemplateResponse(
            "custom_results.html",
            {
                "request": request,
                "result": result,
                "steps": steps,
                "model_info": result["model_info"]
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/custom-status")
async def get_custom_status():
    """API pour vérifier le statut des données personnalisées"""
    has_data = custom_data_service.data is not None
    return {
        "success": True,
        "has_custom_data": has_data,
        "data_info": custom_data_service.model_info if has_data else None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
