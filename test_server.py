import multiprocessing
from multiprocessing.managers import SyncManager
import os
import ipaddress

class BorgTestServer:
    _sharedState = {}
    def __init__(self):
        self.__dict__ = self._sharedState

class _TestServer:
    def __init__(self):
        self.typeString = type('asdf')

    def add(self, a, b):
        return a + b

    def makeServerManager(self):
        show = True
        self.jobQ = multiprocessing.JoinableQueue(-1)
        self.resultQ = multiprocessing.JoinableQueue(-1)
        self.lock = multiprocessing.Lock()

        class JobQueueManager(SyncManager):
            pass

        JobQueueManager.register('get_job_q', callable=lambda: self.jobQ)
        JobQueueManager.register('get_result_q', callable=lambda: self.resultQ)
        JobQueueManager.register('get_lock', callable=lambda: self.lock)
        if show: print('starting manager with address =', ('', self.portNum), ', authkey', self.authKey)
        manager = JobQueueManager(address=('', self.portNum), authkey = self.authKey)
        manager.start()
        print('started server manager')
        return manager

    def respondToClientRequest(self, methodNameAndArgs, sharedResultQ):
        show = True
        if show: print('in respondToClientRequest() with', methodNameAndArgs)
        try:
            if type(methodNameAndArgs) == self.typeString:
                self.execResult = None
                exec('self.execResult = ' + methodNameAndArgs)
            else:
                methodName = methodNameAndArgs[0]
                sharedResultQ.put(_TestServer.__dict__[methodName](self, *methodNameAndArgs[1:]) )
        except Exception as ex:
            print('received exception in TestServer when', methodNameAndArgs, 'executed.  returning exception', ex)
            sharedResultQ.put(ex)
            
class TestServer(BorgTestServer, _TestServer):
    portNum = 65001
    #portNum = 8084
    authKey = b'testMyServer'
    def __init__(self):
        BorgTestServer.__init__(self)
        if self._sharedState:
            return
        _TestServer.__init__(self)
        self.run()
        
    def run(self):
        show = True
        self.serverManager = self.makeServerManager()
        while True:
            if show: print('waiting for method call...')
            queueData = self.jobQ.get()
            self.respondToClientRequest(queueData, self.resultQ)
if __name__ == '__main__':
    ts = TestServer()
