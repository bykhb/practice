import streamlit as st
import pandas as pd
import plotly.express as px

def main():
    st.set_page_config(page_title="Offering Framework Planner", layout="wide")
    st.title("Offering Framework Planner")

    # Sidebar for input
    st.sidebar.header("Input Parameters")
    market_size = st.sidebar.number_input("Market Size ($M)", min_value=0, value=1000)
    growth_rate = st.sidebar.slider("Market Growth Rate (%)", 0, 30, 5)
    market_share = st.sidebar.slider("Target Market Share (%)", 0, 100, 10)
    
    # Main content
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Market Opportunity")
        opportunity = market_size * (market_share / 100)
        st.metric("Total Addressable Market", f"${market_size}M")
        st.metric("Our Market Opportunity", f"${opportunity:.1f}M")
        
        # Create a pie chart
        fig = px.pie(values=[opportunity, market_size - opportunity], 
                     names=['Our Opportunity', 'Rest of Market'],
                     title='Market Share Distribution')
        st.plotly_chart(fig)
        
    with col2:
        st.subheader("5-Year Projection")
        years = range(1, 6)
        projections = [market_size * ((1 + growth_rate/100) ** year) for year in years]
        
        df = pd.DataFrame({
            'Year': years,
            'Market Size ($M)': projections
        })
        
        st.line_chart(df.set_index('Year'))
        
    # Offering Framework
    st.subheader("Offering Framework")
    col3, col4, col5 = st.columns(3)
    
    with col3:
        st.write("**Value Proposition**")
        st.text_area("Enter your value proposition", height=100)
        
    with col4:
        st.write("**Key Features**")
        for i in range(3):
            st.text_input(f"Feature {i+1}")
            
    with col5:
        st.write("**Target Customers**")
        st.multiselect("Select target customer segments", 
                       ["Enterprise", "SMB", "Startups", "Government", "Education"])

if __name__ == "__main__":
    main()
