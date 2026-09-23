"""
M-Pesa Safaricom Daraja STK Push Integration Module
Glamour Hub Sales Management System
Handles OAuth access token generation, STK Push initiation, phone number formatting,
and STK transaction status querying.
"""

import os
import re
import base64
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables if available
load_dotenv()

class MpesaService:
    """
    Safaricom M-Pesa Daraja API Integration Service.
    Supports both Sandbox and Production environments.
    """

    # Safaricom Daraja Sandbox Default Test Credentials
    # (Used as fallback if environment variables are not set)
    SANDBOX_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY", "c7QGZ1G5rQ30Z7c4B2WvA9f8G6h5j4k3")
    SANDBOX_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET", "s7QGZ1G5rQ30Z7c4B2WvA9f8G6h5j4k3")
    SANDBOX_SHORTCODE = os.getenv("MPESA_SHORTCODE", "174379")
    SANDBOX_PASSKEY = os.getenv(
        "MPESA_PASSKEY",
        "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
    )
    DEFAULT_CALLBACK_URL = os.getenv("MPESA_CALLBACK_URL", "https://mydomain.com/mpesa/callback")

    @classmethod
    def get_config(cls):
        """Retrieve current M-Pesa configuration settings."""
        env = os.getenv("MPESA_ENV", "sandbox").lower()
        is_sandbox = env != "production"

        base_url = (
            "https://sandbox.safaricom.co.ke"
            if is_sandbox else
            "https://api.safaricom.co.ke"
        )

        consumer_key = os.getenv("MPESA_CONSUMER_KEY", cls.SANDBOX_CONSUMER_KEY)
        consumer_secret = os.getenv("MPESA_CONSUMER_SECRET", cls.SANDBOX_CONSUMER_SECRET)
        shortcode = os.getenv("MPESA_SHORTCODE", cls.SANDBOX_SHORTCODE)
        passkey = os.getenv("MPESA_PASSKEY", cls.SANDBOX_PASSKEY)
        callback_url = os.getenv("MPESA_CALLBACK_URL", cls.DEFAULT_CALLBACK_URL)

        return {
            "env": "sandbox" if is_sandbox else "production",
            "base_url": base_url,
            "consumer_key": consumer_key,
            "consumer_secret": consumer_secret,
            "shortcode": shortcode,
            "passkey": passkey,
            "callback_url": callback_url,
        }

    @staticmethod
    def format_phone_number(phone: str) -> str:
        """
        Formats a Kenyan phone number into international standard 254XXXXXXXXX.
        Supports inputs like: 0712345678, 0112345678, +254712345678, 254712345678.
        Returns None if invalid.
        """
        if not phone:
            return None
        
        # Remove whitespace, dashes, plus sign
        cleaned = re.sub(r"[\s\-\+]", "", str(phone).strip())

        # If starts with 07 or 01 (10 digits total)
        if re.match(r"^0[17]\d{8}$", cleaned):
            return "254" + cleaned[1:]

        # If starts with 254 and has 12 digits
        if re.match(r"^254[17]\d{8}$", cleaned):
            return cleaned

        # If 9 digits starting with 7 or 1
        if re.match(r"^[17]\d{8}$", cleaned):
            return "254" + cleaned

        return None

    @classmethod
    def get_access_token(cls) -> str:
        """
        Fetches an OAuth access token from Safaricom Daraja API.
        """
        config = cls.get_config()
        url = f"{config['base_url']}/oauth/v1/generate?grant_type=client_credentials"

        try:
            response = requests.get(
                url,
                auth=(config["consumer_key"], config["consumer_secret"]),
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            token = data.get("access_token")
            if not token:
                raise ValueError("Access token missing in response from Safaricom API.")
            return token
        except requests.exceptions.RequestException as e:
            err_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    err_json = e.response.json()
                    err_msg = err_json.get("errorMessage", e.response.text)
                except Exception:
                    err_msg = e.response.text
            raise ConnectionError(f"M-Pesa Auth Error: {err_msg}")

    @classmethod
    def initiate_stk_push(
        cls,
        phone_number: str,
        amount: float,
        account_reference: str = "GlamourHub",
        transaction_desc: str = "Payment for goods"
    ) -> dict:
        """
        Initiates an M-Pesa STK Push prompt on the customer's phone.
        Returns a dictionary with status and transaction identifiers.
        """
        formatted_phone = cls.format_phone_number(phone_number)
        if not formatted_phone:
            return {
                "success": False,
                "message": "Invalid Kenyan phone number format. Please enter e.g. 0712345678 or 0112345678."
            }

        # Amount must be integer >= 1 for Daraja STK Push
        amt_int = int(round(amount))
        if amt_int < 1:
            return {
                "success": False,
                "message": "Payment amount must be at least 1 KES."
            }

        try:
            token = cls.get_access_token()
            config = cls.get_config()

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            data_to_encode = f"{config['shortcode']}{config['passkey']}{timestamp}"
            password = base64.b64encode(data_to_encode.encode()).decode("utf-8")

            url = f"{config['base_url']}/mpesa/stkpush/v1/processrequest"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            payload = {
                "BusinessShortCode": config["shortcode"],
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amt_int,
                "PartyA": formatted_phone,
                "PartyB": config["shortcode"],
                "PhoneNumber": formatted_phone,
                "CallBackURL": config["callback_url"],
                "AccountReference": account_reference[:12],
                "TransactionDesc": transaction_desc[:12]
            }

            response = requests.post(url, json=payload, headers=headers, timeout=20)
            res_data = response.json()

            response_code = res_data.get("ResponseCode")
            if response_code == "0":
                return {
                    "success": True,
                    "checkout_request_id": res_data.get("CheckoutRequestID"),
                    "merchant_request_id": res_data.get("MerchantRequestID"),
                    "customer_message": res_data.get("CustomerMessage", "STK Push sent to phone."),
                    "phone_number": formatted_phone,
                    "amount": amt_int
                }
            else:
                return {
                    "success": False,
                    "message": res_data.get("ResponseDescription") or res_data.get("CustomerMessage") or "STK Push failed."
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to initiate STK Push: {str(e)}"
            }

    @classmethod
    def query_stk_status(cls, checkout_request_id: str) -> dict:
        """
        Queries the current status of an STK Push transaction from Daraja API.
        Returns dict with status ('COMPLETED', 'PENDING', 'FAILED', 'CANCELLED'),
        receipt_number, and descriptive message.
        """
        if not checkout_request_id:
            return {
                "status": "FAILED",
                "message": "Checkout Request ID is required for status query."
            }

        try:
            token = cls.get_access_token()
            config = cls.get_config()

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            data_to_encode = f"{config['shortcode']}{config['passkey']}{timestamp}"
            password = base64.b64encode(data_to_encode.encode()).decode("utf-8")

            url = f"{config['base_url']}/mpesa/stkpushquery/v1/query"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            payload = {
                "BusinessShortCode": config["shortcode"],
                "Password": password,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id
            }

            response = requests.post(url, json=payload, headers=headers, timeout=15)
            res_data = response.json()

            result_code = str(res_data.get("ResultCode", ""))
            result_desc = res_data.get("ResultDesc", "")

            if result_code == "0":
                # Extract receipt code if available in ResultDesc or construct fallback reference
                receipt = None
                if "Receipt" in result_desc or "code" in result_desc.lower():
                    # Attempt regex extraction of M-Pesa receipt code format (10 alphanumeric e.g. QHX3K4ABCD)
                    match = re.search(r"\b([A-Z0-9]{10})\b", result_desc)
                    if match:
                        receipt = match.group(1)

                return {
                    "status": "COMPLETED",
                    "receipt_number": receipt,
                    "result_desc": result_desc,
                    "message": "✅ Payment successfully confirmed via M-Pesa!"
                }
            elif result_code == "1032":
                return {
                    "status": "CANCELLED",
                    "result_desc": result_desc,
                    "message": "❌ Transaction was cancelled by customer on phone."
                }
            elif result_code == "1037":
                return {
                    "status": "FAILED",
                    "result_desc": result_desc,
                    "message": "⚠️ Transaction timed out. Customer did not enter PIN in time."
                }
            elif result_code == "1":
                return {
                    "status": "FAILED",
                    "result_desc": result_desc,
                    "message": "❌ Insufficient M-Pesa account balance."
                }
            else:
                # Check if still processing / pending
                response_code = res_data.get("ResponseCode")
                if response_code == "0" and not result_code:
                    return {
                        "status": "PENDING",
                        "result_desc": result_desc or "Processing payment prompt...",
                        "message": "⏳ Payment request is pending customer PIN entry."
                    }

                return {
                    "status": "FAILED",
                    "result_desc": result_desc or res_data.get("ResponseDescription", "Unknown error"),
                    "message": f"Payment failed: {result_desc or 'Transaction not completed'}"
                }

        except Exception as e:
            return {
                "status": "PENDING",
                "message": f"Could not check status: {str(e)}"
            }
