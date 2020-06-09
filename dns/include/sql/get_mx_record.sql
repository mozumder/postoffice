PREPARE get_mx_record(VARCHAR(255)) AS
WITH mx_record AS (
    SELECT
        dns_mx_record.hostname as hostname,
        dns_mx_record.preference as preference,
        dns_mx_record.searchdomain as domainname,
        dns_mx_record.ttl as ttl,
        dns_mx_record.domain_id as domain_id
    FROM
        dns_mx_record
    WHERE
        dns_mx_record.searchname = $1
)
SELECT
    {RR_TYPE_MX} as type,
    true as nxdomain,
    mx_record.domainname as domainname,
    mx_record.ttl as ttl,
    NULL::varchar(255) as nsname,
    NULL::varchar(255) as rname,
    NULL::int as serial,
    NULL::int as refresh,
    NULL::int as retry,
    NULL::int as expiry,
    NULL::int as nxttl,
    mx_record.hostname as hostname,
    NULL::inet as ip_address,
    mx_record.preference as preference
FROM
    mx_record
WHERE
    mx_record.hostname is NOT NULL
UNION
SELECT
    {RR_TYPE_NS} as type, --{RR_TYPE_NS}
    true as nxdomain,
    mx_record.domainname as domainname,
    dns_ns_record.ttl as ttl,
    dns_ns_record.name as nsname,
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
    dns_ns_record
LEFT OUTER JOIN
    mx_record
ON
    mx_record.domain_id = dns_ns_record.domain_id
WHERE
    mx_record.hostname is NOT NULL
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
    NOT EXISTS (select * from mx_record)
ORDER BY
    length(dns_domain.name) DESC
LIMIT 1)
;
