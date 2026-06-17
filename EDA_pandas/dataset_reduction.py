import os
import pandas as pd

if __name__ == '__main__':
    # datasets should be inside datasets directory, in current working directory
    cwd = os.getcwd()
    datasets_basepath = os.path.join(cwd, 'datasets')

    reviews_dataset_filename = 'rotten_tomatoes_movie_reviews_clean.csv'
    reviews_dataset_path = os.path.join(datasets_basepath, reviews_dataset_filename)

    # Load clen reviews CSV
    reviews_df = pd.read_csv(reviews_dataset_path)
    reviews_df.info()
    print(f'{len(reviews_df)} rows')
    print(f'{reviews_df['id'].unique().shape[0]} original movies')

    # Apply stratified subsampling by movie (id)
    proportion = 0.2
    subsample = (
        reviews_df[['id', 'creationDate']].groupby('id', as_index=False)
        .apply(lambda x: x.sample(
            # n=max(1, math.ceil(len(x) * proportion)),
            frac=proportion,
            random_state=42)
        )
    )

    stratified_sample = reviews_df.loc[subsample.index]
    stratified_sample.info()
    print(f'{len(stratified_sample)} rows')
    print(f'{stratified_sample['id'].unique().shape[0]} subsampled movies')

    # Save subsampled dataset
    stratified_sample.to_csv(os.path.join(datasets_basepath, 'rotten_tomatoes_movie_reviews_clean_subsampled.csv'), index=False)

    # original_id_counts = reviews_df.groupby('id').size()
    # print(f"Original proportion {original_id_counts.sort_values(ascending=False).head()}")
    #
    # id_counts = stratified_sample.groupby('id').size()
    # print(f"Sampled proportion {id_counts.sort_values(ascending=False).head()}")

