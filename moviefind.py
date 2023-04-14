import os
import pandas as pd
from imdb import IMDb
from lxml import etree
from transformations import imdb_person_transform, imdb_company_transform, imdb_movie_transform

# Get the current script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the CSV file names in a 'data' folder within the same directory
person_csv = os.path.join(script_dir, 'data', 'person.csv')
production_company_csv = os.path.join(script_dir, 'data', 'production_company.csv')
personal_csv = os.path.join(script_dir, 'data', 'personal.csv')
imdb_movies_csv = os.path.join(script_dir, 'data', 'imdb_movies.csv')
director_csv = os.path.join(script_dir, 'data', 'director.csv')
moviecast_csv = os.path.join(script_dir, 'data', 'moviecast.csv')
writer_csv = os.path.join(script_dir, 'data', 'writer.csv')

class MovieParse:
    def __init__(self, movieid, watchdate, rating, method):
        self.movieid = movieid
        self.watchdate = watchdate
        self.rating = rating
        self.method = method

        exists = self.check_exists(imdb_movies_csv)
        if exists:
            print('Duplicate Movie: adding personal data')
            self.insert_data(personal_only=True)
        else:
            self.root = imdb_api(self.movieid)
            self.insert_data()

    def check_exists(self, csv_file):
        if pd.read_csv(csv_file).id.astype(str).str.lstrip('0').str.contains(self.movieid.lstrip('0')).any():
            return True
        else:
            return False

    def insert_data(self, personal_only=False):
        if not personal_only:
            # Insert movie data
            tmpdf = pd.read_html(str(imdb_movie_transform()(self.root)))[0]
            tmpdf.to_csv(imdb_movies_csv, mode='a', header=False, index=False)

            # Insert person data
            person_dfs = []
            for role in ['cast', 'director', 'producer', 'writer', 'composer', 'cinematographer']:
                person_dfs.append(pd.read_html(str(imdb_person_transform(role)(self.root)))[0])
            all_persons = pd.concat(person_dfs).reset_index(drop=True)
            all_persons = all_persons.drop_duplicates()
            all_persons.to_csv(person_csv, mode='a', header=False, index=False)

            # Insert company data
            prod_comp = pd.read_html(str(imdb_company_transform('production-companies')(self.root)))[0]
            prod_comp = prod_comp.drop_duplicates()
            prod_comp.to_csv(production_company_csv, mode='a', header=False, index=False)

            # Insert movie and person connections
            for role, csv_file in [('cast', moviecast_csv),
                                ('director', director_csv),
                                ('writer', writer_csv),
                                ]:
                role_df = pd.read_html(str(imdb_person_transform(role)(self.root)))[0]
                role_df['movie_id'] = self.movieid
                role_df['person_id'] = role_df['ID'].astype(str)
                role_df = role_df[['person_id', 'movie_id']]
                last_id = pd.read_csv(csv_file)['id'].max() if os.path.exists(csv_file) else 0
                role_df['id'] = range(int(last_id) + 1, int(last_id) + len(role_df) + 1)
                role_df = role_df[['id', 'movie_id', 'person_id']]
                role_df.to_csv(csv_file, mode='a', header=False, index=False)

        # Insert personal data
        new_entry = pd.DataFrame({'movie_id': [self.movieid],
                                'watch_date': [self.watchdate],
                                'rating': [self.rating],
                                'method': [self.method]})
        last_id = pd.read_csv(personal_csv)['id'].max() if os.path.exists(personal_csv) else 0
        new_entry['id'] = last_id + 1
        new_entry = new_entry[['id', 'movie_id', 'watch_date', 'rating', 'method']]
        new_entry.to_csv(personal_csv, mode='a', header=False, index=False)


def imdb_api(movieid):
    ia = IMDb()
    tmp = ia.get_movie(movieid)
    root = etree.fromstring(tmp.asXML())
    return root

if __name__ == "__main__":
    movie_id = "0133093"
    watch_date = "2023-04-14"
    rating = 9
    method = "Blu-ray"

    movie_parse = MovieParse(movie_id, watch_date, rating, method)
