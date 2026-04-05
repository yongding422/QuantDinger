# IB Gateway Connection Issue - Resolution Notes

## Problem
QuantDinger running in Docker couldn't connect to IB Gateway running on the host machine.

## Root Causes & Fixes

### 1. Docker Network Isolation
**Problem:** Docker containers can't directly reach host's localhost services.
**Fix:** Migrated from Docker deployment to local deployment (Option A):
- PostgreSQL: kept in Docker (port 5432)
- Backend: running locally (port 5000)
- Frontend: running via nginx locally (port 8888)

### 2. IB Gateway API Port Not Listening
**Problem:** IB Gateway wasn't exposing its API port (4002).
**Fix:** Configured via VNC:
- Enable "ActiveX and Socket Clients"
- Uncheck "Allow connections from localhost only"
- Set Socket port to 4002

### 3. API Key Validation Bug (Bug #1)
**Problem:** `test_connection` API required api_key/secret_key for ALL exchanges, including IBKR which doesn't use them.
**File:** `backend_api_python/app/routes/strategy.py`
**Fix:** Line ~694 - Added check to skip validation for IBKR and MT5:
```python
# Before:
if not api_key or not secret_key:
    return jsonify({'code': 0, 'msg': 'Please provide API key and secret key', 'data': None})

# After:
exchange_id = resolved.get('exchange_id', '')
if exchange_id not in ('ibkr', 'mt5') and (not api_key or not secret_key):
    return jsonify({'code': 0, 'msg': 'Please provide API key and secret key', 'data': None})
```

### 4. Connected Property Bug (Bug #2)
**Problem:** Code called `ibkr_client.connected()` but `connected` is a **property**, not a method.
**File:** `backend_api_python/app/services/strategy.py`
**Fix:** Line ~343:
```python
# Before:
if ibkr_client and ibkr_client.connected():

# After:
if ibkr_client and ibkr_client.connected:
```

## Files Modified
- `/home/yong/Projects/QuantDinger/backend_api_python/app/routes/strategy.py`
- `/home/yong/Projects/QuantDinger/backend_api_python/.env` (DATABASE_URL changed to 127.0.0.1)

## Setup Commands

### Start Backend:
```bash
cd ~/Projects/QuantDinger/backend_api_python
source .venv/bin/activate
python run.py
```

### Start Frontend (nginx):
```bash
sudo nginx -s reload  # or: sudo service nginx start
```

### Start IB Gateway:
```bash
cd /home/yong/Jts/ibgateway/1044
xvfb-run -a ./ibgateway
```

## Connection Settings
- IB Gateway: 127.0.0.1:4002 (paper trading)
- QuantDinger Frontend: http://localhost:8888
- QuantDinger API: http://localhost:5000

## Alternative: Using Docker Backend
If you want to use Docker for backend instead:
1. Update DATABASE_URL in .env to: `postgresql://quantdinger:quantdinger123@host.docker.internal:5432/quantdinger`
2. Add `extra_hosts: - "host.docker.internal:host-gateway"` to docker-compose.yml
3. Use socat to relay IB Gateway: `socat TCP-LISTEN:4003,fork,reuseaddr TCP:127.0.0.1:4002`

