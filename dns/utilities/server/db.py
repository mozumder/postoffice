from .codes import *

def protecc_str(name:str):
    return name.replace('"', r'\"').replace("'", r"\'")

async def db_lookup(db_pool, query):
    # FIXME: Capitalized DNS queries.
    print(f'Got query: name={query[2]}, type={RR_TYPE[RR_TYPE_LOOKUP[query[0]]]}, class={DNS_CLASS[DNS_CLASS_LOOKUP[query[1]]]}')
    results = []
    if query[1] == DNS_CLASS_INTERNET:
        if query[0] == RR_TYPE_A:
            domainname = ".".join(query[3][1:])
            name = protecc_str(".".join(query[3]))
            conn = await db_pool.acquire()
            records = await conn.fetch(f"execute get_a_record('{name}')")
            print(f'{records=}')
            await db_pool.release(conn)
            for record in records:
                results.append((RR_TYPE_A,record))
    return results

async def DBConnecter(db_pool_fut, q):
    db_pool = await db_pool_fut
    while True:
        result = await response_queue(db_pool,q)

async def DBConnectInit(conn):
    # TODO: Add prepared statements on connection
    await conn.execute('prepare get_a_record(TEXT) as select dns_a_record.fqdn, ttl, ip_address,  dns_domain.id from dns_a_record left outer join dns_domain on dns_a_record.domain_id = dns_domain.id where dns_a_record.fqdn = $1;')
    

def RunDBThread(q):
    print(f'Starting DB Thread')

    db_name = settings.DATABASES['default']['NAME']
    db_user = settings.DATABASES['default']['USER']
    db_password = settings.DATABASES['default']['PASSWORD']
    db_host = settings.DATABASES['default']['HOST']
    db_port = settings.DATABASES['default']['PORT']
    dsn = f'postgres://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

    db_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(db_loop)
    db_pool_fut = asyncpg.create_pool(dsn,init=DBConnect_Init)
    db_loop.run_until_complete(DBConnecter(db_pool_fut,q))

