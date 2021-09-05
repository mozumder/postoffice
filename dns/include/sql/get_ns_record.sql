PREPARE get_ns_record(VARCHAR(255)) AS
WITH ns_record AS
(
SELECT
    dns_ns_record.ttl as ttl,
    dns_ns_record.name as nsname
FROM
    dns_ns_record
WHERE
    dns_ns_record.searchdomain = $1
)
SELECT
    {RR_TYPE_NS} as type, --{RR_TYPE_NS}
    true as nxdomain,
    $1 as domainname,
    ns_record.ttl as ttl,
    ns_record.nsname as nsname,
    NULL::varchar(255) as rname,
    NULL::int as serial,
    NULL::int as refresh,
    NULL::int as retry,
    NULL::int as expiry,
    NULL::int as nxttl,
    NULL::varchar(255) as hostname,
    NULL::inet as ip_address,
    NULL::int as preference
FROM
    ns_record
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
    NULL::varchar(255) as hostname,
    NULL::inet as ip_address,
    NULL::int as preference
FROM
    dns_domain, dns_soa_record
WHERE
    '.' || $1 LIKE '%.' || dns_domain.name AND
    dns_domain.id = dns_soa_record.domain_id AND
    NOT EXISTS (select * from ns_record)
ORDER BY
    length(dns_domain.name) DESC
LIMIT 1)
;
