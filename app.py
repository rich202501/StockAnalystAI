import streamlit as st
import matplotlib.pyplot as plt
from financial_analyst import financial_analyst

def main():
    st.title("AI Financial Analyst App")

    company_name = st.text_input("Company name:")
    analyze_button = st.button("Analyze")

    if analyze_button:
        if company_name:
            st.write("Analyzing... Please wait...")

            try:
                investment_thesis, hist = financial_analyst(company_name)

                # 选择 Open 和 Close 字段用于图表
                hist_selected = hist[['Open', 'Close']]

                # 绘图
                fig, ax = plt.subplots()
                hist_selected.plot(kind='line', ax=ax)
                ax.set_title(f"{company_name} Stock Price")
                ax.set_xlabel("Date")
                ax.set_ylabel("Stock Price")
                st.pyplot(fig)

                st.subheader("📊 Investment Thesis / Recommendation:")
                st.markdown(investment_thesis, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter a company name.")

if __name__ == "__main__":
    main()
