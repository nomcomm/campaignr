from openai import OpenAI
import os, requests, warnings, fnmatch, sys, re
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from IPython.display import display, Image, Audio
import numpy as np
warnings.filterwarnings('ignore')

OpenAI.api_key   = os.environ["OPENAI_API_KEY"]
openai_client	= OpenAI(api_key = OpenAI.api_key) 
headers		  = {"Content-Type": "application/json","Authorization": f"Bearer {OpenAI.api_key}"}
gpt_model		= "gpt-4o-mini"


def generate_simple(input_prompt):
	payload = {"model": gpt_model, "messages": [{ "role": "user", "content": [ { "type": "text",
		"text": input_prompt  },]}],}
	
	response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
	
	complex_response	= response.json()['choices'][0]['message']['content']
	return complex_response


def split_text_into_sections(text):
	# Regex pattern to match markers like {{0. ...}}, {{1. ...}}, etc.
	pattern = r'(\{\{\d+[^}]*\}\})'
	
	# Split the text based on the pattern, keeping the markers as separate elements
	sections = re.split(pattern, text)
	
	# List to store the structured content
	structured_sections = []
	current_section = ''

	for part in sections:
		# Check if the part matches the section marker
		if re.match(pattern, part):
			# If there's already content in current_section, add it to structured_sections
			if current_section:
				structured_sections.append(current_section.strip())
			# Start a new section with the current marker
			current_section = part
		else:
			# Append the text to the current section
			current_section += " " + part.strip()
	
	# Add the last section if there's any leftover content
	if current_section:
		structured_sections.append(current_section.strip())
	
	# Remove any empty items from the beginning of the list
	structured_sections = [section for section in structured_sections if section]
	
	return structured_sections



def generate_campaign_concept(n_ideas):
	concept_prompt	= "You are a campaign planner and organizer for a public communication campaign about health." +\
								  "You generate " + str(n_ideas) + " concept ideas for much-needed campaigns. " +\
								  """You are free to pick the topic - whether it is 
								  alcohol, drug use, accident prevention, etc -- that is up to you. 
								  You briefly list the issue, the goal of the campaign, the need for it (ideally with stats/facts). 
								  In terms of goal, you can chose between a general awareness campaign (goal to raise awereness about issue 
								  and make people know things about it),
								  a campaign targeting at peoples' attitudes and beliefs (goal to change their minds), 
								  and a campaign targeting at changing a behavior (e.g. make people separate waste, reduce texting and driving, 
								  or simply adopt or refrain from a health behavior, etc.).
								  All in less than 4 sentences.
								  You list  each generated idea line by line, like this 
                                  {{1. Issue: ... Need: ... Goal: ...}}
                                  {{2. Issue: ... Need: ... Goal: ... }}
                                  ... You don't use fluffy language that is just Kumbaya, but you are factful, concise, and confident.
								  """
	campaign_ideas = generate_simple(concept_prompt)
	campaign_ideas = split_text_into_sections(campaign_ideas)
	
	return campaign_ideas


