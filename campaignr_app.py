import streamlit as st
from openai import OpenAI
import re
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import pdfkit
import base64

# --- App Configuration ---
st.set_page_config(page_title="campAIgnR 🚀", page_icon="🎯", layout="wide")


# --- MASTER PROMPT ---
# This is the final, most detailed prompt, engineered to produce a substantive, elaborate, and professional proposal in a single pass.
DEFAULT_PROPOSAL_PROMPT = """
You are a top-tier public communication campaign strategist with a Ph.D. in health communication. Your task is to write a complete, detailed, and comprehensive campaign proposal draft based on the user's concept. The final document should be professional, substantive, and suitable for a grant application or strategic review.

**Campaign Concept:**
- **Issue:** {communication_issue}
- **Need and Audience:** {need_and_audience}
- **Main Goal:** {main_goal}

**CRITICAL INSTRUCTIONS:**
1.  **Structure and Formatting:**
    - The very first line of your response must be the campaign's main title. Do not use Markdown like '#' for the main title.
    - Every subsequent main section MUST start with a `##` Markdown header (e.g., `## Introduction`).
    - Sub-sections within "Formative Research" must start with a `###` header (e.g., `### Situation Analysis`).
    - Do not include any conversational text, preambles, or postscripts. Your output must be ONLY the proposal itself.

2.  **Depth and Length:**
    - This is the most important instruction. Each section must be **thoroughly elaborated**. Do not write short, bullet-point summaries.
    - Develop a coherent, written argument for each section, aiming for a substantial length of **at least 500-700 words per main section**.
    - The goal is a document of several pages, not a brief outline.

---
**SECTION-SPECIFIC GUIDANCE (Follow these closely):**

**## Introduction**
Frame the problem with compelling background statistics from reputable sources (e.g., CDC, NIH). Articulate the campaign's core purpose and why it is urgently needed. This should serve as a powerful mission statement and executive summary, setting a professional and evidence-based tone for the entire document.

**## Goals**
Specify 3-5 distinct campaign goals using the SMART framework (Specific, Measurable, Attainable, Relevant, Time-bound). Number each goal. Clearly differentiate between awareness goals (e.g., "Increase knowledge of X by 20%"), attitude/belief goals (e.g., "Reduce perceived peer approval of Y by 15%"), and behavioral goals (e.g., "Achieve a 10% reduction in self-reported Z behavior"). For each goal, define the specific metric and the timeline (e.g., "as measured by pre- and post-campaign surveys over a six-month period").

**## Formative Research**
This section must contain the following three sub-sections, each fully developed.

**### Situation Analysis**
Provide a deep analysis of the problem's causal web. Discuss the social, cultural, economic, and psychological factors contributing to the issue. Cite relevant research to support your analysis. Conclude by identifying the most malleable factors that the campaign can realistically target.

**### Audience Analysis**
Develop a detailed profile of the primary audience. Go beyond demographics to discuss psychographics: their values, beliefs, media consumption habits (be specific: which platforms, who do they follow?), and key barriers or motivators for change. Identify and describe important secondary audiences (e.g., parents, university staff) and their potential role.

**### Analysis of Previous Communication Efforts**
Analyze at least two real, well-known campaigns that have addressed similar health issues. For each, critically evaluate its theoretical basis, messaging strategy, successes, and failures, citing published evaluations if possible. Conclude with a summary of actionable lessons that will inform this new campaign's design.

**## Theory and Messages**
Select a primary socio-behavioral theory (e.g., Health Belief Model, Theory of Planned Behavior, Social Norms Approach). Justify why this theory is the best fit for this specific problem and audience. Then, based on the theory's core constructs, outline the key message strategies. Provide 3-4 detailed examples of message concepts that a creative team could develop into full ads.

**## Exposure and Channels**
Propose a strategic, multi-channel media plan with a clear timeline. Detail a phased rollout: Phase 1 (Awareness/Teaser), Phase 2 (Main Engagement/Education), Phase 3 (Reinforcement/Call-to-Action). For each phase, specify the channels (e.g., targeted social media ads, on-campus events, influencer collaborations) and the specific type of content to be deployed on each.

**## Evaluation**
Design a comprehensive evaluation plan that directly links back to the stated goals. Distinguish clearly between **Process Evaluation** (monitoring campaign implementation, reach, engagement, and fidelity) and **Outcome Evaluation** (measuring the achievement of the SMART goals). Describe the methodology in detail, including specific survey instruments, digital analytics to track, and qualitative methods like focus groups. Crucially, explain the research design, including the need for a **baseline measurement** and the use of a **control group** or quasi-experimental design to help establish the campaign's causal impact, explaining that this is necessary to rule out other societal trends.

**## Summary and Outlook**
Write a powerful, concluding statement that summarizes the strategic approach and reiterates the campaign's potential for meaningful, lasting change.

**## Appendix**
Briefly list and describe the types of materials that would be included in a full proposal appendix (e.g., "1. Detailed Timeline (Gantt Chart): A visual project plan...", "2. Creative Briefs: Detailed guides for the creative team...", "3. Detailed Budget Breakdown...", "4. Sample Survey Instruments...").

---
Begin the proposal now.
"""

