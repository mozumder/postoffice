import requests
import logging

from dns.models import A_Record, DynamicDNS, DynamicDNSAccount, IPLog

logger = logging.getLogger("dns")

class DynamicDNSManager:
    @staticmethod
    def update(ping_url):
        try:
            logger.debug(f"Pinging: {ping_url}")
            r = requests.get(url=ping_url, timeout=1)
        except requests.exceptions.ConnectionError:
            logger.error(f"Can't connect to ping URL {ping_url}")
            return 2
        except requests.exceptions.Timeout:
            logger.error(f"Taking too long to ping {ping_url}")
            return 1
        except requests.exceptions.TooManyRedirects:
            logger.error(f"Too many redirects while connecting to {ping_url}")
            return 2
        
        if r.status_code == 404:
            logger.error(f"Ping URL problem: 404 Not Found {ping_url}")
            return 2
        elif r.status_code == 403:
            logger.error(f"Ping URL problem: 403 Permission denied {ping_url}")
            return 2
        elif r.status_code != 200:
            logger.error(f"Problem pinging {ping_url}")
            return 2
        new_ip = r.text
        logger.debug(f"Received IP Address: {new_ip}")
        try:
            current_ip = IPLog.objects.all()[0].ip
        except IndexError:
            current_ip = None
        if current_ip == new_ip:
            return

        for dyn in DynamicDNS.objects.all():
            if new_ip != dyn.a_record.ip_address and dyn.a_record.dynamic_ip == True:
                try:
                    account = DynamicDNSAccount.objects.filter(domains=dyn.a_record.domain)[0]
                except IndexError as e:
                    logger.error(f"No Dynamic DNS Account found")
                    raise e
                endpoint = account.endpoint
                password = dyn.password if dyn.password else account.password
                payload = {
                    'username':account.username,
                    'password':password,
                    'id':dyn.dyndns_id,
                    'ip':new_ip,
                }
                try:
                    logger.debug(f"Connecting to DNS Update URL: {endpoint} with payload {payload}")
                    dnsupdate = requests.post(url=endpoint, data=payload, timeout=15)
                except requests.exceptions.ConnectionError:
                    logger.warning(f"Can't connect to Update DNS URL {endpoint}")
                    return 1
                except requests.exceptions.Timeout:
                    logger.warning(f"Taking too long to connect to Update DNS URL {endpoint}")
                    return 1
                except requests.exceptions.TooManyRedirects:
                    logger.warning(f"Too many redirects while connecting to Update DNS URL {endpoint}")
                    return 1
                if dnsupdate.status_code == 404:
                    logger.warning(f"Problem updating DNS: 404 Not Found {endpoint}")
                    return 1
                elif dnsupdate.status_code == 403:
                    logger.warning(f"Problem udpating DNS: 403 Permission denied {endpoint}")
                    return 1
                elif dnsupdate.status_code != 200:
                    logger.warning(f"Problem updating DNS with URL {endpoint}")
                    return 1
                logger.debug(f"DNS Update status: {dnsupdate.text}")
                if dnsupdate.text == 'error-auth':
                    logger.error(f"Problem authenticating DNS record: Check username/password")
                    return 2
                elif dnsupdate.text == 'error-auth-suspend':
                    logger.error(f"Problem authenticating DNS record: User is suspended.")
                    return 2
                elif dnsupdate.text == 'error-auth-voided':
                    logger.error(f"Problem authenticating DNS record: User account revoked.")
                    return 2
                elif dnsupdate.text == 'error-record-invalid':
                    logger.error(f"Unable to update record in system database. Record does not exist in the system.")
                    return 2
                elif dnsupdate.text == 'error-record-auth':
                    logger.error(f"Problem updating DNS record. User does not have access to this record")
                    return 2
                elif dnsupdate.text == 'error-record-ip-same':
                    logger.warning(f"IP address didn't change so nothing was done.")
                    continue
                elif dnsupdate.text == 'error-system':
                    logger.warning(f"Problem updating DNS record. General DNS server system error caught and recognized by the system.")
                    return 1
                elif dnsupdate.text == 'error':
                    logger.warning(f"Problem updating DNS record. General DNS server system error unrecognized by the system.")
                    return 1
                    
                elif dnsupdate.text == 'success':
                    a_record = dyn.a_record
                    a_record.ip_address = new_ip
                    a_record.save()
                    logger.info(f"Updated {a_record} with new IP address {new_ip}")
                    continue
                else:
                    logger.warning(f"Problem updating DNS record.")
                    return 1

        NewIPLog = IPLog(ip=new_ip)
        NewIPLog.save()

        return
