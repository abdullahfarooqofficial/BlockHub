from functools import wraps
from flask import redirect, session
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def login_required(f):
    """
    Decorator to require user login.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

# Wallet API Integration

def get_wallet_data(address, network):
    """
    Fetch wallet information from Covalent API.
    """

    api_key = os.getenv("COVALENT_API_KEY")
    print("API Key Loaded:", bool(api_key))

    network_map = {

        "ethereum": "eth-mainnet",
        "bsc": "bsc-mainnet",
        "polygon": "matic-mainnet",
        "base": "base-mainnet"
    }
    network_symbol = {

        "ethereum": "ETH",
        "bsc": "BNB",
        "polygon": "POL",
        "base": "ETH"

    }

    chain = network_map.get(network)
    symbol = network_symbol.get(network, "")


    if not chain:
        return {
            "address": address,
            "network": network,
            "balance": "Unsupported Network",
            "transactions": []
        }


    url = f"https://api.covalenthq.com/v1/{chain}/address/{address}/balances_native/"
    #url = f"https://api.goldrush.com/v1/{chain}/address/{address}/balances_v2/"
    

    headers = {
        "Authorization": f"Bearer {api_key}"
    }


    response = requests.get(
        url,
        #auth=(api_key, "")
        headers=headers
    )

    # print("Balance URL:", url)
    # print("Balance Status:", response.status_code)
    # print("Balance Response:", repr(response.text[:500]))
    print("\n===== BALANCE DEBUG =====")
    print("URL:", url)
    print("STATUS:", response.status_code)
    print("HEADERS:", response.headers)
    print("BODY:", repr(response.text[:500]))
    print("=========================\n")

    if response.status_code != 200:
        return {
            "address": address,
            "network": network,
            "balance": "Unavailable",
            "transactions": [],
            "error": f"Balance API Error ({response.status_code})"
        }

    data = response.json()
    print(data)

    balance = "0.00"

    if data.get("data"):

        items = data["data"].get("items", [])

        
        for item in items:
            

            if item.get("contract_ticker_symbol"):

                raw_balance = int(item.get("balance", 0))
                decimals = item.get("contract_decimals", 18)
                symbol = item.get("contract_ticker_symbol", "")

                balance_symbol = network_symbol.get(network, symbol)
                balance = f"{raw_balance / (10 ** decimals):,.6f} {balance_symbol}"

                break
                
    transactions = []

    tx_url = f"https://api.covalenthq.com/v1/{chain}/address/{address}/transactions_v3/"

    tx_response = requests.get(
        tx_url,
        #auth=(api_key, "")
        headers=headers
    )
    
    print("Transaction Status:", tx_response.status_code)
    print("Transaction Response:", tx_response.text[:500])
    

    if tx_response.status_code != 200:
        tx_data = {}

    else:
        tx_data = tx_response.json()

    if tx_data.get("data"):

        items = tx_data["data"].get("items", [])
        
        for tx in items[:10]:

            raw_value = int(tx.get("value", 0))


            # Check normal ETH transfer
            if raw_value > 0:

                value = raw_value / (10 ** 18)


            else:

                value = 0

                # Check token transfer events
                for event in tx.get("log_events") or []:

                    decoded = event.get("decoded")

                    if decoded:

                        params = decoded.get("params") or []

                        for param in params:

                            if param.get("name") == "value":

                                value = int(
                                    param.get("value", 0)
                                ) / (10 ** 18)

                                break


            transactions.append({
                "hash": tx.get("tx_hash"),
                "from": tx.get("from_address"),
                "to": tx.get("to_address"),
                "value": value,
                "status": tx.get("successful"),
                "time": tx.get("block_signed_at"),
                "block": tx.get("block_height"),
                "gas_used": tx.get("gas_spent"),
                "gas_price": tx.get("gas_price")
            })

    return {

    "address": address,

    "network": network,

    "balance": balance,

    "transactions": transactions

    }
    
# def get_transaction_data(tx_hash, network):

#     api_key = os.getenv("COVALENT_API_KEY")

#     network_map = {
#         "ethereum": "eth-mainnet",
#         "bsc": "bsc-mainnet",
#         "polygon": "matic-mainnet"
#     }

#     chain = network_map.get(network)

#     if not chain:
#         return None

#     url = f"https://api.covalenthq.com/v1/{chain}/transaction_v2/{tx_hash}/"

#     headers = {
#         "Authorization": f"Bearer {api_key}"
#     }

#     response = requests.get(url, headers=headers)

#     #Sprint("Transaction Details Status:", response.status_code)
#     print("URL:", url)
#     print("Status:", response.status_code)
#     print("Response:", response.text[:500])

#     if response.status_code != 200:
#         return None

#     data = response.json()

#     if not data.get("data"):
#         return None

#     items = data["data"].get("items", [])

#     if not items:
#         return None

#     tx = items[0]

#     return {
#         "hash": tx.get("tx_hash"),
#         "from": tx.get("from_address"),
#         "to": tx.get("to_address"),
#         "status": tx.get("successful"),
#         "block": tx.get("block_height"),
#         "time": tx.get("block_signed_at"),
#         "gas_used": tx.get("gas_spent"),
#         "gas_price": tx.get("gas_price"),
#         "value": tx.get("value", 0)
#     }