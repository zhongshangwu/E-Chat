from server import Server


if __name__ == '__main__':
    server = Server()
    print('Server started at %s:%s....' % server.addr)
    server.serve_forever()
