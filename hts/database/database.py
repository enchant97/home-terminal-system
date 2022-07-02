"""
Contains the SQLAlchemy database object

use:
    from database.models import Amodel
    from database.dao import Adao
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
