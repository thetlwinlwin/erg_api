from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from factory import oauth2
from factory.routers.auth import auth_router
from factory.routers.c_channel.orders import cchannel_orders_router
from factory.routers.customer import customer_router
from factory.routers.ds.orders import ds_orders_router
from factory.routers.roof.orders import roof_orders_router
from factory.routers.stream.stream import stream_router
from factory.schema import token_schema

app = FastAPI()

# as we got alembic, we don't need this anymore
# models.Base.metadata.create_all(bind=engine)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def greetings(manger_info: token_schema.PayloadData = Depends(oauth2.get_listener)):
    return {"greeting": "Welcome from ERG"}


app.include_router(auth_router)
app.include_router(customer_router)
app.include_router(ds_orders_router)
app.include_router(roof_orders_router)
app.include_router(cchannel_orders_router)
app.include_router(stream_router)
