'use client';

import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from 'recharts';
import { PerformanceMetrics } from '@/lib/api';

interface PerformanceChartProps {
  metrics: PerformanceMetrics | null;
}

const COLORS = ['#3b82f6', '#22c55e', '#a855f7'];

export default function PerformanceChart({ metrics }: PerformanceChartProps) {
  if (!metrics) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-500">
        No performance data available
      </div>
    );
  }

  // Prepare data for pie chart - predictions by model
  const modelData = Object.entries(metrics.metrics_by_model || {}).map(
    ([model, data]: [string, any]) => ({
      name: model.toUpperCase(),
      value: data.predictions || 0,
    })
  );

  // If no model data, show placeholder
  if (modelData.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-500">
        <div className="text-center">
          <p>No model performance data yet</p>
          <p className="text-sm mt-1">Create predictions to see metrics</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={modelData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={80}
            paddingAngle={5}
            dataKey="value"
            label={({ name, percent }) =>
              `${name} ${(percent * 100).toFixed(0)}%`
            }
            labelLine={{ stroke: '#6b7280' }}
          >
            {modelData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={COLORS[index % COLORS.length]}
                stroke="transparent"
              />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: '#1f2937',
              border: '1px solid #374151',
              borderRadius: '8px',
            }}
            formatter={(value: number) => [`${value} predictions`, 'Count']}
          />
          <Legend
            verticalAlign="bottom"
            height={36}
            formatter={(value) => (
              <span style={{ color: '#9ca3af' }}>{value}</span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
