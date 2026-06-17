import pandas as pd
import os
import html
import re
from datetime import datetime


def clean_movies_dataset(movies_dataset_path, min_date = datetime.strptime('2000-01-01', '%Y-%m-%d')) -> pd.DataFrame:
    # Load movie csv
    movies_df = pd.read_csv(movies_dataset_path)
    # Get dataset basic info
    movies_df.info()

    # We only want the following columns
    # id (Required)
    # title (Non-null)
    # genre
    # audienceScore
    # tomatoMeter
    # releaseDate[Theaters/Streaming] (Non-null, oldest date)

    movies_df = movies_df[['id', 'title', 'genre', 'audienceScore', 'tomatoMeter', 'releaseDateTheaters', 'releaseDateStreaming']]
    # Check column reduction effect on memory
    movies_df.info()
    print(f'Movie samples before cleaning {len(movies_df)}')

    # Filtering by null
    movies_df = movies_df[
        movies_df['id'].notnull() &
        movies_df['title'].notnull() &
        movies_df['genre'].notnull() &
        movies_df['audienceScore'].notnull() &
        movies_df['tomatoMeter'].notnull() &
        movies_df['releaseDateTheaters'].notnull() | movies_df['releaseDateStreaming'].notnull()
    ]

    # Filtering by releaseDate (only keep movies with a release date recent than year 2000)
    # Get oldest date and store in new column
    movies_df['releaseDate'] = movies_df[['releaseDateTheaters', 'releaseDateStreaming']].min(axis=1, skipna=True)
    movies_df.drop(columns=['releaseDateTheaters', 'releaseDateStreaming'], inplace=True)
    movies_df['releaseDate'] = movies_df['releaseDate'].astype('datetime64[ns]')
    # Apply actual filtering
    movies_df = movies_df[movies_df['releaseDate'] >= min_date]

    # Check filtering effect
    movies_df.info()
    print(f'Movie samples after cleaning {len(movies_df)}')

    return movies_df

def clean_reviews_dataset(reviews_dataset_path, filter_titles: list[str], min_word_count: int = 150) -> pd.DataFrame:
    # Load movie csv
    reviews_df = pd.read_csv(reviews_dataset_path)
    # Get dataset basic info
    reviews_df.info()

    # We only want the following columns
    # id (Required)
    # creationDate
    # reviewText(Non-null)
    # scoreSentiment(Non-null)
    # reviewState

    reviews_df = reviews_df[['id', 'creationDate', 'reviewText', 'scoreSentiment', 'reviewState']]
    reviews_df.info()

    # Filtering by null
    reviews_df = reviews_df[
        reviews_df['id'].notnull() &
        reviews_df['creationDate'].notnull() &
        reviews_df['reviewText'].notnull() &
        reviews_df['scoreSentiment'].notnull() &
        reviews_df['reviewState'].notnull()
    ]
    reviews_df.info()
    print(len(reviews_df))

    # Filter by movie id (review id)
    reviews_df = reviews_df[reviews_df['id'].isin(filter_titles)]
    reviews_df.info()
    print(len(reviews_df))

    # Replace html encoded characters with decoded characters
    def normalize_text(text):
        text = html.unescape(text)
        text = re.sub(r'[\u00A0\u2007\u202F]', ' ', text) # NBSP -> normal space
        text = re.sub(r'\s+', ' ', text)  # collapse whitespace
        return text.strip()

    reviews_df['reviewText'] = reviews_df['reviewText'].apply(normalize_text)

    # Filter by reviewText length
    word_regex = re.compile(
        r"[A-Za-z0-9]+(?:['’,.-][A-Za-z0-9]+)*",
        re.UNICODE
    )
    word_count = lambda text: len(word_regex.findall(text))
    reviews_df = reviews_df[reviews_df['reviewText'].apply(word_count) >= min_word_count]

    reviews_df.info()
    print(len(reviews_df))

    return reviews_df



if __name__ == '__main__':

    # datasets should be inside datasets directory, in current working directory
    cwd = os.getcwd()
    datasets_basepath = os.path.join(cwd, 'datasets')

    # Clean movies dataset
    movies_dataset_filename = 'rotten_tomatoes_movies.csv'
    movies_dataset_path = os.path.join(datasets_basepath, movies_dataset_filename)

    movies_df = clean_movies_dataset(movies_dataset_path)
    # Save cleaned movies dataset
    movies_df.to_csv(os.path.join(datasets_basepath, 'rotten_tomatoes_movies_clean.csv'), index=False)


    # Get movie ids
    movie_ids = movies_df['id'].unique().tolist()
    print(f"Unique movie ids {len(movie_ids)}")

    # Clean movie reviews dataset
    reviews_dataset_filename = 'rotten_tomatoes_movie_reviews.csv'
    reviews_dataset_path = os.path.join(datasets_basepath, reviews_dataset_filename)

    reviews_df = clean_reviews_dataset(reviews_dataset_path, filter_titles = movie_ids, min_word_count = 30)
    # Save cleaned movie revies dataset
    reviews_df.to_csv(os.path.join(datasets_basepath, 'rotten_tomatoes_movie_reviews_clean.csv'), index=False)
