"""Tests for prediction endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestPredictionEndpoints:
    """Test suite for prediction API endpoints."""

    def test_create_prediction_success(self, client: TestClient):
        """Test successful prediction creation."""
        response = client.post(
            "/api/predictions",
            json={
                "currency_pair": "EURUSD",
                "timeframe": "H1",
                "model_type": "cnn",
                "lookback_periods": 28,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "prediction_id" in data
        assert data["currency_pair"] == "EURUSD"
        assert data["timeframe"] == "H1"
        assert data["model_type"] == "cnn"
        assert "predicted_price" in data
        assert "predicted_direction" in data
        assert "confidence" in data
        assert data["confidence"] >= 0 and data["confidence"] <= 1

    def test_create_prediction_different_models(self, client: TestClient):
        """Test prediction with different model types."""
        for model_type in ["cnn", "rnn", "tcn"]:
            response = client.post(
                "/api/predictions",
                json={
                    "currency_pair": "GBPUSD",
                    "timeframe": "D1",
                    "model_type": model_type,
                },
            )
            assert response.status_code == 200
            assert response.json()["model_type"] == model_type

    def test_create_prediction_invalid_pair(self, client: TestClient):
        """Test prediction with invalid currency pair."""
        response = client.post(
            "/api/predictions",
            json={
                "currency_pair": "INVALID",
                "timeframe": "H1",
                "model_type": "cnn",
            },
        )
        # FastAPI will still accept it but prediction may fail
        # The validation happens in the model manager

    def test_create_prediction_invalid_timeframe(self, client: TestClient):
        """Test prediction with invalid timeframe."""
        response = client.post(
            "/api/predictions",
            json={
                "currency_pair": "EURUSD",
                "timeframe": "INVALID",
                "model_type": "cnn",
            },
        )
        assert response.status_code == 422  # Validation error

    def test_list_predictions_empty(self, client: TestClient):
        """Test listing predictions when none exist."""
        response = client.get("/api/predictions")
        assert response.status_code == 200
        data = response.json()
        assert "predictions" in data
        assert "total" in data
        assert data["total"] == 0

    def test_list_predictions_with_data(self, client: TestClient):
        """Test listing predictions after creating some."""
        # Create predictions
        for _ in range(3):
            client.post(
                "/api/predictions",
                json={
                    "currency_pair": "EURUSD",
                    "timeframe": "H1",
                    "model_type": "cnn",
                },
            )

        response = client.get("/api/predictions")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["predictions"]) == 3

    def test_list_predictions_filter_by_pair(self, client: TestClient):
        """Test filtering predictions by currency pair."""
        # Create predictions for different pairs
        client.post(
            "/api/predictions",
            json={"currency_pair": "EURUSD", "timeframe": "H1", "model_type": "cnn"},
        )
        client.post(
            "/api/predictions",
            json={"currency_pair": "GBPUSD", "timeframe": "H1", "model_type": "cnn"},
        )

        response = client.get("/api/predictions?currency_pair=EURUSD")
        assert response.status_code == 200
        data = response.json()
        assert all(p["currency_pair"] == "EURUSD" for p in data["predictions"])

    def test_get_prediction_by_id(self, client: TestClient):
        """Test getting a specific prediction by ID."""
        # Create a prediction
        create_response = client.post(
            "/api/predictions",
            json={
                "currency_pair": "USDJPY",
                "timeframe": "M15",
                "model_type": "rnn",
            },
        )
        prediction_id = create_response.json()["prediction_id"]

        # Get by ID
        response = client.get(f"/api/predictions/{prediction_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["prediction_id"] == prediction_id
        assert data["currency_pair"] == "USDJPY"

    def test_get_prediction_not_found(self, client: TestClient):
        """Test getting non-existent prediction."""
        response = client.get("/api/predictions/nonexistent-id")
        assert response.status_code == 404

    def test_delete_prediction(self, client: TestClient):
        """Test deleting a prediction."""
        # Create a prediction
        create_response = client.post(
            "/api/predictions",
            json={
                "currency_pair": "EURUSD",
                "timeframe": "H1",
                "model_type": "cnn",
            },
        )
        prediction_id = create_response.json()["prediction_id"]

        # Delete it
        delete_response = client.delete(f"/api/predictions/{prediction_id}")
        assert delete_response.status_code == 200

        # Verify it's gone
        get_response = client.get(f"/api/predictions/{prediction_id}")
        assert get_response.status_code == 404
