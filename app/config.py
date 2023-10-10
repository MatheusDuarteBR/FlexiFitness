"""
All the properties will be defined
"""
DEBUG = True
USERNAME = 'pollux'
PASSWORD = 'pollux123'
SERVER = '127.0.0.1'
DB = 'flexifitness'

SQLALCHEMY_DATABASE_URI = f"postgresql://{USERNAME}:{PASSWORD}@{SERVER}/{DB}"
SQLACHEMY_TRACK_MODIFICATIONS = True

SECRET_KEY="28782878"