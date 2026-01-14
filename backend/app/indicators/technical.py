"""Technical indicators calculation module."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np


class TechnicalIndicators:
    """Calculator for technical indicators used in forex trading."""

    AVAILABLE_INDICATORS = [
        # Moving Averages
        "sma", "ema", "wma", "hma",
        # Momentum
        "rsi", "macd", "macd_signal", "macd_hist", "roc", "ppo", "kst",
        # Volatility
        "bollinger_upper", "bollinger_middle", "bollinger_lower", "atr",
        # Oscillators
        "stochastic_k", "stochastic_d", "cci",
        # Trend
        "adx", "aroon_up", "aroon_down",
    ]

    def __init__(self):
        """Initialize the indicator calculator."""
        self._cache = {}

    def list_indicators(self) -> List[str]:
        """List all available indicators."""
        return self.AVAILABLE_INDICATORS.copy()

    def calculate_all(
        self,
        currency_pair: str,
        timeframe: str,
        periods: int = 100,
        indicator_list: Optional[List[str]] = None,
    ) -> Dict[str, List[dict]]:
        """Calculate all requested indicators.

        Args:
            currency_pair: Currency pair
            timeframe: Timeframe
            periods: Number of periods
            indicator_list: List of indicators to calculate (None = all)

        Returns:
            Dictionary mapping indicator names to their values
        """
        # Generate sample OHLCV data for demo
        data = self._generate_sample_data(currency_pair, timeframe, periods)

        indicators_to_calc = indicator_list or self.AVAILABLE_INDICATORS

        results = {}
        for indicator in indicators_to_calc:
            if indicator in self.AVAILABLE_INDICATORS:
                values = self._calculate_indicator(indicator, data)
                results[indicator] = values

        return results

    def _generate_sample_data(
        self,
        currency_pair: str,
        timeframe: str,
        periods: int,
    ) -> Dict[str, np.ndarray]:
        """Generate sample OHLCV data for demo purposes."""
        base_prices = {
            "EURUSD": 1.0850, "GBPUSD": 1.2650, "USDJPY": 149.50,
            "AUDUSD": 0.6550, "USDCHF": 0.8750, "USDCAD": 1.3550,
            "NZDUSD": 0.6150, "EURGBP": 0.8550, "EURJPY": 162.25,
            "GBPJPY": 189.25, "AUDJPY": 97.85,
        }

        base = base_prices.get(currency_pair, 1.0)
        np.random.seed(hash(f"{currency_pair}{timeframe}") % 2**32)

        # Generate realistic price movements
        returns = np.random.normal(0, 0.002, periods)
        close = base * np.cumprod(1 + returns)

        # Generate OHLC from close
        volatility = np.abs(np.random.normal(0, 0.001, periods))
        high = close * (1 + volatility)
        low = close * (1 - volatility)
        open_prices = np.roll(close, 1)
        open_prices[0] = base

        # Generate volume
        volume = np.random.randint(1000, 10000, periods)

        # Generate timestamps
        tf_minutes = {"M1": 1, "M5": 5, "M15": 15, "M30": 30, "H1": 60, "H4": 240, "D1": 1440}
        minutes = tf_minutes.get(timeframe, 60)
        end_time = datetime.utcnow()
        timestamps = [end_time - timedelta(minutes=minutes * i) for i in range(periods)]
        timestamps.reverse()

        return {
            "open": open_prices,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume.astype(float),
            "timestamps": timestamps,
        }

    def _calculate_indicator(
        self,
        indicator: str,
        data: Dict[str, np.ndarray],
    ) -> List[dict]:
        """Calculate a single indicator."""
        close = data["close"]
        high = data["high"]
        low = data["low"]
        timestamps = data["timestamps"]

        if indicator == "sma":
            values = self._sma(close, 20)
        elif indicator == "ema":
            values = self._ema(close, 20)
        elif indicator == "wma":
            values = self._wma(close, 20)
        elif indicator == "hma":
            values = self._hma(close, 20)
        elif indicator == "rsi":
            values = self._rsi(close, 14)
        elif indicator == "macd":
            macd, _, _ = self._macd(close)
            values = macd
        elif indicator == "macd_signal":
            _, signal, _ = self._macd(close)
            values = signal
        elif indicator == "macd_hist":
            _, _, hist = self._macd(close)
            values = hist
        elif indicator == "roc":
            values = self._roc(close, 10)
        elif indicator == "ppo":
            values = self._ppo(close)
        elif indicator == "kst":
            values = self._kst(close)
        elif indicator == "bollinger_upper":
            _, upper, _ = self._bollinger_bands(close)
            values = upper
        elif indicator == "bollinger_middle":
            middle, _, _ = self._bollinger_bands(close)
            values = middle
        elif indicator == "bollinger_lower":
            _, _, lower = self._bollinger_bands(close)
            values = lower
        elif indicator == "atr":
            values = self._atr(high, low, close, 14)
        elif indicator == "stochastic_k":
            k, _ = self._stochastic(high, low, close)
            values = k
        elif indicator == "stochastic_d":
            _, d = self._stochastic(high, low, close)
            values = d
        elif indicator == "cci":
            values = self._cci(high, low, close, 20)
        elif indicator == "adx":
            values = self._adx(high, low, close, 14)
        elif indicator == "aroon_up":
            up, _ = self._aroon(high, low, 25)
            values = up
        elif indicator == "aroon_down":
            _, down = self._aroon(high, low, 25)
            values = down
        else:
            values = np.zeros(len(close))

        # Format output
        return [
            {"timestamp": ts, "value": float(v) if not np.isnan(v) else 0.0}
            for ts, v in zip(timestamps, values)
        ]

    # Moving Averages
    def _sma(self, data: np.ndarray, period: int) -> np.ndarray:
        """Simple Moving Average."""
        result = np.full(len(data), np.nan)
        for i in range(period - 1, len(data)):
            result[i] = np.mean(data[i - period + 1:i + 1])
        return result

    def _ema(self, data: np.ndarray, period: int) -> np.ndarray:
        """Exponential Moving Average."""
        result = np.full(len(data), np.nan)
        multiplier = 2 / (period + 1)
        result[period - 1] = np.mean(data[:period])
        for i in range(period, len(data)):
            result[i] = (data[i] - result[i - 1]) * multiplier + result[i - 1]
        return result

    def _wma(self, data: np.ndarray, period: int) -> np.ndarray:
        """Weighted Moving Average."""
        result = np.full(len(data), np.nan)
        weights = np.arange(1, period + 1)
        for i in range(period - 1, len(data)):
            result[i] = np.average(data[i - period + 1:i + 1], weights=weights)
        return result

    def _hma(self, data: np.ndarray, period: int) -> np.ndarray:
        """Hull Moving Average."""
        half_period = period // 2
        sqrt_period = int(np.sqrt(period))
        wma_half = self._wma(data, half_period)
        wma_full = self._wma(data, period)
        diff = 2 * wma_half - wma_full
        return self._wma(diff, sqrt_period)

    # Momentum Indicators
    def _rsi(self, data: np.ndarray, period: int = 14) -> np.ndarray:
        """Relative Strength Index."""
        result = np.full(len(data), np.nan)
        deltas = np.diff(data)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])

        for i in range(period, len(data)):
            avg_gain = (avg_gain * (period - 1) + gains[i - 1]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i - 1]) / period
            if avg_loss == 0:
                result[i] = 100
            else:
                rs = avg_gain / avg_loss
                result[i] = 100 - (100 / (1 + rs))

        return result

    def _macd(self, data: np.ndarray) -> tuple:
        """MACD (Moving Average Convergence Divergence)."""
        ema12 = self._ema(data, 12)
        ema26 = self._ema(data, 26)
        macd_line = ema12 - ema26
        signal_line = self._ema(macd_line, 9)
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    def _roc(self, data: np.ndarray, period: int = 10) -> np.ndarray:
        """Rate of Change."""
        result = np.full(len(data), np.nan)
        for i in range(period, len(data)):
            if data[i - period] != 0:
                result[i] = ((data[i] - data[i - period]) / data[i - period]) * 100
        return result

    def _ppo(self, data: np.ndarray) -> np.ndarray:
        """Percentage Price Oscillator."""
        ema12 = self._ema(data, 12)
        ema26 = self._ema(data, 26)
        return np.where(ema26 != 0, ((ema12 - ema26) / ema26) * 100, 0)

    def _kst(self, data: np.ndarray) -> np.ndarray:
        """Know Sure Thing oscillator."""
        roc1 = self._sma(self._roc(data, 10), 10)
        roc2 = self._sma(self._roc(data, 15), 10)
        roc3 = self._sma(self._roc(data, 20), 10)
        roc4 = self._sma(self._roc(data, 30), 15)
        return roc1 + 2 * roc2 + 3 * roc3 + 4 * roc4

    # Volatility Indicators
    def _bollinger_bands(self, data: np.ndarray, period: int = 20, std_dev: float = 2.0):
        """Bollinger Bands."""
        middle = self._sma(data, period)
        std = np.full(len(data), np.nan)
        for i in range(period - 1, len(data)):
            std[i] = np.std(data[i - period + 1:i + 1])
        upper = middle + std_dev * std
        lower = middle - std_dev * std
        return middle, upper, lower

    def _atr(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14):
        """Average True Range."""
        tr = np.maximum(
            high - low,
            np.maximum(
                np.abs(high - np.roll(close, 1)),
                np.abs(low - np.roll(close, 1))
            )
        )
        tr[0] = high[0] - low[0]
        return self._sma(tr, period)

    # Oscillators
    def _stochastic(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14):
        """Stochastic Oscillator."""
        k = np.full(len(close), np.nan)
        for i in range(period - 1, len(close)):
            highest = np.max(high[i - period + 1:i + 1])
            lowest = np.min(low[i - period + 1:i + 1])
            if highest - lowest != 0:
                k[i] = ((close[i] - lowest) / (highest - lowest)) * 100
        d = self._sma(k, 3)
        return k, d

    def _cci(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 20):
        """Commodity Channel Index."""
        tp = (high + low + close) / 3
        sma_tp = self._sma(tp, period)
        mad = np.full(len(tp), np.nan)
        for i in range(period - 1, len(tp)):
            mad[i] = np.mean(np.abs(tp[i - period + 1:i + 1] - sma_tp[i]))
        return np.where(mad != 0, (tp - sma_tp) / (0.015 * mad), 0)

    # Trend Indicators
    def _adx(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14):
        """Average Directional Index."""
        tr = self._atr(high, low, close, 1)
        plus_dm = np.maximum(high - np.roll(high, 1), 0)
        minus_dm = np.maximum(np.roll(low, 1) - low, 0)

        plus_di = 100 * self._ema(plus_dm, period) / self._ema(tr, period)
        minus_di = 100 * self._ema(minus_dm, period) / self._ema(tr, period)

        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10)
        return self._ema(dx, period)

    def _aroon(self, high: np.ndarray, low: np.ndarray, period: int = 25):
        """Aroon Indicator."""
        aroon_up = np.full(len(high), np.nan)
        aroon_down = np.full(len(low), np.nan)

        for i in range(period, len(high)):
            high_idx = np.argmax(high[i - period:i + 1])
            low_idx = np.argmin(low[i - period:i + 1])
            aroon_up[i] = ((period - (period - high_idx)) / period) * 100
            aroon_down[i] = ((period - (period - low_idx)) / period) * 100

        return aroon_up, aroon_down
