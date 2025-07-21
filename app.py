# streamlit_app/app.py
import streamlit as st
import matplotlib.pyplot as plt
from financial_analyst import financial_analyst

def main():
    st.title("AI Financial Analyst App")

    company_name = st.text_input("Company name:")
    analyze_button = st.button("Analyze")

    if analyze_button:
        if company_name:
            st.write("Analyzing... Please wait.")
            
            investment_thesis, hist = financial_analyst(f"Give investment analysis for company {company_name}")

            hist_selected = hist[['Open', 'Close']]
            fig, ax = plt.subplots()
            hist_selected.plot(kind='line', ax=ax)
            ax.set_title(f"{company_name.upper()} Stock Price")
            ax.set_xlabel("Date")
            ax.set_ylabel("Stock Price")
            st.pyplot(fig)

            st.write("Investment Thesis / Recommendation:")
            st.markdown(investment_thesis, unsafe_allow_html=True)
        else:
            st.warning("Please enter the company name.")

if __name__ == "__main__":
    main()
