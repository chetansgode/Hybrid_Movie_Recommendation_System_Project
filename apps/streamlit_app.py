#import require library
import streamlit as st
import requests

#this is is depend on fastapi to predict output
#this app we are using in local system and also in docker file too so url of both are diff to predict same thing
#adjust url if host url not available then take by default local url 


import os

BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# http://127.0.0.1:8000/recommendation
# http://127.0.0.1:8000/evaluate_model
# http://127.0.0.1:8000/top_n_movie?n=5


url_recommedation = f"{BASE_URL}/recommendation"
url_top_n_movie = f"{BASE_URL}/top_n_movie"
url_evaluate=f"{BASE_URL}/evaluate_model"

