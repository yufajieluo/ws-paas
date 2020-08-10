import os
import sys
import time
import asyncio
#from commRedis import RedisHandler


#redis_handler = RedisHandler(host = '192.168.65.2', port = 6379, pswd = '', db = 0)
#redis_handler.connect()

async def rpop(key):
    #return redis_handler.conn.brpop(key)
    time.sleep(5)
    return

async def func1(key, status):
    print('func1 begin')
    while True:
        #result = redis_handler.conn.rpop(key)
        print('status is {0}'.format(status))
        result = 'func111111'
        status['agent']['expect'] = 'pending'
        print('get result is {0}'.format(result))
        #if result:
        #    print('func1 get result {0}'.format(result))
        #else:
        await asyncio.sleep(2)
    print('func1 finish')
    return

async def func2(key, status):
    print('func2 begin')
    while True:
        #result = redis_handler.conn.rpop(key)
        print('status is {0}'.format(status))
        result = 'func22222222'
        status['application']['expect'] = 'pending'
        print('get result is {0}'.format(result))
        #if result:
        #    print('func2 get result {0}'.format(result))
        #else:
        await asyncio.sleep(2)
    print('func2 finish')
    return

def main():
    status = {'agent': {'intime': 'normal', 'expect': 'normal'}, 'application': {'intime': 'normal', 'expect': 'normal'}, 'health': {'intime': 'normal', 'expect': 'normal'}}
    tasks = [loop.create_task(func1('test', status)), loop.create_task(func2('test1', status))]
    loop.run_until_complete(asyncio.wait(tasks))

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    main()