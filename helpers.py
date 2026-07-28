from functools import wraps
from flask import redirect, session
import requests

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
    Fetch wallet information from blockchain API.
    """

    # API integration will be added here later

    return {
        "address": address,
        "network": network,
        "balance": "0.00",
        "transactions": []
    }