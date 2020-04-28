DROP FUNCTION IF EXISTS get_a_record(character varying);
CREATE OR REPLACE FUNCTION get_a_record(
    searchname varchar(255)
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
    nxttl INT,
    out_cname VARCHAR(255),
    out_ip_address INET
)
AS
$BODY$
DECLARE
    cname_check RECORD;
    result RECORD;
BEGIN

SELECT
    dns_cname_record.canonical_name as cname,
    dns_cname_record.ttl as ttl,
    dns_domain.id as founddomain_id,
    dns_domain.name as domainname
INTO
    cname_check
FROM
    dns_cname_record
LEFT OUTER JOIN
    dns_domain
ON
    dns_domain.id = dns_cname_record.domain_id
WHERE
    dns_cname_record.fqdn = searchname
;

IF FOUND THEN
    RETURN QUERY
    SELECT
        {RR_TYPE_A} as type,
        true as nxdomain,
        cname_check.domainname as domainname,
        dns_a_record.ttl as ttl,
        NULL::varchar(255) as nsname,
        NULL::varchar(255) as rname,
        NULL::int as serial,
        NULL::int as refresh,
        NULL::int as retry,
        NULL::int as expiry,
        NULL::int as nxttl,
        cname_check.cname as cname,
        dns_a_record.ip_address as ip_address
    FROM
        dns_a_record
    WHERE
        dns_a_record.fqdn = cname_check.cname
    UNION
    SELECT
        {RR_TYPE_CNAME} as type,
        true as nxdomain,
        cname_check.domainname as domainname,
        cname_check.ttl as ttl,
        NULL::varchar(255) as nsname,
        NULL::varchar(255) as rname,
        NULL::int as serial,
        NULL::int as refresh,
        NULL::int as retry,
        NULL::int as expiry,
        NULL::int as nxttl,
        cname_check.cname as cname,
        NULL::inet as ip_address
    UNION
    SELECT
        {RR_TYPE_NS} as type,
        true as nxdomain,
        cname_check.domainname as domainname,
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
    WHERE
        cname_check.founddomain_id = dns_ns_record.domain_id
    ;
ELSE
    SELECT
        dns_a_record.id as found_a_record_id,
        dns_a_record.ip_address as ip_address,
        dns_a_record.ttl as ttl,
        dns_domain.id as founddomain_id,
        dns_domain.name as domainname
    INTO
        result
    FROM
        dns_a_record
    LEFT OUTER JOIN
        dns_domain
    ON
        dns_domain.id = dns_a_record.domain_id
    WHERE
        dns_a_record.fqdn = searchname
    ;

    IF FOUND THEN
        RETURN QUERY
        SELECT
            {RR_TYPE_A} as type,
            true as nxdomain,
            result.domainname as domainname,
            result.ttl as ttl,
            NULL::varchar(255) as nsname,
            NULL::varchar(255) as rname,
            NULL::int as serial,
            NULL::int as refresh,
            NULL::int as retry,
            NULL::int as expiry,
            NULL::int as nxttl,
            NULL::varchar(255) as cname,
            result.ip_address as ip_address
        UNION
        SELECT
            {RR_TYPE_NS} as type,
            true as nxdomain,
            result.domainname as domainname,
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
        WHERE
            result.founddomain_id = dns_ns_record.domain_id
        ;
    ELSE
        RETURN QUERY
        SELECT
            {RR_TYPE_SOA} as type,
        exists(
            SELECT 1
            FROM
                dns_aaaa_record
            WHERE
                dns_aaaa_record.fqdn = searchname
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
            '.' || searchname LIKE '%.' || dns_domain.name AND
            dns_domain.id = dns_soa_record.domain_id
        ORDER BY
            length(dns_domain.name) DESC
        LIMIT 1
        ;
    END IF;
END IF;
RETURN ;
END
$BODY$
LANGUAGE plpgsql;
;
PREPARE get_a_record(VARCHAR(255)) AS
SELECT * from get_a_record($1) ;
