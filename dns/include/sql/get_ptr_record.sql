PREPARE get_ptr_record(VARCHAR(255)) AS
WITH ptr_record AS (
    SELECT
        dns_ptr_record.searchdomain as domainname,
        dns_ptr_record.ttl as ttl,
        dns_ptr_record.hostname as hostname,
        dns_ptr_record.domain_id as domain_id
    FROM
        dns_ptr_record
    WHERE
        dns_ptr_record.searchname = $1
)
SELECT
    {RR_TYPE_PTR} as type,
    true as nxdomain,
    ptr_record.domainname as domainname,
    ptr_record.ttl as ttl,
    NULL::varchar(255) as nsname,
    NULL::varchar(255) as rname,
    NULL::int as serial,
    NULL::int as refresh,
    NULL::int as retry,
    NULL::int as expiry,
    NULL::int as nxttl,
    ptr_record.hostname as hostname
FROM
    ptr_record
UNION
SELECT
    {RR_TYPE_NS} as type, --{RR_TYPE_NS}
    true as nxdomain,
    ptr_record.domainname as domainname,
    dns_ns_record.ttl as ttl,
    dns_ns_record.name as nsname,
    NULL::varchar(255) as rname,
    NULL::int as serial,
    NULL::int as refresh,
    NULL::int as retry,
    NULL::int as expiry,
    NULL::int as nxttl,
    NULL::varchar(255) as hostname
FROM
    dns_ns_record
LEFT OUTER JOIN
    ptr_record
ON
    ptr_record.domain_id = dns_ns_record.domain_id
WHERE
    ptr_record.hostname is NOT NULL
UNION
(SELECT
    {RR_TYPE_SOA} as type,
    exists(
        SELECT 1
        FROM
            dns_a_record,
            dns_aaaa_record,
            dns_cname_record
        WHERE
            dns_a_record.searchname = $1 OR
            dns_aaaa_record.searchname = $1 OR
            dns_cname_record.searchname = $1
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
    NULL::varchar(255) as hostname
FROM
    dns_domain, dns_soa_record
WHERE
    '.' || $1 LIKE '%.' || dns_domain.name AND
    dns_domain.id = dns_soa_record.domain_id AND
    NOT EXISTS (select * from ptr_record)
ORDER BY
    length(dns_domain.name) DESC
LIMIT 1)
;
