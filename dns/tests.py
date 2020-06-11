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
        my_admin = User.objects.create_superuser('tester', 'test@example.net', 'nopassword')

#        proc = subprocess.Popen(
#            ["./manage.py", 'createsuperuser', '--username', 'tester', '--email', 'test@example.net', '--noinput'],
#            env=my_env
#        )
#        proc.wait()
        proc = subprocess.Popen(
            ["./manage.py", 'createdomain', '--email', 'dns@example.net', 'example.net', '199.29.17.254', 'ns0.dnsprovider.com', 'ns1.dnsprovider.com'],
            env=my_env
        )
        proc.wait()
        proc = subprocess.Popen(
            ["./manage.py", 'addhost', '-dyn', 'example.net', '199.29.17.254', 'www'],
            env=my_env
        )
        proc.wait()
        proc = subprocess.Popen(
            ["./manage.py", 'addhost', '-dyn', 'example.net', '199.29.17.254', 'mail'],
            env=my_env
        )
        proc.wait()
        proc = subprocess.Popen(
            ["./manage.py", 'addhost', '-dyn', 'example.net', '199.29.17.254', 'cdn'],
            env=my_env
        )
        proc.wait()
        proc = subprocess.Popen(
            ["./manage.py", 'addredundantadddress', 'example.net', '6.113.127.2', 'cdn'],
            env=my_env
        )
        proc.wait()
        proc = subprocess.Popen(
            ["./manage.py", 'addhost', '-6', 'fe80::dead:beef:cafe:babe', 'example.net', '6.113.127.2', 'smtp'],
            env=my_env
        )
        proc.wait()
        proc = subprocess.Popen(
            ["./manage.py", 'addhost', '-mx', '-dyn', 'example.net', '199.29.17.254', 'mail'],
            env=my_env
        )
        proc = subprocess.Popen(
            ["./manage.py", 'createredirect', 'example.net', 'mail', 'mail2'],
            env=my_env
        )
        proc.wait()
        proc = subprocess.Popen(
            ["./manage.py", 'addtxtrecord', 'example.net', 'Sendinblue-code:3fe1ac48ac4588d17c0515b589b70bf4'],
            env=my_env
        )
        proc.wait()
        proc = subprocess.Popen(
            ["./manage.py", 'addtxtrecord', 'example.net', 'v=spf1 a mx ptr include:spf.sendinblue.com +ip4:199.29.17.254 +ip4:6.113.127.2 -all'],
            env=my_env
        )
        proc.wait()
        proc = subprocess.Popen(
            ["./manage.py", 'addtxtrecord', 'example.net', 'google-site-verification=Fi4VWVWVF8D0njI1JTUbXzKpQRGwYbPw6tgYUCdW5xc'],
            env=my_env
        )
        proc.wait()
        proc = subprocess.Popen(
            ["./manage.py", 'addtxtrecord', '-n', '2020060201._domainkey', 'example.net', 'v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8BMIIBCgKCAQEA0kIjkMO4lXDTvmtiYdAv7ieKOQJXAKp+2wfXfvAG0Jex7APqKWnl816b4/voyyy8JcsrFph2Ug1EAKlSp9Rx/BomZM8aT1HmWeU4yIBvziexOTIsyRD5L6cveu38l7oIaruPJma4t8rHqQZfqLnHNWSO4lrkXKrGUYWTEN58DVjOmKAWSeTR6IPreb2qHiY2KVb5iJOv/zhR322yf5BC3JvxZ56BDXATaMjjVYpDNTslQp7jbu1wwxlmh2S5xx7VNqs7Zv90Yb2dIGQmgsJnh3YQhwibWK2CUbzeD9jXXq1RIs/wzTrK4cgutzHvOPTHoEMaB7RfbdGU9PTYWAmAbwIDAQAB'],
            env=my_env
        )
        proc.wait()
        proc = subprocess.Popen(
            ["./manage.py", 'addtxtrecord', '-n', '_dmarc', 'example.net', 'v=DMARC1; p=reject; sp=reject; rua=mailto:dmarcrua@example.net!10m; ruf=mailto:dmarcruf@example.net!10m; rf=afrf; pct=100; ri=86400'],
            env=my_env
        )
        proc.wait()
        proc = subprocess.Popen(
            ["./manage.py", 'addcaarecord', 'example.net', 'issue', 'letsencrypt.org'],
            env=my_env
        )
        proc.wait()
        proc = subprocess.Popen(
            ["./manage.py", 'addcaarecord', 'example.net', 'iodef', 'mailto:info@example.net'],
            env=my_env
        )
        proc.wait()
        proc = subprocess.Popen(
            ["./manage.py", 'addsrvrecord', '-pri', '0', '-w', '1', 'example.net', '_imaps', '_tcp', '993', 'mail.example.net'],
            env=my_env
        )
        proc.wait()
        proc = subprocess.Popen(
            ["./manage.py", 'addsrvrecord', '-pri', '0', '-w', '1', 'example.net', '_imap', '_tcp', '143', 'mail.example.net'],
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

    def test_a_record(self):
        """Test domain A record lookup. Should return succesful DNS lookup and
additional authority data.
        """
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 2, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;example.net.			IN	A

;; ANSWER SECTION:
example.net.		14400	IN	A	199.29.17.254

;; AUTHORITY SECTION:
example.net.		14400	IN	NS	ns1.dnsprovider.com.
example.net.		14400	IN	NS	ns0.dnsprovider.com.

"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'example.net'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_a_record_cap(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 2, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;example.neT.			IN	A

;; ANSWER SECTION:
example.neT.		14400	IN	A	199.29.17.254

;; AUTHORITY SECTION:
example.net.		14400	IN	NS	ns1.dnsprovider.com.
example.net.		14400	IN	NS	ns0.dnsprovider.com.
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'example.neT'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_negative_a_record(self):
        test=""";; flags: qr rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;badexample.net.			IN	A
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'badexample.net'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_negative_a_record_nodot(self):
        test=""";; flags: qr rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;badexamplenet.			IN	A
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'badexamplenet'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_a_record_subdomain(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 2, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;www.example.net.		IN	A

;; ANSWER SECTION:
www.example.net.	14400	IN	A	199.29.17.254

;; AUTHORITY SECTION:
example.net.		14400	IN	NS	ns1.dnsprovider.com.
example.net.		14400	IN	NS	ns0.dnsprovider.com.
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'www.example.net'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_negative_a_record_subdomain(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 1, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;wwww.example.net.		IN	A

;; AUTHORITY SECTION:
example.net.		14400	IN	SOA	ns0.dnsprovider.com. dns.example.net. 0 43200 3600 2419200 180
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'wwww.example.net'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_soa_record_subdomain(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 2, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;www.example.net.		IN	SOA

;; ANSWER SECTION:
example.net.		14400	IN	SOA	ns0.dnsprovider.com. dns.example.net. 0 43200 3600 2419200 180

;; AUTHORITY SECTION:
example.net.		14400	IN	NS	ns0.dnsprovider.com.
example.net.		14400	IN	NS	ns1.dnsprovider.com.
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'www.example.net', 'SOA'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_soa_record(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 2, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;example.net.			IN	SOA

;; ANSWER SECTION:
example.net.		14400	IN	SOA	ns0.dnsprovider.com. dns.example.net. 0 43200 3600 2419200 180

;; AUTHORITY SECTION:
example.net.		14400	IN	NS	ns0.dnsprovider.com.
example.net.		14400	IN	NS	ns1.dnsprovider.com.
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'example.net', 'SOA'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_soa_record_cap(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 2, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;example.neT.			IN	SOA

;; ANSWER SECTION:
example.net.		14400	IN	SOA	ns0.dnsprovider.com. dns.example.net. 0 43200 3600 2419200 180

;; AUTHORITY SECTION:
example.net.		14400	IN	NS	ns0.dnsprovider.com.
example.net.		14400	IN	NS	ns1.dnsprovider.com.
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '@127.0.0.1', 'example.neT', 'SOA', '+nostat'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_negative_soa_record_cap(self):
        test=""";; flags: qr rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;exampleneT.			IN	SOA
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'exampleneT', 'SOA'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_soa_record_negative_subdomain(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 2, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;wwww.example.net.		IN	SOA

;; ANSWER SECTION:
example.net.		14400	IN	SOA	ns0.dnsprovider.com. dns.example.net. 0 43200 3600 2419200 180

;; AUTHORITY SECTION:
example.net.		14400	IN	NS	ns0.dnsprovider.com.
example.net.		14400	IN	NS	ns1.dnsprovider.com.
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'wwww.example.net', 'SOA'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_negative_soa_record(self):
        test=""";; flags: qr rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;badexample.net.			IN	SOA
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'badexample.net', 'SOA'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_negative_soa_record_negative_subdomain(self):
        test=""";; flags: qr rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;wwww.badexample.net.		IN	SOA
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'wwww.badexample.net', 'SOA'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_redundant_a_record_subdomain(self):
        """Test A record lookup for a subdomain with multiple IP addresses.
        Should return succesful DNS lookup with 2 answers and 2 authority data.
        """
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 2, AUTHORITY: 2, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;cdn.example.net.		IN	A

;; ANSWER SECTION:
cdn.example.net.	14400	IN	A	199.29.17.254
cdn.example.net.	14400	IN	A	6.113.127.2

;; AUTHORITY SECTION:
example.net.		14400	IN	NS	ns1.dnsprovider.com.
example.net.		14400	IN	NS	ns0.dnsprovider.com.
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'cdn.example.net'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_negative_aaaa_record(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 1, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;example.net.			IN	AAAA

;; AUTHORITY SECTION:
example.net.		14400	IN	SOA	ns0.dnsprovider.com. dns.example.net. 0 43200 3600 2419200 180
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'example.net', 'AAAA'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_aaaa_record_subdomain(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 2, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;smtp.example.net.		IN	AAAA

;; ANSWER SECTION:
smtp.example.net.	14400	IN	AAAA	fe80::dead:beef:cafe:babe

;; AUTHORITY SECTION:
example.net.		14400	IN	NS	ns1.dnsprovider.com.
example.net.		14400	IN	NS	ns0.dnsprovider.com.
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'smtp.example.net', 'AAAA'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_aaaa_record_subdomain_cap(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 2, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;smtP.example.net.		IN	AAAA

;; ANSWER SECTION:
smtP.example.net.	14400	IN	AAAA	fe80::dead:beef:cafe:babe

;; AUTHORITY SECTION:
example.net.		14400	IN	NS	ns1.dnsprovider.com.
example.net.		14400	IN	NS	ns0.dnsprovider.com.
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'smtP.example.net', 'AAAA'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_negative_aaaa_record_subdomain(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 1, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;www.example.net.		IN	AAAA

;; AUTHORITY SECTION:
example.net.		14400	IN	SOA	ns0.dnsprovider.com. dns.example.net. 0 43200 3600 2419200 180
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'www.example.net', 'AAAA'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_negative_aaaa_record_negative_subdomain(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 1, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;wwww.example.net.		IN	AAAA

;; AUTHORITY SECTION:
example.net.		14400	IN	SOA	ns0.dnsprovider.com. dns.example.net. 0 43200 3600 2419200 180
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'wwww.example.net', 'AAAA'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_mx_record(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 2, ADDITIONAL: 2

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;example.net.			IN	MX

;; ANSWER SECTION:
example.net.		14400	IN	MX	0 mail.example.net.

;; AUTHORITY SECTION:
example.net.		14400	IN	NS	ns0.dnsprovider.com.
example.net.		14400	IN	NS	ns1.dnsprovider.com.

;; ADDITIONAL SECTION:
mail.example.net.	14400	IN	A	199.29.17.254
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'example.net', 'MX'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_mx_record_cap(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 2, ADDITIONAL: 2

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;example.neT.			IN	MX

;; ANSWER SECTION:
example.neT.		14400	IN	MX	0 mail.example.net.

;; AUTHORITY SECTION:
example.net.		14400	IN	NS	ns0.dnsprovider.com.
example.net.		14400	IN	NS	ns1.dnsprovider.com.

;; ADDITIONAL SECTION:
mail.example.net.	14400	IN	A	199.29.17.254
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'example.neT', 'MX'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_negative_mx_record(self):
        test=""";; flags: qr rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;badexample.net.			IN	MX
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'badexample.net', 'MX'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_negative_mx_record_subdomain(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 1, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;www.example.net.		IN	MX

;; AUTHORITY SECTION:
example.net.		14400	IN	SOA	ns0.dnsprovider.com. dns.example.net. 0 43200 3600 2419200 180
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'www.example.net', 'MX'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_negative_mx_record_negative_subdomain(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 1, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;wwww.example.net.		IN	MX

;; AUTHORITY SECTION:
example.net.		14400	IN	SOA	ns0.dnsprovider.com. dns.example.net. 0 43200 3600 2419200 180
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'wwww.example.net', 'MX'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_ns_record(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 2, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;example.net.			IN	NS

;; ANSWER SECTION:
example.net.		14400	IN	NS	ns0.dnsprovider.com.
example.net.		14400	IN	NS	ns1.dnsprovider.com.
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'example.net', 'NS'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_ns_record_cap(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 2, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;examplE.neT.			IN	NS

;; ANSWER SECTION:
example.net.		14400	IN	NS	ns0.dnsprovider.com.
example.net.		14400	IN	NS	ns1.dnsprovider.com.
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'examplE.neT', 'NS'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_negative_ns_record(self):
        test=""";; flags: qr rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;badexample.net.			IN	NS
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'badexample.net', 'NS'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_ns_record_subdomain(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 1, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;www.example.net.		IN	NS

;; AUTHORITY SECTION:
example.net.		14400	IN	SOA	ns0.dnsprovider.com. dns.example.net. 0 43200 3600 2419200 180
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'www.example.net', 'NS'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_ns_record_negative_subdomain(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 1, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;wwww.example.net.		IN	NS

;; AUTHORITY SECTION:
example.net.		14400	IN	SOA	ns0.dnsprovider.com. dns.example.net. 0 43200 3600 2419200 180
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'wwww.example.net', 'NS'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_txt_record(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 3, AUTHORITY: 2, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;example.net.			IN	TXT

;; ANSWER SECTION:
example.net.		14400	IN	TXT	"google-site-verification=Fi4VWVWVF8D0njI1JTUbXzKpQRGwYbPw6tgYUCdW5xc"
example.net.		14400	IN	TXT	"v=spf1 a mx ptr include:spf.sendinblue.com +ip4:199.29.17.254 +ip4:6.113.127.2 -all"
example.net.		14400	IN	TXT	"Sendinblue-code:3fe1ac48ac4588d17c0515b589b70bf4"

;; AUTHORITY SECTION:
example.net.		14400	IN	NS	ns0.dnsprovider.com.
example.net.		14400	IN	NS	ns1.dnsprovider.com.
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'example.net', 'TXT'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_txt_record_cap(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 3, AUTHORITY: 2, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;examplE.neT.			IN	TXT

;; ANSWER SECTION:
examplE.neT.		14400	IN	TXT	"google-site-verification=Fi4VWVWVF8D0njI1JTUbXzKpQRGwYbPw6tgYUCdW5xc"
examplE.neT.		14400	IN	TXT	"v=spf1 a mx ptr include:spf.sendinblue.com +ip4:199.29.17.254 +ip4:6.113.127.2 -all"
examplE.neT.		14400	IN	TXT	"Sendinblue-code:3fe1ac48ac4588d17c0515b589b70bf4"

;; AUTHORITY SECTION:
example.net.		14400	IN	NS	ns0.dnsprovider.com.
example.net.		14400	IN	NS	ns1.dnsprovider.com.
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'examplE.neT', 'TXT'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_negative_txt_record(self):
        test=""";; flags: qr rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;badexample.net.			IN	TXT
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'badexample.net', 'TXT'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_txt_record_subdomain(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 1, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;www.example.net.		IN	TXT

;; AUTHORITY SECTION:
example.net.		14400	IN	SOA	ns0.dnsprovider.com. dns.example.net. 0 43200 3600 2419200 180
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'www.example.net', 'TXT'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_negative_txt_record_subdomain(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 1, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;wwww.example.net.		IN	TXT

;; AUTHORITY SECTION:
example.net.		14400	IN	SOA	ns0.dnsprovider.com. dns.example.net. 0 43200 3600 2419200 180
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'wwww.example.net', 'TXT'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_txt_record_subdomain_domainkey(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 2, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;2020060201._domainkey.example.net. IN	TXT

;; ANSWER SECTION:
2020060201._domainkey.example.net. 14400 IN TXT	"v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8BMIIBCgKCAQEA0kIjkMO4lXDTvmtiYdAv7ieKOQJXAKp+2wfXfvAG0Jex7APqKWnl816b4/voyyy8JcsrFph2Ug1EAKlSp9Rx/BomZM8aT1HmWeU4yIBvziexOTIsyRD5L6cveu38l7oIaruPJma4t8rHqQZfqLnHNWSO4lrkXKrGUYWTEN58DVjOmKAWSeTR6IPreb2qHiY2K" "Vb5iJOv/zhR322yf5BC3JvxZ56BDXATaMjjVYpDNTslQp7jbu1wwxlmh2S5xx7VNqs7Zv90Yb2dIGQmgsJnh3YQhwibWK2CUbzeD9jXXq1RIs/wzTrK4cgutzHvOPTHoEMaB7RfbdGU9PTYWAmAbwIDAQAB"

;; AUTHORITY SECTION:
example.net.		14400	IN	NS	ns1.dnsprovider.com.
example.net.		14400	IN	NS	ns0.dnsprovider.com.
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', '2020060201._domainkey.example.net', 'TXT'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_txt_record_subdomain_dmarc(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 2, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;_dmarc.example.net.		IN	TXT

;; ANSWER SECTION:
_dmarc.example.net.	14400	IN	TXT	"v=DMARC1; p=reject; sp=reject; rua=mailto:dmarcrua@example.net!10m; ruf=mailto:dmarcruf@example.net!10m; rf=afrf; pct=100; ri=86400"

;; AUTHORITY SECTION:
example.net.		14400	IN	NS	ns1.dnsprovider.com.
example.net.		14400	IN	NS	ns0.dnsprovider.com.
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', '_dmarc.example.net', 'TXT'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_cname_record_subdomain(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 2, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;mail2.example.net.		IN	CNAME

;; ANSWER SECTION:
mail2.example.net.	14400	IN	CNAME	mail.example.net.

;; AUTHORITY SECTION:
example.net.		14400	IN	NS	ns1.dnsprovider.com.
example.net.		14400	IN	NS	ns0.dnsprovider.com.
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'mail2.example.net', 'CNAME'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_a_cname_record_subdomain(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 2, AUTHORITY: 2, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;mail2.example.net.		IN	A

;; ANSWER SECTION:
mail.example.net.	14400	IN	A	199.29.17.254
mail2.example.net.	14400	IN	CNAME	mail.example.net.

;; AUTHORITY SECTION:
example.net.		14400	IN	NS	ns1.dnsprovider.com.
example.net.		14400	IN	NS	ns0.dnsprovider.com.
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'mail2.example.net'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_caa_record(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 2, AUTHORITY: 2, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;example.net.			IN	CAA

;; ANSWER SECTION:
example.net.		14400	IN	CAA	0 issue "letsencrypt.org"
example.net.		14400	IN	CAA	0 iodef "mailto:info@example.net"

;; AUTHORITY SECTION:
example.net.		14400	IN	NS	ns0.dnsprovider.com.
example.net.		14400	IN	NS	ns1.dnsprovider.com.
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', 'example.net', 'CAA'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_srv_record(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 2, ADDITIONAL: 2

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;_imaps._tcp.example.net.	IN	SRV

;; ANSWER SECTION:
_imaps._tcp.example.net. 14400	IN	SRV	0 1 993 mail.example.net.

;; AUTHORITY SECTION:
example.net.		14400	IN	NS	ns1.dnsprovider.com.
example.net.		14400	IN	NS	ns0.dnsprovider.com.

;; ADDITIONAL SECTION:
mail.example.net.	14400	IN	A	199.29.17.254
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', '_imaps._tcp.example.net', 'SRV'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_srv_record_cap(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 2, ADDITIONAL: 2

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;_imapS._tcP.examplE.neT.	IN	SRV

;; ANSWER SECTION:
_imapS._tcP.examplE.neT. 14400	IN	SRV	0 1 993 mail.example.net.

;; AUTHORITY SECTION:
example.net.		14400	IN	NS	ns1.dnsprovider.com.
example.net.		14400	IN	NS	ns0.dnsprovider.com.

;; ADDITIONAL SECTION:
mail.example.net.	14400	IN	A	199.29.17.254
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', '_imapS._tcP.examplE.neT', 'SRV'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)

    def test_negative_srv_record(self):
        test=""";; flags: qr aa rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 1, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;_tcp.example.net.		IN	SRV

;; AUTHORITY SECTION:
example.net.		14400	IN	SOA	ns0.dnsprovider.com. dns.example.net. 0 43200 3600 2419200 180
"""
        result = subprocess.run(
            ['dig', '-p', '2123', '+nostat', '@127.0.0.1', '_tcp.example.net', 'SRV'],
            stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        self.assertIn(test, output)


"""./manage.py createdomain --email dns@example.net example.net 199.29.17.254 ns0.dnsprovider.com ns1.dnsprovider.com
./manage.py addhost -dyn example.net 199.29.17.254 admin
./manage.py addhost -dyn example.net 199.29.17.254 api
./manage.py addhost -dyn example.net 199.29.17.254 beta
./manage.py addhost -dyn example.net 199.29.17.254 blog
./manage.py addhost -dyn example.net 199.29.17.254 bobby
./manage.py addhost -dyn example.net 199.29.17.254 cdn
./manage.py addredundantadddress example.net 6.113.127.2 cdn
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
./manage.py createredirect example.net mail mail2
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
