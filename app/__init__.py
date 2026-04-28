from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config
import os

#Initialize extensions
db= SQLAlchemy()
jwt=JWTManager()
Limiter = Limiter(
    key_func = get_remote_address,
    default_limits=['200 per day', '50 per hour']
)