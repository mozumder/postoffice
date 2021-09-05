PREPARE get_soa_record(VARCHAR(255)) AS
WITH soa_record AS
(
SELECT
    EXISTS(
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
    dns_domain.id as domainid,
    dns_domain.name as domainname,
    dns_soa_record.ttl as ttl,
    dns_soa_record.nameserver as nsname,
    dns_soa_record.rname as rname,
    dns_soa_record.serial as serial,
    dns_soa_record.refresh as refresh,
    dns_soa_record.retry as retry,
    dns_soa_record.expiry as expiry,
    dns_soa_record.nxttl as nxttl
FROM
    dns_domain, dns_soa_record
WHERE
    '.' || $1 LIKE '%.' || dns_domain.name AND
    dns_domain.id = dns_soa_record.domain_id
ORDER BY
    length(dns_domain.name) DESC
LIMIT 1
)
SELECT
    {RR_TYPE_SOA} as type,
    soa_record.nxdomain as nxdomain,
    soa_record.domainname as domainname,
    soa_record.ttl as ttl,
    soa_record.nsname as nsname,
    soa_record.rname as rname,
    soa_record.serial as serial,
    soa_record.refresh as refresh,
    soa_record.retry as retry,
    soa_record.expiry as expiry,
    soa_record.nxttl as nxttl
FROM
    soa_record
UNION
SELECT
    {RR_TYPE_NS} as type, --{RR_TYPE_NS}
    true as nxdomain,
    soa_record.domainname as domainname,
    dns_ns_record.ttl as ttl,
    dns_ns_record.name as nsname,
    NULL::varchar(255) as rname,
    NULL::int as serial,
    NULL::int as refresh,
    NULL::int as retry,
    NULL::int as expiry,
    NULL::int as nxttl
FROM
    dns_ns_record, soa_record
WHERE
    soa_record.domainid = dns_ns_record.domain_id
;
