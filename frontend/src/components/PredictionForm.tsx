'use client';

import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import api, { PredictionInput, PredictionOutput } from '@/lib/api';

const CURRENCY_PAIRS = [
  'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCHF',
  'USDCAD', 'NZDUSD', 'EURGBP', 'EURJPY', 'GBPJPY', 'AUDJPY',
];

const TIMEFRAMES = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1'];

const MODEL_TYPES = [
  { value: 'cnn', label: 'CNN', description: 'Convolutional Neural Network' },
  { value: 'rnn', label: 'RNN', description: 'Recurrent Neural Network (LSTM)' },
  { value: 'tcn', label: 'TCN', description: 'Temporal Convolutional Network' },
];

interface PredictionFormProps {
  onPredictionCreated?: (prediction: PredictionOutput) => void;
}

export default function PredictionForm({ onPredictionCreated }: PredictionFormProps) {
  const [formData, setFormData] = useState<PredictionInput>({
    currency_pair: 'EURUSD',
    timeframe: 'H1',
    model_type: 'cnn',
    lookback_periods: 28,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const prediction = await api.predictions.create(formData);
      onPredictionCreated?.(prediction);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create prediction');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'lookback_periods' ? parseInt(value, 10) : value,
    }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Currency Pair */}
      <div>
        <label
          htmlFor="currency_pair"
          className="block text-sm font-medium text-gray-300 mb-1"
        >
          Currency Pair
        </label>
        <select
          id="currency_pair"
          name="currency_pair"
          value={formData.currency_pair}
          onChange={handleChange}
          className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          {CURRENCY_PAIRS.map((pair) => (
            <option key={pair} value={pair}>
              {pair}
            </option>
          ))}
        </select>
      </div>

      {/* Timeframe */}
      <div>
        <label
          htmlFor="timeframe"
          className="block text-sm font-medium text-gray-300 mb-1"
        >
          Timeframe
        </label>
        <select
          id="timeframe"
          name="timeframe"
          value={formData.timeframe}
          onChange={handleChange}
          className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          {TIMEFRAMES.map((tf) => (
            <option key={tf} value={tf}>
              {tf}
            </option>
          ))}
        </select>
      </div>

      {/* Model Type */}
      <div>
        <label
          htmlFor="model_type"
          className="block text-sm font-medium text-gray-300 mb-1"
        >
          Model Type
        </label>
        <select
          id="model_type"
          name="model_type"
          value={formData.model_type}
          onChange={handleChange}
          className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          {MODEL_TYPES.map((model) => (
            <option key={model.value} value={model.value}>
              {model.label} - {model.description}
            </option>
          ))}
        </select>
      </div>

      {/* Lookback Periods */}
      <div>
        <label
          htmlFor="lookback_periods"
          className="block text-sm font-medium text-gray-300 mb-1"
        >
          Lookback Periods
        </label>
        <input
          type="number"
          id="lookback_periods"
          name="lookback_periods"
          value={formData.lookback_periods}
          onChange={handleChange}
          min={1}
          max={100}
          className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <p className="text-xs text-gray-500 mt-1">
          Number of historical periods to analyze (1-100)
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/50 rounded-lg px-4 py-3 text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-600/50 disabled:cursor-not-allowed text-white font-medium py-2 px-4 rounded-lg transition flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            Generating...
          </>
        ) : (
          'Generate Prediction'
        )}
      </button>
    </form>
  );
}
