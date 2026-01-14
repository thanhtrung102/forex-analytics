"""API routes for ML model management."""

from fastapi import APIRouter, HTTPException

from app.api.dependencies import ModelManagerDep
from app.db.schemas import ModelInfo, ModelListResponse

router = APIRouter()


@router.get("", response_model=ModelListResponse)
async def list_models(model_manager: ModelManagerDep):
    """List all available ML models."""
    models = model_manager.list_models()
    return ModelListResponse(models=models, total=len(models))


@router.get("/{model_id}", response_model=ModelInfo)
async def get_model(model_id: str, model_manager: ModelManagerDep):
    """Get detailed information about a specific model."""
    model_info = model_manager.get_model_info(model_id)
    if model_info is None:
        raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")
    return model_info


@router.post("/{model_id}/reload")
async def reload_model(model_id: str, model_manager: ModelManagerDep):
    """Reload a specific model from disk."""
    try:
        model_manager.reload_model(model_id)
        return {"status": "success", "message": f"Model {model_id} reloaded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
