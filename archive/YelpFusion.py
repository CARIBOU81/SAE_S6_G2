import os
from yelpapi import YelpAPI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YELP_API_KEY")

yelp_api = YelpAPI(API_KEY)