import time
from multiprocessing import Process, Manager

class C1(object):
    def __init__(self, d):
        self.d = d
        return
    def f1(self, **kwargs):
        while True:
            print('f1 shm d is {0}'.format(self.d))
            #self.d['wife'] = 'dxj'
            dd = self.d['status']
            dd['agent']['intime'] = '11111'
            self.d['status'] = dd
            time.sleep(2)

class C2(object):
    def __init__(self, d):
        self.d = d
        return
    def f2(self, **kwargs):
        while True:
            print('f2 shm d is {0}'.format(self.d))
            #self.d['qingren'] = 'wtt'
            dd = self.d['status']
            dd['agent']['expect'] = '11111'
            self.d['status'] = dd
            time.sleep(2)

def f1(d):
    while True:
        print('f1 shm d is {0}'.format(d))
        d['wife'] = 'dxj'
        print('f1 shm d is {0}'.format(d))
        time.sleep(2)

def f2(d):
    while True:
        print('f2 shm d is {0}'.format(d))
        #kwargs['d']['wife'] = 'dxj'
        time.sleep(2)

if __name__ == '__main__':
    with Manager() as manager:
        d = manager.dict({'name':'wshuai'})
        d = manager.dict({'status': {'agent': {'intime': 'normal', 'expect': 'normal'}, 'application': {'intime': 'normal', 'expect': 'normal'}, 'health': {'intime': 'normal', 'expect': 'normal'}}})
        #d = {'name': 'wshuai', 'wife': 'wtt'}

        c1 = C1(d)
        c2 = C2(d)
        p1 = Process(target=c1.f1, kwargs={'d':d})
        p2 = Process(target=c2.f2, kwargs={'d':d})
        p1.start()
        p2.start()
        p1.join()
        p2.join()

        #print(d)
        #print(l)