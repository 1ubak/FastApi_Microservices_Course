import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
from dotenv import load_dotenv

# Project is following Microservices with FastAPI course
# link: https://www.youtube.com/watch?v=Cy9fAvsXGZA
# completed to 51:00 - refund order not implemented

# start the server:
# uvicorn main:app --reload --port=8000

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']

)

redis = get_redis_connection(
    host="redis-15095.c245.us-east-1-3.ec2.cloud.redislabs.com",
    port="15095",
    password=os.getenv('REDIS_PASSWORD'),
    decode_responses=True
)


class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis


@app.get('/products')
def all_products():
    return [format(pk) for pk in Product.all_pks()]


def format(pk: str):
    product = Product.get(pk)

    return {
        'id': product.pk,
        'name': product.name,
        'price': product.price,
        'quantity': product.quantity
    }


@app.post('/products')
def create(product: Product):
    return product.save()


@app.get('/products/{pk}')
def get(pk: str):
    return Product.get(pk)


@app.delete('/products/{pk}')
def delete(pk: str) -> Product:
    return Product.delete(pk)


@app.get("/")
async def root():
    return {"message": "Hello World"}


