import streamlit as st
import matplotlib.pyplot as plt
from financial_analyst import financial_analyst

def main():
    st.set_page_config(page_title="AI Financial Analyst", layout="centered")
    st.title("📈 AI Financial Analyst")

    company_name = st.text_input("Enter company name (e.g. Apple, Tesla)", value="", max_chars=50)

    if st.button("🔍 Analyze"):
        if company_name.strip():
            st.info("🔄 Analyzing company data... Please wait.")

            try:
                # 调用分析函数，构建清晰的 Prompt
                prompt = f"Give investment analysis for company {company_name.strip()}"
                investment_thesis, hist = financial_analyst(prompt)

                # 显示股价图
                if hist is not None and not hist.empty:
                    st.subheader(f"📊 {company_name.upper()} Stock Price (1Y)")
                    fig, ax = plt.subplots()
                    hist[['Open', 'Close']].plot(ax=ax)
                    ax.set_xlabel("Date")
                    ax.set_ylabel("Price (USD)")
                    ax.set_title(f"{company_name.upper()} Stock History")
                    ax.grid(True)
                    st.pyplot(fig)
                else:
                    st.warning("⚠️ No stock history data available.")

                # 显示投资建议
                st.subheader("🧠 Investment Thesis / Recommendation")
                st.markdown(investment_thesis, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Error: {e}")
        else:
            st.warning("⚠️ Please enter a valid company name.")

if __name__ == "__main__":
    main()
