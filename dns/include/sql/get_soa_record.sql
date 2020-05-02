DROP FUNCTION IF EXISTS get_soa_record(character varying);
CREATE OR REPLACE FUNCTION get_soa_record(
    search varchar(255)
    )
RETURNS TABLE (
    type INT,
    nxdomain BOOLEAN,
    domainname VARCHAR(255),
    ttl INT,
    nsname VARCHAR(255),
    rname VARCHAR(255),
    serial INT,
    refresh INT,
    retry INT,
    expiry INT,
    nxttl INT
)
AS
$BODY$
DECLARE
    result RECORD;
BEGIN

SELECT
    exists(
        SELECT 1
        FROM
            dns_a_record,
            dns_aaaa_record,
            dns_cname_record
        WHERE
            dns_a_record.searchname = search OR
            dns_aaaa_record.searchname = search OR
            dns_cname_record.searchname = search
        ) as nxdomain,
    dns_soa_record.ttl as ttl,
    dns_domain.id as domainid,
    dns_domain.name as domainname,
    dns_soa_record.nameserver as nsname,
    dns_soa_record.rname as rname,
    dns_soa_record.serial as serial,
    dns_soa_record.refresh as refresh,
    dns_soa_record.retry as retry,
    dns_soa_record.expiry as expiry,
    dns_soa_record.nxttl as nxttl
INTO
    result
FROM
    dns_domain, dns_soa_record
WHERE
    '.' || search LIKE '%.' || dns_domain.name AND
    dns_domain.id = dns_soa_record.domain_id
ORDER BY
    length(dns_domain.name) DESC
LIMIT 1
;

IF FOUND THEN
    RETURN QUERY
    SELECT
        {RR_TYPE_SOA} as type,
        result.nxdomain as nxdomain,
        result.domainname as domainname,
        result.ttl as ttl,
        result.nsname as nsname,
        result.rname as rname,
        result.serial as serial,
        result.refresh as refresh,
        result.retry as retry,
        result.expiry as expiry,
        result.nxttl as nxttl
    UNION
    SELECT
        {RR_TYPE_NS} as type,
        result.nxdomain as nxdomain,
        result.domainname as domainname,
        dns_ns_record.ttl as ttl,
        dns_ns_record.name as nsname,
        NULL::varchar(255) as rname,
        NULL::int as serial,
        NULL::int as refresh,
        NULL::int as retry,
        NULL::int as expiry,
        NULL::int as nxttl
    FROM
        dns_ns_record
    WHERE
        result.domainid = dns_ns_record.domain_id
    ;
END IF;
RETURN ;
END
$BODY$
LANGUAGE plpgsql;
;
PREPARE get_soa_record(VARCHAR(255)) AS
SELECT * from get_soa_record($1) ;
