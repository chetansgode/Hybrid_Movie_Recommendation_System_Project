import pandas as pd
import joblib
import os
import sys

# Fix imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
MODEL_DIR = os.path.join(ROOT_DIR, "models")

sys.path.append(ROOT_DIR)

# Load models
pivot_table_rating = joblib.load(os.path.join(MODEL_DIR, "pivot_table_rating.pkl"))
collab_model = joblib.load(os.path.join(MODEL_DIR, "collab_model.pkl"))
movie_df = joblib.load(os.path.join(MODEL_DIR, "movie_df.pkl"))
cosine_sim = joblib.load(os.path.join(MODEL_DIR, "cosine_sim.pkl"))
df = joblib.load(os.path.join(MODEL_DIR, "df.pkl"))

class MovieRecommender:

    def __init__(self):
        self.pivot_table_rating = pivot_table_rating
        self.collab_model = collab_model
        self.movie_df = movie_df
        self.cosine_sim = cosine_sim
        self.df = df

    # ------------------------------
    # get_top_n_rated_movies
    # ------------------------------    

    def get_top_n_rated_movies(self, n):
        return {
        "message": f"Top {n} rated movies",
        "data": self.df[['title','Weight']]
            .drop_duplicates()
            .sort_values('Weight', ascending=False)
            .head(n)
            .reset_index(drop=True)
            .round({'Weight': 3})
            .to_dict(orient="records")
    }
    # ------------------------------
    # Hybrid Recommendation Function
    # ------------------------------
    def final_hybrid_recommendation(self, movie_name, no_of_recommendation=5):

        if movie_name not in self.pivot_table_rating.index:
            return f"Movie '{movie_name}' not in training data or less than 50 rating counts"

        # Step 1: Collaborative Filtering
        movie_index = self.pivot_table_rating.index.get_loc(movie_name)

        distances, indices = self.collab_model.kneighbors(
            self.pivot_table_rating.iloc[movie_index, :].values.reshape(1, -1),
            n_neighbors=20
        )

        movie_indices = indices[0][1:]

        hybrid_df = pd.DataFrame({
            "title": self.pivot_table_rating.index[movie_indices]
        })

        # Step 2: Content Similarity
        indices_content = pd.Series(
            self.movie_df.index,
            index=self.movie_df['title']
        ).to_dict()

        idx = indices_content.get(movie_name, None)

        if idx is not None:
            sim_scores = list(enumerate(self.cosine_sim[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

            sim_scores_dict = {
                self.movie_df['title'].iloc[i[0]]: i[1]
                for i in sim_scores
            }

            hybrid_df['content_sim'] = hybrid_df['title'].map(sim_scores_dict)

        else:
            hybrid_df['content_sim'] = 0

        # Step 3: Popularity
        hybrid_df = hybrid_df.merge(
            self.df[['title', 'Weight']].drop_duplicates(),
            on='title',
            how='left'
        )

        # Step 4: Final Score
        hybrid_df['final_score'] = round(
            0.5 * (1 / (1 + distances[0][1:])) +
            0.3 * hybrid_df['content_sim'] +
            0.2 * hybrid_df['Weight'] / hybrid_df['Weight'].max()
        ,3)

        hybrid_df = hybrid_df.sort_values(
            'final_score',
            ascending=False
        ).reset_index()
        hybrid_df.index=hybrid_df.index+1

        return hybrid_df[['title', 'final_score']].head(no_of_recommendation)


    # ------------------------------
    # Model Evaluation
    # ------------------------------
    def evaluate_model(self):

        scores = []

        users = self.df['userId'].unique()[:20]

        for user in users:

            user_data = self.df[self.df['userId'] == user]

            liked_movies = user_data[
                user_data['rating'] >= 4
            ]['title'].tolist()

            if len(liked_movies) < 2:
                continue

            test_movie = liked_movies[0]
            actual_movies = liked_movies[1:]

            try:
                recommended = self.final_hybrid_recommendation(
                    test_movie,
                    20
                )['title'].tolist()

            except:
                continue

            recommended = [i.lower() for i in recommended]
            actual_movies = [i.lower() for i in actual_movies]

            hit = len(set(recommended) & set(actual_movies)) / len(recommended)

            scores.append(hit)

        return (f"Average_Recommendation_Score_model: {round(sum(scores) / len(scores),4)*100} %")