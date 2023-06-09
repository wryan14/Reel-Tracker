import os
import pandas as pd
from imdb import IMDb
from lxml import etree
from transformations import imdb_person_transform, imdb_company_transform, imdb_movie_transform

# Get the current script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the CSV file names in a 'data' folder within the same directory
person_csv = os.path.join(script_dir, 'data', 'imdb_person.csv')
personal_csv = os.path.join(script_dir, 'data', 'personal.csv')
imdb_movies_csv = os.path.join(script_dir, 'data', 'imdb_movies.csv')
director_csv = os.path.join(script_dir, 'data', 'director.csv')
moviecast_csv = os.path.join(script_dir, 'data', 'moviecast.csv')
writer_csv = os.path.join(script_dir, 'data', 'writer.csv')

class MovieParse:
    """
    A class to parse and insert movie and personal data into CSV files.
    
    Attributes
    ----------
    movieid : str
        The IMDb ID of the movie.
    watchdate : str
        The date the movie was watched.
    rating : int
        The rating assigned to the movie.
    method : str
        The method used to watch the movie.

    Methods
    -------
    check_exists(csv_file: str) -> bool
        Check if the movie exists in the given CSV file.
    insert_data(personal_only: bool = False) -> None
        Insert movie and personal data into appropriate CSV files.
    """
    def __init__(self, movieid, watchdate, rating, method):
        """
        Initialize a MovieParse object with movie ID, watch date, rating, and method.

        Parameters
        ----------
        movieid : str
            The IMDb ID of the movie.
        watchdate : str
            The date the movie was watched.
        rating : int
            The rating assigned to the movie.
        method : str
            The method used to watch the movie.
        """
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

    def check_exists(self, csv_file: str) -> bool:
        """
        Check if the movie exists in the given CSV file.

        Parameters
        ----------
        csv_file : str
            The CSV file to check for the movie.

        Returns
        -------
        bool
            True if the movie exists in the CSV file, False otherwise.
        """
        if pd.read_csv(csv_file).id.astype(str).str.lstrip('0').str.contains(self.movieid.lstrip('0')).any():
            return True
        else:
            return False

    def insert_data(self, personal_only: bool = False) -> None:
        """
        Insert movie and personal data into appropriate CSV files.

        If personal_only is True, insert only personal data. Otherwise, insert movie and personal data.

        Parameters
        ----------
        personal_only : bool, optional
            Whether to insert only personal data or not (default is False).
        """
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
            all_persons = all_persons[~all_persons['ID'].isnull()]
            all_persons['ID'] = all_persons['ID'].apply(lambda x: int(x))
            all_persons.to_csv(person_csv, mode='a', header=False, index=False)



            # Insert movie and person connections
            for role, csv_file in [('cast', moviecast_csv),
                                ('director', director_csv),
                                ('writer', writer_csv),
                                ]:
                role_df = pd.read_html(str(imdb_person_transform(role)(self.root)))[0]
                role_df['movie_id'] = self.movieid
                role_df = role_df[~role_df['ID'].isnull()]
                role_df['person_id'] = role_df['ID'].apply(lambda x: str(int(x)))
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


def imdb_api(movieid: str) -> etree._Element:
    """
    Get the XML root of an IMDb movie object.

    Parameters
    ----------
    movieid : str
        The IMDb ID of the movie.

    Returns
    -------
    etree._Element
        The XML root of the IMDb movie object.
    """
    ia = IMDb()
    tmp = ia.get_movie(movieid)
    root = etree.fromstring(tmp.asXML())
    return root

if __name__ == "__main__":
    movie_id = "0099810"
    watch_date = "2023-04-14"
    rating = 9
    method = "Blu-ray"

    movie_parse = MovieParse(movie_id, watch_date, rating, method)