DEFAULT_IMAGE_PROMPT = """
A cover image for a public health campaign titled: "{campaign_title}".
Atmospheric, themed to a university campus milieu (Michigan State University, green and white colors, a subtle Spartan helmet motif).
The style should hint at a hard-boiled detective genre but with a quirky, positive spirit.
The outer edges of the image are blurred and in shadow, focusing the viewer on the center.
"""

# --- Helper Functions ---
def get_openai_client(api_key): return OpenAI(api_key=api_key)

def generate_text(client, prompt_text):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt_text}]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"An error occurred with the OpenAI API: {e}"); return None

def generate_image(client, prompt_text):
    try:
        response = client.images.generate(
            model="dall-e-3", prompt=prompt_text, size="1024x1024",
            quality="standard", n=1, response_format="b64_json"
        )
        return response.data[0].b64_json
    except Exception as e:
        st.error(f"An error occurred with DALL-E: {e}"); return None

def extract_title_from_text(text):
    lines = text.splitlines()
    return lines[0].strip().replace("#", "") if lines else "Untitled Campaign"

def parse_text_for_html(text):
    sections = []
    # Split the text by '## ' and '### ' headers
    parts = re.split(r'\n(## |### )', '\n' + text)
    if len(parts) > 1:
        for i in range(1, len(parts), 2):
            header_marker = parts[i]
            content_block = parts[i+1]
            block_lines = content_block.splitlines()
            header_text = header_marker + block_lines[0]
            content = '\n'.join(block_lines[1:]).strip()
            sections.append((header_text, content))
    return sections

# --- Streamlit UI ---
st.title("🚀 campAIgnR: Proposal Draft Assistant")

with st.sidebar:
    st.title("campAIgnR 🎯")
    st.markdown("Create campaign proposal drafts with genAI.")
    openai_api_key = st.text_input("🔑 Enter your OpenAI API Key:", type="password", key="api_key_input")
    author_name = st.text_input("👤 Author/Director Name:", placeholder="e.g., Dr. Jane Doe", key="author_input")
    with st.expander("Advanced: Edit Prompts"):
        st.text_area("Main Proposal Prompt", value=DEFAULT_PROPOSAL_PROMPT, height=300, key="prompt_main")
        st.text_area("Cover Image Prompt", value=DEFAULT_IMAGE_PROMPT, height=150, key="prompt_image")
    st.caption("A tool for rapid campaign prototyping.")

st.info(
    "**Important:** This tool generates a first draft. It is a starting point, not a final product. "
    "You **must** fact-check all claims, statistics, and references. Use this draft as a foundation to expand upon "
    "with your own research and expertise."
)

st.subheader("Enter your campaign concept:")
col1, col2 = st.columns(2)
with col1:
    communication_issue = st.text_area("1. The Communication Issue:", height=150, placeholder="e.g., Excessive and high-risk drinking on college campuses.", key="issue_input")
with col2:
    need_and_audience = st.text_area("2. The Need and Intended Audience:", height=150, placeholder="e.g., College students (18-24) often misperceive peer drinking norms...", key="audience_input")
main_goal = st.text_area("3. The Main Campaign Goal:", height=100, placeholder="e.g., To correct misperceptions of drinking norms and reduce high-risk drinking behaviors...", key="goal_input")

