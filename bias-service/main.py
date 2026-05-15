from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from urllib.parse import urlparse

app = FastAPI()
