import multiprocessing
from multiprocessing.managers import SyncManager
import os
import ipaddress
from test_server import TestServer

class TestClientGeneric:
    def startClient(self, ipAddress, portNum, authKey):
        self.manager = self.makeClientManager(ipAddress, portNum, authKey)
        self.jobQ = self.manager.get_job_q()
        self.resultQ = self.manager.get_result_q()
        self.lock = self.manager.get_lock()

    def makeClientManager(self, ipAddress, portNum, authKey):
        show = True
        class ServerQueueManager(SyncManager):
            pass

        ServerQueueManager.register('get_job_q')
        ServerQueueManager.register('get_result_q')
        ServerQueueManager.register('get_lock')

        if show: print('starting clientManager at address', (ipAddress, portNum), 'with authkey', authKey)

        manager = ServerQueueManager(address=(ipAddress, portNum), authkey = authKey)
        manager.connect()
        if show: print('client connected to %s:%s'%(ipAddress, portNum))
        return manager

    def serverMethodCall(self, args):
        show = True
        try:
            self.lock.acquire()
            while not self.resultQ.empty():
                garbage = self.resultQueue.get()
            if show: print('in serverMethodCall with args', args)
            self.jobQ.put(args)
            data = self.resultQ.get()
            return data
        finally:
            self.lock.release()

class TestClient(TestClientGeneric):
    def __init__(self):
        self.ipAddress = '127.0.0.1'
        self.portNum = TestServer.portNum
        self.authKey = TestServer.authKey
        print('authKey', self.authKey)
        self.startClient(self.ipAddress, self.portNum, self.authKey)

    def add(self, a, b):
        return self.serverMethodCall(('add', a, b))

if __name__ == '__main__':
    ts = TestClient()
    print('2 + 2 =', ts.add(2,2))
