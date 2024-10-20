import httpx
from typing import Union
import string    
import random # define the random module  
import os
import traceback
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File
from fastapi import FastAPI, Request, Depends, UploadFile, status, Response, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse
from sqlalchemy.orm import Session
import sys
from datetime import datetime  # Import the date type
import traceback
from typing import List
import json
from app import main

app = FastAPI()

# CORS middleware
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chat_history = []

base_url = "/api"

@app.get(base_url + "/privacy-policy", status_code=200)
def welcome(request: Request, response: Response):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Privacy Policy</title>
    </head>
    <body>
        <h3>Introduction</h3>
        <p>Soul Canvas ("we," "our," "us") is committed to protecting your privacy. This Privacy Policy explains how your personal information is collected, used, and shared when you visit or make a purchase from [Your Website/App Name] (the "Site" or "App").</p>
        <h3>Information We Collect</h3>
        <p> 
            When you visit the Site, we automatically collect certain information about your device, including information about your web browser, IP address, time zone, and some of the cookies that are installed on your device. Additionally, as you browse the Site, we collect information about the individual web pages or products that you view, what websites or search terms referred you to the Site, and information about how you interact with the Site. We refer to this automatically collected information as "Device Information."
        </p>
        <h3>How We Use Your Information</h3>
        <p>
            We use the Order Information that we collect generally to fulfill any orders placed through the Site (including processing your payment information, arranging for shipping, and providing you with invoices and/or order confirmations). Additionally, we use this Order Information to:

        Communicate with you;
        Screen our orders for potential risk or fraud; and
        When in line with the preferences you have shared with us, provide you with information or advertising relating to our products or services.
        We use the Device Information that we collect to help us screen for potential risk and fraud (in particular, your IP address), and more generally to improve and optimize our Site (for example, by generating analytics about how our customers browse and interact with the Site, and to assess the success of our marketing and advertising campaigns).
        </p>
    </body>
    </html>
    """
    response.status_code = status.HTTP_200_OK
    return HTMLResponse(content=html_content)

@app.get(base_url + "/", status_code=200)
def welcome(request: Request, response: Response):
    response.status_code = status.HTTP_200_OK
    return "Welcome to webhook"

@app.get(base_url + "/webhook", status_code=200)
def webhook_callback(request: Request, response: Response):
    print("webhook start")
    request_param = {
        "mode": request.query_params.get("hub.mode"),
        "challenge": request.query_params.get("hub.challenge"),
        "verify_token": request.query_params.get("hub.verify_token")
    }

    my_token = "EEEE0-0289747-SC-820479"
    
    if request_param["mode"] and request_param["verify_token"]:

        if request_param["mode"] == "subscribe" and request_param["verify_token"] == my_token:
            response.status_code = status.HTTP_200_OK
            #return request_param["challenge"]
            return JSONResponse(content=int(request_param["challenge"]))
        else:
            response.status_code = status.HTTP_403_FORBIDDEN
            
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return None
    

async def send_message(to, message):
    try:

        token = "EAAW70TyVLb8BOyA6NyQpVBxCuZBTcZBpWvbqLjWb8eIWKcq9ZBGVlOrPm3lof1Gp8LjYZAzhknL4ttGHMCEkPBC2H5t0LcA26YpSf1dE0QS735EQwjjSGMycRf9m0orZBq8h6ZBzWfjTTETr1m0vBZAux4AEM7JRbR5oEalap8HvucDmgmczCvD6NWQQRZAxoXks2PwI8X2aHF4e0RMHsLQZD"
        async with httpx.AsyncClient() as client:
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to,
                
                "type": "text",
                "text": {
                    "body": message
                }
            }
            headers = {
                "Authorization": f"Bearer {token}"
            }
            response = await client.post("https://graph.facebook.com/v19.0/336244906239007/messages", json=payload, headers=headers)
            data = response.json()
            # print("message sent: ", data)
            return {"data": data}
    except Exception as e:
        print(traceback.format_exc())
        print(str(e))


@app.get(base_url + "/get-message", status_code=200)
async def generate_response(msg: str, request: Request, response: Response):
    await send_message("918699437166", msg)
    # request_body = await request.body()
    # request_body_json = request_body.decode("utf-8")  # Decode byte string to UTF-8
    # request_body_data = json.loads(request_body_json)  # Parse JSON data
    print(msg)  # Print the request body


def generate_random_id():
    S = 18  # number of characters in the string.  
    # call random.choices() string module to find the string in Uppercase + numeric data.  
    ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = S))    
    return str(ran)

@app.post(base_url + "/webhook", status_code=200)
async def webhook_msg(request: Request, response: Response):
    try:
        request_body = await request.body()
        request_body_json = request_body.decode("utf-8")  # Decode byte string to UTF-8
        request_body_data = json.loads(request_body_json)  # Parse JSON data
        # print(request_body_data)  # Print the request body

        if request_body_data['entry'] and request_body_data['entry'][0]['changes'] \
            and request_body_data['entry'][0]['changes'][0]['value'] and request_body_data['entry'][0]['changes'][0]['value']['messages']:
            # print("messages: ")
            # print(request_body_data['entry'][0]['changes'][0]['value']['messages'])

            msg_from = request_body_data['entry'][0]['changes'][0]['value']['messages'][0]['from']
            msg_body = request_body_data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']

            user_message = {
                'from': msg_from,
                'text': msg_body
            }
            # print("user_message = ", user_message)
            
            # question_id = generate_random_id()
            # user_chat_history = get_user_chat_history(msg_from, question_id, msg_body)
            global chat_history

            if msg_body.lower() == "new session":
                chat_history = []
                print("New session created")
                await send_message(msg_from, "New session created. How may I help you?")
                return {"message": "Request received"}
            elif msg_body.lower() == "no":
                chat_history = []
                await send_message(msg_from, "Thanks! It was nice talking to you :) \nHave a nice Day!\nBye!")
                return {"message": "Request received"}
            
            print("chat_history: ", chat_history)

            output, chat_history = main(msg_body, chat_history)
            # print("OUTPUT: ", output)
            # update_answer(msg_from, question_id, output)
            await send_message(msg_from, output)
            await send_message(msg_from, "Do you have any follow up question? If not please type 'No'")

            return {"message": "Request received"}
    except Exception as e:
        print("Exception: ", str(e))

    