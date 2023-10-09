import pymongo
from dotenv import load_dotenv
import os

load_dotenv()


class MongoDB:
      def __init__(self,db_name, collection_name):
         self.client = pymongo.MongoClient(os.getenv('URL_MONGODB'))
         self.db = self.client[db_name]
         self.collection = self.db[collection_name]
   
      def insert(self, data):
         self.collection.insert_one(data)
   
      def find(self, query):
         return self.collection.find(query)
   
      def find_one(self, query):
         return self.collection.find_one(query)
   
      def update(self, query, data):
         self.collection.update_one(query, data, upsert=True)
      
      def update_many(self, query, data):
         self.collection.update_many(query, data, upsert=True)
   
      def delete(self, query):
         self.collection.delete_one(query)
   
      def delete_many(self, query):
         self.collection.delete_many(query)
   
      def upsert(self, query, data):
         self.collection.update_one(query, data, upsert=True)
         
      def upsert_many(self, query, data):
         self.collection.update_many(query, data, upsert=True)
         
      def drop(self):
         self.collection.drop()
   
      def close(self):
         self.client.close()
         
         
         