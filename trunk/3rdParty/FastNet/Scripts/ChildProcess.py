# -*- coding: utf-8 -*-
import sys, traceback, json, time

def ProcessEntry(params):
    import HttpServer

    try:
        server = HttpServer.HttpServer(json.loads(params))
        time.sleep(0.1)
        server.timeout = 2
        server.serve_forever()
    except Exception as e:
        traceback.print_exc()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    sys.path.append(sys.argv[2])
    ProcessEntry(sys.argv[1])