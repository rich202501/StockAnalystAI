import os
import json
import requests
import streamlit as st
import yfinance as yf
from yahooquery import Ticker
from openai import OpenAI

# 读取 Streamlit secrets 中的 API 密钥
serper_api_key = st.secrets["SERPER_API_KEY"]
openai_api_key = st.secrets["OPENAI_API_KEY"]

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_company_news(company_name):
    headers = {
        'X-API-KEY': serper_api_key,
        'Content-Type': 'application/json'
    }
    data = { 'q': company_name }
    response = requests.post('https://google.serper.dev/news', headers=headers, json=data)
    return response.json().get('news')

def write_news_to_file(news, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        for item in news:
            if item:
                file.write(f"Title: {item.get('title', 'No title')}\n")
                file.write(f"Link: {item.get('link', 'No link')}\n")
                file.write(f"Date: {item.get('date', 'No date')}\n\n")

def get_stock_evolution(ticker, period="1y"):
    try:
        hist = yf.Ticker(ticker).history(period=period)
    except Exception as e:
        print(e)
        return None

    with open("investment.txt", "a") as file:
        file.write(f"\nStock Evolution for {ticker}:\n")
        file.write(hist.to_string())
        file.write("\n")
    return hist

def get_financial_statements(ticker):
    company = Ticker(ticker)
    try:
        balance = company.balance_sheet().to_string()
        cashflow = company.cash_flow(trailing=False).to_string()
        income = company.income_statement().to_string()
        valuation = str(company.valuation_measures)
    except Exception as e:
        print(f"Error fetching financials: {e}")
        return

    with open("investment.txt", "a") as file:
        file.write("\nBalance Sheet\n" + balance)
        file.write("\nCash Flow\n" + cashflow)
        file.write("\nIncome Statement\n" + income)
        file.write("\nValuation Measures\n" + valuation)

def get_data(company_name, ticker, period="1y", filename="investment.txt"):
    news = get_company_news(company_name)
    if news:
        write_news_to_file(news, filename)
    hist = get_stock_evolution(ticker, period)
    get_financial_statements(ticker)
    return hist

def financial_analyst(request):
    st.write(f"Received request: {request}")
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[{
            "role": "user",
            "content": f"What is the company name and stock ticker from this request: {request}"
        }],
        functions=[{
            "name": "get_data",
            "description": "Get financial data for a company",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {"type": "string"},
                    "company_ticker": {"type": "string"},
                    "period": {"type": "string"},
                    "filename": {"type": "string"}
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

    with open("investment.txt", "r") as file:
        content = file.read()[:14000]

    final_response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "user", "content": request},
            msg,
            {"role": "system", "content": """Write a detailed investment thesis in HTML based on the data. \
            Provide buy/sell recommendation, time horizon, and source references."""},
            {"role": "assistant", "content": content}
        ]
    )

    return final_response.choices[0].message.content, hist
