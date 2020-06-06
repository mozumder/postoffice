import unittest
from io import StringIO
import subprocess, os
from django.core.management import call_command
from django.test import TestCase, SimpleTestCase
from django.contrib.auth.models import User
from django.test.testcases import SerializeMixin

# Create your tests here.

class DNSTest(SimpleTestCase):
    databases = '__all__'
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        my_env = {**os.environ, 'DJANGO_RUN_ENV': 'test'}
        my_admin = User.objects.create_superuser('myuser', 'myemail@test.com', 'mypassword')

#        proc = subprocess.Popen(
#            ["./manage.py", 'createsuperuser', '--username', 'tester', '--email', 'test@example.net', '--noinput'],
#            env=my_env
#        )
#        proc.wait()
        proc = subprocess.Popen(
            ["./manage.py", 'createdomain', 'example.net', '199.29.17.254', 'ns0.dnsprovider.com', 'ns1.dnsprovider.com'],
            env=my_env
        )
        proc.wait()
        proc = subprocess.Popen(
            ["./manage.py", 'addhost', '-dyn', 'example.net', '199.29.17.254', 'admin'],
            env=my_env
        )
        proc.wait()
        cls.proc = subprocess.Popen(
            ["./manage.py", "rundnsserver", '--port', '2123'],
            env=my_env
        )
        print(f'Spawned DNS server with process id {cls.proc.pid}')
    @classmethod
    def tearDownClass(cls):
        cls.proc.kill()
        super().tearDownClass()

    def test_domain(self):
        test=""";; QUESTION SECTION:
;example.net.			IN	A

;; ANSWER SECTION:
example.net.		14400	IN	A	199.29.17.254

;; AUTHORITY SECTION:
example.net.		14400	IN	NS	ns0.dnsprovider.com.
example.net.		14400	IN	NS	ns1.dnsprovider.com.
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '@127.0.0.1', 'example.net', '+nostat'],
            stdout=subprocess.PIPE)
        outputstring = result.stdout.decode('utf-8')
        print(outputstring)
        self.assertIn(test, outputstring)

    def test_admindomain(self):
        test=""";; QUESTION SECTION:
;admin.example.net.		IN	A

;; ANSWER SECTION:
admin.example.net.	14400	IN	A	199.29.17.254

;; AUTHORITY SECTION:
example.net.		14400	IN	NS	ns0.dnsprovider.com.
example.net.		14400	IN	NS	ns1.dnsprovider.com.
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '@127.0.0.1', 'admin.example.net', '+nostat'],
            stdout=subprocess.PIPE)
        outputstring = result.stdout.decode('utf-8')
        print(outputstring)
        self.assertIn(test, outputstring)

