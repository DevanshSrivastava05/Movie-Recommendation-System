import streamlit as st
import pickle
import pandas as pd

import requests

st.markdown(
    """
    <style>
.poster-container {
    display: inline-block;
    margin: 10px;
    height: auto;
    width: 200px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.5);
    transition: transform 0.8s ease, filter 0.5s ease;
}

.poster-container img {
    width: 100;
    height: auto;

}

.poster-container h3 {
    text-align: center;
    margin-top: 3px;
    font-size: 18px; 
    color: black; 
}

    
.poster-container:hover {
        transform: scale(1.09); 
        filter: brightness(0.6); 
    }

.poster-container.active {
        transform: scale(1.14); 
        filter: brightness(1); 
        z-index: 2; 
     
    }

@media (max-width: 768px) {
    .poster-container {
        width: 40%;
    }
}
</style>
"""
,    unsafe_allow_html=True)

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=11c33e380fbc20d611aeacd80791e529&language=en-US".format(movie_id)
    max_retries = 25
    retry_count = 0
    while retry_count < max_retries:
        try:
            data = requests.get(url)
            data = data.json()
            if 'poster_path' in data and data['poster_path']:
                poster_path = data['poster_path']
                full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                return full_path, data.get('imdb_id')  # Return IMDb ID along with poster URL
            else:
                return None, None
        except Exception as e:
            print("Error fetching poster:", e)
            retry_count += 1
    print("Failed to fetch poster after {} retries".format(max_retries))
    return None, None

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distance = similarity[movie_index]
    movies_list = sorted(list(enumerate(distance)), reverse=True, key=lambda x: x[1])[1:10]
    recommended_movies = []
    recommended_movie_poster = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        # Fetch poster of the movie and IMDb ID
        poster_url, imdb_id = fetch_poster(movie_id)
        recommended_movie_poster.append((poster_url, imdb_id))  # Store both poster URL and IMDb ID
    return recommended_movies, recommended_movie_poster

movies_dict = pickle.load(open('movie_list.pkl','rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl','rb'))
st.title('CineSage: Your Personalized Movie Guide')
selected_movie = st.selectbox('Select a movie', movies['title'].values)
if st.button('Recommend'):
    names, posters = recommend(selected_movie)

    num_cols = 3
    num_rows = 3
    total_recommendations = min(len(posters), num_cols * num_rows)
    for i in range(0, total_recommendations, num_cols):
        row_posters = posters[i:i + num_cols]
        row_names = names[i:i + num_cols]
        col1, col2, col3 = st.columns(3)
        dummy_poster_url = "https://dummyimage.com/500x800/cccccc/000000&text=Poster+Not+Available"
        for j in range(num_cols):
            with col1 if j == 0 else col2 if j == 1 else col3:
                if j < len(row_posters):
                    poster_url, imdb_id = row_posters[j]  # Extract poster URL and IMDb ID
                    st.markdown(
                    f"""
                    <a href="https://www.imdb.com/title/{imdb_id}" target="_blank">
                        <div class="poster-container">
                            <img src="{poster_url}" alt="{row_names[j]}" style="width:100%;">
                            <h3 style="text-align:center;">{row_names[j]}</h3>
                        </div>
                    </a>
                    """
                    , unsafe_allow_html=True)
                else:
                    st.image(dummy_poster_url, use_column_width=True)
                    st.markdown(f"**{row_names[j]}**")