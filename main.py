from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai

client = genai.Client()

app = FastAPI()

class Message (BaseModel):

    faq : str

class message_server(BaseModel):

    id: int
    question: str
    response : str

next_id =0


faqs = []

SYSTEM_INSTRUCTIONS = """
    You are an FAQ assistant.
    Your task is to compare the user's question with the following predefined list of questions and answers.
    Determine which predefined question is the most semantically similar to the user's question.
    If there is a clear match, respond only with the corresponding answer.
    Do not include explanations, reasoning, additional text, labels, or formatting.
    If the user's question does not match any of the available FAQ questions, respond exactly with:
    This is not an FAQ.
    FAQ list:
    What are your business hours?
    Answer: Monday to Friday, 8:00 AM to 6:00 PM.
    Where are you located?
    Answer: We are located in Medellín, Colombia.
    What services do you offer?
    Answer: We offer consulting and customer support services.
    How can I schedule an appointment?
    Answer: You can schedule an appointment through our website.
    What payment methods do you accept?
    Answer: We accept cash, credit cards, and bank transfers.    
    """


@app.post ("/ask",status_code= 201)
async def ask (message : Message):

    global next_id

    interaction = await client.aio.interactions.create(
        model="gemini-3.1-flash-lite",
        system_instruction= SYSTEM_INSTRUCTIONS,
        input= message.faq,
        generation_config={
            "thinking_level" : "low"
        }
    )

    response = interaction.output_text

    faq= message_server(
        id = next_id,
        question= message.faq,
        response = response
    )

    faqs.append(faq)

    next_id += 1
    
    return {message.faq : response}

@app.get("/responses")
async def list_responses():

    return faqs

@app.get("/response/{response_id}", status_code=201)
async def search_response (response_id : int):

    for item in faqs:
        if item.id == response_id:
            return item 

    raise HTTPException(
        status_code=404,
        detail= "the response doesn't exist"
    )

@app.delete("/response/{response_id}")
async def delete_response(response_id : int):

    for item in faqs:
        if item.id == response_id:
            faqs.remove(item)
            return faqs

    raise HTTPException(
        status_code= 404,
        detail= "The item doesn't exist"
    )