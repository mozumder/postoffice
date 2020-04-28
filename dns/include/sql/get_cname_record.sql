DROP FUNCTION IF EXISTS get_cname_record(character varying);
CREATE OR REPLACE FUNCTION get_cname_record(
    searchname varchar(255)
    )
RETURNS TABLE (
    type INT,
    nonexstent BOOLEAN,
    domainname VARCHAR(255),
    ttl INT,
    nsname VARCHAR(255),
    rname VARCHAR(255),
    serial INT,
    refresh INT,
    retry INT,
    expiry INT,
    nxttl INT,
    out_canonical_name VARCHAR(255)
)
AS
$BODY$
DECLARE
    result RECORD;
BEGIN

SELECT
    dns_cname_record.ttl as ttl,
    dns_cname_record.canonical_name as canonical_name,
    dns_domain.name as domainname,
    dns_domain.id as founddomain_id
INTO
    result
FROM
    dns_cname_record,
    dns_domain
WHERE
    dns_domain.id = dns_cname_record.domain_id AND
    dns_cname_record.fqdn = searchname
;
IF FOUND THEN
    RETURN QUERY
    SELECT
        {RR_TYPE_CNAME} as type,
        NULL::bool as nonexistent,
        result.domainname as domainname,
        result.ttl as ttl,
        NULL::varchar(255) as nsname,
        NULL::varchar(255) as rname,
        NULL::int as serial,
        NULL::int as refresh,
        NULL::int as retry,
        NULL::int as expiry,
        NULL::int as nxttl,
        result.canonical_name as canonical_name
    FROM
        dns_cname_record,
        dns_domain
    WHERE
        dns_domain.id = result.founddomain_id AND
        dns_cname_record.fqdn = searchname
    UNION
    SELECT
        {RR_TYPE_NS} as type,
        NULL::bool as nonexistent,
        dns_domain.name as domainname,
        dns_ns_record.ttl as ttl,
        dns_ns_record.name as nsname,
        NULL::varchar(255) as rname,
        NULL::int as serial,
        NULL::int as refresh,
        NULL::int as retry,
        NULL::int as expiry,
        NULL::int as nxttl,
        NULL::varchar(255) as canonical_name
    FROM
        dns_domain, dns_cname_record, dns_ns_record
    WHERE
        dns_cname_record.fqdn = searchname AND
        dns_domain.id = dns_cname_record.domain_id AND
        dns_domain.id = dns_ns_record.domain_id
    ;
ELSE
    RETURN QUERY
    SELECT
        {RR_TYPE_SOA} as type,
        NULL::bool as nonexistent,
        dns_domain.name as domainname,
        dns_soa_record.ttl as ttl,
        dns_soa_record.nameserver as nsname,
        dns_soa_record.rname as rname,
        dns_soa_record.serial as serial,
        dns_soa_record.refresh as refresh,
        dns_soa_record.retry as retry,
        dns_soa_record.expiry as expiry,
        dns_soa_record.nxttl as nxttl,
        NULL::varchar(255) as canonical_name
    FROM
        dns_domain, dns_soa_record
    WHERE
        '.' || searchname LIKE '%.' || dns_domain.name AND
        dns_domain.id = dns_soa_record.domain_id
    ORDER BY
        length(dns_domain.name) DESC
    LIMIT 1
    ;
END IF;
RETURN ;
END
$BODY$
LANGUAGE plpgsql;
;
PREPARE get_cname_record(VARCHAR(255)) AS
SELECT * from get_cname_record($1) ;
