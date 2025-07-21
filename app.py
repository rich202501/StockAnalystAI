import streamlit as st
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
from financial_analyst import financial_analyst

def main():
    st.set_page_config(page_title="📈 AI Financial Analyst", layout="wide")
    st.title("💼 AI Financial Analyst")

    company_name = st.text_input("Enter Company Name (e.g. Apple, Tesla):")
    analyze_button = st.button("🔍 Analyze")

    if analyze_button:
        if company_name:
            st.info("⏳ Analyzing... Please wait 20~30 seconds.")
            
            # 传入完整请求，触发分析
            investment_thesis, hist = financial_analyst(f"Give investment analysis for company {company_name}")

            # 显示股价图
            st.subheader(f"📊 {company_name.upper()} Historical Stock Prices")
            hist_selected = hist[['Open', 'Close']]
            fig, ax = plt.subplots()
            hist_selected.plot(kind='line', ax=ax)
            ax.set_title(f"{company_name.upper()} Stock Price (Open vs Close)")
            ax.set_xlabel("Date")
            ax.set_ylabel("Price ($)")
            st.pyplot(fig)

            # 显示分析报告（使用 HTML 完整渲染）
            st.subheader("📋 Investment Thesis / Recommendation")
            components.html(f"""
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: 'Segoe UI', sans-serif;
                        padding: 20px;
                        color: #333;
                        line-height: 1.6;
                        background-color: #f9f9f9;
                    }}
                    h2 {{
                        color: #1a73e8;
                        border-bottom: 1px solid #ddd;
                        padding-bottom: 4px;
                    }}
                    h3 {{
                        color: #3c4043;
                        margin-top: 30px;
                    }}
                    ul {{
                        padding-left: 20px;
                    }}
                    li {{
                        margin-bottom: 10px;
                    }}
                    p {{
                        margin-bottom: 10px;
                        font-size: 16px;
                    }}
                    a {{
                        color: #1a73e8;
                        text-decoration: none;
                    }}
                    a:hover {{
                        text-decoration: underline;
                    }}
                </style>
            </head>
            <body>
                {investment_thesis}
            </body>
            </html>
            """, height=1000, scrolling=True)
        else:
            st.warning("⚠️ Please enter the company name.")

if __name__ == "__main__":
    main()
