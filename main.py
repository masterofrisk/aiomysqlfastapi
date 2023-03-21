from datetime import datetime
from fastapi import FastAPI, Response, Depends, Request, status, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.param_functions import Query
import uvicorn
import json
import asyncio
import aiomysql
from typing_extensions import Annotated

app = FastAPI(
    openapi_url="/mypage.html",
    title="MY-API",
    description="My API with only one file.py and free mysql interaction.",
    version="1.0.1",
    redoc_favicon_url="/logo-dark.png"
)
security = HTTPBasic()
sql1 = 'YOUR_MYSQL_HOST'
sql2 = 'YOUR_MYSQL_USER'
sql3 = 'YOUR_MYSQL_PWD'
sql4 = 'YOUR_MYSQL_SCHEMA'


def sync_dbuser(u: str, t: str):
    result = asyncio.run(dbuser(u, t))
    return result


async def dbuser(u1: str, t1: str):
    pool = await aiomysql.create_pool(
        host=sql1,
        user=sql2,
        password=sql3,
        db=sql4,
        autocommit=True
    )
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT 'ok' ok FROM tbluser where id='" + u1 + "' and token='" + t1 + "';")
            row = await cursor.fetchone()
            if row is None:
                result = "no"
            else:
                result = "ok"
    pool.close()
    return result


def get_current_username(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    if sync_dbuser(credentials.username, credentials.password) != "ok":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Authentication",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def instr(int_start=1, str_text='', str_what=''):
    return str_text.find(str_what, int_start - 1) + 1


def replaceall(str_text, str_old, str_new):
    x = str_text
    while instr(1, x, str_old) > 0:
        x = x.replace(str_old, str_new, )
    return x


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
    # tags=["Routes"],
)
async def get_webhookids(
        username: Annotated[str, Depends(get_current_username)],
):
    pool = await aiomysql.create_pool(
        host=sql1,
        user=sql2,
        password=sql3,
        db=sql4,
        autocommit=True
    )
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT id, wh_url, wh_name, status FROM tblwhid where user_id='" + username + "' order by id;")
            result = await cursor.fetchall()
    pool.close()
    await pool.wait_closed()
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There are no webhooks for this user yet')
    else:
        # result_list = [list(row) for row in result]  # Convert tuple rows to list rows
        result_list = [{'wh_id': x[0], 'wh_url': x[1], 'wh_name': x[2], 'status': x[3]} for x in result]
        response_data = {"webhooks": result_list}
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
    # tags=["Routes"],
)
async def get_webhooks(
        username: Annotated[str, Depends(get_current_username)],
        id: int = Query(0, description="The ID used to initiate a query for your webhook content.", title="ID"),
        whid: int = Query(0, description="The ID of the webhook url.", title="WH ID"),
        limit: int = Query(20,
                           description="The maximum number of webhook contents that can be retrieved per API call is 100 and cannot be exceeded.",
                           title="Limit"),
):
    pool = await aiomysql.create_pool(
        host=sql1,
        user=sql2,
        password=sql3,
        db=sql4,
        autocommit=True
    )
    if limit > 100:
        limit = 100
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT id, content, ip, api, dt, wh_id FROM tblwh where id>=" + str(id) + " and wh_id='" + str(
                    whid) + "' and user_id='" + username + "' order by id limit " + str(limit) + ";")
            result = await cursor.fetchall()
    pool.close()
    await pool.wait_closed()
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There are no webhooks for this user yet')
    else:
        # result_list = [list(row) for row in result]  # Convert tuple rows to list rows
        result_list = [{'id': x[0], 'content': x[1], 'ip': x[2], 'api': x[3], 'dt': x[4], 'wh_id': x[5]} for x in
                       result]
        response_data = {"whcontent": result_list}
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
    pool = await aiomysql.create_pool(
        host=sql1,
        user=sql2,
        password=sql3,
        db=sql4,
        autocommit=True
    )
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT id, content, ip, api, dt, wh_id FROM tblwh where id=" + str(
                    id) + " and user_id='" + username + "';")
            result = await cursor.fetchone()
    pool.close()
    await pool.wait_closed()
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='The webhook id does not exist for such user')
    else:
        response_data = {'id': result[0], 'content': result[1], 'ip': result[2], 'api': result[3], 'dt': result[4],
                         'wh_id': result[5]}
        return Response(content=json.dumps(response_data), media_type="application/json")


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
async def add_webhook(content: str, request: Request, username: Annotated[str, Depends(get_current_username)]):
    pool = await aiomysql.create_pool(
        host=sql1,
        user=sql2,
        password=sql3,
        db=sql4,
        autocommit=True
    )
    client_host = request.client.host
    now = datetime.now()
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute(
                "Insert Into tblwh(content,ip,api,dt,user_id, wh_id) Values(trim(both '''' from Quote('" + content.replace(
                    "'", "''") + "')),'" + client_host + "',true,'" + now.strftime(
                    "%Y-%m-%d %H:%M:%S") + "'," + username + ",0);")
    pool.close()
    await pool.wait_closed()
    if result is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='The webhook could not be post')
    else:
        return {"result": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", log_level="info", port=4343, reload=True, host='0.0.0.0')
