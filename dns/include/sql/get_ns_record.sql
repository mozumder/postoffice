DROP FUNCTION IF EXISTS get_ns_record(character varying(255));
CREATE OR REPLACE FUNCTION get_ns_record(
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
    dns_domain.id as found_domain_id,
    dns_domain.name as domainname
INTO
    result
FROM
    dns_domain
WHERE
    search = dns_domain.name
ORDER BY
    length(dns_domain.name) DESC
LIMIT 1
;

IF FOUND THEN RETURN QUERY
-- MX and NS records must never point to CNAME
    SELECT
        {RR_TYPE_NS} as type,
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
        result.found_domain_id = dns_ns_record.domain_id
    ;
ELSE
    RETURN QUERY
    SELECT
        {RR_TYPE_SOA} as type,
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
        '.' || search LIKE '%.' || dns_domain.name AND
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
PREPARE get_ns_record(VARCHAR(255)) AS
SELECT * from get_ns_record($1) ;
