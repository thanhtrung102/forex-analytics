"""Tests for trade endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestTradeEndpoints:
    """Test suite for trade API endpoints."""

    def test_list_trades_empty(self, client: TestClient):
        """Test listing trades when none exist."""
        response = client.get("/api/trades")
        assert response.status_code == 200
        data = response.json()
        assert "trades" in data
        assert "total" in data
        assert data["total"] == 0

    def test_get_trade_not_found(self, client: TestClient):
        """Test getting non-existent trade."""
        response = client.get("/api/trades/nonexistent-id")
        assert response.status_code == 404

    def test_get_trades_summary(self, client: TestClient):
        """Test getting trades summary by pair."""
        response = client.get("/api/trades/summary/by-pair")
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data


class TestBacktestEndpoints:
    """Test suite for backtest API endpoints."""

    def test_run_backtest_success(self, client: TestClient):
        """Test running a backtest."""
        response = client.post(
            "/api/backtest",
            json={
                "currency_pair": "EURUSD",
                "timeframe": "H1",
                "model_type": "cnn",
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "initial_balance": 10000.0,
                "leverage": 100,
                "risk_factor": 1.0,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "backtest_id" in data
        assert data["currency_pair"] == "EURUSD"
        assert "total_trades" in data
        assert "win_rate" in data
        assert "final_balance" in data

    def test_run_backtest_different_models(self, client: TestClient):
        """Test backtesting with different models."""
        for model_type in ["cnn", "rnn", "tcn"]:
            response = client.post(
                "/api/backtest",
                json={
                    "currency_pair": "GBPUSD",
                    "timeframe": "D1",
                    "model_type": model_type,
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-15",
                },
            )
            assert response.status_code == 200
            assert response.json()["model_type"] == model_type

    def test_list_backtests(self, client: TestClient):
        """Test listing backtest runs."""
        # Run a backtest first
        client.post(
            "/api/backtest",
            json={
                "currency_pair": "EURUSD",
                "timeframe": "H1",
                "model_type": "cnn",
                "start_date": "2024-01-01",
                "end_date": "2024-01-07",
            },
        )

        response = client.get("/api/backtest")
        assert response.status_code == 200
        data = response.json()
        assert "backtests" in data
        assert len(data["backtests"]) >= 1

    def test_get_backtest_by_id(self, client: TestClient):
        """Test getting a specific backtest by ID."""
        # Run a backtest
        create_response = client.post(
            "/api/backtest",
            json={
                "currency_pair": "USDJPY",
                "timeframe": "M30",
                "model_type": "tcn",
                "start_date": "2024-02-01",
                "end_date": "2024-02-07",
            },
        )
        backtest_id = create_response.json()["backtest_id"]

        # Get by ID
        response = client.get(f"/api/backtest/{backtest_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["backtest_id"] == backtest_id
        assert data["currency_pair"] == "USDJPY"

    def test_get_backtest_trades(self, client: TestClient):
        """Test getting trades from a backtest."""
        # Run a backtest
        create_response = client.post(
            "/api/backtest",
            json={
                "currency_pair": "EURUSD",
                "timeframe": "H1",
                "model_type": "cnn",
                "start_date": "2024-01-01",
                "end_date": "2024-01-14",
            },
        )
        backtest_id = create_response.json()["backtest_id"]

        # Get trades
        response = client.get(f"/api/backtest/{backtest_id}/trades")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_backtest_not_found(self, client: TestClient):
        """Test getting non-existent backtest."""
        response = client.get("/api/backtest/nonexistent-id")
        assert response.status_code == 404
