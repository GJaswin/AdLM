from google import genai
from google.genai import types
from pydantic import BaseModel

# Replace with your actual Gemini API Key
client = genai.Client(api_key='AIzaSyCU7wQ-di4WtNWv4EgCRlpClWf7rIFvDCQ')

class AdAnalysis(BaseModel):
   url: str 
   desc: str
   malicious: bool

def malverts(ads_list):
    response = client.models.generate_content(
        model='gemini-2.5-flash-preview-05-20', 
        config=types.GenerateContentConfig(
            system_instruction="You are an LLM which can analyse advertisement URLs by fetching their content and determining whether it is a malicious ad or not. NSFW ads, fake and suspicious products, betting sites being advertised count as malicious ads. Return whether each ad is malicious or not, along with a one line description of the ad contents. Additionally, avoid analysing links that are not actual ads but just links to normal websites, only return analysis for actual ads",response_schema=list[AdAnalysis],response_mime_type="application/json"

        ),
        
        contents=f'{ads_list}'
    )
    return response.text