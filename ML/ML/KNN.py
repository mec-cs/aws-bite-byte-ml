import json
import random
import redis
import numpy as np
import mysql.connector
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

class KNN:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="readreplica.c1kwu2kwmcn6.eu-central-1.rds.amazonaws.com",
            user="admin",
            password="fjwnoawKQ30_n",
        )

        self.cursor = self.connection.cursor()
        self.r = redis.Redis(host='localhost', port=6379, db=0)
        
    def read(self, userID):
        cached_data = self.r.get(0)
        if cached_data:
            temp = tuple(json.loads(cached_data))
            print(len(temp))
            self.df = np.array(temp)
        else:
            query = "SELECT cuisine, course, diet, prep_time, ingredients FROM recipe_database.recipe"
            self.cursor.execute(query)
            temp = self.cursor.fetchall()
            self.df = np.array(temp)
            self.r.set(0, json.dumps(temp), ex=300)

        query = "SELECT id FROM recipe_database.recipe WHERE owner_id = %s"
        self.cursor.execute(query, (userID,))
        self.owned_recipes = self.cursor.fetchall()
        self.owned_recipes = [i - 1 for i in self.owned_recipes for i in i] 

        query = "SELECT recipe_id FROM interaction_database.favorites WHERE user_id = %s"
        self.cursor.execute(query, (userID,))
        self.favorite_recipes = self.cursor.fetchall()
        self.favorite_recipes = [i - 1 for i in self.favorite_recipes for i in i]

        query = "SELECT recipe_id FROM interaction_database.likes WHERE user_id = %s"
        self.cursor.execute(query, (userID,))
        self.liked_recipes = self.cursor.fetchall()
        self.liked_recipes = [i - 1 for i in self.liked_recipes for i in i]

        query = "SELECT recipe_id FROM interaction_database.click_history WHERE user_id = %s"
        self.cursor.execute(query, (userID,))
        self.clicked_recipes = self.cursor.fetchall()
        self.clicked_recipes = [i - 1 for i in self.clicked_recipes for i in i]

        #self.cursor.close()
        #self.connection.close()

    def parse(self):
        self.cuisine = self.df[:, 0]
        self.course = self.df[:, 1]
        self.diet = self.df[:, 2]
        self.prep_time = [float(i) for i in self.df[:, 3]]
        self.ingredients = self.df[:, 4]

    def encode(self):
        OHE = OneHotEncoder(sparse_output=False)
        self.cuisine_matrix = OHE.fit_transform(np.array(self.cuisine).reshape(-1, 1))
        self.course_matrix = OHE.fit_transform(np.array(self.course).reshape(-1, 1))
        self.diet_matrix = OHE.fit_transform(np.array(self.diet).reshape(-1, 1))
        self.prep_time_matrix = MinMaxScaler().fit_transform(np.array(self.prep_time).reshape(-1, 1))
        self.ingredients_matrix = TfidfVectorizer().fit_transform(self.ingredients).toarray()

    def fit(self, n):
        features = np.hstack((self.cuisine_matrix, self.course_matrix, self.diet_matrix, self.prep_time_matrix, self.ingredients_matrix))
        user_profile1 = np.mean(features[self.favorite_recipes], axis=0)
        user_profile2 = np.mean(features[self.liked_recipes], axis=0)
        user_profile3 = np.mean(features[self.clicked_recipes], axis=0)
        user_profile = np.vstack((user_profile1, user_profile2, user_profile3))
        nearest = NearestNeighbors(n_neighbors=n, algorithm='auto')
        features[self.favorite_recipes + self.liked_recipes + self.clicked_recipes + self.owned_recipes] = 100
        nearest.fit(features)
        distances, indices = nearest.kneighbors(user_profile)

        self.table = np.vstack((distances.flatten(), indices.flatten()))
        unique, unique_indices = np.unique(self.table[1], return_index=True)
        for i in unique_indices:
            if(i < n):
                self.table[0][i] *= np.abs(np.mean(self.table[0]) - 1*np.std(self.table[0]))
            elif(i >= n and i < n*2):
                self.table[0][i] *= np.abs(np.mean(self.table[0]) - 2*np.std(self.table[0]))
            elif(i >= n*2 and i < n*3):
                self.table[0][i] *= np.abs(np.mean(self.table[0]) - 3*np.std(self.table[0]))
        self.table = self.table[:,unique_indices]
        self.table = self.table[:,np.argsort(self.table[0])]
        self.recommend = list(map(int, self.table[1][0:n] + 1))

    def main(self, userID, n):
        try:
            self.read(userID)
            self.parse()
            self.encode()
            self.fit(n)
            return self.recommend
        except:
            temp = self.favorite_recipes + self.liked_recipes + self.clicked_recipes + self.owned_recipes
            if(temp != []):
                available = [i for i in range(1, len(self.df) + 1) if i not in temp]
                return random.sample(available, n)
            else:
                return random.sample(range(1, len(self.df) + 1), n)