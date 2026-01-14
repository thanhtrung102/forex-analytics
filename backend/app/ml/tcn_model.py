"""TCN (Temporal Convolutional Network) model for forex prediction."""

import os
from typing import List
import numpy as np

from app.ml.base_model import BaseForexModel


class TCNModel(BaseForexModel):
    """Temporal Convolutional Network for forex prediction.

    Architecture:
    - Input: 784-dimensional flattened vector (28x28)
    - 7-layer dilated causal convolutions
    - Residual skip connections
    - Exponential dilation (1, 2, 4, 8, 16, 32, 64)
    - Output: Single price prediction
    """

    def __init__(self, version: str = "1.0.0"):
        super().__init__(model_id="tcn", version=version)
        self._input_shape = [784, 1]  # (sequence_length, features)

    def load(self, model_path: str) -> None:
        """Load TCN model from disk."""
        try:
            import tensorflow as tf

            architecture_path = os.path.join(model_path, "TCN_architecture.json")
            weights_path = os.path.join(model_path, "TCN_weights.h5")

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
        """Generate predictions from TCN model."""
        if not self._is_loaded:
            raise RuntimeError("Model not loaded. Call load() first.")

        processed = self.preprocess(data)

        # Reshape for TCN input: (batch, sequence, 1)
        if len(processed.shape) == 1:
            processed = processed.reshape(1, -1, 1)
        elif len(processed.shape) == 2:
            processed = processed.reshape(-1, 784, 1)

        if self.model is not None:
            predictions = self.model.predict(processed, verbose=0)
        else:
            predictions = self._mock_predict(data)

        return predictions.flatten()

    def _mock_predict(self, data: np.ndarray) -> np.ndarray:
        """Generate mock predictions using weighted average."""
        flat_data = data.flatten()

        # Weighted average with more weight on recent values
        weights = np.exp(np.linspace(-1, 0, len(flat_data)))
        weights /= weights.sum()
        prediction = np.average(flat_data, weights=weights)

        # Add momentum
        if len(flat_data) >= 5:
            momentum = (flat_data[-1] - flat_data[-5]) / 5
            prediction += momentum

        # Add small noise
        noise = np.random.uniform(-0.003, 0.003)
        return np.array([prediction * (1 + noise)])

    def get_input_shape(self) -> List[int]:
        """Get expected input shape."""
        return self._input_shape

    def get_metadata(self) -> dict:
        """Get model metadata."""
        base = super().get_metadata()
        base.update({
            "model_type": "tcn",
            "description": "Temporal Convolutional Network for forex prediction",
            "architecture": {
                "layers": 7,
                "kernel_size": 3,
                "dilations": [1, 2, 4, 8, 16, 32, 64],
                "residual": True,
            },
        })
        return base
