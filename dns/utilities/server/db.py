import os
import sys
import logging
import inspect

from django.db.utils import ProgrammingError, OperationalError

# TODO: Optimize UNION statements into single query
from .codes import *


def protecc_str(name:str):
    return name.replace('"', r'\"').replace("'", r"\'")

query_commands = {
    RR_TYPE_A:'get_a_record',
    RR_TYPE_AAAA:'get_aaaa_record',
    RR_TYPE_CNAME:'get_cname_record',
    RR_TYPE_MX:'get_mx_record',
    RR_TYPE_NS:'get_ns_record',
    RR_TYPE_SOA:'get_soa_record',
    RR_TYPE_TXT:'get_txt_record',
    RR_TYPE_PTR:'get_ptr_record',
    RR_TYPE_CAA:'get_caa_record',
    RR_TYPE_SRV:'get_srv_record',
}

async def db_lookup(db_pool, query):
    dns_logger = logging.getLogger("dnsserver")
    # FIXME: Capitalized DNS queries.
    name = protecc_str(query[3]).lower()
    dns_logger.debug(f'Got {RR_TYPE[RR_TYPE_LOOKUP[query[0]]]} query: {name}')
    results = []
    if query[1] == DNS_CLASS_INTERNET:
        conn = await db_pool.acquire()
        try:
            records = await conn.fetch(f"execute {query_commands[query[0]]}('{name}')")
        except KeyError:
            await db_pool.release(conn)
            return -1
        await db_pool.release(conn)
        for record in records:
            results.append(record)
#    dns_logger.debug(results)
    return results

async def DBConnectInit(conn):
    dns_logger = logging.getLogger("dnsserver")
    db_logger = logging.getLogger("database")
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
            db_logger.info('No SQL prepared statements file: %s' % dir+'/'+file_name)
            pass
        except (OSError, IOError) as e:
            db_logger.error('Error reading SQL prepared statements file: %s' % file_name)
            raise e
        else:
            sql_prepare=file.read().strip()
            if sql_prepare:
                try:
                    await conn.execute(sql_prepare.format(**template_values))
                except (OperationalError, ProgrammingError) as e:
                    type, value, tb = sys.exc_info()
                    db_logger.error(f"Failed preparing statements statements with {type.__name__}!")
                    db_logger.error(f'- Specifically, {value}')
                    db_logger.error("- Please review the most recent stack entries:\n" + "".join(traceback.format_list(traceback.extract_tb(tb, limit=5))))
                    dns_logger.error(f'Caught Database error {value} while trying to exectute sql file {file_name}')
                    dns_logger.error(f'- Ignoring and continuing')

