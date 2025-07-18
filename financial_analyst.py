import os
import requests
import json
from dotenv import load_dotenv
import yfinance as yf
from yahooquery import Ticker
import openai

load_dotenv()

# Load keys from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
serper_api_key = os.getenv("SERP_API_KEY")

def get_company_news(company_name):
    headers = {
        'X-API-KEY': serper_api_key,
        'Content-Type': 'application/json'
    }
    data = {
        'q': company_name
    }
    response = requests.post('https://google.serper.dev/news', headers=headers, json=data)
    return response.json().get('news')

def write_news_to_file(news, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        for news_item in news:
            if news_item:
                file.write(f"Title: {news_item.get('title', 'No title')}\n")
                file.write(f"Link: {news_item.get('link', 'No link')}\n")
                file.write(f"Date: {news_item.get('date', 'No date')}\n\n")

def get_stock_evolution(company_name, period="1y"):
    try:
        hist = yf.Ticker(company_name).history(period=period)
    except Exception as e:
        print(e)
        return None
    with open("investment.txt", "a") as file:
        file.write(f"\nStock Evolution for {company_name}:\n")
        file.write(hist.to_string())
        file.write("\n")
    return hist

def get_financial_statements(ticker):
    company = Ticker(ticker)
    try:
        balance_sheet = company.balance_sheet().to_string()
        cash_flow = company.cash_flow(trailing=False).to_string()
        income_statement = company.income_statement().to_string()
        valuation_measures = str(company.valuation_measures)
    except Exception as e:
        print(f"Error while getting financials: {e}")
        return

    with open("investment.txt", "a") as file:
        file.write("\nBalance Sheet\n" + balance_sheet)
        file.write("\nCash Flow\n" + cash_flow)
        file.write("\nIncome Statement\n" + income_statement)
        file.write("\nValuation Measures\n" + valuation_measures)

def get_data(company_name, company_ticker, period="1y", filename="investment.txt"):
    news = get_company_news(company_name)
    if news:
        write_news_to_file(news, filename)
    else:
        print("No news found.")
    hist = get_stock_evolution(company_ticker)
    get_financial_statements(company_ticker)
    return hist

def financial_analyst(request):
    print(f"Received request: {request}")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k-0613",
        messages=[{
            "role": "user",
            "content": f"Given the user request, what is the company name and the company stock ticker?: {request}"
        }],
        functions=[{
            "name": "get_data",
            "description": "Get financial data on a specific company for investment purposes",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {"type": "string", "description": "Company name"},
                    "company_ticker": {"type": "string", "description": "Ticker symbol"},
                    "period": {"type": "string", "description": "Analysis period"},
                    "filename": {"type": "string", "description": "Output filename"}
                },
                "required": ["company_name", "company_ticker"]
            }
        }],
        function_call={"name": "get_data"},
    )

    message = response["choices"][0]["message"]
    if message.get("function_call"):
        arguments = json.loads(message["function_call"]["arguments"])
        hist = get_data(arguments["company_name"], arguments["company_ticker"], arguments.get("period", "1y"), arguments.get("filename", "investment.txt"))

        with open("investment.txt", "r") as file:
            content = file.read()[:14000]

        second_response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "user", "content": request},
                message,
                {"role": "system", "content": (
                    "Write a detailed investment thesis in HTML. Give a recommendation to buy or not. "
                    "Be honest. Include data analysis for short and long-term investment."
                )},
                {"role": "assistant", "content": content},
            ],
        )
        return second_response["choices"][0]["message"]["content"], hist
