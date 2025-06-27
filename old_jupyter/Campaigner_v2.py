# campAIgner.py

import streamlit as st
from openai import OpenAI


# App Config
st.set_page_config(page_title="CampAIgnR 🚀", page_icon="🎯", layout="wide")

# Sidebar
with st.sidebar:
    st.title("campAIgner 🎯")
    st.markdown("Create campaign proposal drafts with genAI.")
    openai_api_key = st.text_input("🔑 Enter your OpenAI API Key:", type="password")
    st.markdown("---")
    st.caption("Streamlit App Based on Python Script")

# Main Page
st.title("🚀 Campaign Proposal Draft Writing Assistant")

st.subheader("Enter information about the campaign:")

col1, col2 = st.columns(2)

with col1:
    communication_issue = st.text_area(
        "1. Describe the communication issue:", height=150, placeholder="e.g., Distracted driving, particularly among new/young drivers ..."
    )

with col2:
    need_and_audience = st.text_area(
        "2. State the need and intended audience:", height=150, placeholder="e.g., Young drivers, while digitally savvy, are highly vulnerable. They may underestimate the risks of distracted driving, face strong social pressure to stay connected, and lack established, safe driving routines/norms ..."
    )

main_goal = st.text_area(
    "3. Define the main campaign goal:", height=100, placeholder="e.g., Raise awareness of the true risks of distracted driving, provide simple, habit-forming solutions, and foster a commitment to safety ..."
)

# Action Button
st.markdown("### Ready?")
generate = st.button("🎨 Generate My Campaign Proposal Draft")

# Processing
if generate:
    if not openai_api_key:
        st.error("Please enter your OpenAI API Key in the sidebar.")
    elif not (communication_issue and need_and_audience and main_goal):
        st.error("Please fill out all the fields to generate a campaign message.")
    else:
        OpenAI.api_key = openai_api_key

        prompt = (
            f"You are a top-tier political campaign strategist.\n\n"
            f"You are a campaign planner and organizer for a public communication campaign about health. Here is a description of the campaign concept:\n"
            f"Communication Issue: {communication_issue}\n"
            f"Need and Audience: {need_and_audience}\n"
            f"Main Campaign Goal: {main_goal}\n\n"
            f" Your job now is to draft a first sketch of the campaign plan/proposal. \n"
            f"The structure and format for this is fixed and includes these numbered sections, which are to be formatted exactly as follows :\n"
            f"{{0. [Generate and insert a clear and compelling ccampaign title]}}\n" 
            f"{{1. Introduction}}: A brief motivational introduction about the issue and the overall context and goal/aim of the campaign. \n"
            f"A bit like a mission statement or summary, mixed with a sense of purpose or direction.\n"
            f"{{2. Goals}}: These are typically specified as \n"
            f"a) whatever the key goal/aim/objctive is \n"
            f"b) just a goal of how many people will be exposed to the campaign.\n"
            f"(make sure the goals follow the s-m-a-r-t format, i.e. are specific, measureable, attainable, realistic/relevant, and time-bound.\n"
            f"You can have different goals, or structure them into subgoals as you see fit. For example, an overarching goal could be to raise aareness\n"
            f"about the issue, it could be to shift public or individual attitudes in the population or target audience, or it could be a behavior change goal.\n"
            f"Importantly, you are very specific about those goals - whether they are about exposed people, gain in knowledge, change in attitude, or behavior.\n"
            f"{{3.1 Formative Research - Situation Analysis}},  \n"
            f"For the situation analysis: This describes the causal web that makes the issue a problem (e.g. alcohol, smoking etc... what is it that causes this to be apublic health issue, which of those factors are malleable etc.\n"
            f"{{3.2 Formative Research - Audience Analysis}}, \n"
            f"For the audience analysis. This specifies the primary and potential secondary audiences, and describes their \n"
            f"current knowledge, their relevant demographics and attitudes, and their media habits, i.e. how they can be reached.\n"
            f"{{3.3 Formative Research - Analysis of Previous Communication Efforts}}.\n"
            f"For the analysis of previous efforts: Are there well-known efforts that have been conducted. Eg., if the campaign \n"
            f"were about wildfire prevention, then you would have to mention the Smokey Bear campaign. It is important that \n"
            f"you are fact-based! Do not make up campaigns that did not exist.\n"
            f"{{4. Theory and Messages}}: This lists the main socio-behavioral theory  to be used. For example, a drug prevention campaign may use \n"
            f"Inoculation Theory. You could also use just plain vanilla social-cognitive theory, or the theory of reasoned \n"
            f"action/theory of planned behavior, social norms, \n"
            f"the stages-of-change approach, the health belief model, or generic social marketing. Based on the theory you \n"
            f"chose, you then generate a rough descriptions of the kinds of messaging that follows from that.\n"
            f"You do not have to create polished messages, just describe in broad, brushstroke terms how the theory suggests \n"
            f"certain kinds of messages and describe them at large so that a designer or message creator can then craft some \n"
            f"examples.\n"
            f"{{5. Exposure and Channels}}: This section describes how the messages will reach the audience. For example, will the campaign leverage roadside \n"
            f"billboard messaging (adequate to prevent in-the-moment behaviors like texting and driving), or will it use radio ads,\n"
            f"or social media messages, or posters in bathroom stalls, or whatever.\n"
            f"You describe the general media strategy and you become quite concrete about how the campaign will look like, \n"
            f"including a time-phased description of what will happen when.\n"
            f"{{6. Evaluation}}: Finally, you will describe how the campaign will be evaluated. You describe how the performance \n"
            f"will be measured online (process evaluation) and after-the-fact (outcome evaluation), which measures will be used \n"
            f"(e.g. survey, behavior counting, analysis of traces, digital analytics), who and how they will be collected, \n"
            f"and when. You can also specify aspects of the evaluation design, i.e. how you can ascertain that it is the campaign \n"
            f"that  moved the needle on the issue (e.g. need a baseline, need a control group?).\n"
            f"{{7. Summary and Outlook}}: A quick statement about what the campaign will have changed, how the world will look like. \n"
            f"Factual, but also optimistic and motivational\n"
            f"{{8. Appendix}}: details like e.g. Time-Plan, Message Briefs, Budget. All with less than 2 breaks\n"
            f"Important formatting requirements: \n"
            f"You will keep the sections exactly as specified, particularly the {{number of section: section content}} structure. \n"
            f"Transitions between sections have a double line break. \n"
            f"Otherwise, you just write text in plain text without further breaks or additional symbols or comments. \n"
            f"Only the separations between titles or subtitles have single breaks.\n"
            f"Thus, you only return larger sections for {{0. Title}}, {{1. Introduction}}, {{2 ...}}, {{3.1 ...}}, {{3.2 ...}}. . Just those large chunks. \n"
        )

        try:
             client = OpenAI(api_key=OpenAI.api_key)
             response = client.chat.completions.create(
                         model="gpt-4o", 
                         messages=[
                             {"role": "system", "content": "You are a top-tier public health campaign strategist who writes detailed campaign proposals based on user input."},
                             {"role": "user", "content": prompt}  # Your detailed prompt is the user's request
                         ])
             campaign_message = response.choices[0].message.content
             st.success("✅ Here’s your campaign proposal draft:")
             st.write(campaign_message)

        except Exception as e:
             st.error(f"⚠️ An error occurred: {str(e)}")
