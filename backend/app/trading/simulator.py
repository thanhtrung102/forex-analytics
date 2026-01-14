"""Trading simulation engine for backtesting."""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
import numpy as np


class OrderType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class Order:
    """Represents a trading order."""
    order_type: OrderType
    entry_price: float
    entry_time: datetime
    lot_size: float = 0.01
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    profit_loss: float = 0.0
    profit_pips: float = 0.0
    is_closed: bool = False


@dataclass
class SimulationState:
    """State of the trading simulation."""
    balance: float
    equity: float
    margin_used: float = 0.0
    open_orders: List[Order] = field(default_factory=list)
    closed_orders: List[Order] = field(default_factory=list)
    max_balance: float = 0.0
    max_drawdown: float = 0.0


class TradingSimulator:
    """Event-driven trading simulation engine.

    Simulates trading based on ML model predictions with:
    - Take profit and stop loss
    - Leverage and margin calculations
    - Risk management
    """

    def __init__(
        self,
        model_manager,
        initial_balance: float = 10000.0,
        leverage: int = 100,
        risk_factor: float = 1.0,
        lot_size: float = 0.01,
        spread_pips: float = 2.0,
    ):
        """Initialize the trading simulator.

        Args:
            model_manager: ModelManager instance for predictions
            initial_balance: Starting account balance
            leverage: Trading leverage (e.g., 100 = 100:1)
            risk_factor: Risk multiplier for position sizing
            lot_size: Base lot size for trades
            spread_pips: Spread in pips to simulate
        """
        self.model_manager = model_manager
        self.initial_balance = initial_balance
        self.leverage = leverage
        self.risk_factor = risk_factor
        self.lot_size = lot_size
        self.spread_pips = spread_pips

    async def run_backtest(
        self,
        currency_pair: str,
        timeframe: str,
        model_type: str,
        start_date: date,
        end_date: date,
    ) -> Dict[str, Any]:
        """Run backtesting simulation.

        Args:
            currency_pair: Currency pair to trade
            timeframe: Timeframe for trading
            model_type: ML model type to use
            start_date: Start date for backtest
            end_date: End date for backtest

        Returns:
            Dictionary containing backtest results
        """
        # Initialize state
        state = SimulationState(
            balance=self.initial_balance,
            equity=self.initial_balance,
            max_balance=self.initial_balance,
        )

        # Generate simulated price data
        prices = self._generate_price_data(currency_pair, timeframe, start_date, end_date)

        # Run simulation
        for i, price_bar in enumerate(prices):
            # Check existing orders
            self._check_orders(state, price_bar)

            # Generate prediction every N bars
            if i % 5 == 0 and i > 28:
                lookback_data = np.array([p["close"] for p in prices[i-28:i]])
                signal = self._generate_signal(
                    model_type, currency_pair, timeframe, lookback_data, price_bar
                )

                if signal and len(state.open_orders) < 3:
                    self._open_order(state, signal, price_bar)

            # Update equity
            self._update_equity(state, price_bar["close"])

        # Close any remaining orders
        for order in state.open_orders:
            self._close_order(order, prices[-1]["close"], prices[-1]["timestamp"])
            state.closed_orders.append(order)
        state.open_orders.clear()

        return self._compile_results(state, currency_pair, start_date, end_date)

    def _generate_price_data(
        self,
        currency_pair: str,
        timeframe: str,
        start_date: date,
        end_date: date,
    ) -> List[Dict[str, Any]]:
        """Generate simulated price data for backtesting."""
        base_prices = {
            "EURUSD": 1.0850, "GBPUSD": 1.2650, "USDJPY": 149.50,
            "AUDUSD": 0.6550, "USDCHF": 0.8750, "USDCAD": 1.3550,
            "NZDUSD": 0.6150, "EURGBP": 0.8550, "EURJPY": 162.25,
            "GBPJPY": 189.25, "AUDJPY": 97.85,
        }

        base = base_prices.get(currency_pair, 1.0)
        np.random.seed(hash(f"{currency_pair}{start_date}") % 2**32)

        # Calculate number of bars
        tf_minutes = {"M1": 1, "M5": 5, "M15": 15, "M30": 30, "H1": 60, "H4": 240, "D1": 1440}
        minutes = tf_minutes.get(timeframe, 60)
        total_minutes = int((datetime.combine(end_date, datetime.max.time()) -
                            datetime.combine(start_date, datetime.min.time())).total_seconds() / 60)
        num_bars = min(total_minutes // minutes, 5000)

        prices = []
        current_price = base
        current_time = datetime.combine(start_date, datetime.min.time())

        for _ in range(num_bars):
            # Generate OHLC
            change = np.random.normal(0, 0.002)
            volatility = abs(np.random.normal(0, 0.001))

            open_price = current_price
            close_price = current_price * (1 + change)
            high_price = max(open_price, close_price) * (1 + volatility)
            low_price = min(open_price, close_price) * (1 - volatility)

            prices.append({
                "timestamp": current_time,
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": np.random.randint(1000, 10000),
            })

            current_price = close_price
            current_time += timedelta(minutes=minutes)

        return prices

    def _generate_signal(
        self,
        model_type: str,
        currency_pair: str,
        timeframe: str,
        lookback_data: np.ndarray,
        current_bar: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Generate trading signal from model prediction."""
        try:
            result = self.model_manager.predict(
                model_type=model_type,
                currency_pair=currency_pair,
                timeframe=timeframe,
            )

            predicted_change = result["price_change"]
            confidence = result["confidence"]

            # Only trade on confident predictions
            if confidence < 0.6:
                return None

            if predicted_change > 0.001:  # Bullish signal
                return {
                    "type": OrderType.BUY,
                    "confidence": confidence,
                    "predicted_change": predicted_change,
                }
            elif predicted_change < -0.001:  # Bearish signal
                return {
                    "type": OrderType.SELL,
                    "confidence": confidence,
                    "predicted_change": abs(predicted_change),
                }

        except Exception:
            pass

        return None

    def _open_order(
        self,
        state: SimulationState,
        signal: Dict[str, Any],
        price_bar: Dict[str, Any],
    ) -> None:
        """Open a new order based on signal."""
        entry_price = price_bar["close"]

        # Calculate take profit and stop loss
        atr = (price_bar["high"] - price_bar["low"])  # Simplified ATR
        tp_distance = atr * 2 * self.risk_factor
        sl_distance = atr * 1.5 * self.risk_factor

        if signal["type"] == OrderType.BUY:
            take_profit = entry_price + tp_distance
            stop_loss = entry_price - sl_distance
            # Add spread for buy orders
            entry_price += self._pips_to_price(self.spread_pips, entry_price)
        else:
            take_profit = entry_price - tp_distance
            stop_loss = entry_price + sl_distance

        order = Order(
            order_type=signal["type"],
            entry_price=entry_price,
            entry_time=price_bar["timestamp"],
            lot_size=self.lot_size,
            take_profit=take_profit,
            stop_loss=stop_loss,
        )

        state.open_orders.append(order)
        state.margin_used += self._calculate_margin(order)

    def _check_orders(
        self,
        state: SimulationState,
        price_bar: Dict[str, Any],
    ) -> None:
        """Check if any orders should be closed."""
        to_close = []

        for order in state.open_orders:
            should_close = False
            exit_price = None

            if order.order_type == OrderType.BUY:
                if price_bar["high"] >= order.take_profit:
                    exit_price = order.take_profit
                    should_close = True
                elif price_bar["low"] <= order.stop_loss:
                    exit_price = order.stop_loss
                    should_close = True
            else:  # SELL
                if price_bar["low"] <= order.take_profit:
                    exit_price = order.take_profit
                    should_close = True
                elif price_bar["high"] >= order.stop_loss:
                    exit_price = order.stop_loss
                    should_close = True

            if should_close and exit_price:
                self._close_order(order, exit_price, price_bar["timestamp"])
                to_close.append(order)

        # Move closed orders
        for order in to_close:
            state.open_orders.remove(order)
            state.closed_orders.append(order)
            state.balance += order.profit_loss
            state.margin_used -= self._calculate_margin(order)

            # Track max balance and drawdown
            if state.balance > state.max_balance:
                state.max_balance = state.balance
            drawdown = (state.max_balance - state.balance) / state.max_balance
            if drawdown > state.max_drawdown:
                state.max_drawdown = drawdown

    def _close_order(
        self,
        order: Order,
        exit_price: float,
        exit_time: datetime,
    ) -> None:
        """Close an order and calculate P&L."""
        order.exit_price = exit_price
        order.exit_time = exit_time
        order.is_closed = True

        # Calculate profit/loss
        if order.order_type == OrderType.BUY:
            pip_diff = self._price_to_pips(exit_price - order.entry_price, order.entry_price)
        else:
            pip_diff = self._price_to_pips(order.entry_price - exit_price, order.entry_price)

        order.profit_pips = pip_diff
        order.profit_loss = pip_diff * order.lot_size * 10  # $10 per pip per lot

    def _update_equity(self, state: SimulationState, current_price: float) -> None:
        """Update equity based on open positions."""
        unrealized_pnl = 0.0
        for order in state.open_orders:
            if order.order_type == OrderType.BUY:
                pips = self._price_to_pips(current_price - order.entry_price, order.entry_price)
            else:
                pips = self._price_to_pips(order.entry_price - current_price, order.entry_price)
            unrealized_pnl += pips * order.lot_size * 10

        state.equity = state.balance + unrealized_pnl

    def _calculate_margin(self, order: Order) -> float:
        """Calculate required margin for an order."""
        return (order.lot_size * 100000) / self.leverage

    def _pips_to_price(self, pips: float, reference_price: float) -> float:
        """Convert pips to price difference."""
        if reference_price > 10:  # JPY pairs
            return pips * 0.01
        return pips * 0.0001

    def _price_to_pips(self, price_diff: float, reference_price: float) -> float:
        """Convert price difference to pips."""
        if reference_price > 10:  # JPY pairs
            return price_diff / 0.01
        return price_diff / 0.0001

    def _compile_results(
        self,
        state: SimulationState,
        currency_pair: str,
        start_date: date,
        end_date: date,
    ) -> Dict[str, Any]:
        """Compile simulation results."""
        total_trades = len(state.closed_orders)
        winning_trades = sum(1 for o in state.closed_orders if o.profit_loss > 0)
        losing_trades = sum(1 for o in state.closed_orders if o.profit_loss <= 0)
        total_pnl = sum(o.profit_loss for o in state.closed_orders)

        win_rate = winning_trades / total_trades if total_trades > 0 else 0

        # Calculate Sharpe ratio (simplified)
        if total_trades > 1:
            returns = [o.profit_loss for o in state.closed_orders]
            sharpe = (np.mean(returns) / np.std(returns)) * np.sqrt(252) if np.std(returns) > 0 else 0
        else:
            sharpe = 0

        return {
            "currency_pair": currency_pair,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "initial_balance": self.initial_balance,
            "final_balance": state.balance,
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "total_profit_loss": total_pnl,
            "win_rate": win_rate,
            "max_drawdown": state.max_drawdown,
            "sharpe_ratio": sharpe,
            "trades": [
                {
                    "type": o.order_type.value,
                    "entry_price": o.entry_price,
                    "exit_price": o.exit_price,
                    "entry_time": o.entry_time,
                    "exit_time": o.exit_time,
                    "lot_size": o.lot_size,
                    "take_profit": o.take_profit,
                    "stop_loss": o.stop_loss,
                    "profit_loss": o.profit_loss,
                    "profit_pips": o.profit_pips,
                }
                for o in state.closed_orders
            ],
        }
