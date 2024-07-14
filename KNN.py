import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

class KNN:
    def __init__(self, userID, liked_recipes, n):
        self.file_path = "cuisines_final.csv"
        self.userID = userID
        self.liked_recipes = liked_recipes
        self.n = n
        
    def read(self):
        self.df = pd.read_csv(self.file_path)

    def parse(self):
        self.cuisine = [i for i in self.df['cuisine']]
        self.course = [i for i in self.df['course']]
        self.diet = [i for i in self.df['diet']]
        self.prep_time = [int("".join(filter(str.isdigit, i))) for i in self.df['prep_time']]
        self.ingredients = [i for i in self.df['ingredients']]

    def encode(self):
        self.cuisine_matrix = OneHotEncoder(sparse_output=False).fit_transform(np.array(self.cuisine).reshape(-1, 1))
        self.course_matrix = OneHotEncoder(sparse_output=False).fit_transform(np.array(self.course).reshape(-1, 1))
        self.diet_matrix = OneHotEncoder(sparse_output=False).fit_transform(np.array(self.diet).reshape(-1, 1))
        self.prep_time_matrix = MinMaxScaler().fit_transform(np.array(self.prep_time).reshape(-1, 1))
        self.ingredients_matrix = TfidfVectorizer().fit_transform(self.ingredients).toarray()

    def fit(self):
        self.features = np.hstack((self.cuisine_matrix, self.course_matrix, self.diet_matrix, self.prep_time_matrix, self.ingredients_matrix))
        self.user_profile = np.mean(self.features[self.liked_recipes], axis=0)
        self.nearest = NearestNeighbors(n_neighbors=self.n+len(self.liked_recipes), algorithm='auto')
        self.nearest.fit(self.features)
        self.distances, self.indices = self.nearest.kneighbors([self.user_profile])
        self.recommend = np.setdiff1d(self.indices.flatten(), self.liked_recipes)

    def print(self):
        for i in self.liked_recipes:
            print("Name: " + self.df.iloc[i, 0], end="\n\n")
            #print("Description: " + self.df.iloc[i, 1], end="\n\n")
            print("Cuisine: " + self.df.iloc[i, 2], end="\n\n")
            print("Course: " + self.df.iloc[i, 3], end="\n\n")
            print("Diet: " + self.df.iloc[i, 4], end="\n\n")
            print("Prep_time: " + self.df.iloc[i, 5], end="\n\n")
            print("Ingredients: " + self.df.iloc[i, 6], end="\n\n")
            #print("Instructions: " + self.df.iloc[i, 7] end="\n\n")

        for i in self.recommend:
            print("Name: " + self.df.iloc[i, 0], end="\n\n")
            #print("Description: " + self.df.iloc[i, 1], end="\n\n")
            print("Cuisine: " + self.df.iloc[i, 2], end="\n\n")
            print("Course: " + self.df.iloc[i, 3], end="\n\n")
            print("Diet: " + self.df.iloc[i, 4], end="\n\n")
            print("Prep_time: " + self.df.iloc[i, 5], end="\n\n")
            print("Ingredients: " + self.df.iloc[i, 6], end="\n\n")
            #print("Instructions: " + self.df.iloc[i, 7], end="\n\n")

    def main(self):
        self.read()
        self.parse()
        self.encode()
        self.fit()
        self.print()
