import os
import sys
import json
import requests
import re
from datetime import datetime

run_program = True

def validate_argument(date_string):
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def currencies(api_key):
    url = "https://api.fastforex.io/currencies"
    headers = {"accept": "application/json"}
    params = {
        "api_key": api_key
    }
    response = requests.get(url, headers=headers, params=params)
    response = json.loads(response.text)

    return response["currencies"]

def convert(api_key, base_currency, target_currency):
    url = "https://api.fastforex.io/fetch-one"
    headers = {"accept": "application/json"}
    params = {
        "api_key": api_key,
        "from": base_currency,
        "to": target_currency
    }
    response = requests.get(url, headers=headers, params=params)
    response = json.loads(response.text)

    return response["result"][target_currency]

if __name__ == "__main__":
    if len(sys.argv) != 2 or not validate_argument(sys.argv[1]):
        print("Usage: python script.py YYYY-MM-DD")
        sys.exit(1)

    date = sys.argv[1]

    with open('config.json', 'r') as file:
        config = json.load(file)

    api_key = config['api_key']
    currencies_list = currencies(api_key)
    cache = {}

    while run_program:
        while run_program:
            amount = input()
            pattern = r'^\d+(\.\d{1,2})?$'
            if re.match(pattern, amount):
                break
            elif amount.lower() == "end":
                run_program = False
            else:
                print("Please enter a valid amount")

        while run_program:
            base_currency = input().upper()
            if base_currency in currencies_list:
                break
            elif base_currency.lower() == "end":
                run_program = False
            else:
                print("Please enter a valid currency")

        while run_program:
            target_currency = input().upper()
            if target_currency in currencies_list:
                break
            elif target_currency.lower() == "end":
                run_program = False
            else:
                print("Please enter a valid currency")

        if run_program == False:
            break

        try:
            multiplier = cache[base_currency][target_currency]
        except:
            multiplier = convert(api_key, base_currency, target_currency)
            try: 
                cache[base_currency][target_currency] = multiplier
            except:
                cache[base_currency] = {}
                cache[base_currency][target_currency] = multiplier

        converted_amount = float(amount) * float(multiplier)
        converted_amount = round(converted_amount, 2)

        print(f"{amount} {base_currency} is {converted_amount} {target_currency}")

        data_to_add = {
            "date": date,
            "amount": amount,
            "base_currency": base_currency,
            "target_currency": target_currency,
            "converted_amount": converted_amount
        }

        if not os.path.exists("conversions.json"):
            with open("conversions.json", "w") as file:
                json.dump([], file)

        with open("conversions.json", "r") as file:
            data = json.load(file)

        data.append(data_to_add)

        with open("conversions.json", "w") as file:
            json.dump(data, file)
            