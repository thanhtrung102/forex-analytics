'use client';

import { Trade } from '@/lib/api';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface TradeTableProps {
  trades: Trade[];
  showBacktestColumn?: boolean;
}

export default function TradeTable({
  trades,
  showBacktestColumn = false,
}: TradeTableProps) {
  if (!trades || trades.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No trades to display
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-gray-700">
            <th className="pb-3 text-gray-400 font-medium">Type</th>
            <th className="pb-3 text-gray-400 font-medium">Pair</th>
            <th className="pb-3 text-gray-400 font-medium">Entry</th>
            <th className="pb-3 text-gray-400 font-medium">Exit</th>
            <th className="pb-3 text-gray-400 font-medium">Lot Size</th>
            <th className="pb-3 text-gray-400 font-medium">P&L</th>
            <th className="pb-3 text-gray-400 font-medium">Pips</th>
            <th className="pb-3 text-gray-400 font-medium">Status</th>
            {showBacktestColumn && (
              <th className="pb-3 text-gray-400 font-medium">Backtest</th>
            )}
          </tr>
        </thead>
        <tbody>
          {trades.map((trade) => (
            <tr
              key={trade.trade_id}
              className="border-b border-gray-700/50 hover:bg-gray-700/30 transition"
            >
              {/* Trade Type */}
              <td className="py-3">
                <span
                  className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${
                    trade.trade_type === 'BUY'
                      ? 'bg-green-500/20 text-green-400'
                      : 'bg-red-500/20 text-red-400'
                  }`}
                >
                  {trade.trade_type === 'BUY' ? (
                    <TrendingUp className="w-3 h-3" />
                  ) : (
                    <TrendingDown className="w-3 h-3" />
                  )}
                  {trade.trade_type}
                </span>
              </td>

              {/* Currency Pair */}
              <td className="py-3 font-medium">{trade.currency_pair}</td>

              {/* Entry Price */}
              <td className="py-3 font-mono text-gray-300">
                {trade.entry_price.toFixed(5)}
              </td>

              {/* Exit Price */}
              <td className="py-3 font-mono text-gray-300">
                {trade.exit_price ? trade.exit_price.toFixed(5) : '-'}
              </td>

              {/* Lot Size */}
              <td className="py-3">{trade.lot_size.toFixed(2)}</td>

              {/* P&L */}
              <td
                className={`py-3 font-medium ${
                  (trade.profit_loss || 0) >= 0
                    ? 'text-green-400'
                    : 'text-red-400'
                }`}
              >
                {trade.profit_loss !== null && trade.profit_loss !== undefined
                  ? `$${trade.profit_loss.toFixed(2)}`
                  : '-'}
              </td>

              {/* Pips */}
              <td
                className={`py-3 ${
                  (trade.profit_pips || 0) >= 0
                    ? 'text-green-400'
                    : 'text-red-400'
                }`}
              >
                {trade.profit_pips !== null && trade.profit_pips !== undefined
                  ? trade.profit_pips.toFixed(1)
                  : '-'}
              </td>

              {/* Status */}
              <td className="py-3">
                <span
                  className={`px-2 py-1 rounded text-xs font-medium ${
                    trade.status === 'CLOSED'
                      ? 'bg-gray-500/20 text-gray-400'
                      : trade.status === 'OPEN'
                      ? 'bg-blue-500/20 text-blue-400'
                      : 'bg-yellow-500/20 text-yellow-400'
                  }`}
                >
                  {trade.status}
                </span>
              </td>

              {/* Backtest ID (optional) */}
              {showBacktestColumn && (
                <td className="py-3 text-gray-500 text-xs">
                  {trade.backtest_run_id
                    ? trade.backtest_run_id.substring(0, 8)
                    : '-'}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
