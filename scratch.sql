WITH name_record AS (
    SELECT
        dns_a_record.searchname as name,
        dns_a_record.searchdomain as domainname,
        dns_a_record.ttl as ttl,
        dns_cname_record.canonical_name as cname,
        dns_a_record.domain_id as domain_id,
        dns_a_record.ip_address as ip_address
    FROM
        dns_a_record
    LEFT OUTER JOIN
        dns_cname_record
    ON
        dns_a_record.host_id=dns_cname_record.host_id AND
        dns_cname_record.searchname = 'bad.mozumder.net'
    WHERE
        dns_a_record.searchname = 'bad.mozumder.net' OR
        dns_cname_record.canonical_name IS NOT NULL
)
SELECT
    {RR_TYPE_SOA} as type,
    exists(
        SELECT 1
        FROM
            dns_aaaa_record
        WHERE
            dns_aaaa_record.searchname = 'bad.mozumder.net'
    ) as nxdomain,
    dns_domain.name as domainname,
    dns_soa_record.ttl as ttl,
    dns_soa_record.nameserver as nsname,
    dns_soa_record.rname as rname,
    dns_soa_record.serial as serial,
    dns_soa_record.refresh as refresh,
    dns_soa_record.retry as retry,
    dns_soa_record.expiry as expiry,
    dns_soa_record.nxttl as nxttl,
    NULL::varchar(255) as cname,
    NULL::inet as ip_address
FROM
    dns_domain, dns_soa_record
WHERE
    '.' || 'bad.mozumder.net' LIKE '%.' || dns_domain.name AND
    dns_domain.id = dns_soa_record.domain_id AND
    NOT EXISTS (select * from name_record)
ORDER BY
    length(dns_domain.name) DESC
LIMIT 1
;

