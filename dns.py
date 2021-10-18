import dnslib
import time
import pickle
import socket
import sys


def check_cache():
    global dns_cache
    overdue_records = []
    for name in dns_cache:
        for type in dns_cache[name]:
            s, end = dns_cache[name][type]
            if end < int(time.time()):
                overdue_records.append((name, type))
    for name, type in overdue_records:
        del dns_cache[name][type]


def get_google_answer():
    global dns_cache
    data, address = server_receive_socket.recvfrom(1024)
    answer = dnslib.DNSRecord.parse(data)
    print(answer)
    for element in answer.rr:
        if element.rname in dns_cache:
            dns_cache[element.rname][element.rtype] = (element, int(time.time()) + element.ttl)
        else:
            dns_cache[element.rname] = {element.rtype: (element, int(time.time()) + element.ttl)}


dns_cache = {}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_socket.bind(('localhost', 53))

server_socket.settimeout(0)
server_receive_socket.settimeout(0)

time_start = time.time()

try:
    try:
        with open('cache.txt', 'rb') as f:
            dns_cache = pickle.load(f)
            check_cache()
    except IOError:
        pass
    while True:
        try:
            data = None
            try:
                data, address = server_socket.recvfrom(1024)
            except OSError:
                pass
            if data:
                info = dnslib.DNSRecord.parse(data)
                date_from_cache = []
                for element in info.questions:
                    if element.qname in dns_cache and element.qtype in dns_cache[element.qname]:
                        s, end = dns_cache[element.qname][element.qtype]
                        print('RECORD ' + str(element.qname) + ' TYPE ' + str(element.qtype) + ' DATE ' + str(time.ctime(end)))
                        print("FROM CACHE:")
                        print(s)
                        date_from_cache.append(element)
                    else:
                        print('RECORD ' + str(element.qname) + ' TYPE ' + str(element.qtype))
                for element in date_from_cache:
                    info.questions.remove(element)
                if info.questions:
                    try:
                        server = ('8.8.8.8', 53)
                        server_receive_socket.sendto(info.pack(), server)
                        print('REQUEST ' + str(server[0]) + ":" + str(server[1]))
                    except OSError:
                        pass
        except OSError:
            pass
        try:
            get_google_answer()
        except OSError:
            pass
        if time.time() - time_start > 120:
            check_cache()
            time_start = time.time()
        time.sleep(0.1)
except:
    pass
finally:
    server_socket.close()
    server_receive_socket.close()
    with open('cache.txt', 'wb') as f:
        pickle.dump(dns_cache, f)
    time.sleep(1)
    sys.exit(0)