"""./manage.py createdomain --email dns@example.net example.net 199.29.17.254 ns0.dnsprovider.com ns1.dnsprovider.com
./manage.py addhost -dyn example.net 199.29.17.254 admin
./manage.py addhost -dyn example.net 199.29.17.254 api
./manage.py addhost -dyn example.net 199.29.17.254 beta
./manage.py addhost -dyn example.net 199.29.17.254 blog
./manage.py addhost -dyn example.net 199.29.17.254 bobby
./manage.py addhost -dyn example.net 199.29.17.254 cdn
./manage.py addredundantadddress example.net 199.29.17.254 cdn
./manage.py addhost -dyn example.net 199.29.17.254 chris
./manage.py addhost -dyn example.net 199.29.17.254 db
./manage.py addhost -dyn example.net 199.29.17.254 django
./manage.py addhost -dyn example.net 199.29.17.254 ftp
./manage.py addhost -dyn example.net 199.29.17.254 git
./manage.py addhost -dyn example.net 199.29.17.254 gitlab
./manage.py addhost -dyn example.net 199.29.17.254 home
./manage.py addhost -dyn example.net 199.29.17.254 imap
./manage.py addhost -dyn example.net 199.29.17.254 jose
./manage.py addhost -6 fe80::dead:beef:cafe:babe example.net 6.113.127.2 la
./manage.py addhost -mx -dyn example.net 199.29.17.254 mail
./manage.py addhost -dyn example.net 199.29.17.254 mohammed
./manage.py addhost -dyn example.net 199.29.17.254 news
./manage.py addhost -dyn example.net 199.29.17.254 ns
./manage.py addhost -dyn example.net 199.29.17.254 ns0
./manage.py addhost -dyn example.net 199.29.17.254 ns1
./manage.py addhost -dyn example.net 199.29.17.254 ns2
./manage.py addhost -dyn example.net 199.29.17.254 ns3
./manage.py addhost -dyn example.net 199.29.17.254 ns4
./manage.py addhost -dyn example.net 199.29.17.254 ns5
./manage.py addhost -dyn example.net 199.29.17.254 ntp
./manage.py addhost -dyn example.net 199.29.17.254 ntp0
./manage.py addhost -dyn example.net 199.29.17.254 ntp1
./manage.py addhost -dyn example.net 199.29.17.254 pop
./manage.py addhost -dyn example.net 199.29.17.254 redis
./manage.py addhost -dyn example.net 199.29.17.254 rspamd
./manage.py addhost -6 fe80::dead:beef:cafe:babe example.net 6.113.127.2 smtp
./manage.py addhost -dyn example.net 199.29.17.254 stats
./manage.py addhost -dyn example.net 199.29.17.254 steve
./manage.py addhost -dyn example.net 199.29.17.254 uwsgi
./manage.py addhost -dyn example.net 199.29.17.254 vpn
./manage.py addhost -dyn example.net 199.29.17.254 www
./manage.py createredirect example.net la mail2
./manage.py addtxtrecord example.net 'Sendinblue-code:3fe1ac48ac4588d17c0515b589b70bf4'
./manage.py addtxtrecord example.net 'v=spf1 a mx ptr include:spf.sendinblue.com +ip4:199.29.17.254 +ip4:6.113.127.2 -all'
./manage.py addtxtrecord example.net 'google-site-verification=Fi4VWVWVF8D0njI1JTUbXzKpQRGwYbPw6tgYUCdW5xc'
./manage.py addtxtrecord -n 2020060201._domainkey example.net 'v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8BMIIBCgKCAQEA0kIjkMO4lXDTvmtiYdAv7ieKOQJXAKp+2wfXfvAG0Jex7APqKWnl816b4/voyyy8JcsrFph2Ug1EAKlSp9Rx/BomZM8aT1HmWeU4yIBvziexOTIsyRD5L6cveu38l7oIaruPJma4t8rHqQZfqLnHNWSO4lrkXKrGUYWTEN58DVjOmKAWSeTR6IPreb2qHiY2KVb5iJOv/zhR322yf5BC3JvxZ56BDXATaMjjVYpDNTslQp7jbu1wwxlmh2S5xx7VNqs7Zv90Yb2dIGQmgsJnh3YQhwibWK2CUbzeD9jXXq1RIs/wzTrK4cgutzHvOPTHoEMaB7RfbdGU9PTYWAmAbwIDAQAB'
./manage.py addtxtrecord -n _dmarc example.net 'v=DMARC1; p=reject; sp=reject; rua=mailto:dmarcrua@example.net!10m; ruf=mailto:dmarcruf@example.net!10m; rf=afrf; pct=100; ri=86400'
./manage.py addcaarecord example.net issue letsencrypt.org
./manage.py addcaarecord example.net iodef mailto:info@example.net
./manage.py addsrvrecord -pri 0 -w 1 example.net _imaps _tcp 993 mail.example.net
./manage.py addsrvrecord -pri 0 -w 1 example.net _imap _tcp 143 mail.example.net

./manage.py createdomain --email dns@business.com business.com  199.29.17.254 ns0.dnsprovider.com ns1.dnsprovider.com ns2.dnsmadeeasy.com
./manage.py addhost -dyn business.com 108.51.234.125 www
./manage.py addmailexchange business.com mail.example.net

./manage.py createzone --email info@example.com 10.IN-ADDR.ARPA ns.example.com


dig @127.0.0.1 example.net
dig @127.0.0.1 example.neT
dig @127.0.0.1 examplenet
dig @127.0.0.1 www.example.net
dig @127.0.0.1 wwww.example.net
dig @127.0.0.1 cdn.example.net
dig @127.0.0.1 example.net SOA
dig @127.0.0.1 example.neT SOA
dig @127.0.0.1 examplenet SOA
dig @127.0.0.1 www.example.net SOA
dig @127.0.0.1 wwww.example.net SOA
dig @127.0.0.1 example.net AAAA
dig @127.0.0.1 example.neT AAAA
dig @127.0.0.1 examplenet AAAA
dig @127.0.0.1 www.example.net AAAA
dig @127.0.0.1 wwww.example.net AAAA
dig @127.0.0.1 la.example.net AAAA
dig @127.0.0.1 example.net MX
dig @127.0.0.1 example.neT MX
dig @127.0.0.1 examplenet MX
dig @127.0.0.1 www.example.net MX
dig @127.0.0.1 wwww.example.net MX
dig @127.0.0.1 example.net NS
dig @127.0.0.1 example.neT NS
dig @127.0.0.1 examplenet NS
dig @127.0.0.1 www.example.net NS
dig @127.0.0.1 wwww.example.net NS
dig @127.0.0.1 254.17.29.199.in-addr.arpa PTR
dig @127.0.0.1 2.127.113.6.in-addr.arpa PTR
dig @127.0.0.1 example.net TXT
dig @127.0.0.1 example.neT TXT
dig @127.0.0.1 examplenet TXT
dig @127.0.0.1 www.example.net TXT
dig @127.0.0.1 wwww.example.net TXT
dig @127.0.0.1 2020060201._domainkey.example.net TXT
dig @127.0.0.1 _dmarc.example.net TXT
dig @127.0.0.1 mail2.example.net
dig @127.0.0.1 mail2.example.net CNAME
"""
