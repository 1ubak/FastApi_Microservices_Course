import os
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from redis_om import get_redis_connection, HashModel
from dotenv import load_dotenv
from starlette.requests import Request
import requests

load_dotenv()

app = FastAPI()

# start the server:
# uvicorn main:app --reload --port=8001

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


class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str # pending, completed, refunded

    class Meta:
        database = redis


@app.get("/orders/{pk}")
def get(pk: str) -> Order:
    return Order.get(pk)


@app.post("/orders")
async def create(request: Request, background_tasks: BackgroundTasks): #id, Quantity
    body = await request.json()

    req = requests.get('http://localhost:8000/products/%s' % body['id'])

    product = req.json()

    order = Order(
        product_id=body['id'],
        price=product['price'],
        fee=0.2 * product['price'],
        total = 1.2 * product['price'],
        quantity=body['quantity'],
        status='pending'
    )

    order.save()

    background_tasks.add_task(order_completed, order)

    return order


def order_completed(order: Order):
    time.sleep(5)
    order.status = 'completed'
    order.save()
    redis.xadd('order_completed', order.dict(), '*')
