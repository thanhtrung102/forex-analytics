/**
 * Tests for the centralized API client.
 */

import api, { PredictionInput, BacktestInput } from '../src/lib/api';

// Mock fetch globally
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('API Client', () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  describe('Health Check', () => {
    it('should check API health', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'healthy', version: '1.0.0' }),
      });

      const result = await api.health.check();

      expect(result.status).toBe('healthy');
      expect(result.version).toBeDefined();
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/health'),
        expect.any(Object)
      );
    });
  });

  describe('Models', () => {
    it('should list available models', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          models: [
            { model_id: 'cnn', model_type: 'cnn', version: '1.0.0' },
            { model_id: 'rnn', model_type: 'rnn', version: '1.0.0' },
            { model_id: 'tcn', model_type: 'tcn', version: '1.0.0' },
          ],
          total: 3,
        }),
      });

      const result = await api.models.list();

      expect(result.models).toHaveLength(3);
      expect(result.total).toBe(3);
    });

    it('should get model info by id', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          model_id: 'cnn',
          model_type: 'cnn',
          version: '1.0.0',
          description: 'Convolutional Neural Network',
          input_shape: [28, 28, 1],
          supported_pairs: ['EURUSD', 'GBPUSD'],
          supported_timeframes: ['H1', 'D1'],
        }),
      });

      const result = await api.models.get('cnn');

      expect(result.model_id).toBe('cnn');
      expect(result.input_shape).toEqual([28, 28, 1]);
    });
  });

  describe('Predictions', () => {
    it('should create a prediction', async () => {
      const input: PredictionInput = {
        currency_pair: 'EURUSD',
        timeframe: 'H1',
        model_type: 'cnn',
        lookback_periods: 28,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          prediction_id: '123e4567-e89b-12d3-a456-426614174000',
          currency_pair: 'EURUSD',
          timeframe: 'H1',
          predicted_price: 1.0855,
          predicted_direction: 'UP',
          confidence: 0.85,
          model_type: 'cnn',
          model_version: '1.0.0',
          created_at: '2024-01-15T10:00:00Z',
        }),
      });

      const result = await api.predictions.create(input);

      expect(result.prediction_id).toBeDefined();
      expect(result.currency_pair).toBe('EURUSD');
      expect(result.predicted_direction).toBe('UP');
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/predictions'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(input),
        })
      );
    });

    it('should get a prediction by id', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          prediction_id: '123',
          currency_pair: 'EURUSD',
          predicted_direction: 'DOWN',
        }),
      });

      const result = await api.predictions.get('123');

      expect(result.prediction_id).toBe('123');
    });

    it('should list predictions with pagination', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          predictions: [{ prediction_id: '1' }, { prediction_id: '2' }],
          total: 10,
          page: 1,
          page_size: 2,
        }),
      });

      const result = await api.predictions.list({ page: 1, page_size: 2 });

      expect(result.predictions).toHaveLength(2);
      expect(result.total).toBe(10);
    });
  });

  describe('Backtest', () => {
    it('should run a backtest', async () => {
      const input: BacktestInput = {
        currency_pair: 'GBPUSD',
        timeframe: 'H4',
        model_type: 'rnn',
        start_date: '2024-01-01',
        end_date: '2024-01-14',
        initial_balance: 10000,
        leverage: 100,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          backtest_id: 'bt-123',
          currency_pair: 'GBPUSD',
          total_trades: 50,
          winning_trades: 30,
          losing_trades: 20,
          win_rate: 0.6,
          total_profit_loss: 500,
          max_drawdown: 0.15,
        }),
      });

      const result = await api.backtest.run(input);

      expect(result.backtest_id).toBe('bt-123');
      expect(result.win_rate).toBe(0.6);
      expect(result.total_trades).toBe(50);
    });

    it('should list backtests', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          backtests: [{ backtest_id: 'bt-1' }, { backtest_id: 'bt-2' }],
          total: 2,
        }),
      });

      const result = await api.backtest.list();

      expect(result.backtests).toHaveLength(2);
    });
  });

  describe('Indicators', () => {
    it('should get indicators for a pair', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          currency_pair: 'EURUSD',
          timeframe: 'H1',
          indicators: {
            rsi: [{ timestamp: '2024-01-15T10:00:00Z', value: 55 }],
            macd: [{ timestamp: '2024-01-15T10:00:00Z', value: 0.0012 }],
          },
          generated_at: '2024-01-15T10:00:00Z',
        }),
      });

      const result = await api.indicators.get('EURUSD', 'H1', {
        indicators: 'rsi,macd',
      });

      expect(result.currency_pair).toBe('EURUSD');
      expect(result.indicators.rsi).toBeDefined();
      expect(result.indicators.macd).toBeDefined();
    });

    it('should list available indicators', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          indicators: ['rsi', 'macd', 'sma', 'ema'],
          categories: {
            moving_averages: ['sma', 'ema'],
            momentum: ['rsi', 'macd'],
          },
        }),
      });

      const result = await api.indicators.list();

      expect(result.indicators).toContain('rsi');
      expect(result.categories.momentum).toContain('rsi');
    });
  });

  describe('Metrics', () => {
    it('should get performance metrics', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          total_predictions: 100,
          total_trades: 50,
          total_backtests: 10,
          overall_win_rate: 0.65,
          total_profit_loss: 1500,
          best_performing_pair: 'EURUSD',
          best_performing_model: 'cnn',
        }),
      });

      const result = await api.metrics.get();

      expect(result.total_predictions).toBe(100);
      expect(result.overall_win_rate).toBe(0.65);
    });

    it('should get summary metrics', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          counts: {
            predictions: 100,
            trades: 50,
            backtests: 10,
          },
          recent_predictions: [],
          recent_backtests: [],
        }),
      });

      const result = await api.metrics.summary();

      expect(result.counts.predictions).toBe(100);
    });
  });

  describe('Error Handling', () => {
    it('should handle API errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: async () => ({ detail: 'Model not found' }),
      });

      await expect(api.models.get('nonexistent')).rejects.toMatchObject({
        detail: 'Model not found',
        status: 404,
      });
    });

    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(api.health.check()).rejects.toThrow('Network error');
    });
  });
});
