from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pandas as pd
import sys
import os

# Fix path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
sys.path.append(ROOT_DIR)

# import pydantic model
from src.pydantic_model import MovieRequest,RecommendationResponse,RecommendationItem

# Import your recommender
from notebook.final_model import MovieRecommender

#load model
model = MovieRecommender()


#create Fastapi object
app=FastAPI()
Model_version=1.1

#Create Endpoint 
@app.get("/")
def hello():
    return{'Message':'This API recommendate movie to users'}

#endpoint
@app.get('/health')               
def health_check() -> dict :                #for machine visualisation
    return {
            'status':'ok',
            'version':Model_version,
            'model_loaded':model is not None}


#endpoint
@app.post("/top_n_movie")
def top_n_movie(n : int=10):
    try:
        return JSONResponse(status_code=200,content=model.get_top_n_rated_movies(n))
    except Exception as e:
         return JSONResponse(status_code=500,content={"error": str(e)})





@app.post("/recommendation",response_model=RecommendationResponse) #for output verification
def recommedation_of_movies(data:MovieRequest):    #for input varification
    movie_name= data.movie_name
    no_of_recommendation= data.no_of_recommendation

    result = model.final_hybrid_recommendation(
        movie_name,
        no_of_recommendation
    )


    try:
        return JSONResponse(status_code=200,content={
        "watched_movie": data.movie_name,
        "recommendations": result.to_dict(orient="records")            #this create dataframe to dict
    })

    except Exception as e:
         return JSONResponse(status_code=500,content={"error": str(e)})



  
#endpoint to check model performance
@app.post("/evaluate_model")
def evaluate_model():
    try:

        return JSONResponse(status_code=200,content=model.evaluate_model())
    except Exception as e:
        return JSONResponse(status_code=500,content={"error": str(e)})






# print(model.final_hybrid_recommendation('Toy Story (1995)',5))

# print(model.evaluate_model())

# print(model.get_top_n_rated_movies(10))