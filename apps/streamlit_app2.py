#it is giving continuous output by storing in variable 


#import require library
import pandas as pd
import streamlit as st
import requests
import os
import joblib

titles=joblib.load("models/title.pkl")     #already list

BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

url_recommedation = f"{BASE_URL}/recommendation"
url_top_n_movie = f"{BASE_URL}/top_n_movie"
url_evaluate=f"{BASE_URL}/evaluate_model"


st.set_page_config(
    page_title="Hybrid Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Hybrid Movie Recommendation System")

# ✅ Session state initialization
if "top_movies" not in st.session_state:
    st.session_state.top_movies = None

if "recommend_movies" not in st.session_state:
    st.session_state.recommend_movies = None

if "model_score" not in st.session_state:
    st.session_state.model_score = None


st.text('--'*120)

###################top n movies

st.header("Top Movies by Weightage :")

n=st.number_input('How Many top movies do you want ?',value=10,max_value=101)

number={'n':n}

if st.button('Top Rated Movies'):
    response = requests.post(f"{url_top_n_movie}?n={n}", json=number)

    if response.status_code == 200:
        result = response.json()
        st.session_state.top_movies = result.get("data", [])
    else:
        error_msg = response.json().get("error", "Unknown error occurred")
        st.error(f"Error: {error_msg}")

# ✅ Show stored output
if st.session_state.top_movies:
    st.subheader(f"Top '{ n }' Movie recommendated :")
    for i, movie in enumerate(st.session_state.top_movies, start=1):
        st.write(f"{i}. {movie['title']} (Score: {movie['Weight']})")

st.text('--'*120)

#############################recommendation of movies

st.header("Get movie recommendations using **Hybrid (Content + Collaborative + Popularity)** filtering :")

col1, col2 = st.columns(2)

with col1:
    movie_name = st.selectbox('Select a Movie:', titles)
    st.write('You selected:', movie_name)

with col2:
    no_of_recommendation = st.slider(
        "Number of Recommendations",
        min_value=1,
        max_value=20,
        value=5
    )
    st.write('You selected:', no_of_recommendation)

entry={'movie_name':movie_name,'no_of_recommendation':no_of_recommendation}

if st.button("Recommend Movies 🎯"):
    response = requests.post(url_recommedation, json=entry)

    if response.status_code == 200:
        result = response.json()
        st.session_state.recommend_movies = result.get("recommendations", [])
    else:
        error_msg = response.json().get("error", "Unknown error occurred")
        st.error(f"Error: {error_msg}")

# ✅ Show stored output
if st.session_state.recommend_movies:
    st.subheader(f"Movies recommended after movie '{movie_name}':")
    for i, movie in enumerate(st.session_state.recommend_movies, start=1):
        st.write(f"{i}. {movie['title']} (Score: {movie['final_score']})")

st.text('--'*120)


#############################Evaluation of model

st.header('Checking performance of Recommendation model in percentage')

if st.button('Checking performance'):
    response = requests.post(url_evaluate)

    if response.status_code == 200:
        st.session_state.model_score = response.json()
    else:
        error_msg = response.json().get("error", "Unknown error occurred")
        st.error(f"Error: {error_msg}")

# ✅ Show stored output
if st.session_state.model_score:
    st.subheader(st.session_state.model_score)

st.text('--'*120)

