from pydantic import BaseModel
from typing import List

class MovieRequest(BaseModel):
    movie_name: str
    no_of_recommendation: int



#for output
class RecommendationItem(BaseModel):
    title: str
    final_score: float


class RecommendationResponse(BaseModel):
    watched_movie: str
    recommendations: List[RecommendationItem]


    