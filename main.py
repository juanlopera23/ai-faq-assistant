from fastapi import FastAPI
from pydantic import BaseModel
from google import genai

client = genai.Client()

interaction = client.interactions.create(
    model="gemini-3.8-flash",
    input="Explain how AI works in a few words"
)
print(interaction.output_text)

app = FastAPI()

class Message (BaseModel):

    faq : str



faqs = {
    "What are your business hours?": "Monday to Friday, 8:00 AM to 6:00 PM.",
    "Where are you located?": "We are located in Medellín, Colombia.",
    "What services do you offer?": "We offer consulting and customer support services.",
    "How can I schedule an appointment?": "You can schedule an appointment through our website.",
    "What payment methods do you accept?": "We accept cash, credit cards, and bank transfers."
}

@app.get("/faqs")
async def list_faqs ():

    return faqs

@app.post ("/ask")
async def ask (message : Message):

    value = faqs.get(message.faq, "the faq doesn't exists")

    return {message.faq : value}