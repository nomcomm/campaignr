# campAIgner.py

import streamlit as st
import openai

# App Config
st.set_page_config(page_title="campAIgner 🚀", page_icon="🎯", layout="wide")

# Sidebar
with st.sidebar:
    st.title("campAIgner 🎯")
    st.markdown("Create winning campaign proposals powered by OpenAI.")
    openai_api_key = st.text_input("🔑 Enter your OpenAI API Key:", type="password")
    st.markdown("---")
    st.caption("Streamlit App Based on Python Script")

# Main Page
st.title("🚀 Campaign Proposal Writing Assistant")

st.subheader("Enter information about the campaign:")

col1, col2 = st.columns(2)

with col1:
    communication_issue = st.text_area(
        "1. Describe the communication issue:", height=150, placeholder="e.g., Low voter turnout among young adults..."
    )

with col2:
    need_and_audience = st.text_area(
        "2. State the need and intended audience:", height=150, placeholder="e.g., Need to mobilize college students in swing states..."
    )

main_goal = st.text_area(
    "3. Define the main campaign goal:", height=100, placeholder="e.g., Increase voter registration among 18-24-year-olds by 20%..."
)

# Action Button
st.markdown("### Ready?")
generate = st.button("🎨 Generate My Campaign Proposal")

# Processing
if generate:
    if not openai_api_key:
        st.error("Please enter your OpenAI API Key in the sidebar.")
    elif not (communication_issue and need_and_audience and main_goal):
        st.error("Please fill out all the fields to generate a campaign message.")
    else:
        openai.api_key = openai_api_key

        prompt = (
            f"You are a top-tier political campaign strategist.\n\n"
            f"Communication Issue: {communication_issue}\n"
            f"Need and Audience: {need_and_audience}\n"
            f"Main Campaign Goal: {main_goal}\n\n"
            f"Using this information, craft a powerful, inspiring campaign messaging strategy. "
            f"Make it actionable and appropriate for the audience."
        )

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional campaign messaging expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=600
            )

            campaign_message = response["choices"][0]["message"]["content"]

            st.success("✅ Here’s your campaign messaging strategy:")
            st.write(campaign_message)

        except Exception as e:
            st.error(f"⚠️ An error occurred: {str(e)}")
