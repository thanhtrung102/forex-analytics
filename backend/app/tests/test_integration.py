"""Integration tests for the forex analytics API."""

import pytest
from fastapi.testclient import TestClient


class TestHealthAndRoot:
    """Test health check and root endpoints."""

    def test_health_check(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data


class TestModelsEndpoints:
    """Test ML models management endpoints."""

    def test_list_models(self, client: TestClient):
        """Test listing available models."""
        response = client.get("/api/models")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert "total" in data
        assert data["total"] >= 3  # CNN, RNN, TCN

    def test_get_model_info(self, client: TestClient):
        """Test getting model information."""
        response = client.get("/api/models/cnn")
        assert response.status_code == 200
        data = response.json()
        assert data["model_id"] == "cnn"
        assert "input_shape" in data
        assert "supported_pairs" in data

    def test_get_model_not_found(self, client: TestClient):
        """Test getting non-existent model."""
        response = client.get("/api/models/nonexistent")
        assert response.status_code == 404


class TestIndicatorsEndpoints:
    """Test technical indicators endpoints."""

    def test_get_indicators(self, client: TestClient):
        """Test getting indicators for a pair."""
        response = client.get("/api/indicators/EURUSD/H1?periods=50")
        assert response.status_code == 200
        data = response.json()
        assert data["currency_pair"] == "EURUSD"
        assert data["timeframe"] == "H1"
        assert "indicators" in data
        assert len(data["indicators"]) > 0

    def test_get_specific_indicators(self, client: TestClient):
        """Test getting specific indicators."""
        response = client.get("/api/indicators/GBPUSD/D1?indicators=rsi,macd,sma")
        assert response.status_code == 200
        data = response.json()
        assert "rsi" in data["indicators"]
        assert "macd" in data["indicators"]
        assert "sma" in data["indicators"]

    def test_list_available_indicators(self, client: TestClient):
        """Test listing available indicators."""
        response = client.get("/api/indicators/list")
        assert response.status_code == 200
        data = response.json()
        assert "indicators" in data
        assert "categories" in data
        assert "moving_averages" in data["categories"]
        assert "momentum" in data["categories"]


class TestMetricsEndpoints:
    """Test metrics and analytics endpoints."""

    def test_get_metrics(self, client: TestClient):
        """Test getting overall metrics."""
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "total_predictions" in data
        assert "total_trades" in data
        assert "total_backtests" in data
        assert "overall_win_rate" in data

    def test_get_summary(self, client: TestClient):
        """Test getting summary metrics."""
        response = client.get("/api/metrics/summary")
        assert response.status_code == 200
        data = response.json()
        assert "counts" in data
        assert "recent_predictions" in data
        assert "recent_backtests" in data


@pytest.mark.integration
class TestFullWorkflow:
    """Integration tests for complete workflows."""

    def test_prediction_workflow(self, client: TestClient):
        """Test complete prediction workflow."""
        # 1. List available models
        models_response = client.get("/api/models")
        assert models_response.status_code == 200
        models = models_response.json()["models"]
        assert len(models) > 0

        # 2. Create a prediction
        pred_response = client.post(
            "/api/predictions",
            json={
                "currency_pair": "EURUSD",
                "timeframe": "H1",
                "model_type": "cnn",
            },
        )
        assert pred_response.status_code == 200
        prediction = pred_response.json()
        prediction_id = prediction["prediction_id"]

        # 3. Retrieve the prediction
        get_response = client.get(f"/api/predictions/{prediction_id}")
        assert get_response.status_code == 200
        assert get_response.json()["prediction_id"] == prediction_id

        # 4. List predictions
        list_response = client.get("/api/predictions")
        assert list_response.status_code == 200
        assert list_response.json()["total"] >= 1

        # 5. Check metrics
        metrics_response = client.get("/api/metrics")
        assert metrics_response.status_code == 200
        assert metrics_response.json()["total_predictions"] >= 1

    def test_backtest_workflow(self, client: TestClient):
        """Test complete backtesting workflow."""
        # 1. Run backtest
        backtest_response = client.post(
            "/api/backtest",
            json={
                "currency_pair": "GBPUSD",
                "timeframe": "H4",
                "model_type": "rnn",
                "start_date": "2024-01-01",
                "end_date": "2024-01-14",
                "initial_balance": 5000.0,
                "leverage": 50,
            },
        )
        assert backtest_response.status_code == 200
        backtest = backtest_response.json()
        backtest_id = backtest["backtest_id"]

        # 2. Verify results
        assert "total_trades" in backtest
        assert "win_rate" in backtest
        assert "max_drawdown" in backtest

        # 3. Get backtest details
        get_response = client.get(f"/api/backtest/{backtest_id}")
        assert get_response.status_code == 200

        # 4. Get trades from backtest
        trades_response = client.get(f"/api/backtest/{backtest_id}/trades")
        assert trades_response.status_code == 200

        # 5. List all backtests
        list_response = client.get("/api/backtest")
        assert list_response.status_code == 200
        assert list_response.json()["total"] >= 1

    def test_indicators_with_prediction(self, client: TestClient):
        """Test using indicators alongside predictions."""
        # 1. Get indicators for a pair
        ind_response = client.get("/api/indicators/USDJPY/H1?indicators=rsi,macd")
        assert ind_response.status_code == 200
        indicators = ind_response.json()["indicators"]

        # 2. Make prediction for same pair
        pred_response = client.post(
            "/api/predictions",
            json={
                "currency_pair": "USDJPY",
                "timeframe": "H1",
                "model_type": "tcn",
            },
        )
        assert pred_response.status_code == 200

        # Both should work together in a real trading scenario
        assert "rsi" in indicators
        assert pred_response.json()["predicted_direction"] in ["UP", "DOWN", "NEUTRAL"]
