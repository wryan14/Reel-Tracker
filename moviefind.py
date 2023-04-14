from imdb import IMDb
from lxml import etree
import pandas as pd
import psycopg2
from transformations import imdb_person_transform, imdb_company_transform, imdb_movie_transform


class MovieParse():
    def __init__(self, movieid, watchdate, rating, method):
        '''
            movieid: IMDB Movie ID
            watchdate: Date Movie was watched (YYYY-mm-dd)
            rating: Personal Rating of Movie
        '''
        self.movieid = movieid
        self.watchdate = watchdate 
        self.rating = rating 
        self.method = method
        
        # data base connections 
        self.connection = psycopg2.connect(user='wryan14', password='89957', host='127.0.0.1', port='5432', database='mydb')
        self.cursor = self.connection.cursor() 
        
        exists = self.check_exists()
        if exists==True:
            print('Duplicate Movie: adding personal data')
            self.personal_insert()
            self.connection.commit()
        else:
            self.root = imdb_api(self.movieid)
            self.movie_insert()
            self.person_insert()
            self.personal_insert()
            self.company_insert()
            self.connection.commit()
            
            
    def check_exists(self, table='imdb_movie'):
       
        query = '''SELECT COUNT(id) FROM {} WHERE id={}'''.format(table, self.movieid.lstrip('0'))
        self.cursor.execute(query)
        self.connection.commit()
        rc = self.cursor.fetchall()[0][0]
        
        if rc!=0:
            return True
        else:
            return False
    
    def check_author_exists(self, personid):
        query = '''SELECT COUNT(id) FROM imdb_person WHERE id={}'''.format(personid.lstrip('0'))
        self.cursor.execute(query)
        self.connection.commit() 
        rc = self.cursor.fetchall()[0][0]
        if rc!=0:
            return True
        else:
            return False

    def check_company_exists(self, personid):
        query = '''SELECT COUNT(id) FROM imdb_company WHERE id={}'''.format(personid.lstrip('0'))
        self.cursor.execute(query)
        self.connection.commit() 
        rc = self.cursor.fetchall()[0][0]
        if rc!=0:
            return True
        else:
            return False

    def personal_insert(self):
        query = '''INSERT INTO personal (movie_id, watch_date, rating, method) VALUES (%s, %s, %s, %s)'''
        record_to_insert = (self.movieid, self.watchdate, self.rating, self.method)
        self.cursor.execute(query, record_to_insert)
        # self.connection.commit() 
    
    def movie_insert(self):
        query = '''INSERT INTO imdb_movie (id, title, runtime, budget, opening_weekend, 
        worldwide_gross, rating, votes, cover_url, cover_url_full, plot_outline, year,
        plot, synopsis, locations, genres) VALUES (%s, %s, %s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s)'''
        
        tmpdf = pd.read_html(str(imdb_movie_transform()(self.root)))[0]
        record_to_insert = [list(row) for row in tmpdf.itertuples(index=False)][0] 
        self.cursor.execute(query, record_to_insert)
        # self.connection.commit()
    
    def person_insert(self):
        '''Gather person data from XML file'''
        moviecast = pd.read_html(str(imdb_person_transform('cast')(self.root)))[0]
        director = pd.read_html(str(imdb_person_transform('director')(self.root)))[0]
        producer = pd.read_html(str(imdb_person_transform('producer')(self.root)))[0]
        writer = pd.read_html(str(imdb_person_transform('writer')(self.root)))[0]
        composer = pd.read_html(str(imdb_person_transform('composer')(self.root)))[0]
        cinemat = pd.read_html(str(imdb_person_transform('cinematographer')(self.root)))[0]
        
        all_persons = pd.concat([moviecast, director, producer, writer, composer, cinemat])
        all_persons = all_persons.reset_index(drop=True)
        
        all_persons['duplicate'] = all_persons['ID'].apply(lambda x: self.check_author_exists(str(x)))
        new_persons = all_persons[all_persons['duplicate']==False]
        new_persons = new_persons.drop_duplicates()
        
        # add new persons
        for idx, row in new_persons.iterrows():
            record_to_insert = [row['ID'], row['Name']]
            query = '''INSERT INTO imdb_person (id, name) VALUES (%s,%s)'''
            self.cursor.execute(query, record_to_insert)
            # self.connection.commit()
        
        # add movie and person connections
        moviecast['ID'].apply(lambda x: self.movie_person_insert('moviecast', [self.movieid, x]))
        director['ID'].apply(lambda x: self.movie_person_insert('director', [self.movieid, x]))
        producer['ID'].apply(lambda x: self.movie_person_insert('producer', [self.movieid, x]))
        writer['ID'].apply(lambda x: self.movie_person_insert('writer', [self.movieid, x]))
        composer['ID'].apply(lambda x: self.movie_person_insert('composer', [self.movieid, x]))
        cinemat['ID'].apply(lambda x: self.movie_person_insert('cinemat', [self.movieid, x]))

    def company_insert(self):
        '''Gather production company data from XML file'''
        prod_comp = pd.read_html(str(imdb_company_transform('production-companies')(self.root)))[0]
        all_companies = prod_comp 
        all_companies['duplicate'] = all_companies['ID'].apply(lambda x: self.check_company_exists(str(x)))
        new_companies = all_companies[all_companies['duplicate']==False]
        new_companies = new_companies.drop_duplicates()
        # add new persons
        for idx, row in new_companies.iterrows():
            record_to_insert = [row['ID'], row['Name']]
            query = '''INSERT INTO imdb_company (id, name) VALUES (%s,%s)'''
            self.cursor.execute(query, record_to_insert)
            # self.connection.commit()
        
        prod_comp['ID'].apply(lambda x: self.movie_company_insert('production_company',[self.movieid, x]))
        
    
    def movie_person_insert(self, table, values:list):
        record_to_insert = values 
        query = '''INSERT INTO {} (movie_id, person_id) VALUES (%s,%s)'''.format(table)
        self.cursor.execute(query, record_to_insert)
        # self.connection.commit()
        
    def movie_company_insert(self, table, values:list):
        record_to_insert = values
        query = '''INSERT INTO {} (movie_id, company_id) VALUES (%s,%s)'''.format(table)
        self.cursor.execute(query, record_to_insert)
        # self.connection.commit()
    
        

        
def imdb_api(movieid):
    ia = IMDb()
    tmp = ia.get_movie(movieid)
    root = etree.fromstring(tmp.asXML())
    return root