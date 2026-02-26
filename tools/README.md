# tools

Helper scripts and the simulator.

## API keys

Create a tenant-wide key (local):

```bash
python3 tools/api_keys/create_api_key.py --tenant demo
```

## Simulator

Run the HTTP simulator against a local API:

```bash
python3 tools/simulator/sim_http.py --base-url http://127.0.0.1:8000 --tenant demo --devices 5 --interval-s 5
```
