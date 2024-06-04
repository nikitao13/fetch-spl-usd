import requests

def fetch_tokens(wallet):
    url = "https://api.mainnet-beta.solana.com"
    headers = { "Content-Type": "application/json" }

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [
            wallet,
            {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
            {"encoding": "jsonParsed"}
        ]
    }

    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        response_json = response.json()

        if "result" in response_json:
            token_accounts = response_json["result"]["value"]
            tokens = {}

            for account in token_accounts:
                token_info = account["account"]["data"]["parsed"]["info"]
                token_amount = token_info["tokenAmount"]
                balance = float(token_amount["uiAmount"])

                tokens[token_info["mint"]] = balance

            return tokens
        else:
            raise Exception("failed to fetch tokens: No result in response")
    else:
        raise Exception(f"failed to fetch tokens: HTTP {response.status_code}")


def fetch_token_prices(token_addresses, api_key):
    url = "https://api.coingecko.com/api/v3/simple/token_price/solana"
    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": api_key
    }    
    params = {
        "contract_addresses": ",".join(token_addresses),
        "vs_currencies": "usd"
    }

    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"failed to fetch token prices: HTTP {response.status_code}")


def calculate_total_value(wallet, api_key):
    tokens = fetch_tokens(wallet)
    token_addresses = list(tokens.keys())

    try:
        prices = fetch_token_prices(token_addresses, api_key)
    except Exception as e:
        print(e)
        return 0
    
    total_value = 0
    for token_address, balance in tokens.items():
        if token_address in prices:
            price = prices[token_address]["usd"]
            total_value += balance * price

    return total_value


def main():
    # Solana Wallet Address
    wallet = ""
    # CoinGecko Demo API Key (Free)
    api_key = ""

    total_value = calculate_total_value(wallet, api_key)
    formatted_value = "${:,.0f}".format(total_value)
    print(formatted_value)


main()