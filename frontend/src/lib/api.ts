/**
 * Centralized API client for backend communication.
 * All backend calls should go through this module.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Types
export interface ModelInfo {
  model_id: string;
  model_type: string;
  version: string;
  description: string;
  input_shape: number[];
  supported_pairs: string[];
  supported_timeframes: string[];
  metrics: Record<string, unknown>;
}

export interface PredictionInput {
  currency_pair: string;
  timeframe: string;
  model_type: string;
  lookback_periods?: number;
}

export interface PredictionOutput {
  prediction_id: string;
  currency_pair: string;
  timeframe: string;
  predicted_price: number;
  predicted_direction: 'UP' | 'DOWN' | 'NEUTRAL';
  confidence: number;
  model_type: string;
  model_version: string;
  created_at: string;
}

export interface BacktestInput {
  currency_pair: string;
  timeframe: string;
  model_type: string;
  start_date: string;
  end_date: string;
  initial_balance?: number;
  leverage?: number;
  risk_factor?: number;
}

export interface BacktestResult {
  backtest_id: string;
  currency_pair: string;
  timeframe: string;
  model_type: string;
  start_date: string;
  end_date: string;
  initial_balance: number;
  final_balance: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  total_profit_loss: number;
  win_rate: number;
  max_drawdown: number;
  sharpe_ratio: number | null;
  created_at: string;
}

export interface Trade {
  trade_id: string;
  prediction_id?: string;
  backtest_run_id?: string;
  currency_pair: string;
  trade_type: 'BUY' | 'SELL';
  entry_price: number;
  exit_price?: number;
  lot_size: number;
  leverage: number;
  take_profit?: number;
  stop_loss?: number;
  profit_loss?: number;
  profit_pips?: number;
  status: 'OPEN' | 'CLOSED' | 'CANCELLED';
  created_at: string;
  closed_at?: string;
}

export interface IndicatorData {
  timestamp: string;
  value: number;
}

export interface IndicatorsResponse {
  currency_pair: string;
  timeframe: string;
  indicators: Record<string, IndicatorData[]>;
  generated_at: string;
}

export interface PerformanceMetrics {
  total_predictions: number;
  total_trades: number;
  total_backtests: number;
  overall_win_rate: number;
  total_profit_loss: number;
  best_performing_pair?: string;
  best_performing_model?: string;
  metrics_by_pair: Record<string, unknown>;
  metrics_by_model: Record<string, unknown>;
  generated_at: string;
}

export interface ApiError {
  detail: string;
  status: number;
}

// Helper function for API requests
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;

  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
  };

  const response = await fetch(url, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error: ApiError = {
      detail: `API Error: ${response.statusText}`,
      status: response.status,
    };
    try {
      const data = await response.json();
      error.detail = data.detail || error.detail;
    } catch {
      // Use default error message
    }
    throw error;
  }

  return response.json();
}

// API client object with all endpoints
export const api = {
  // Health check
  health: {
    check: () => apiRequest<{ status: string; version: string }>('/health'),
  },

  // Models
  models: {
    list: () =>
      apiRequest<{ models: ModelInfo[]; total: number }>('/api/models'),

    get: (modelId: string) =>
      apiRequest<ModelInfo>(`/api/models/${modelId}`),
  },

  // Predictions
  predictions: {
    create: (data: PredictionInput) =>
      apiRequest<PredictionOutput>('/api/predictions', {
        method: 'POST',
        body: JSON.stringify(data),
      }),

    get: (id: string) =>
      apiRequest<PredictionOutput>(`/api/predictions/${id}`),

    list: (params?: { page?: number; page_size?: number; currency_pair?: string }) => {
      const searchParams = new URLSearchParams();
      if (params?.page) searchParams.set('page', params.page.toString());
      if (params?.page_size) searchParams.set('page_size', params.page_size.toString());
      if (params?.currency_pair) searchParams.set('currency_pair', params.currency_pair);
      const query = searchParams.toString();
      return apiRequest<{ predictions: PredictionOutput[]; total: number; page: number; page_size: number }>(
        `/api/predictions${query ? `?${query}` : ''}`
      );
    },
  },

  // Backtest
  backtest: {
    run: (data: BacktestInput) =>
      apiRequest<BacktestResult>('/api/backtest', {
        method: 'POST',
        body: JSON.stringify(data),
      }),

    get: (id: string) =>
      apiRequest<BacktestResult>(`/api/backtest/${id}`),

    list: () =>
      apiRequest<{ backtests: BacktestResult[]; total: number }>('/api/backtest'),

    getTrades: (id: string) =>
      apiRequest<{ trades: Trade[]; total: number }>(`/api/backtest/${id}/trades`),
  },

  // Indicators
  indicators: {
    get: (pair: string, timeframe: string, params?: { periods?: number; indicators?: string }) => {
      const searchParams = new URLSearchParams();
      if (params?.periods) searchParams.set('periods', params.periods.toString());
      if (params?.indicators) searchParams.set('indicators', params.indicators);
      const query = searchParams.toString();
      return apiRequest<IndicatorsResponse>(
        `/api/indicators/${pair}/${timeframe}${query ? `?${query}` : ''}`
      );
    },

    list: () =>
      apiRequest<{ indicators: string[]; categories: Record<string, string[]> }>(
        '/api/indicators/list'
      ),
  },

  // Trades
  trades: {
    list: (params?: { page?: number; page_size?: number; status?: string }) => {
      const searchParams = new URLSearchParams();
      if (params?.page) searchParams.set('page', params.page.toString());
      if (params?.page_size) searchParams.set('page_size', params.page_size.toString());
      if (params?.status) searchParams.set('status', params.status);
      const query = searchParams.toString();
      return apiRequest<{ trades: Trade[]; total: number; page: number; page_size: number }>(
        `/api/trades${query ? `?${query}` : ''}`
      );
    },

    get: (id: string) =>
      apiRequest<Trade>(`/api/trades/${id}`),
  },

  // Metrics
  metrics: {
    get: () =>
      apiRequest<PerformanceMetrics>('/api/metrics'),

    summary: () =>
      apiRequest<{
        counts: { predictions: number; trades: number; backtests: number };
        recent_predictions: Array<{
          id: string;
          pair: string;
          direction: string;
          confidence: number;
          created_at: string;
        }>;
        recent_backtests: Array<{
          id: string;
          pair: string;
          model: string;
          win_rate: number;
          pnl: number;
          created_at: string;
        }>;
      }>('/api/metrics/summary'),
  },
};

export default api;
