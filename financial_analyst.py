import os
import json
import requests
import yfinance as yf
import streamlit as st
from yahooquery import Ticker
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 文件

openai_api_key = st.secrets["OPENAI_API_KEY"]
serper_api_key = st.secrets["SERP_API_KEY"]
client = OpenAI(api_key=openai_api_key)


def get_company_news(company_name):
    headers = {
        'X-API-KEY': serper_api_key,
        'Content-Type': 'application/json'
    }
    response = requests.post('https://google.serper.dev/news', headers=headers, json={'q': company_name})
    return response.json().get('news', [])


def write_news_to_file(news, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for item in news:
            f.write(f"Title: {item.get('title')}\nLink: {item.get('link')}\nDate: {item.get('date')}\n\n")


def get_stock_evolution(ticker, period="1y"):
    hist = yf.Ticker(ticker).history(period=period)
    with open("investment.txt", "a") as f:
        f.write(f"\nStock Evolution for {ticker}:\n")
        f.write(hist.to_string())
        f.write("\n")
    return hist


def get_financial_statements(ticker):
    company = Ticker(ticker)
    with open("investment.txt", "a") as f:
        f.write("\nBalance Sheet\n")
        f.write(str(company.balance_sheet()))
        f.write("\nCash Flow\n")
        f.write(str(company.cash_flow(trailing=False)))
        f.write("\nIncome Statement\n")
        f.write(str(company.income_statement()))
        f.write("\nValuation Measures\n")
        f.write(str(company.valuation_measures))


def get_data(company_name, ticker, filename="investment.txt"):
    news = get_company_news(company_name)
    if news:
        write_news_to_file(news, filename)
    hist = get_stock_evolution(ticker)
    get_financial_statements(ticker)
    return hist


def financial_analyst(request):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[{
            "role": "user",
            "content": f"Extract the company name and ticker from this request: {request}"
        }],
        functions=[{
            "name": "get_data",
            "description": "Get stock/financial info",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {"type": "string"},
                    "company_ticker": {"type": "string"},
                },
                "required": ["company_name", "company_ticker"]
            }
        }],
        function_call={"name": "get_data"}
    )

    msg = response.choices[0].message
    args = json.loads(msg.function_call.arguments)

    company_name = args["company_name"]
    ticker = args["company_ticker"]
    hist = get_data(company_name, ticker)

    with open("investment.txt", "r") as f:
        context = f.read()[:14000]

    final = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "user", "content": request},
            msg,
            {"role": "system", "content": """Write a detailed HTML investment report with clear buy/sell recommendations, numbers, and references."""},
            {"role": "assistant", "content": context}
        ]
    )

    return final.choices[0].message.content, hist
