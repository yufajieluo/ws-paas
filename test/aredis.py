import asyncio
from commRedis import ARedisHandler

async def func1(redis_conn, key):
    print('func1 begin')
    while True:
        print('func1 get result from {0}'.format(key))
        result = await redis_conn.brpop(key,timeout=1)
        print('result is {0}'.format(result))
        if result:
            print('func1 get result {0}'.format(result))
    print('func1 finish')
    return

async def func2(redis_conn, key):
    print('func2 begin')
    while True:
        print('func2 get result from {0}'.format(key))
        result = await redis_conn.brpop(key,timeout=1)
        print('result is {0}'.format(result))
        if result:
            print('func2 get result {0}'.format(result))
    print('func2 finish')
    return

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    
    aredis_handler = ARedisHandler(host = '192.168.65.2', port = 6379, pswd = None, db = 0)
    task = loop.create_task(aredis_handler.connect())
    loop.run_until_complete(task)
    
    print('====={0}'.format(task.result()))

    tasks = [
        loop.create_task(func1(aredis_handler.conn, 'test')),
        loop.create_task(func2(aredis_handler.conn, 'test1')),
    ]
    loop.run_until_complete(asyncio.wait(tasks))