if st.button("🎨 Generate Campaign Components", use_container_width=True):
    for key in list(st.session_state.keys()):
        if key not in ['api_key_input', 'author_input', 'issue_input', 'audience_input', 'goal_input', 'prompt_main', 'prompt_image']:
            st.session_state.pop(key)
            
    if not all([st.session_state.api_key_input, st.session_state.author_input, st.session_state.issue_input, st.session_state.audience_input, st.session_state.goal_input]):
        st.error("Please fill out all fields, including your API Key and Name in the sidebar.")
    else:
        client = get_openai_client(st.session_state.api_key_input)
        with st.spinner("Generating full, detailed proposal and cover image... This may take several minutes."):
            full_prompt = st.session_state.prompt_main.format(
                communication_issue=st.session_state.issue_input,
                need_and_audience=st.session_state.audience_input,
                main_goal=st.session_state.goal_input
            )
            proposal_text = generate_text(client, full_prompt)
            if not proposal_text:
                st.error("Failed to generate proposal text. The AI may have returned an empty response. Please try again."); st.stop()
            st.session_state.final_text_output = proposal_text
            
            campaign_title = extract_title_from_text(proposal_text)
            st.session_state.campaign_title = campaign_title
            
            image_prompt = st.session_state.prompt_image.format(campaign_title=campaign_title)
            image_b64 = generate_image(client, image_prompt)
            if image_b64: st.session_state.cover_image_b64 = image_b64
        
        st.success("✅ Campaign components generated successfully!")

# --- Display Results ---
if 'final_text_output' in st.session_state:
    st.markdown("---"); st.header(f"Campaign: {st.session_state.get('campaign_title', 'Untitled')}")
    
    tab1, tab2, tab3 = st.tabs(["📜 **Full Proposal Text**", "🖼️ **Cover Image**", "📄 **Formatted Report (Optional)**"])
    
    with tab1:
        st.subheader("Raw Proposal Text"); st.text_area(
            "This is the complete raw text for your proposal. Copy it or use the download button.", 
            value=st.session_state.final_text_output, height=500
        )
        st.download_button("⬇️ Download Text File (.txt)", st.session_state.final_text_output.encode('utf-8'),
            f"{st.session_state.campaign_title}.txt", "text/plain", use_container_width=True)

    with tab2:
        st.subheader("Campaign Cover Image")
        if 'cover_image_b64' in st.session_state:
            st.image(f"data:image/png;base64,{st.session_state.cover_image_b64}", caption="AI-generated cover image.")
            image_bytes = base64.b64decode(st.session_state.cover_image_b64)
            st.download_button("⬇️ Download Image (.png)", image_bytes,
                f"{st.session_state.campaign_title}_cover.png", "image/png", use_container_width=True)
        else: st.warning("Could not generate an image.")

    with tab3:
        st.subheader("Generate Formatted Report")
        st.warning("PDF generation requires `wkhtmltopdf` to be installed on your system.")
        if st.checkbox("Generate styled report from the text above"):
            with st.spinner("Creating formatted documents..."):
                sections_for_html = parse_text_for_html(st.session_state.final_text_output)
                env = Environment(loader=FileSystemLoader("templates"))
                template = env.get_template("report_template.html")
                report_data = {
                    'report_title': st.session_state.campaign_title, 'author_name': f"Directed by {st.session_state.author_input}",
                    'title_image_b64': st.session_state.get('cover_image_b64'), 'sections': sections_for_html,
                    'generation_date': datetime.now().strftime('%Y-%m-%d')}
                html_content = template.render(report_data)
                
                try: pdf_content = pdfkit.from_string(html_content, False, options={'enable-local-file-access': None})
                except Exception as e: pdf_content = None; st.error(f"PDF generation failed: {e}", icon="⚠️")

                st.markdown("---"); st.subheader("Downloads")
                dl_col1, dl_col2 = st.columns(2)
                with dl_col1:
                    st.download_button("⬇️ Download HTML Report", html_content.encode('utf-8'),
                        f"{st.session_state.campaign_title}.html", "text/html", use_container_width=True)
                with dl_col2:
                    if pdf_content:
                        st.download_button("⬇️ Download PDF Report", pdf_content,
                            f"{st.session_state.campaign_title}.pdf", "application/pdf", use_container_width=True)
                    else:
                        st.button("PDF Download Unavailable", disabled=True, use_container_width=True)

                st.markdown("---"); st.write("HTML Report Preview:")
                st.components.v1.html(html_content, height=600, scrolling=True)