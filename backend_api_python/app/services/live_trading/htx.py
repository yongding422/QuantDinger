"""
HTX (Huobi) direct REST client for spot and USDT-margined perpetual swap.

References:
- Spot base URL: https://api.huobi.pro
- USDT swap base URL: https://api.hbdm.com
- Spot auth: query params with HmacSHA256 signature
- Swap auth: query params with HmacSHA256 signature, request body in JSON
"""

from __future__ import annotations

import base64
import hashlib
import hmac
from decimal import Decimal, ROUND_DOWN
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlencode, urlparse
import datetime
import time

from app.services.live_trading.base import BaseRestClient, LiveOrderResult, LiveTradingError
from app.services.live_trading.symbols import to_htx_contract_code, to_htx_spot_symbol


class HtxClient(BaseRestClient):
    def __init__(
        self,
        *,
        api_key: str,
        secret_key: str,
        base_url: str = "https://api.huobi.pro",
        futures_base_url: str = "https://api.hbdm.com",
        timeout_sec: float = 15.0,
        market_type: str = "swap",
        broker_id: str = "",
    ):
        chosen_base = futures_base_url if str(market_type or "").strip().lower() == "swap" else base_url
        super().__init__(base_url=chosen_base, timeout_sec=timeout_sec)
        self.spot_base_url = (base_url or "https://api.huobi.pro").rstrip("/")
        self.futures_base_url = (futures_base_url or "https://api.hbdm.com").rstrip("/")
        self.api_key = (api_key or "").strip()
        self.secret_key = (secret_key or "").strip()
        self.market_type = (market_type or "swap").strip().lower()
        self.broker_id = (broker_id or "").strip()
        if self.market_type not in ("spot", "swap"):
            self.market_type = "swap"
        if not self.api_key or not self.secret_key:
            raise LiveTradingError("Missing HTX api_key/secret_key")

        self._spot_account_id: Optional[str] = None
        self._contract_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}
        self._contract_cache_ttl_sec = 300.0
        self._lever_cache: Dict[str, int] = {}

    def _format_spot_client_order_id(self, client_order_id: Optional[str]) -> str:
        prefix = str(self.broker_id or "").strip()
        raw = str(client_order_id or "").strip()
        if not prefix and not raw:
            return ""

        if not raw:
            raw = str(int(time.time() * 1000))

        allowed = []
        for ch in raw:
            if ch.isalnum() or ch in ("_", "-"):
                allowed.append(ch)
        suffix = "".join(allowed).strip("-_")
        if not suffix:
            suffix = str(int(time.time() * 1000))

        if prefix:
            if suffix.startswith(prefix):
                combined = suffix
            else:
                combined = f"{prefix}-{suffix}"
        else:
            combined = suffix
        return combined[:64]

    @staticmethod
    def _utc_ts() -> str:
        return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

    @staticmethod
    def _to_dec(x: Any) -> Decimal:
        try:
            return Decimal(str(x))
        except Exception:
            return Decimal("0")

    @staticmethod
    def _floor_to_int(value: Decimal) -> int:
        try:
            return int(value.to_integral_value(rounding=ROUND_DOWN))
        except Exception:
            return 0

    def _sign_params(self, *, method: str, base_url: str, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        signed = dict(params or {})
        signed["AccessKeyId"] = self.api_key
        signed["SignatureMethod"] = "HmacSHA256"
        signed["SignatureVersion"] = "2"
        signed["Timestamp"] = self._utc_ts()
        encoded = urlencode(sorted((str(k), str(v)) for k, v in signed.items()))
        host = urlparse(base_url).netloc
        payload = "\n".join([str(method or "GET").upper(), host, path, encoded])
        digest = hmac.new(self.secret_key.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).digest()
        signed["Signature"] = base64.b64encode(digest).decode("utf-8")
        return signed

    def _spot_public_request(self, method: str, path: str, *, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        old_base = self.base_url
        self.base_url = self.spot_base_url
        try:
            code, data, text = self._request(method, path, params=params)
        finally:
            self.base_url = old_base
        if code >= 400:
            raise LiveTradingError(f"HTX spot HTTP {code}: {text[:500]}")
        if isinstance(data, dict) and str(data.get("status") or "").lower() == "error":
            raise LiveTradingError(f"HTX spot error: {data}")
        return data if isinstance(data, dict) else {"raw": data}

    def _spot_private_request(self, method: str, path: str, *, params: Optional[Dict[str, Any]] = None, json_body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        signed_params = self._sign_params(method=method, base_url=self.spot_base_url, path=path, params=params or {})
        old_base = self.base_url
        self.base_url = self.spot_base_url
        try:
            code, data, text = self._request(method, path, params=signed_params, json_body=json_body)
        finally:
            self.base_url = old_base
        if code >= 400:
            raise LiveTradingError(f"HTX spot HTTP {code}: {text[:500]}")
        if isinstance(data, dict) and str(data.get("status") or "").lower() == "error":
            raise LiveTradingError(f"HTX spot error: {data}")
        return data if isinstance(data, dict) else {"raw": data}

    def _swap_private_request(self, method: str, path: str, *, params: Optional[Dict[str, Any]] = None, json_body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        signed_params = self._sign_params(method=method, base_url=self.futures_base_url, path=path, params=params or {})
        old_base = self.base_url
        self.base_url = self.futures_base_url
        try:
            code, data, text = self._request(method, path, params=signed_params, json_body=json_body)
        finally:
            self.base_url = old_base
        if code >= 400:
            raise LiveTradingError(f"HTX swap HTTP {code}: {text[:500]}")
        if isinstance(data, dict) and str(data.get("status") or "").lower() == "error":
            raise LiveTradingError(f"HTX swap error: {data}")
        return data if isinstance(data, dict) else {"raw": data}

    def _swap_public_request(self, method: str, path: str, *, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        old_base = self.base_url
        self.base_url = self.futures_base_url
        try:
            code, data, text = self._request(method, path, params=params)
        finally:
            self.base_url = old_base
        if code >= 400:
            raise LiveTradingError(f"HTX swap HTTP {code}: {text[:500]}")
        if isinstance(data, dict) and str(data.get("status") or "").lower() == "error":
            raise LiveTradingError(f"HTX swap error: {data}")
        return data if isinstance(data, dict) else {"raw": data}

    def ping(self) -> bool:
        try:
            if self.market_type == "spot":
                self._spot_public_request("GET", "/v1/common/timestamp")
            else:
                self._swap_public_request("GET", "/linear-swap-api/v1/swap_contract_info")
            return True
        except Exception:
            return False

    def _get_spot_account_id(self) -> str:
        if self._spot_account_id:
            return self._spot_account_id
        raw = self._spot_private_request("GET", "/v1/account/accounts")
        data = raw.get("data") or []
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                if str(item.get("type") or "").lower() == "spot" and str(item.get("state") or "").lower() in ("working", ""):
                    self._spot_account_id = str(item.get("id") or "")
                    if self._spot_account_id:
                        return self._spot_account_id
            for item in data:
                if isinstance(item, dict) and item.get("id"):
                    self._spot_account_id = str(item.get("id"))
                    return self._spot_account_id
        raise LiveTradingError("HTX spot account id not found")

    def get_accounts(self) -> Any:
        if self.market_type == "spot":
            return self._spot_private_request("GET", "/v1/account/accounts")
        return self.get_balance()

    def get_balance(self) -> Any:
        if self.market_type == "spot":
            account_id = self._get_spot_account_id()
            return self._spot_private_request("GET", f"/v1/account/accounts/{account_id}/balance")
        raw = self._swap_private_request("POST", "/linear-swap-api/v1/swap_cross_account_info", json_body={"margin_account": "USDT"})
        data = raw.get("data")
        if data:
            return raw
        return self._swap_private_request("POST", "/linear-swap-api/v1/swap_account_info", json_body={})

    def get_positions(self, *, symbol: str = "") -> Any:
        if self.market_type == "spot":
            balance = self.get_balance()
            items = (((balance.get("data") or {}).get("list")) if isinstance(balance, dict) else None) or []
            base_asset = ""
            if symbol:
                base_asset = str(symbol).split("/", 1)[0].split(":", 1)[0].strip().upper()
            rows = []
            for item in items:
                if not isinstance(item, dict):
                    continue
                ccy = str(item.get("currency") or "").upper()
                if not ccy or (base_asset and ccy != base_asset):
                    continue
                bal = self._to_dec(item.get("balance") or "0")
                if bal <= 0:
                    continue
                rows.append({
                    "symbol": f"{ccy}/USDT",
                    "bal": float(bal),
                    "availBal": float(self._to_dec(item.get("balance") or "0")),
                    "cost_open": 0,
                    "profit_unreal": 0,
                })
            return {"data": rows}

        body = {"contract_code": to_htx_contract_code(symbol)} if symbol else {}
        raw = self._swap_private_request("POST", "/linear-swap-api/v1/swap_cross_position_info", json_body=body)
        data = raw.get("data")
        if data:
            return raw
        return self._swap_private_request("POST", "/linear-swap-api/v1/swap_position_info", json_body=body)

    def get_ticker(self, *, symbol: str) -> Dict[str, Any]:
        if self.market_type == "spot":
            raw = self._spot_public_request("GET", "/market/detail/merged", params={"symbol": to_htx_spot_symbol(symbol)})
        else:
            raw = self._swap_public_request("GET", "/linear-swap-ex/market/detail/merged", params={"contract_code": to_htx_contract_code(symbol)})
        tick = raw.get("tick") if isinstance(raw, dict) else {}
        return tick if isinstance(tick, dict) else {}

    def get_contract_info(self, *, symbol: str) -> Dict[str, Any]:
        key = to_htx_contract_code(symbol)
        cached = self._contract_cache.get(key)
        now = time.time()
        if cached:
            ts, obj = cached
            if obj and (now - float(ts or 0)) <= float(self._contract_cache_ttl_sec or 300):
                return obj
        raw = self._swap_public_request("GET", "/linear-swap-api/v1/swap_contract_info", params={"contract_code": key})
        data = raw.get("data") or []
        obj = data[0] if isinstance(data, list) and data and isinstance(data[0], dict) else {}
        if obj:
            self._contract_cache[key] = (now, obj)
        return obj

    def _base_to_contracts(self, *, symbol: str, qty: float) -> int:
        req = self._to_dec(qty)
        if req <= 0:
            return 0
        info = self.get_contract_info(symbol=symbol) or {}
        contract_size = self._to_dec(info.get("contract_size") or info.get("contractSize") or "1")
        if contract_size <= 0:
            contract_size = Decimal("1")
        contracts = req / contract_size
        val = self._floor_to_int(contracts)
        return val if val > 0 else 1

    def set_leverage(self, *, symbol: str, leverage: float) -> bool:
        if self.market_type == "spot":
            return False
        contract_code = to_htx_contract_code(symbol)
        try:
            lv = int(float(leverage or 1))
        except Exception:
            lv = 1
        if lv < 1:
            lv = 1
        try:
            self._swap_private_request(
                "POST",
                "/linear-swap-api/v1/swap_cross_switch_lever_rate",
                json_body={"contract_code": contract_code, "lever_rate": lv, "margin_account": "USDT"},
            )
            self._lever_cache[contract_code] = lv
            return True
        except Exception:
            try:
                self._swap_private_request(
                    "POST",
                    "/linear-swap-api/v1/swap_switch_lever_rate",
                    json_body={"contract_code": contract_code, "lever_rate": lv},
                )
                self._lever_cache[contract_code] = lv
                return True
            except Exception:
                return False

    def place_market_order(
        self,
        *,
        symbol: str,
        side: str,
        qty: float,
        reduce_only: bool = False,
        pos_side: str = "",
        client_order_id: Optional[str] = None,
    ) -> LiveOrderResult:
        if self.market_type == "spot":
            account_id = self._get_spot_account_id()
            sd = str(side or "").strip().lower()
            if sd not in ("buy", "sell"):
                raise LiveTradingError(f"Invalid side: {side}")
            amount = float(qty or 0)
            if amount <= 0:
                raise LiveTradingError("Invalid qty")
            order_type = f"{sd}-market"
            if sd == "buy":
                tick = self.get_ticker(symbol=symbol)
                last = float(tick.get("close") or tick.get("price") or tick.get("lastPrice") or 0)
                if last <= 0:
                    raise LiveTradingError("HTX spot market buy requires latest price for qty->value conversion")
                amount = amount * last
            body = {
                "account-id": account_id,
                "symbol": to_htx_spot_symbol(symbol),
                "type": order_type,
                "amount": f"{amount:.12f}".rstrip("0").rstrip("."),
                "source": "spot-api",
            }
            formatted_client_order_id = self._format_spot_client_order_id(client_order_id)
            if formatted_client_order_id:
                body["client-order-id"] = formatted_client_order_id
            raw = self._spot_private_request("POST", "/v1/order/orders/place", json_body=body)
            data = raw.get("data")
            oid = str(data or "")
            return LiveOrderResult(exchange_id="htx", exchange_order_id=oid, filled=0.0, avg_price=0.0, raw=raw)

        contract_code = to_htx_contract_code(symbol)
        volume = self._base_to_contracts(symbol=symbol, qty=qty)
        if volume <= 0:
            raise LiveTradingError("Invalid HTX swap volume")
        sd = str(side or "").strip().lower()
        if sd not in ("buy", "sell"):
            raise LiveTradingError(f"Invalid side: {side}")
        offset = "close" if reduce_only else "open"
        lever_rate = int(self._lever_cache.get(contract_code) or 5)
        body = {
            "contract_code": contract_code,
            "volume": volume,
            "direction": sd,
            "offset": offset,
            "lever_rate": lever_rate,
            "order_price_type": "opponent",
        }
        if self.broker_id:
            body["channel_code"] = self.broker_id
        if client_order_id:
            body["client_order_id"] = str(client_order_id)[:64]
        raw = self._swap_private_request("POST", "/linear-swap-api/v1/swap_order", json_body=body)
        data = raw.get("data") or {}
        oid = str(data.get("order_id_str") or data.get("order_id") or "")
        return LiveOrderResult(exchange_id="htx", exchange_order_id=oid, filled=0.0, avg_price=0.0, raw=raw)

    def place_limit_order(
        self,
        *,
        symbol: str,
        side: str,
        size: float,
        price: float,
        reduce_only: bool = False,
        pos_side: str = "",
        client_order_id: Optional[str] = None,
    ) -> LiveOrderResult:
        px = float(price or 0)
        qty = float(size or 0)
        if px <= 0 or qty <= 0:
            raise LiveTradingError("Invalid size/price")
        sd = str(side or "").strip().lower()
        if sd not in ("buy", "sell"):
            raise LiveTradingError(f"Invalid side: {side}")

        if self.market_type == "spot":
            account_id = self._get_spot_account_id()
            body = {
                "account-id": account_id,
                "symbol": to_htx_spot_symbol(symbol),
                "type": f"{sd}-limit",
                "amount": f"{qty:.12f}".rstrip("0").rstrip("."),
                "price": f"{px:.12f}".rstrip("0").rstrip("."),
                "source": "spot-api",
            }
            formatted_client_order_id = self._format_spot_client_order_id(client_order_id)
            if formatted_client_order_id:
                body["client-order-id"] = formatted_client_order_id
            raw = self._spot_private_request("POST", "/v1/order/orders/place", json_body=body)
            data = raw.get("data")
            oid = str(data or "")
            return LiveOrderResult(exchange_id="htx", exchange_order_id=oid, filled=0.0, avg_price=0.0, raw=raw)

        contract_code = to_htx_contract_code(symbol)
        volume = self._base_to_contracts(symbol=symbol, qty=qty)
        lever_rate = int(self._lever_cache.get(contract_code) or 5)
        body = {
            "contract_code": contract_code,
            "volume": volume,
            "direction": sd,
            "offset": "close" if reduce_only else "open",
            "lever_rate": lever_rate,
            "price": px,
            "order_price_type": "limit",
        }
        if self.broker_id:
            body["channel_code"] = self.broker_id
        if client_order_id:
            body["client_order_id"] = str(client_order_id)[:64]
        raw = self._swap_private_request("POST", "/linear-swap-api/v1/swap_order", json_body=body)
        data = raw.get("data") or {}
        oid = str(data.get("order_id_str") or data.get("order_id") or "")
        return LiveOrderResult(exchange_id="htx", exchange_order_id=oid, filled=0.0, avg_price=0.0, raw=raw)

    def cancel_order(self, *, symbol: str, order_id: str = "", client_order_id: str = "") -> Dict[str, Any]:
        if self.market_type == "spot":
            if order_id:
                return self._spot_private_request("POST", f"/v1/order/orders/{str(order_id)}/submitcancel")
            if client_order_id:
                return self._spot_private_request("POST", "/v1/order/orders/submitCancelClientOrder", json_body={"client-order-id": str(client_order_id)})
            raise LiveTradingError("HTX cancel_order requires order_id or client_order_id")

        body: Dict[str, Any] = {"contract_code": to_htx_contract_code(symbol)}
        if order_id:
            body["order_id"] = str(order_id)
        elif client_order_id:
            body["client_order_id"] = str(client_order_id)
        else:
            raise LiveTradingError("HTX cancel_order requires order_id or client_order_id")
        return self._swap_private_request("POST", "/linear-swap-api/v1/swap_cancel", json_body=body)

    def get_order(self, *, symbol: str, order_id: str = "", client_order_id: str = "") -> Dict[str, Any]:
        if self.market_type == "spot":
            if order_id:
                raw = self._spot_private_request("GET", f"/v1/order/orders/{str(order_id)}")
                data = raw.get("data") if isinstance(raw, dict) else {}
                return data if isinstance(data, dict) else {}
            if client_order_id:
                raw = self._spot_private_request("GET", "/v1/order/orders/getClientOrder", params={"clientOrderId": str(client_order_id)})
                data = raw.get("data") if isinstance(raw, dict) else {}
                return data if isinstance(data, dict) else {}
            raise LiveTradingError("HTX get_order requires order_id or client_order_id")

        body: Dict[str, Any] = {"contract_code": to_htx_contract_code(symbol)}
        if order_id:
            body["order_id"] = str(order_id)
        elif client_order_id:
            body["client_order_id"] = str(client_order_id)
        else:
            raise LiveTradingError("HTX get_order requires order_id or client_order_id")
        raw = self._swap_private_request("POST", "/linear-swap-api/v1/swap_order_info", json_body=body)
        data = raw.get("data") or []
        if isinstance(data, list) and data and isinstance(data[0], dict):
            return data[0]
        return {}

    def wait_for_fill(
        self,
        *,
        symbol: str,
        order_id: str = "",
        client_order_id: str = "",
        max_wait_sec: float = 3.0,
        poll_interval_sec: float = 0.5,
    ) -> Dict[str, Any]:
        end_ts = time.time() + float(max_wait_sec or 0.0)
        last: Dict[str, Any] = {}
        while True:
            try:
                last = self.get_order(symbol=symbol, order_id=str(order_id or ""), client_order_id=str(client_order_id or "")) or {}
            except Exception:
                last = last or {}

            filled = 0.0
            avg_price = 0.0
            fee = 0.0
            fee_ccy = "USDT"
            status = str(last.get("status") or last.get("state") or "")
            try:
                filled = float(
                    last.get("field-amount") or
                    last.get("filled_amount") or
                    last.get("trade_volume") or
                    last.get("trade_volume_avg") or
                    0.0
                )
            except Exception:
                filled = 0.0
            try:
                avg_price = float(
                    last.get("field-cash-amount") or 0.0
                )
                if filled > 0 and avg_price > 0:
                    avg_price = avg_price / filled
                else:
                    avg_price = float(last.get("field-avg-price") or last.get("trade_avg_price") or last.get("price") or 0.0)
            except Exception:
                avg_price = 0.0
            try:
                fee = abs(float(last.get("fee") or last.get("trade_fee") or 0.0))
            except Exception:
                fee = 0.0
            fee_ccy = str(last.get("fee_asset") or last.get("fee_currency") or fee_ccy or "").strip() or "USDT"

            if filled > 0 and avg_price > 0:
                return {"filled": filled, "avg_price": avg_price, "fee": fee, "fee_ccy": fee_ccy, "status": status, "order": last}
            if str(status).lower() in ("filled", "partial-filled", "submitted", "canceled", "cancelled", "6", "7"):
                return {"filled": filled, "avg_price": avg_price, "fee": fee, "fee_ccy": fee_ccy, "status": status, "order": last}
            if time.time() >= end_ts:
                return {"filled": filled, "avg_price": avg_price, "fee": fee, "fee_ccy": fee_ccy, "status": status, "order": last}
            time.sleep(float(poll_interval_sec or 0.5))
