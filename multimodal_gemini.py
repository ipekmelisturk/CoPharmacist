import google.generativeai as genai
import time
import json
import os
from dotenv import load_dotenv
load_dotenv("GOOGLE_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=google_api_key)
from google.api_core import retry

gemini_retry = retry.Retry(
    initial=2.0,
    maximum=10.0,
    multiplier=1.0,
    deadline=60.0
)

class PrescriptionBot:
    def __init__(self):
        # Changed instructions to according to project description
        system_instruction = "You are an expert pharmacist specializing in handwritten medical prescriptions. Try to analyze images of documents and extracting the text. Analyze the provided image and return a description of the text in the image, including the prescription details if applicable."
        # Changed the model name accordingly
        self.prescription_model  = genai.GenerativeModel("models/gemini-1.5-pro-latest", system_instruction=system_instruction, generation_config={"response_mime_type": "application/json"})
        # TO DO: Add later on chat model for patient to talk a pharmacist

        #self.chat_model = genai.GenerativeModel("models/gemini-1.5-pro-latest", system_instruction=system_instruction)

        #self.transcript_model = genai.GenerativeModel(model_name="gemini-1.5-flash")

        recommendation_system_prompt = """\
You are a helper to a patient who sent an image for handwritten medical prescriptions. You should:
- Use the patient's prescription image.
- Extract the name of the medication, its dosage, and frequency.
- Provide side effects and recommendations for the medication.
Return the extracted information.
"""
        self.recommendation_model = genai.GenerativeModel("models/gemini-1.5-flash", system_instruction=recommendation_system_prompt)

        self.messages = [] # Chat history
        self.prompt_prescription = """\
Your patient has uploaded an image of a handwritten medical prescription. Extract the medication details from the image, including the name of the medication, dosage, and side effects. 
Using this JSON schema:
    PrescriptionDetails = {
        "medication_name": str,
        "dosage": str,
        "side_effects": str,
        "recommendations": str
    }
Return a `PrescriptionDetails`.
"""
        return
    
    @gemini_retry
    def generate_response(self, prompt) -> str:
        self.messages.append({'role': 'user', 'parts': [prompt]})
        response = self.chat_model.generate_content(self.messages)
        self.messages.append(response.candidates[0].content)
        return response.text

    @gemini_retry
    def process_file(self, file_path) -> dict:
        
        # upload file
        file = genai.upload_file(path=file_path)

        # verify the API has successfully received the files
        while file.state.name == "PROCESSING":
            time.sleep(1)
            file = genai.get_file(file.name)

        if file.state.name == "FAILED":
            raise ValueError(file.state.name)
        
        # generate response
        prompt = self.prompt_prescription
        self.messages.append({'role': 'user', 'parts': [file, prompt]})
        response = self.prescription_model.generate_content(self.messages, request_options={"timeout": 60})
        self.messages.append(response.candidates[0].content)
        return json.loads(response.text)

    
    