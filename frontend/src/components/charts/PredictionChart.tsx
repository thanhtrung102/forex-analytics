'use client';

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

interface Prediction {
  id: string;
  pair: string;
  direction: string;
  confidence: number;
  created_at: string;
}

interface PredictionChartProps {
  predictions: Prediction[];
}

export default function PredictionChart({ predictions }: PredictionChartProps) {
  if (!predictions || predictions.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-500">
        No prediction data available
      </div>
    );
  }

  // Transform data for chart
  const chartData = predictions.map((pred) => ({
    name: `${pred.pair}`,
    confidence: pred.confidence * 100,
    direction: pred.direction,
    time: new Date(pred.created_at).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    }),
  }));

  // Get color based on direction
  const getBarColor = (direction: string) => {
    switch (direction) {
      case 'UP':
        return '#22c55e'; // green
      case 'DOWN':
        return '#ef4444'; // red
      default:
        return '#6b7280'; // gray
    }
  };

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis
            dataKey="name"
            stroke="#9ca3af"
            tick={{ fill: '#9ca3af', fontSize: 12 }}
          />
          <YAxis
            stroke="#9ca3af"
            tick={{ fill: '#9ca3af', fontSize: 12 }}
            domain={[0, 100]}
            tickFormatter={(value) => `${value}%`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1f2937',
              border: '1px solid #374151',
              borderRadius: '8px',
            }}
            labelStyle={{ color: '#fff' }}
            formatter={(value: number, name: string, props: any) => [
              `${value.toFixed(1)}%`,
              `Confidence (${props.payload.direction})`,
            ]}
          />
          <Bar dataKey="confidence" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getBarColor(entry.direction)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
