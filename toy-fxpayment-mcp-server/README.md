# toy-fxpayment-mcp-server

This is a toy implementation of an MCP server providing two tools:
* **get_fx_rate**
* **create_payment**

## get_fx_rate
This tool uses [Fixer](https://fixer.io/) to get the latest exchange rates for currencies.

**NOTE:**\
An API key must be provided in the `FOREX_API_KEY` environment variable.  The free tier for their API does not allow the use of `USD`, `GBP`, `MXN` as the base currency.

## create_payment
This tool simulates the creation of a new payment between two parties.  It calls one of JPM mock endpoints.

## Setup
If using pip:
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If using uv:
```
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```