def generate_basic_campaign_plan(input_campaign_concept):

		campaign_planning_prompt  = "You are a campaign planner and organizer for a public communication campaign about health. Here is a description of the campaign concept: "+\
								"-->" + input_campaign_concept + "." +\
								""" Your job now is to draft a first sketch of the campaign plan/proposal. 
								The structure and format for this is fixed and includes these numbered sections, which are to be formatted exactly as follows :
								
								{{0. [Generate and insert a clear and compelling ccampaign title]}} 
								
								{{1. Introduction}}: A brief motivational introduction about the issue and the overall context and goal/aim of the campaign. 
								A bit like a mission statement or summary, mixed with a sense of purpose or direction.
								
								{{2. Goals}}: These are typically specified as 
								a) whatever the key goal/aim/objctive is 
								b) just a goal of how many people will be exposed to the campaign.
								(make sure the goals follow the s-m-a-r-t format, i.e. are specific, measureable, attainable, realistic/relevant, 
								and time-bound.
								You can have different goals, or structure them into subgoals as you see fit. For example, an overarching goal could be to raise aareness
								about the issue, it could be to shift public or individual attitudes in the population or target audience, or it could be a behavior change goal.
								Importantly, you are very specific about those goals - whether they are about exposed people, gain in knowledge, change in attitude, or behavior.
								
								{{3.1 Formative Research - Situation Analysis}},  
								For the situation analysis: This describes the causal web that makes the issue a problem (e.g. alcohol, smoking 
								etc... what is it that causes this to be apublic health issue, which of those factors are malleable etc.
								
								{{3.2 Formative Research - Audience Analysis}}, 
								For the audience analysis. This specifies the primary and potential secondary audiences, and describes their 
								current knowledge, their relevant demographics and attitudes, and their media habits, i.e. how they can be reached.
								
								{{3.3 Formative Research - Analysis of Previous Communication Efforts}}.
								For the analysis of previous efforts: Are there well-known efforts that have been conducted. Eg., if the campaign 
								were about wildfire prevention, then you would have to mention the Smokey Bear campaign. It is important that 
								you are fact-based! Do not make up campaigns that did not exist.
								
								{{4. Theory and Messages}}: This lists the main socio-behavioral theory  to be used. For example, a drug prevention campaign may use 
								Inoculation Theory. You could also use just plain vanilla social-cognitive theory, or the theory of reasoned 
								action/theory of planned behavior, social norms, 
								the stages-of-change approach, the health belief model, or generic social marketing. Based on the theory you 
								chose, you then generate a rough descriptions of the kinds of messaging that follows from that.
								You do not have to create polished messages, just describe in broad, brushstroke terms how the theory suggests 
								certain kinds of messages and describe them at large so that a designer or message creator can then craft some 
								examples.
								
								{{5. Exposure and Channels}}: This section describes how the messages will reach the audience. For example, will the campaign leverage roadside 
								billboard messaging (adequate to prevent in-the-moment behaviors like texting and driving), or will it use radio ads,
								or social media messages, or posters in bathroom stalls, or whatever.
								You describe the general media strategy and you become quite concrete about how the campaign will look like, 
								including a time-phased description of what will happen when.
								
								{{6. Evaluation}}: Finally, you will describe how the campaign will be evaluated. You describe how the performance 
								will be measured online (process evaluation) and after-the-fact (outcome evaluation), which measures will be used 
								(e.g. survey, behavior counting, analysis of traces, digital analytics), who and how they will be collected, 
								and when. You can also specify aspects of the evaluation design, i.e. how you can ascertain that it is the campaign 
								that  moved the needle on the issue (e.g. need a baseline, need a control group?).
								
								{{7. Summary and Outlook}}: A quick statement about what the campaign will have changed, how the world will look like. 
								Factual, but also optimistic and motivational
								
								{{8. Appendix}}: details like e.g. Time-Plan, Message Briefs, Budget. All with less than 2 breaks
								
								Important formatting requirements: 
								You will keep the sections exactly as specified, particularly the {{number of section: section content}} structure. 
								Transitions between sections have a double line break. 
								Otherwise, you just write text in plain text without further breaks or additional symbols or comments. 
								Only the separations between titles or subtitles have single breaks.
								Thus, you only return larger sections for {{0. Title}}, {{1. Introduction}}, {{2 ...}}, {{3.1 ...}}, {{3.2 ...}}. . Just those large chunks. """
		
		basic_campaign_plan = generate_simple(campaign_planning_prompt)
		basic_campaign_plan = split_text_into_sections(basic_campaign_plan)
		return basic_campaign_plan


def generate_campaign_cover(input_campaign_title):
	cover_image_prompt	   = "Generate a prompt for a cover image for a public health campaign titled: " + input_campaign_title + "." +\
							   "Remove  clutter text, like prompts or # and * , just focus on the description. " +\
							   "Make it atmospheric and themed to the milieu it is set in, incorporating color and design elements " +\
							   "that match the theme of Michigan State University, like the Spartan helmet, green and white, or Michigan." +\
							   "Also hint at the hard-boiled detective genre, but with a touch of quirkiness and positive spirit. "+\
							   "Make the outer parts of the image blurred and in the shadows." 
	
	payload = {"model": gpt_model, "messages": [{ "role": "user", "content": [ { "type": "text",
			  "text": cover_image_prompt  },]}],}
	response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
	cover_image_prompt = response.json()['choices'][0]['message']['content']
	response = openai_client.images.generate(model="dall-e-3",
					prompt = cover_image_prompt,
					size="1024x1024", quality="standard", n=1)
	image_response = requests.get(response.data[0].url)
	
	os.makedirs("./01_output/"+ input_campaign_title, exist_ok=True)
	image_title = "./01_output/" + input_campaign_title + "/" + input_campaign_title + "_Cover.png"
	if image_response.status_code == 200:
		with open(image_title, 'wb') as f:
			f.write(image_response.content)
		print("Image downloaded and saved ...")
	
	# Load and display the Cover
	img = mpimg.imread(image_title)
	plt.imshow(img)
	plt.axis('off')  
	plt.title(input_campaign_title)
	plt.show()
	return image_title