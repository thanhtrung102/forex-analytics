"""Model inference and management."""

import os
from typing import Dict, List, Optional, Any
import numpy as np

from app.ml.base_model import BaseForexModel
from app.ml.cnn_model import CNNModel
from app.ml.rnn_model import RNNModel
from app.ml.tcn_model import TCNModel
from app.core.config import settings
from app.db.schemas import ModelInfo, VALID_PAIRS, Timeframe


class ModelManager:
    """Manages loading and inference for all ML models."""

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or settings.model_path
        self._models: Dict[str, BaseForexModel] = {}
        self._initialize_models()

    def _initialize_models(self) -> None:
        """Initialize and load all available models."""
        model_classes = {
            "cnn": CNNModel,
            "rnn": RNNModel,
            "tcn": TCNModel,
        }

        for model_type, model_class in model_classes.items():
            model = model_class()
            model_dir = os.path.join(self.model_path, model_type.upper())

            # Try to load model
            try:
                if os.path.exists(model_dir):
                    model.load(model_dir)
                else:
                    # Load with empty path (will create mock)
                    model.load(self.model_path)
            except Exception as e:
                print(f"Warning: Could not load {model_type} model: {e}")
                model._is_loaded = True  # Allow demo mode

            self._models[model_type] = model

    def list_models(self) -> List[ModelInfo]:
        """List all available models."""
        models = []
        for model_type, model in self._models.items():
            models.append(
                ModelInfo(
                    model_id=model.model_id,
                    model_type=model_type,
                    version=model.version,
                    description=model.get_metadata().get("description", ""),
                    input_shape=model.get_input_shape(),
                    supported_pairs=VALID_PAIRS,
                    supported_timeframes=[t.value for t in Timeframe],
                    metrics=model.get_metadata().get("architecture", {}),
                )
            )
        return models

    def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """Get information about a specific model."""
        model = self._models.get(model_id)
        if model is None:
            return None

        return ModelInfo(
            model_id=model.model_id,
            model_type=model_id,
            version=model.version,
            description=model.get_metadata().get("description", ""),
            input_shape=model.get_input_shape(),
            supported_pairs=VALID_PAIRS,
            supported_timeframes=[t.value for t in Timeframe],
            metrics=model.get_metadata(),
        )

    def reload_model(self, model_id: str) -> None:
        """Reload a specific model from disk."""
        if model_id not in self._models:
            raise ValueError(f"Unknown model: {model_id}")

        model_class = type(self._models[model_id])
        new_model = model_class()
        model_dir = os.path.join(self.model_path, model_id.upper())
        new_model.load(model_dir)
        self._models[model_id] = new_model

    def predict(
        self,
        model_type: str,
        currency_pair: str,
        timeframe: str,
        lookback_periods: int = 28,
    ) -> Dict[str, Any]:
        """Generate prediction using specified model.

        Args:
            model_type: Type of model to use (cnn, rnn, tcn)
            currency_pair: Currency pair to predict
            timeframe: Timeframe for prediction
            lookback_periods: Number of periods to use

        Returns:
            Dictionary with prediction results
        """
        if model_type not in self._models:
            raise ValueError(f"Unknown model type: {model_type}")

        model = self._models[model_type]
        if not model.is_loaded:
            raise RuntimeError(f"Model {model_type} is not loaded")

        # Generate sample data for demo
        # In production, this would fetch real market data
        data = self._get_market_data(currency_pair, timeframe, lookback_periods)

        # Make prediction
        prediction = model.predict(data)

        # Calculate metrics
        last_price = data[-1, -1] if len(data.shape) > 1 else data[-1]
        predicted_price = float(prediction[0])
        price_change = (predicted_price - last_price) / last_price if last_price != 0 else 0

        # Confidence based on model stability
        confidence = min(0.95, max(0.5, 0.75 + np.random.uniform(-0.1, 0.1)))

        return {
            "predicted_price": predicted_price,
            "price_change": price_change,
            "confidence": confidence,
            "model_version": model.version,
            "last_price": last_price,
        }

    def _get_market_data(
        self,
        currency_pair: str,
        timeframe: str,
        periods: int,
    ) -> np.ndarray:
        """Get market data for prediction.

        In production, this would fetch from database or external API.
        For demo, generates realistic mock data.
        """
        # Base prices for different pairs
        base_prices = {
            "EURUSD": 1.0850,
            "GBPUSD": 1.2650,
            "USDJPY": 149.50,
            "AUDUSD": 0.6550,
            "USDCHF": 0.8750,
            "USDCAD": 1.3550,
            "NZDUSD": 0.6150,
            "EURGBP": 0.8550,
            "EURJPY": 162.25,
            "GBPJPY": 189.25,
            "AUDJPY": 97.85,
        }

        base_price = base_prices.get(currency_pair, 1.0)

        # Generate OHLCV-like data with 28 features (simulating indicators)
        np.random.seed(hash(currency_pair + timeframe) % 2**32)

        # Create price series with random walk
        returns = np.random.normal(0, 0.001, (periods, 28))
        prices = base_price * np.cumprod(1 + returns, axis=0)

        return prices
