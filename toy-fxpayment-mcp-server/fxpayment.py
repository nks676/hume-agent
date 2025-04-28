from typing import Any
from datetime import date, datetime
import uuid
import os
import httpx
from mcp.server.fastmcp import FastMCP

# Constants
MCP_SERVER_NAME     = "fx_payment"
FOREX_API_KEY       = os.environ["FOREX_API_KEY"]
FOREX_API_BASE      = "https://data.fixer.io/api"
PAYMENT_API_BASE    = "https://api-mock.payments.jpmorgan.com/tsapi/ef/v2/transactions"
USER_AGENT          = MCP_SERVER_NAME + "/1.0"

# Initialize FastMCP server
mcp = FastMCP(MCP_SERVER_NAME)

async def make_forex_request(url: str) -> dict[str, Any] | None:
    """Make a request to the Forex API."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br"  # Support for compressed responses
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

async def make_payment_request(url: str, body: dict) -> dict[str, Any] | str:
    """Make a request to the Payment API with minimal error handling."""
    headers = {
        'User-Agent': USER_AGENT,
        'Content-Type': 'application/json',  # Ensure the content type is JSON
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=body, headers=headers, timeout=30.0)

            response.raise_for_status()
            return response.json()

        except httpx.RequestError as exc:
            return f"RequestError occurred while requesting: {exc}"
        except httpx.HTTPStatusError as exc:
            return f"Error response {exc.response.status_code} after posting {exc.request.content}"
        except Exception as e:
            return f"Unexpected error occurred while submitting payload: {body} | Exception: {str(e)}"

@mcp.tool()
async def get_fx_rate(base: str, symbols: str) -> str:
    """Get latest rates of one or more currencies.

    Args:
        base:       Three-letter base currency code (e.g., 'USD', 'EUR')
        symbols:    Comma-separated list of symbols to get rates for (e.g., 'USD,EUR,GBP')
    """
    url = f"{FOREX_API_BASE}/latest?base={base}&symbols={symbols}&access_key={FOREX_API_KEY}"
    data = await make_forex_request(url)

    # check if the JSON response has "success": True
    # JSON response from the API will look like:
    # {"success":true,"timestamp":1743905344,"base":"EUR","date":"2025-04-06","rates":{"INR":93.739724}}
    if not data or not data.get("success", False):
        return "Unable to fetch forex rates. Please check the base and symbols. {}".format(data.get("error"))
    
    if "rates" not in data:
        return "No rates found in the response. Please check the base and symbols. data: {}".format(data)
    rates = data["rates"]

    # Format the rates into a readable string
    rate_str = []
    for symbol, rate in rates.items():
        rate_str.append(f"{symbol}: {rate:.4f}")
    return f"Latest rates for {base}:\n" + "\n".join(rate_str)

@mcp.tool()
async def create_payment(originatorId: str, counterpartyId: str, rail: str, amount: float, currency: str, memo: str) -> str:
    """Create a new payment.

    Args:
        originatorId:   ID of entity originating payment
        counterpartyId: ID of counterparty for the payment
        rail:           Payment rail to use (WIRE, ACH, FEDNOW, RTP)
        amount:         Amount to be transferred
        currency:       Currency of the originator's account (defaults to 'USD')
        memo:           Optional memo for the payment (max 140 characters)
    """
    url = f"{PAYMENT_API_BASE}"

    # Create the body for the payment request as a json object
    body = {
        'transactionReferenceId': str(uuid.uuid4())[:35],
        'amount': amount,
        'currency': currency,
        'type': rail,
        'recipientId': counterpartyId,
        'debtorAccountId': originatorId,  
        'memo': memo
    }

    # Make the payment request
    data = await make_payment_request(url, body)

    if not data:
        return "Unable to create payment. Please check the parameters and try again. {}".format(data)
    else:
        # JPM's api-mock only returns a few canned responses.  For our demo we will
        # update the response with appropriate values to simulate a successful payment capture.
        updated_data = dict(data)
        updated_data["paymentDate"] = str(date.today())
        updated_data["createdAt"] = str(datetime.now())
        updated_data["amount"] = amount
        updated_data["recipientId"] = counterpartyId
        updated_data["debtorAccountId"] = originatorId
        return f"Payment captured successfully: {updated_data}"

#  {"code":105,"type":"base_currency_access_restricted"}
def format_error(error: dict) -> str:
    """Format an error into a readable string."""

    return f"Error {error['code']}: {error['type']}"

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')