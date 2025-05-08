import os
import streamlit as st
import random
import configparser
import smtplib
import spacy
import torch
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing import Annotated
from typing_extensions import TypedDict

torch.classes.__path__ = [os.path.join(torch.__path__[0], torch.classes.__file__)]

# Load NLP model
nlp = spacy.load("en_core_web_trf")

# Read configuration
config = configparser.ConfigParser()
config_path = os.path.join(os.getcwd(), ".streamlit", "config.ini")
config.read(config_path)

groq_api_key = config["SETTINGS"].get("GROQ_API_KEY")
email_address = config["SETTINGS"].get("EMAIL_ADDRESS")
email_password = config["SETTINGS"].get("EMAIL_PASSWORD")

if not email_address or not email_password or not groq_api_key:
    st.error("Error: Missing configuration values. Check config.ini.")
    st.stop()

# Initialize LLM
llm = ChatGroq(groq_api_key=groq_api_key, model_name="Gemma2-9b-It")

# Define conversation state
class State(TypedDict):
    messages: Annotated[list, add_messages]
    user_email: str
    otp_verified: bool

# Generate OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Send OTP via SMTP
def send_otp_via_smtp(email, otp):
    subject = "Email Verification OTP"
    body = f"Your OTP is: {otp}"

    msg = MIMEMultipart()
    msg["From"] = email_address
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email_address, email_password)
        server.sendmail(email_address, email, msg.as_string())
        server.quit()
        return "OTP sent successfully!"
    except Exception as e:
        return f"Error sending OTP: {e}"

# Extract location from user query
def extract_location(user_message):
    doc = nlp(user_message)
    for ent in doc.ents:
        if ent.label_ in ["GPE", "LOC"]:  
            return ent.text
    return None

# Get response from LLM
def chatbot_response(user_message):
    location = extract_location(user_message)
    modified_query = f"List historical monuments near {location}." if location else user_message
    response = llm.invoke([{"role": "user", "content": modified_query}])
    return response.content

# Chatbot node
def chatbot(state: State):
    last_message = state["messages"][-1].content.lower()
    historical_keywords = ["monument", "historical", "heritage", "ruins", "castle", "temple", "fort", "palace", "tomb"]
    location = extract_location(last_message)

    if location or any(keyword in last_message for keyword in historical_keywords):
        response = chatbot_response(last_message)
        return {"messages": [response]}
    else:
        return {"messages": ["I specialize in historical monuments. Please ask about historical monuments only ."]}

# Ask for email
def ask_for_email(state: State):
    last_message = state["messages"][-1].content.lower()
    trigger_keywords = ["historical places", "travel", "monument", "recommendation"]

    if any(keyword in last_message for keyword in trigger_keywords):
        email = st.text_input("Please share your email if you would like more details about historical monuments via email:", key="email")

        if email:
            if "user_email" in st.session_state and st.session_state.user_email == email:
                return {"messages": [f"OTP already sent to {st.session_state.user_email}. Please verify."]}

            st.session_state.user_email = email
            st.session_state.otp = generate_otp()
            st.session_state.otp_verified = False
            st.session_state.retry_count = 0

            send_otp_via_smtp(email, st.session_state.otp)
            return {"messages": [f"OTP has been sent to {st.session_state.user_email}. Please verify."]}

            if email.lower() in ["no", "n", "skip"]:
                return {"messages": ["No worries! Have a great day!"]}

    return {}



# Verify OTP node
def verify_otp(state: State):
    if "retry_count" not in st.session_state:
        st.session_state.retry_count = 0

    user_otp = st.text_input("Enter OTP:", key="otp_input")

    if user_otp:
        if "otp" in st.session_state and user_otp == st.session_state.otp:
            st.session_state.otp_verified = True
            st.success("OTP verified! You will receive details soon.")
            return {"messages": ["OTP verified! You will receive details soon."]}

        # Handle incorrect OTP attempts
        st.session_state.retry_count += 1
        attempts_left = 3 - st.session_state.retry_count

        if attempts_left > 0:
            st.error(f"Incorrect OTP. Attempts left: {attempts_left}")
        else:
            del st.session_state.otp  # Clear OTP after too many failed attempts
            return {"messages": ["Too many failed attempts. Please request a new OTP."]}

    return {}

# Build graph
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("ask_for_email", ask_for_email)
graph_builder.add_node("verify_otp", verify_otp)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", "ask_for_email")
graph_builder.add_edge("ask_for_email", "verify_otp")
graph_builder.add_edge("verify_otp", END)

graph = graph_builder.compile()

# Streamlit UI
st.title("Historical Monuments Chatbot")
user_input = st.text_input("Hey, I am a historical chatbot! Tell me how I can help you regarding historical monument queries")

if user_input:
    state = {"messages": [{"role": "user", "content": user_input}], "user_email": "", "otp_verified": False}

    for event in graph.stream(state):
        for value in event.values():
            if value and isinstance(value, dict) and "messages" in value:
                for msg in value["messages"]:
                    st.write(f"Assistant: {msg}")
