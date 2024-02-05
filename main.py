import os

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.sql import text


app = FastAPI()
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
if not DATABASE_PASSWORD:
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./test.db")
else:
    DATABASE_URL = f"mysql+mysqlconnector://root:{DATABASE_PASSWORD}@mysql:3306/mysql"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/get-node")
async def get_node():
    node_name = os.environ.get("NODE_NAME")
    return {"message": f"You've get response from node {node_name}"}


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Health check endpoint
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Try executing a simple query to check the database connection
        db.execute(text('SELECT 1'))
        return {"status": "success"}
    except OperationalError as e:
        # Handle database connection failure
        raise HTTPException(status_code=503, detail="Database connection failure")

