import asyncio
import json
from datetime import datetime
from typing_extensions import Annotated

import aiomysql
from fastapi import FastAPI, Response, Depends, Request, status, HTTPException
from fastapi.param_functions import Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import uvicorn

app = FastAPI(
    openapi_url="/mypage.html",
    title="MY-API",
    description="My API with only one file.py and free mysql interaction.",
    version="1.0.1",
    redoc_favicon_url="/logo-dark.png"
)
security = HTTPBasic()

# You can use the python-dotenv package to load environment variables 
# from a .env file. You can install it using pip install python-dotenv
# and then change the following 4 lines.
sql_host = 'YOUR_MYSQL_HOST'
sql_user = 'YOUR_MYSQL_USER'
sql_password = 'YOUR_MYSQL_PWD'
sql_schema = 'YOUR_MYSQL_SCHEMA'

async def create_db_pool():
    return await aiomysql.create_pool(
        host=sql_host,
        user=sql_user,
        password=sql_password,
        db=sql_schema,
        autocommit=True
    )

def sync_dbuser(u: str, t: str):
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(dbuser(u, t))
    return result

async def dbuser(u1: str, t1: str):
    pool = await create_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT 'ok' ok FROM tbluser where id=%s and token=%s;", (u1, t1))
            row = await cursor.fetchone()
            if row is None:
                result = "no"
            else:
                result = "ok"
    pool.close()
    return result

def get_current_username(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    try:
        auth_result = sync_dbuser(credentials.username, credentials.password)
        if auth_result != "ok":
            raise ValueError("Incorrect Authentication")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get(
    '/',
    summary="Verify your credentials by fetching your username.",
    description="Your username will be returned to you.",
    response_description="Your username will be returned to you.",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "username": "1234"
                    }
                }
            },
        },
    },
    status_code=status.HTTP_200_OK,
)
async def get_indx(username: Annotated[str, Depends(get_current_username)]):
    return {"username": username}

@app.get(
    '/webhooks',
    summary="Get a list of webhooks from the system",
    description="Retrieve your webhooks urls.",
    response_description="A List of webhooks.",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "webhooks": [
                            {
                                "wh_id": 0,
                                "wh_url": "https://w2a.fz.pe/?rid=w2e34t",
                                "wh_name": "My personal content",
                                "status": 1
                            },
                            {
                                "wh_id": 1,
                                "wh_url": "https://w2a.fz.pe/?rid=y77ip",
                                "wh_name": "My payment method webhook",
                                "status": 1
                            }
                        ]
                    }
                }
            },
        },
    },
    status_code=status.HTTP_200_OK,
)
async def get_webhookids(username: str = Depends(get_current_username)):
    pool = await create_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            sql_query = """
            SELECT id, wh_url, wh_name, status
            FROM tblwhid
            WHERE user_id=%s
            ORDER BY id
            """
            await cursor.execute(sql_query, (username,))
            result = await cursor.fetchall()    
    pool.close()
    await pool.wait_closed()    
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There are no webhooks for this user yet')
    else:
        response_data = {"webhooks": result}
        return Response(content=json.dumps(response_data), media_type="application/json")

@app.get(
    '/whcontent',
    summary="Get a list of contents from your webhooks.",
    description="Retrieve up to 100 contents from the system, starting with a specified ID.\n\
                 The default ID is 0 and the default number of webhooks to retrieve is 20.",
    response_description="A List of IDs contents.",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "whcontent": [
                            {
                                "id": 1,
                                "content": "My Web Hook Content 1",
                                "ip": "127.0.0.1",
                                "api": 1,
                                "dt": "2022-01-09 05:31:38",
                                "wh_id": 7
                            },
                            {
                                "id": 2,
                                "content": "My Web Hook Content 2",
                                "ip": "127.0.0.1",
                                "api": 0,
                                "dt": "2022-01-09 05:52:02",
                                "wh_id": 0
                            }
                        ]
                    }
                }
            },
        },
    },
    status_code=status.HTTP_200_OK,
)
async def get_webhooks(
        username: Annotated[str, Depends(get_current_username)],
        id: int = Query(0, description="The ID used to initiate a query for your webhook content.", title="ID"),
        whid: int = Query(0, description="The ID of the webhook url.", title="WH ID"),
        limit: int = Query(20,
                           description="The maximum number of webhook contents that can be retrieved per API call is 100 and cannot be exceeded.",
                           title="Limit"),
):
    pool = await create_db_pool()
    if limit > 100: limit = 100    
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            sql_query = """
            SELECT id, content, ip, api, dt, wh_id
            FROM tblwh
            WHERE id>=%s AND wh_id=%s AND user_id=%s
            ORDER BY id
            LIMIT %s
            """
            await cursor.execute(sql_query, (id, whid, username, limit))
            result = await cursor.fetchall()    
    pool.close()
    await pool.wait_closed()    
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There are no webhooks for this user yet')
    else:
        response_data = {"whcontent": result}
        return Response(content=json.dumps(response_data), media_type="application/json")

@app.get(
    '/whcontent/{id}',
    summary="Get a specific webhook content",
    description="Retrieve one specific webhook content using its ID.",
    response_description="One specific ID content.",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "content": "My Web Hook Content 1",
                        "ip": "127.0.0.1",
                        "api": 1,
                        "dt": "2022-01-09 05:31:38",
                        "wh_id": 1
                    }
                }
            },
        },
    },
    status_code=status.HTTP_200_OK,
)
async def get_webhook(
        username: Annotated[str, Depends(get_current_username)],
        id: int
):
    pool = await create_db_pool()    
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            sql_query = """
            SELECT id, content, ip, api, dt, wh_id
            FROM tblwh
            WHERE id=%s AND user_id=%s
            """
            await cursor.execute(sql_query, (id, username))
            result = await cursor.fetchone()    
    pool.close()
    await pool.wait_closed()    
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='The webhook id does not exist for such user')
    else:
        return Response(content=json.dumps(result), media_type="application/json")

@app.post(
    '/whcontent',
    summary="Add your own content as a webhook payload. Always on wh_id = 0.",
    description="If you input your own content as a webhook payload, the 'api' and 'wh_id' variables will be set to 0, indicating no actual webhook was received.\n\
                Otherwise, if a real webhook content was received, the 'wh_id' variable will have a value greater than or equal to 1 and the 'api' variable will \
                be set to 1.\n\
                These variables help distinguish between your own input content and actual webhook content. Always on wh_id = 0.",
    response_description="If the input is successful, a simple message containing 'ok' will be returned.",
    responses={
        201: {
            "content": {
                "application/json": {
                    "example": {
                        "result": "ok"
                    }
                }
            },
        },
    },
    status_code=status.HTTP_201_CREATED
)
async def add_webhook(
    content: str, 
    request: Request, 
    username: Annotated[str, Depends(get_current_username)]
):
    pool = await create_db_pool()
    client_host = request.client.host
    now = datetime.now()    
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            sql_query = """
            INSERT INTO tblwh(content, ip, api, dt, user_id, wh_id)
            VALUES (%s, %s, TRUE, %s, %s, 0)
            """
            result = await cursor.execute(
                sql_query,
                (
                    content,
                    client_host,
                    now.strftime("%Y-%m-%d %H:%M:%S"),
                    username,
                ),
            )            
    pool.close()
    await pool.wait_closed()    
    if result is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='The webhook could not be post')
    else:
        return {"result": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, log_level="info", port=4343, reload=True, host='0.0.0.0')
