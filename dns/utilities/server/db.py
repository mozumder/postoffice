from .codes import *

async def db_lookup(db_pool, query):
    print(f'Got query: name={query[2]}, type={RR_TYPE[RR_TYPE_LOOKUP[query[0]]]}, class={DNS_CLASS[DNS_CLASS_LOOKUP[query[1]]]}')
    results = []
    if query[1] == DNS_CLASS_INTERNET:
        if query[0] == RR_TYPE_A:
            domainname = ".".join(query[3][1:])
            name = ".".join(query[3])
            con = await db_pool.acquire()
            # Open a transaction.
    #        domain = await con.fetchval('select id from dns_domain where name=$1 or name=$2;', domainname,name)
            records = await con.fetch('select dns_a_record.fqdn, ttl, ip_address,  dns_domain.id from dns_a_record left outer join dns_domain on dns_a_record.domain_id = dns_domain.id where dns_a_record.fqdn = $1;', name)
            print(f'{records=}')
            await db_pool.release(con)
            for record in records:
                results.append((RR_TYPE_A,record))
    return results

async def DBConnecter(db_pool_fut, q):
    db_pool = await db_pool_fut
    while True:
        result = await response_queue(db_pool,q)

async def DBConnectInit(conn):
    print('Connecting')

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

