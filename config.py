import os
SECRET_KEY = os.environ.get('SECRET_KEY')

basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True

SQLALCHEMY_TRACK_MODIFICATIONS = False

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
