

async def response_queue(db_pool, q):
    query = q.get()
    result = await responder(db_pool, query)
    print(result)
