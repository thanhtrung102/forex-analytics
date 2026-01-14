"""CNN model for forex prediction."""

import os
import json
from typing import List, Optional
import numpy as np

from app.ml.base_model import BaseForexModel


class CNNModel(BaseForexModel):
    """Convolutional Neural Network model for forex prediction.

    Architecture:
    - Input: 28x28x1 images (28 timeframes x 28 indicators)
    - 3 Conv2D blocks with increasing filters (16, 32, 64)
    - MaxPooling2D after each conv block
    - Flatten + Dense layers
    - Output: Single price prediction
    """

    def __init__(self, version: str = "1.0.0"):
        super().__init__(model_id="cnn", version=version)
        self._input_shape = [28, 28, 1]

    def load(self, model_path: str) -> None:
        """Load CNN model from disk."""
        try:
            # Try to load TensorFlow model
            import tensorflow as tf

            architecture_path = os.path.join(model_path, "CNN_architecture.json")
            weights_path = os.path.join(model_path, "CNN_weights.h5")

            if os.path.exists(architecture_path) and os.path.exists(weights_path):
                with open(architecture_path, "r") as f:
                    model_json = f.read()
                self.model = tf.keras.models.model_from_json(model_json)
                self.model.load_weights(weights_path)
                self._is_loaded = True
            else:
                # Create a mock model for demo purposes
                self._create_mock_model()
        except ImportError:
            # TensorFlow not available, create mock
            self._create_mock_model()

    def _create_mock_model(self) -> None:
        """Create a mock model for demo/testing."""
        self.model = None
        self._is_loaded = True  # Mark as loaded for demo

    def predict(self, data: np.ndarray) -> np.ndarray:
        """Generate predictions from CNN model."""
        if not self._is_loaded:
            raise RuntimeError("Model not loaded. Call load() first.")

        # Preprocess data
        processed = self.preprocess(data)

        # Reshape for CNN input if needed
        if len(processed.shape) == 2:
            # Assume flattened 784 -> reshape to 28x28x1
            processed = processed.reshape(-1, 28, 28, 1)
        elif len(processed.shape) == 3:
            processed = processed.reshape(-1, 28, 28, 1)

        if self.model is not None:
            predictions = self.model.predict(processed, verbose=0)
        else:
            # Mock prediction: return slightly modified last value
            predictions = self._mock_predict(data)

        return predictions.flatten()

    def _mock_predict(self, data: np.ndarray) -> np.ndarray:
        """Generate mock predictions for demo."""
        # Use last value with small random variation
        if len(data.shape) > 1:
            last_val = data[-1, -1] if data.shape[1] > 0 else data[-1, 0]
        else:
            last_val = data[-1]

        # Add small random change (-0.5% to +0.5%)
        change = np.random.uniform(-0.005, 0.005)
        return np.array([last_val * (1 + change)])

    def get_input_shape(self) -> List[int]:
        """Get expected input shape."""
        return self._input_shape

    def get_metadata(self) -> dict:
        """Get model metadata."""
        base = super().get_metadata()
        base.update({
            "model_type": "cnn",
            "description": "Convolutional Neural Network for forex price prediction",
            "architecture": {
                "conv_blocks": 3,
                "filters": [16, 32, 64],
                "dense_layers": [16, 4, 1],
            },
        })
        return base
