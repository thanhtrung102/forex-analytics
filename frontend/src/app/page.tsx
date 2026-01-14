'use client';

import { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, Activity, BarChart3, RefreshCw } from 'lucide-react';
import api, { PerformanceMetrics, PredictionOutput, BacktestResult } from '@/lib/api';
import PredictionForm from '@/components/PredictionForm';
import PredictionChart from '@/components/charts/PredictionChart';
import PerformanceChart from '@/components/charts/PerformanceChart';
import TradeTable from '@/components/TradeTable';

interface SummaryData {
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
}

export default function Dashboard() {
  const [summary, setSummary] = useState<SummaryData | null>(null);
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [latestPrediction, setLatestPrediction] = useState<PredictionOutput | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [summaryData, metricsData] = await Promise.all([
        api.metrics.summary(),
        api.metrics.get(),
      ]);
      setSummary(summaryData);
      setMetrics(metricsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handlePredictionCreated = (prediction: PredictionOutput) => {
    setLatestPrediction(prediction);
    fetchData(); // Refresh metrics
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-400 mb-4">{error}</p>
          <button
            onClick={fetchData}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Forex Analytics Dashboard</h1>
            <p className="text-gray-400 text-sm">ML-powered market predictions</p>
          </div>
          <button
            onClick={fetchData}
            className="flex items-center gap-2 px-4 py-2 bg-gray-800 rounded hover:bg-gray-700 transition"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>
      </header>

      <main className="p-6">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <StatCard
            title="Total Predictions"
            value={summary?.counts.predictions || 0}
            icon={<Activity className="w-5 h-5" />}
            color="blue"
          />
          <StatCard
            title="Total Trades"
            value={summary?.counts.trades || 0}
            icon={<BarChart3 className="w-5 h-5" />}
            color="green"
          />
          <StatCard
            title="Win Rate"
            value={`${((metrics?.overall_win_rate || 0) * 100).toFixed(1)}%`}
            icon={<TrendingUp className="w-5 h-5" />}
            color="purple"
          />
          <StatCard
            title="Total P&L"
            value={`$${(metrics?.total_profit_loss || 0).toFixed(2)}`}
            icon={
              (metrics?.total_profit_loss || 0) >= 0 ? (
                <TrendingUp className="w-5 h-5" />
              ) : (
                <TrendingDown className="w-5 h-5" />
              )
            }
            color={(metrics?.total_profit_loss || 0) >= 0 ? 'green' : 'red'}
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Prediction Form */}
          <div className="lg:col-span-1">
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-lg font-semibold mb-4">New Prediction</h2>
              <PredictionForm onPredictionCreated={handlePredictionCreated} />
            </div>

            {/* Latest Prediction */}
            {latestPrediction && (
              <div className="bg-gray-800 rounded-lg p-6 mt-4">
                <h2 className="text-lg font-semibold mb-4">Latest Prediction</h2>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Pair</span>
                    <span className="font-medium">{latestPrediction.currency_pair}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Direction</span>
                    <span
                      className={`font-medium ${
                        latestPrediction.predicted_direction === 'UP'
                          ? 'text-green-400'
                          : latestPrediction.predicted_direction === 'DOWN'
                          ? 'text-red-400'
                          : 'text-gray-400'
                      }`}
                    >
                      {latestPrediction.predicted_direction}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Confidence</span>
                    <span className="font-medium">
                      {(latestPrediction.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Price</span>
                    <span className="font-medium">
                      {latestPrediction.predicted_price.toFixed(5)}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Charts */}
          <div className="lg:col-span-2">
            <div className="bg-gray-800 rounded-lg p-6 mb-4">
              <h2 className="text-lg font-semibold mb-4">Prediction History</h2>
              <PredictionChart predictions={summary?.recent_predictions || []} />
            </div>

            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-lg font-semibold mb-4">Performance by Model</h2>
              <PerformanceChart metrics={metrics} />
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="mt-6">
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4">Recent Backtests</h2>
            {summary?.recent_backtests && summary.recent_backtests.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead>
                    <tr className="border-b border-gray-700">
                      <th className="pb-3 text-gray-400 font-medium">Pair</th>
                      <th className="pb-3 text-gray-400 font-medium">Model</th>
                      <th className="pb-3 text-gray-400 font-medium">Win Rate</th>
                      <th className="pb-3 text-gray-400 font-medium">P&L</th>
                      <th className="pb-3 text-gray-400 font-medium">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {summary.recent_backtests.map((bt) => (
                      <tr key={bt.id} className="border-b border-gray-700/50">
                        <td className="py-3 font-medium">{bt.pair}</td>
                        <td className="py-3 uppercase text-blue-400">{bt.model}</td>
                        <td className="py-3">{(bt.win_rate * 100).toFixed(1)}%</td>
                        <td
                          className={`py-3 ${
                            bt.pnl >= 0 ? 'text-green-400' : 'text-red-400'
                          }`}
                        >
                          ${bt.pnl.toFixed(2)}
                        </td>
                        <td className="py-3 text-gray-400">
                          {new Date(bt.created_at).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-gray-400 text-center py-8">No backtests yet</p>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

// Stat Card Component
function StatCard({
  title,
  value,
  icon,
  color,
}: {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color: 'blue' | 'green' | 'purple' | 'red';
}) {
  const colorClasses = {
    blue: 'bg-blue-500/10 text-blue-400',
    green: 'bg-green-500/10 text-green-400',
    purple: 'bg-purple-500/10 text-purple-400',
    red: 'bg-red-500/10 text-red-400',
  };

  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-gray-400 text-sm">{title}</span>
        <div className={`p-2 rounded-lg ${colorClasses[color]}`}>{icon}</div>
      </div>
      <p className="text-2xl font-bold">{value}</p>
    </div>
  );
}
