"""
ML Training Job - Runs nightly via GitHub Actions
Demonstrates: Simple model training (demo only)
"""

import os
import json
import pickle
from datetime import datetime

def train_model():
    print(f"[{datetime.utcnow().isoformat()}] Starting ML training...")
    
    # Demo: Create a simple "model" (in reality, this would be sklearn/pytorch/etc)
    model = {
        "type": "demo_forecasting_model",
        "version": datetime.utcnow().strftime("%Y%m%d_%H%M%S"),
        "trained_at": datetime.utcnow().isoformat(),
        "parameters": {
            "learning_rate": 0.01,
            "epochs": 100,
            "features": ["total_orders", "total_revenue", "days_since_signup"]
        },
        "metrics": {
            "mse": 0.023,
            "mae": 0.15,
            "r2": 0.87
        }
    }
    
    # Save model locally (will be uploaded to R2 in next step)
    os.makedirs("artifacts", exist_ok=True)
    model_path = "artifacts/model_latest.pkl"
    
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    
    # Also save metadata as JSON
    with open("artifacts/model_metadata.json", "w") as f:
        json.dump(model, f, indent=2)
    
    print(f"✓ Model trained and saved to {model_path}")
    print(f"  Version: {model['version']}")
    print(f"  Metrics: R² = {model['metrics']['r2']}")
    
    return True

if __name__ == "__main__":
    success = train_model()
    exit(0 if success else 1)
