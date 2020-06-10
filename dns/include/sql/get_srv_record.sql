PREPARE get_srv_record(VARCHAR(255)) AS
WITH srv_record AS (
    SELECT
        dns_srv_record.target as target,
        dns_srv_record.host_id as host_id,
        dns_srv_record.priority as priority,
        dns_srv_record.weight as weight,
        dns_srv_record.port as port,
        dns_srv_record.ttl as ttl,
        dns_srv_record.searchdomain as domainname,
        dns_srv_record.domain_id as domain_id,
        dns_a_record.ip_address as ip_address,
        dns_aaaa_record.ip_address as ip_v6_address
    FROM
        dns_srv_record
    LEFT OUTER JOIN
        dns_a_record
    ON
        dns_a_record.host_id = dns_srv_record.host_id
    LEFT OUTER JOIN
        dns_aaaa_record
    ON
        dns_aaaa_record.host_id = dns_srv_record.host_id
    WHERE
        dns_srv_record.searchname = $1
)
SELECT
    {RR_TYPE_SRV} as type,
    true as nxdomain,
    srv_record.domainname as domainname,
    srv_record.ttl as ttl,
    NULL::varchar(255) as nsname,
    NULL::varchar(255) as rname,
    NULL::int as serial,
    NULL::int as refresh,
    NULL::int as retry,
    NULL::int as expiry,
    NULL::int as nxttl,
    srv_record.target as target,
    NULL::inet as ip_address,
    srv_record.priority as priority,
    srv_record.weight as weight,
    srv_record.port as port
FROM
    srv_record
UNION
SELECT
    {RR_TYPE_NS} as type, --{RR_TYPE_NS}
    true as nxdomain,
    srv_record.domainname as domainname,
    dns_ns_record.ttl as ttl,
    dns_ns_record.name as nsname,
    NULL::varchar(255) as rname,
    NULL::int as serial,
    NULL::int as refresh,
    NULL::int as retry,
    NULL::int as expiry,
    NULL::int as nxttl,
    NULL::varchar(255) as target,
    NULL::inet as ip_address,
    NULL::int as priority,
    NULL::int as weight,
    NULL::int as port
FROM
    dns_ns_record
LEFT OUTER JOIN
    srv_record
ON
    srv_record.domain_id = dns_ns_record.domain_id
WHERE
    srv_record.target is NOT NULL
UNION
SELECT
    {RR_TYPE_A} as type, --{RR_TYPE_A}
    true as nxdomain,
    srv_record.domainname as domainname,
    srv_record.ttl as ttl,
    NULL::varchar(255) as nsname,
    NULL::varchar(255) as rname,
    NULL::int as serial,
    NULL::int as refresh,
    NULL::int as retry,
    NULL::int as expiry,
    NULL::int as nxttl,
    srv_record.target as target,
    srv_record.ip_address as ip_address,
    NULL::int as priority,
    NULL::int as weight,
    NULL::int as port
FROM
    srv_record
WHERE
    srv_record.ip_address IS NOT NULL
UNION
SELECT
    {RR_TYPE_AAAA} as type, --{RR_TYPE_A}
    true as nxdomain,
    srv_record.domainname as domainname,
    srv_record.ttl as ttl,
    NULL::varchar(255) as nsname,
    NULL::varchar(255) as rname,
    NULL::int as serial,
    NULL::int as refresh,
    NULL::int as retry,
    NULL::int as expiry,
    NULL::int as nxttl,
    srv_record.target as target,
    srv_record.ip_v6_address as ip_v6_address,
    NULL::int as priority,
    NULL::int as weight,
    NULL::int as port
FROM
    srv_record
WHERE
    srv_record.ip_v6_address IS NOT NULL
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
    NULL::varchar(255) as target,
    NULL::inet as ip_address,
    NULL::int as priority,
    NULL::int as weight,
    NULL::int as port
FROM
    dns_domain, dns_soa_record
WHERE
    '.' || $1 LIKE '%.' || dns_domain.name AND
    dns_domain.id = dns_soa_record.domain_id AND
    NOT EXISTS (select * from srv_record)
ORDER BY
    length(dns_domain.name) DESC
LIMIT 1)
;
