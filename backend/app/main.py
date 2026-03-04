from fastapi import FastAPI
from .database import engine
from .models import Base

app = FastAPI()

# создаём таблицы при запуске
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "TODO API is running"}