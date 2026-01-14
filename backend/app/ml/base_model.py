"""Base class for forex prediction models."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import numpy as np


class BaseForexModel(ABC):
    """Abstract base class for all forex prediction models."""

    def __init__(self, model_id: str, version: str = "1.0.0"):
        self.model_id = model_id
        self.version = version
        self.model = None
        self._is_loaded = False

    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._is_loaded

    @abstractmethod
    def load(self, model_path: str) -> None:
        """Load model from disk.

        Args:
            model_path: Path to model files
        """
        pass

    @abstractmethod
    def predict(self, data: np.ndarray) -> np.ndarray:
        """Generate predictions from input data.

        Args:
            data: Input data array

        Returns:
            Predicted values
        """
        pass

    @abstractmethod
    def get_input_shape(self) -> List[int]:
        """Get expected input shape for the model.

        Returns:
            List of dimensions
        """
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """Get model metadata.

        Returns:
            Dictionary containing model information
        """
        return {
            "model_id": self.model_id,
            "version": self.version,
            "is_loaded": self._is_loaded,
            "input_shape": self.get_input_shape(),
        }

    def preprocess(self, data: np.ndarray) -> np.ndarray:
        """Preprocess input data before prediction.

        Args:
            data: Raw input data

        Returns:
            Preprocessed data
        """
        # Default: normalize to 0-1 range
        data_min = np.min(data)
        data_max = np.max(data)
        if data_max - data_min > 0:
            return (data - data_min) / (data_max - data_min)
        return data

    def postprocess(self, predictions: np.ndarray, original_data: np.ndarray) -> np.ndarray:
        """Postprocess predictions to original scale.

        Args:
            predictions: Model predictions
            original_data: Original input data for scale reference

        Returns:
            Scaled predictions
        """
        # Default: scale back using original data range
        data_min = np.min(original_data)
        data_max = np.max(original_data)
        return predictions * (data_max - data_min) + data_min
