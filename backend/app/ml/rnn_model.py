"""RNN (LSTM) model for forex prediction."""

import os
from typing import List
import numpy as np

from app.ml.base_model import BaseForexModel


class RNNModel(BaseForexModel):
    """LSTM-based Recurrent Neural Network for forex prediction.

    Architecture:
    - Input: Sequence of 28 timesteps with 28 features
    - 2 stacked LSTM layers (128 units each)
    - Dropout between layers (0.2)
    - Dense output layer
    - Output: Single price prediction
    """

    def __init__(self, version: str = "1.0.0"):
        super().__init__(model_id="rnn", version=version)
        self._input_shape = [28, 28]  # (timesteps, features)

    def load(self, model_path: str) -> None:
        """Load RNN model from disk."""
        try:
            import tensorflow as tf

            architecture_path = os.path.join(model_path, "RNN_architecture.json")
            weights_path = os.path.join(model_path, "RNN_weights.h5")

            if os.path.exists(architecture_path) and os.path.exists(weights_path):
                with open(architecture_path, "r") as f:
                    model_json = f.read()
                self.model = tf.keras.models.model_from_json(model_json)
                self.model.load_weights(weights_path)
                self._is_loaded = True
            else:
                self._create_mock_model()
        except ImportError:
            self._create_mock_model()

    def _create_mock_model(self) -> None:
        """Create a mock model for demo/testing."""
        self.model = None
        self._is_loaded = True

    def predict(self, data: np.ndarray) -> np.ndarray:
        """Generate predictions from RNN model."""
        if not self._is_loaded:
            raise RuntimeError("Model not loaded. Call load() first.")

        processed = self.preprocess(data)

        # Reshape for RNN input: (batch, timesteps, features)
        if len(processed.shape) == 1:
            processed = processed.reshape(1, 28, -1)
        elif len(processed.shape) == 2:
            processed = processed.reshape(-1, 28, 28)

        if self.model is not None:
            predictions = self.model.predict(processed, verbose=0)
        else:
            predictions = self._mock_predict(data)

        return predictions.flatten()

    def _mock_predict(self, data: np.ndarray) -> np.ndarray:
        """Generate mock predictions using trend analysis."""
        if len(data.shape) > 1:
            # Use close prices (assuming last column)
            prices = data[:, -1] if data.shape[1] > 0 else data[:, 0]
        else:
            prices = data

        # Simple trend prediction
        if len(prices) >= 2:
            trend = (prices[-1] - prices[-2]) / prices[-2] if prices[-2] != 0 else 0
            prediction = prices[-1] * (1 + trend * 0.5)
        else:
            prediction = prices[-1]

        # Add small noise
        noise = np.random.uniform(-0.002, 0.002)
        return np.array([prediction * (1 + noise)])

    def get_input_shape(self) -> List[int]:
        """Get expected input shape."""
        return self._input_shape

    def get_metadata(self) -> dict:
        """Get model metadata."""
        base = super().get_metadata()
        base.update({
            "model_type": "rnn",
            "description": "LSTM-based Recurrent Neural Network for forex prediction",
            "architecture": {
                "lstm_layers": 2,
                "units_per_layer": 128,
                "dropout": 0.2,
            },
        })
        return base
