import os
import sys
import logging
import inspect

from django.db.utils import ProgrammingError, OperationalError

# TODO: Optimize UNION statements into single query
from .codes import *

dblogger = logging.getLogger("database")
logger = logging.getLogger(__name__)

def protecc_str(name:str):
    return name.replace('"', r'\"').replace("'", r"\'")

async def db_lookup(db_pool, query):
    # FIXME: Capitalized DNS queries.
    qstring = ".".join(query[3])
    print(f'Got {RR_TYPE[RR_TYPE_LOOKUP[query[0]]]} query: {qstring}')
    results = []
    if query[1] == DNS_CLASS_INTERNET:
        if query[0] == RR_TYPE_A:
            name = protecc_str(".".join(query[3])).lower()
            conn = await db_pool.acquire()
            records = await conn.fetch(f"execute get_a_record('{name}')")
            await db_pool.release(conn)
            for record in records:
                results.append(record)
        elif query[0] == RR_TYPE_AAAA:
            name = protecc_str(".".join(query[3])).lower()
            conn = await db_pool.acquire()
            records = await conn.fetch(f"execute get_aaaa_record('{name}')")
            await db_pool.release(conn)
            for record in records:
                results.append(record)
        elif query[0] == RR_TYPE_CNAME:
            name = protecc_str(".".join(query[3])).lower()
            conn = await db_pool.acquire()
            records = await conn.fetch(f"execute get_cname_record('{name}')")
            await db_pool.release(conn)
            for record in records:
                results.append(record)
        elif query[0] == RR_TYPE_MX:
            name = protecc_str(".".join(query[3])).lower()
            conn = await db_pool.acquire()
            records = await conn.fetch(f"execute get_mx_record('{name}')")
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
        elif query[0] == RR_TYPE_TXT:
            name = protecc_str(".".join(query[3])).lower()
            conn = await db_pool.acquire()
            records = await conn.fetch(f"execute get_txt_record('{name}')")
            await db_pool.release(conn)
            for record in records:
                results.append(record)
        elif query[0] == RR_TYPE_PTR:
            name = protecc_str(".".join(query[3])).lower()
            conn = await db_pool.acquire()
            records = await conn.fetch(f"execute get_ptr_record('{name}')")
            await db_pool.release(conn)
            for record in records:
                results.append(record)
    print(results)
    return results

async def DBConnecter(db_pool_fut, q):
    db_pool = await db_pool_fut
    while True:
        result = await response_queue(db_pool,q)

async def DBConnectInit(conn):
    # TODO: Add prepared statements on connection
    
    sql_files = [
        'get_a_record.sql',
        'get_aaaa_record.sql',
        'get_caa_record.sql',
        'get_cname_record.sql',
        'get_mx_record.sql',
        'get_ns_record.sql',
        'get_ptr_record.sql',
        'get_soa_record.sql',
        'get_srv_record.sql',
        'get_txt_record.sql',
    ]
    template_values = {
        'RR_TYPE_A':RR_TYPE_A,
        'RR_TYPE_AAAA':RR_TYPE_AAAA,
        'RR_TYPE_NS':RR_TYPE_NS,
        'RR_TYPE_NS':RR_TYPE_NS,
        'RR_TYPE_SOA':RR_TYPE_SOA,
        'RR_TYPE_CNAME':RR_TYPE_CNAME,
        'RR_TYPE_MX':RR_TYPE_MX,
        'RR_TYPE_TXT':RR_TYPE_TXT,
        'RR_TYPE_PTR':RR_TYPE_PTR,
        'RR_TYPE_CAA':RR_TYPE_CAA,
        'RR_TYPE_SPF':RR_TYPE_SPF,
        'RR_TYPE_DNAME':RR_TYPE_DNAME,
        'RR_TYPE_SRV':RR_TYPE_SRV,
    }
    dir = os.path.dirname('dns/include/sql/')
    for file_name in sql_files:
        try:
            file = open(dir+'/'+file_name, 'r')
        except FileNotFoundError:
            logger.info('No SQL prepared statements file: %s' % dir+'/'+file_name)
            pass
        except (OSError, IOError) as e:
            logger.error('Error reading SQL prepared statements file: %s' % file_name)
            raise e
        else:
            sql_prepare=file.read().strip()
            if sql_prepare:
                try:
                    await conn.execute(sql_prepare.format(**template_values))
                except (OperationalError, ProgrammingError) as e:
                    type, value, tb = sys.exc_info()
                    dblogger.error(f"Failed preparing statements statements with {type.__name__}!")
                    dblogger.error(f'- Specifically, {value}')
                    dblogger.error("- Please review the most recent stack entries:\n" + "".join(traceback.format_list(traceback.extract_tb(tb, limit=5))))
                    logger.error(f'Caught Database error {value} while trying to exectute sql file {file_name}')
                    logger.error(f'- Ignoring and continuing')


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

