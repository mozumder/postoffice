PREPARE get_a_record(VARCHAR(255)) AS
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
        dns_cname_record.searchname = $1
    WHERE
        dns_a_record.searchname = $1 OR
        dns_cname_record.canonical_name IS NOT NULL
)
SELECT
    {RR_TYPE_A} as type, --{RR_TYPE_A}
    true as nxdomain,
    name_record.domainname as domainname,
    name_record.ttl as ttl,
    NULL::varchar(255) as nsname,
    NULL::varchar(255) as rname,
    NULL::int as serial,
    NULL::int as refresh,
    NULL::int as retry,
    NULL::int as expiry,
    NULL::int as nxttl,
    NULL::varchar(255) as name,
    name_record.ip_address as ip_address
FROM
    name_record
WHERE
    name_record.name is NOT NULL
    AND name_record.cname is NULL
UNION
SELECT
    {RR_TYPE_A} as type, --{RR_TYPE_A}
    true as nxdomain,
    name_record.domainname as domainname,
    name_record.ttl as ttl,
    NULL::varchar(255) as nsname,
    NULL::varchar(255) as rname,
    NULL::int as serial,
    NULL::int as refresh,
    NULL::int as retry,
    NULL::int as expiry,
    NULL::int as nxttl,
    name_record.cname as name,
    name_record.ip_address as ip_address
FROM
    name_record
WHERE
    name_record.cname is NOT NULL
UNION
SELECT
    {RR_TYPE_CNAME} as type, --{RR_TYPE_CNAME}
    true as nxdomain,
    name_record.domainname as domainname,
    name_record.ttl as ttl,
    NULL::varchar(255) as nsname,
    NULL::varchar(255) as rname,
    NULL::int as serial,
    NULL::int as refresh,
    NULL::int as retry,
    NULL::int as expiry,
    NULL::int as nxttl,
    name_record.cname as name,
    NULL::inet as ip_address
FROM
    name_record
WHERE
    name_record.cname is NOT NULL
UNION
SELECT
    {RR_TYPE_NS} as type, --{RR_TYPE_NS}
    true as nxdomain,
    name_record.domainname as domainname,
    dns_ns_record.ttl as ttl,
    dns_ns_record.name as nsname,
    NULL::varchar(255) as rname,
    NULL::int as serial,
    NULL::int as refresh,
    NULL::int as retry,
    NULL::int as expiry,
    NULL::int as nxttl,
    NULL::varchar(255) as cname,
    NULL::inet as ip_address
FROM
    dns_ns_record
LEFT OUTER JOIN
    name_record
ON
    name_record.domain_id = dns_ns_record.domain_id
WHERE
    name_record.cname is NOT NULL
    OR name_record.name is NOT NULL
UNION
(SELECT
    {RR_TYPE_SOA} as type,
    EXISTS(
        SELECT 1
            FROM
                dns_aaaa_record,
                dns_cname_record
            WHERE
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
    NULL::varchar(255) as cname,
    NULL::inet as ip_address
FROM
    dns_domain, dns_soa_record
WHERE
    '.' || $1 LIKE '%.' || dns_domain.name AND
    dns_domain.id = dns_soa_record.domain_id AND
    NOT EXISTS (select * from name_record)
ORDER BY
    length(dns_domain.name) DESC
LIMIT 1)
;
