#! /usr/bin/env pyhton
# -*- coding: utf-8 -*-
import socket
from urllib.parse import urlparse, urlunparse


HOST = ''
PORT = 80

def get_line(con):

    line = ''

    while 1:
        buf = con.recv(1).decode('utf-8')
        if buf == '\r':
            line += buf
            buf = con.recv(1)
            if buf == '\n':
                line += buf
                return line
        else:
            line += buf            

def get_headers(con):

    headers = ''
    while 1:
        line = get_line(con)
        if line is None:
            break;
        if line == '\r\n':
            break;
        else:
            headers += line

    return headers                

def parse_headers(raw_headers):
    
    request_lines = raw_headers.split('\r\n')
    first_line = request_lines[0].split(' ')
    method = first_line[0]
    full_path = first_line[1]
    version = first_line[2]

    print('%s %s' % (method, full_path))

    (schema, netloc, path, params, query, fragment) \
        = urlparse(full_path, 'http')
    i = netloc.find(':')    
    if i > 0:
        address = netloc[:i], int(netloc[i+1:])
    else:
        address = netloc, 80    

    return method, version, schema, address, path, params, query, fragment    

def handle_connection(con):

    #read Header from connection
    headers = get_headers(con)

    if headers is None:
        return
    else:
        method, version, schema, address, path, params, query, fragment = \
        parse_headers(headers)

        path = urlunparse("", "", path, params, query, "")
        req_headers = " ".join([method, path, version]) + "\r\n" +\
        "\r\n".join(req_headers.split('\r\n')[1:])  

        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.settimeout(10)

        try:
            soc.connection(address)
        except socket.error:
            # con.sendall("HTTP/1.1" + str(arg[0]) + " Fail\r\n\r\n")
            con.close()
            soc.close()
        else:
            if req_headers.find('Connection') >= 0:
                req_headers = req_headers.replace('keep-alive', 'close')    
            else:
                req_headers = req_headers + 'Connection: close\r\n'
            req_headers += '\r\n'           
            soc.sendall(req_headers)

            data = ''
            while 1:
                try:
                    buf = soc.recv(8129).decode('utf-8')
                    data += buf
                except Exception:
                    buf = None
                finally:
                    if not buf:
                        soc.close()
                        break

            con.sendall(data)            
            con.close()


def server(host, port):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(500)  #specifies the maximum number of queued connections 
    print('Listening at port %s' % port)

    while 1:
        try:
            con, addr = s.accept()
            handle_connection(con)
        except KeyboardInterrupt:
            print("Bye...")
            break    

if __name__ == '__main__':
    server(HOST, PORT)