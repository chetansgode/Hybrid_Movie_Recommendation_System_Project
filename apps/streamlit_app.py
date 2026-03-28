#import require library
import pandas as pd
import streamlit as st
import requests
import os
import joblib

titles=joblib.load("models/title.pkl")     #already list


#movie_list = titles.tolist()
#this is is depend on fastapi to predict output
#this app we are using in local system and also in docker file too so url of both are diff to predict same thing
#adjust url if host url not available then take by default local url 

#regular for docker .yml file
BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

#if want to run fastapi and streamlit separetly then only use this line otherwise use above line
#BASE_URL = os.getenv("API_URL", "http://host.docker.internal:8000") 
# http://127.0.0.1:8000/recommendation
# http://127.0.0.1:8000/evaluate_model
# http://127.0.0.1:8000/top_n_movie?n=5

url_recommedation = f"{BASE_URL}/recommendation"
url_top_n_movie = f"{BASE_URL}/top_n_movie"
url_evaluate=f"{BASE_URL}/evaluate_model"


st.set_page_config(
    page_title="Hybrid Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Hybrid Movie Recommendation System")

# Session state initialization


st.text('--'*120)

###################top n movies

st.header("Top Movies by Weightage :")

n=st.number_input('How Many top movies do you want ?',value=10,max_value=101)

#fastapi output= {
#   "message": "Top 10 rated movies",
#   "data": [{ "title": "Shawshank Redemption, The (1994)",
#             "Weight": 4.533 },....}

number={'n':n}
if st.button('Top Rated Movies'):

    response = requests.post(f"{url_top_n_movie}?n={n}", json=number)

    if response.status_code == 200:
        result = response.json()
        recommendations = result.get("data", [])

        if recommendations:
            st.subheader(f"Top '{ n }' Movie recommendated :")
            for i, movie in enumerate(recommendations, start=1):
                st.write(f"{i}. {movie['title']} (Score: {movie['Weight']})")
        else:
            st.write("No recommendations found.")    
    else:
        # Handle error responses                    ##in fastapi>>return JSONResponse(status_code=500,content={"error": str(e)})

        error_msg = response.json().get("error", "Unknown error occurred")
        st.error(f"Error: {error_msg}")

st.text('--'*120)
#############################recommendation of movies

st.header("Get movie recommendations using **Hybrid (Content + Collaborative + Popularity)** filtering :")

# Input Section
col1, col2 = st.columns(2)

with col1:
# Streamlit selectbox
    movie_name = st.selectbox('Select a Movie:', titles)
    # Display the selected movie
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



# Button
if st.button("Recommend Movies 🎯"):
    # Send request to FastAPI recommendation endpoint
    response = requests.post(url_recommedation, json=entry)


#   output_fastapi={"watched_movie": "Waiting to Exhale (1995)",
#                   "recommendations": [
#                                       {
#                                       "title": "League of Their Own, A (1992)",
#                                       "final_score": 0.789
#                                        },...}

    if response.status_code == 200:
        result = response.json()
        recommendations = result.get("recommendations", [])

        if recommendations:
            st.subheader(f"Movies recommended after movie  '{movie_name}':")
            for i, movie in enumerate(recommendations, start=1):
                st.write(f"{i}. {movie['title']} (Score: {movie['final_score']})")
        else:
            st.write("No recommendations found.")

    else:
        # Handle error responses                    #fastapi code output >>>content={"error": result}
        error_msg = response.json().get("error", "Unknown error occurred")
        st.error(f"Error: {error_msg}")

st.text('--'*120)


#############################Evaluation of model

st.header('Checking performance of Recommendation model in percentage')

if st.button('Checking performance'):
    response = requests.post(url_evaluate)

    if response.status_code == 200:
        result = response.json()

        if result:
            st.subheader(f"{result}")
        else:
            st.write("No recommendations found.")

    else:
        error_msg = response.json().get("error", "Unknown error occurred")
        st.error(f"Error: {error_msg}")

st.text('--'*120)