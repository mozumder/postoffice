DROP FUNCTION IF EXISTS get_a_record(character varying);
CREATE OR REPLACE FUNCTION get_a_record(
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
    out_ip_address INET
)
AS
$BODY$
DECLARE
    result RECORD;
BEGIN

SELECT
    dns_domain.name as domainname,
    dns_domain.id as founddomain_id
INTO
    result
FROM
    dns_a_record,
    dns_domain
WHERE
    dns_domain.id = dns_a_record.domain_id AND
    dns_a_record.fqdn = searchname
ORDER BY
    length(dns_domain.name) DESC
LIMIT 1
;
IF FOUND THEN
    RETURN QUERY
    SELECT
        {RR_TYPE_A} as type,
        NULL::bool as nonexistent,
        result.domainname as domainname,
        dns_a_record.ttl as ttl,
        NULL::varchar(255) as nsname,
        NULL::varchar(255) as rname,
        NULL::int as serial,
        NULL::int as refresh,
        NULL::int as retry,
        NULL::int as expiry,
        NULL::int as nxttl,
        dns_a_record.ip_address as ip_address
    FROM
        dns_a_record,
        dns_domain
    WHERE
        dns_domain.id = result.founddomain_id AND
        dns_a_record.fqdn = searchname
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
        NULL::inet as ip_address
    FROM
        dns_domain, dns_a_record, dns_ns_record
    WHERE
        dns_a_record.fqdn = searchname AND
        dns_domain.id = dns_a_record.domain_id AND
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
        NULL::inet as ip_address
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
PREPARE get_a_record(VARCHAR(255)) AS
SELECT * from get_a_record($1) ;
