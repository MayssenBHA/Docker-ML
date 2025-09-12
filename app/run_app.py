#!/usr/bin/env python3
"""
Script de lancement pour l'application FastAPI
Ce script peut être exécuté depuis le dossier app/
"""
import sys
import os

# Ajouter le répertoire parent au PATH pour permettre les imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Maintenant importer et lancer l'application
if __name__ == "__main__":
    import uvicorn
    
    # Lancer l'application
    print("🚀 Démarrage de l'application FastAPI...")
    print("📍 URL: http://localhost:8000")
    print("📁 Interface d'upload CSV disponible à la racine")
    print("⏹️  Appuyez sur Ctrl+C pour arrêter\n")
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
