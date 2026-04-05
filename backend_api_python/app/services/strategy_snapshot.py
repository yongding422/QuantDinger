import json
from typing import Any, Dict, Optional

from app.utils.db import get_db_connection


class StrategySnapshotResolver:
    """Resolve stored strategy rows into backtest-ready snapshots."""

    def __init__(self, user_id: int = 1):
        self.user_id = int(user_id or 1)

    def _safe_dict(self, value: Any) -> Dict[str, Any]:
        if isinstance(value, dict):
            return dict(value)
        if isinstance(value, str) and value.strip():
            try:
                parsed = json.loads(value)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass
        return {}

    def _to_bool(self, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in ("1", "true", "yes", "on")
        return bool(value)

    def _to_float(self, value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except Exception:
            return float(default or 0.0)

    def _to_int(self, value: Any, default: int = 0) -> int:
        try:
            return int(value)
        except Exception:
            return int(default or 0)

    def _percent_to_ratio(self, value: Any, default: float = 0.0) -> float:
        raw = self._to_float(value, default)
        if raw <= 0:
            return 0.0
        if raw > 100:
            raw = 100.0
        return raw / 100.0

    def _build_strategy_config(self, trading_config: Dict[str, Any]) -> Dict[str, Any]:
        tc = trading_config or {}
        signal_mode = str(tc.get("signal_mode") or "confirmed").strip().lower()
        signal_timing = "next_bar_open"
        if signal_mode in ("current_bar_close", "close", "same_bar_close"):
            signal_timing = "same_bar_close"

        return {
            "risk": {
                "stopLossPct": self._percent_to_ratio(tc.get("stop_loss_pct")),
                "takeProfitPct": self._percent_to_ratio(tc.get("take_profit_pct")),
                "trailing": {
                    "enabled": self._to_bool(tc.get("trailing_enabled") or tc.get("trailing_stop")),
                    "pct": self._percent_to_ratio(tc.get("trailing_stop_pct")),
                    "activationPct": self._percent_to_ratio(tc.get("trailing_activation_pct")),
                },
            },
            "position": {
                "entryPct": self._percent_to_ratio(tc.get("entry_pct") if tc.get("entry_pct") is not None else 100),
            },
            "scale": {
                "trendAdd": {
                    "enabled": self._to_bool(tc.get("trend_add_enabled")),
                    "stepPct": self._percent_to_ratio(tc.get("trend_add_step_pct")),
                    "sizePct": self._percent_to_ratio(tc.get("trend_add_size_pct")),
                    "maxTimes": self._to_int(tc.get("trend_add_max_times")),
                },
                "dcaAdd": {
                    "enabled": self._to_bool(tc.get("dca_add_enabled")),
                    "stepPct": self._percent_to_ratio(tc.get("dca_add_step_pct")),
                    "sizePct": self._percent_to_ratio(tc.get("dca_add_size_pct")),
                    "maxTimes": self._to_int(tc.get("dca_add_max_times")),
                },
                "trendReduce": {
                    "enabled": self._to_bool(tc.get("trend_reduce_enabled")),
                    "stepPct": self._percent_to_ratio(tc.get("trend_reduce_step_pct")),
                    "sizePct": self._percent_to_ratio(tc.get("trend_reduce_size_pct")),
                    "maxTimes": self._to_int(tc.get("trend_reduce_max_times")),
                },
                "adverseReduce": {
                    "enabled": self._to_bool(tc.get("adverse_reduce_enabled")),
                    "stepPct": self._percent_to_ratio(tc.get("adverse_reduce_step_pct")),
                    "sizePct": self._percent_to_ratio(tc.get("adverse_reduce_size_pct")),
                    "maxTimes": self._to_int(tc.get("adverse_reduce_max_times")),
                },
            },
            "execution": {
                "signalTiming": signal_timing,
            },
        }

    def _fetch_indicator_code(self, indicator_id: Optional[int]) -> str:
        if not indicator_id:
            return ""
        try:
            with get_db_connection() as db:
                cur = db.cursor()
                cur.execute("SELECT code FROM qd_indicator_codes WHERE id = ?", (int(indicator_id),))
                row = cur.fetchone()
                cur.close()
            return (row or {}).get("code") or ""
        except Exception:
            return ""

    def resolve(self, strategy: Dict[str, Any], override_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not strategy:
            raise ValueError("strategy not found")

        override = override_config or {}
        indicator_config = self._safe_dict(strategy.get("indicator_config"))
        trading_config = self._safe_dict(strategy.get("trading_config"))

        cs_type = str(trading_config.get("cs_strategy_type") or trading_config.get("strategy_type") or "single").strip().lower()
        if cs_type == "cross_sectional":
            raise ValueError("Cross-sectional strategies are not supported in strategy backtest yet")

        symbol = str(override.get("symbol") or trading_config.get("symbol") or strategy.get("symbol") or "").strip()
        market = str(override.get("market") or strategy.get("market_category") or trading_config.get("market_category") or "Crypto").strip() or "Crypto"
        if ":" in symbol and "market" not in override:
            maybe_market, maybe_symbol = symbol.split(":", 1)
            market = maybe_market or market
            symbol = maybe_symbol or symbol

        timeframe = str(override.get("timeframe") or trading_config.get("timeframe") or strategy.get("timeframe") or "1D").strip() or "1D"
        initial_capital = self._to_float(override.get("initialCapital", trading_config.get("initial_capital", strategy.get("initial_capital", 10000))), 10000.0)
        leverage = self._to_int(override.get("leverage", trading_config.get("leverage", strategy.get("leverage", 1))), 1)
        commission = self._percent_to_ratio(override.get("commission", trading_config.get("commission", 0)))
        slippage = self._percent_to_ratio(override.get("slippage", trading_config.get("slippage", 0)))
        trade_direction = str(trading_config.get("trade_direction") or "long").strip().lower() or "long"
        enable_mtf = self._to_bool(override.get("enableMtf", market.lower() == "crypto"))

        strategy_type = str(strategy.get("strategy_type") or "IndicatorStrategy").strip() or "IndicatorStrategy"
        strategy_mode = str(strategy.get("strategy_mode") or "signal").strip() or "signal"
        is_script = strategy_type == "ScriptStrategy" or strategy_mode == "script"

        indicator_id = indicator_config.get("indicator_id") or strategy.get("indicator_id")
        indicator_name = indicator_config.get("indicator_name") or ""
        code = (strategy.get("strategy_code") or "").strip() if is_script else (indicator_config.get("indicator_code") or "").strip()
        if not code and indicator_id and not is_script:
            code = self._fetch_indicator_code(indicator_id)

        if not symbol:
            raise ValueError("Strategy symbol is required for backtest")
        if not code:
            raise ValueError("Strategy code is empty and cannot be backtested")

        strategy_config = self._build_strategy_config(trading_config)
        snapshot = {
            "strategy_id": strategy.get("id"),
            "strategy_name": strategy.get("strategy_name") or f"Strategy #{strategy.get('id')}",
            "strategy_type": strategy_type,
            "strategy_mode": strategy_mode,
            "run_type": "strategy_script" if is_script else "strategy_indicator",
            "market": market,
            "symbol": symbol,
            "timeframe": timeframe,
            "initial_capital": initial_capital,
            "commission": commission,
            "slippage": slippage,
            "leverage": leverage,
            "trade_direction": trade_direction,
            "enable_mtf": enable_mtf,
            "indicator_id": int(indicator_id) if str(indicator_id or "").isdigit() else None,
            "indicator_name": indicator_name,
            "indicator_params": trading_config.get("indicator_params") or {},
            "code": code,
            "strategy_config": strategy_config,
            "config_snapshot": {
                "strategyMeta": {
                    "strategyId": strategy.get("id"),
                    "strategyName": strategy.get("strategy_name"),
                    "strategyType": strategy_type,
                    "strategyMode": strategy_mode,
                    "runType": "strategy_script" if is_script else "strategy_indicator",
                },
                "marketConfig": {
                    "market": market,
                    "symbol": symbol,
                    "timeframe": timeframe,
                },
                "signalConfig": {
                    "indicatorId": int(indicator_id) if str(indicator_id or "").isdigit() else None,
                    "indicatorName": indicator_name,
                    "indicatorParams": trading_config.get("indicator_params") or {},
                    "scriptSource": "strategy_code" if is_script else "indicator_code",
                },
                "riskConfig": strategy_config.get("risk") or {},
                "positionConfig": strategy_config.get("position") or {},
                "scaleConfig": strategy_config.get("scale") or {},
                "executionConfig": strategy_config.get("execution") or {},
            },
        }
        return snapshot
