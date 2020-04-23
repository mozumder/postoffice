# TODO: Optimize UNION statements into single query
from .codes import *

def protecc_str(name:str):
    return name.replace('"', r'\"').replace("'", r"\'")

async def db_lookup(db_pool, query):
    # FIXME: Capitalized DNS queries.
    print(f'Got query: name={query[2]}, type={RR_TYPE[RR_TYPE_LOOKUP[query[0]]]}, class={DNS_CLASS[DNS_CLASS_LOOKUP[query[1]]]}')
    results = []
    if query[1] == DNS_CLASS_INTERNET:
        if query[0] == RR_TYPE_A:
            name = protecc_str(".".join(query[3])).lower()
            conn = await db_pool.acquire()
            records = await conn.fetch(f"execute get_a_record('{name}')")
            await db_pool.release(conn)
            for record in records:
                results.append(record)
        elif query[0] == RR_TYPE_NS:
            name = protecc_str(".".join(query[3])).lower()
            conn = await db_pool.acquire()
            records = await conn.fetch(f"execute get_ns_record('{name}')")
            await db_pool.release(conn)
            for record in records:
                results.append(record)
        elif query[0] == RR_TYPE_SOA:
            name = protecc_str(".".join(query[3])).lower()
            conn = await db_pool.acquire()
            records = await conn.fetch(f"execute get_soa_record('{name}')")
            await db_pool.release(conn)
            for record in records:
                results.append(record)
    return results

async def DBConnecter(db_pool_fut, q):
    db_pool = await db_pool_fut
    while True:
        result = await response_queue(db_pool,q)

async def DBConnectInit(conn):
    # TODO: Add prepared statements on connection
    await conn.execute(f'''prepare get_a_record(TEXT) as
select
    {RR_TYPE_A} as type,
    dns_a_record.ttl as ttl,
    ip_address,
    dns_domain.name as domainname,
    NULL::varchar(255) as nsname,
    NULL::varchar(255) as rname,
    NULL::int as serial,
    NULL::int as refresh,
    NULL::int as retry,
    NULL::int as expiry,
    NULL::int as nxttl
from
    dns_a_record
left outer join
    dns_domain
on
    dns_domain.id = dns_a_record.domain_id
where
    dns_a_record.fqdn = $1
union
select
    {RR_TYPE_NS} as type,
    dns_ns_record.ttl as ttl,
    NULL::inet as ip_address,
    dns_domain.name as domainname,
    dns_ns_record.name as nsname,
    NULL::varchar(255) as rname,
    NULL::int as serial,
    NULL::int as refresh,
    NULL::int as retry,
    NULL::int as expiry,
    NULL::int as nxttl
from
    dns_domain
left outer join
    dns_a_record
on
    dns_domain.id = dns_a_record.domain_id
left outer join
    dns_ns_record
on
    dns_domain.id = dns_ns_record.domain_id
where
    dns_a_record.fqdn = $1
union
select
    {RR_TYPE_SOA} as type,
    dns_soa_record.ttl as ttl,
    NULL::inet as ip_address,
    dns_domain.name as domainname,
    dns_soa_record.nameserver as nsname,
    dns_soa_record.rname as rname,
    dns_soa_record.serial as serial,
    dns_soa_record.refresh as refresh,
    dns_soa_record.retry as retry,
    dns_soa_record.expiry as expiry,
    dns_soa_record.nxttl as nxttl
from
    dns_domain
left outer join
    dns_a_record
on
    dns_domain.id = dns_a_record.domain_id
left outer join
    dns_soa_record
on
    dns_domain.id = dns_soa_record.domain_id
where
    dns_a_record.fqdn <> $1 AND
    dns_domain.name <> $1
;
''')

    await conn.execute(f'''prepare get_ns_record(TEXT) as
select
    {RR_TYPE_NS} as type,
    dns_ns_record.ttl as ttl,
    NULL::inet as ip_address,
    dns_domain.name as domainname,
    dns_ns_record.name as nsname,
    NULL::varchar(255) as rname,
    NULL::int as serial,
    NULL::int as refresh,
    NULL::int as retry,
    NULL::int as expiry,
    NULL::int as nxttl
from
    dns_domain
left outer join
    dns_ns_record
on
    dns_domain.id = dns_ns_record.domain_id
where
    dns_ns_record.fqdn = $1
union
select
    {RR_TYPE_SOA} as type,
    dns_soa_record.ttl as ttl,
    NULL::inet as ip_address,
    dns_domain.name as domainname,
    dns_soa_record.nameserver as nsname,
    dns_soa_record.rname as rname,
    dns_soa_record.serial as serial,
    dns_soa_record.refresh as refresh,
    dns_soa_record.retry as retry,
    dns_soa_record.expiry as expiry,
    dns_soa_record.nxttl as nxttl
from
    dns_domain
left outer join
    dns_a_record
on
    dns_domain.id = dns_a_record.domain_id
left outer join
    dns_soa_record
on
    dns_domain.id = dns_soa_record.domain_id
where
    dns_a_record.fqdn <> $1 and
    dns_domain.name <> $1
;
''')
    await conn.execute(f'''prepare get_soa_record(TEXT) as
select
    {RR_TYPE_NS} as type,
    dns_ns_record.ttl as ttl,
    NULL::inet as ip_address,
    dns_domain.name as domainname,
    dns_ns_record.name as nsname,
    NULL::varchar(255) as rname,
    NULL::int as serial,
    NULL::int as refresh,
    NULL::int as retry,
    NULL::int as expiry,
    NULL::int as nxttl
from
    dns_domain
left outer join
    dns_ns_record
on
    dns_domain.id = dns_ns_record.domain_id
where
    dns_ns_record.fqdn = $1
union
select
    {RR_TYPE_SOA} as type,
    dns_soa_record.ttl as ttl,
    NULL::inet as ip_address,
    dns_domain.name as domainname,
    dns_soa_record.nameserver as nsname,
    dns_soa_record.rname as rname,
    dns_soa_record.serial as serial,
    dns_soa_record.refresh as refresh,
    dns_soa_record.retry as retry,
    dns_soa_record.expiry as expiry,
    dns_soa_record.nxttl as nxttl
from
    dns_domain
left outer join
    dns_a_record
on
    dns_domain.id = dns_a_record.domain_id
left outer join
    dns_soa_record
on
    dns_domain.id = dns_soa_record.domain_id
where
    dns_a_record.fqdn = $1
;
''')


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

