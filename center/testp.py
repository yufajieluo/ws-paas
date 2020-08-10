
import sys
from a import A 
#from mission import Mission
#from pool import Pool
#from temq import TemQ


class B(object):
    def __init__(self):
        s = '''def run(self):
            print('this is run')
            return
        '''
        eval(s)
        return


if __name__ == '__main__':
    #pool = Pool(worker_num_min = 2, worker_num_max = 8, maxsize = 10, timeout = 1)
    #pool.process()
    #exec(s)
    
    #exec('B.run = run')
    a = A('wshuai')
    print('A is {}'.format(A.__dict__))
    #b = B()
    a.run()
    print('------')
    sys.exit(0)
'''

import os
import sys
import time
import threading
import multiprocessing

class Join(object):
    def __init__(self):
        self.joins = []
        return
    def set(self, joins):
        self.joins = joins
    def get(self):
        return self.joins

class JT(threading.Thread):
    def __init__(self, join):
        super(JT, self).__init__()
        self.join = join
        return
    def run(self):
        while True:
            print('JT join is {}'.format(self.join.get()))
            self.join.set([1,2])
            for join in self.join.joins:
                print('JT join... join is {}'.format(join))
                #join.join()
            time.sleep(2)

class Worker(multiprocessing.Process):
    def __init__(self, **kwargs):
        super(Worker, self).__init__(**kwargs)
        #self.daemon = True
        self.id = None
        self.start()
        return
    def run(self):
        self.id = os.getpid()
        for index in range(3):
            print('I am worker {}, my parents is {}'.format(self.pid, os.getppid()))
            time.sleep(1)
        print('worker exit')
        return

class Pool(multiprocessing.Process):
    def __init__(self, shm, lock, **kwargs):
        super(Pool, self).__init__(**kwargs)
        self.shm = shm
        self.lock = lock
        self.worker = []
        self.init_worker()
        return
    def init_worker(self):
        self.worker.append(Worker())
        self.worker.append(Worker())
        return
    def run(self):
        index = 0
        while True:
            print('I am pool {}, my parents is {}, self.worker is {}'.format(os.getpid(), os.getppid(), self.worker))
            if index == 2:
                #print('worker {} id is {}'.format(self.worker[0], self.worker[0].pid))
                self.lock.acquire()
                self.shm['join'] = [self.worker.pop().pid]
                self.lock.release()
            if index == 4:
                self.lock.acquire()
                self.shm['join'] = [self.worker.pop().pid]
                self.lock.release()
            index += 1
            time.sleep(3)
            
        return

if __name__ == '__main__':
    manager = multiprocessing.Manager()
    lock = manager.Lock()
    shm = manager.dict({'join':[]})
    pool = Pool(shm, lock)
    pool.start()

    while True:
        print('P {}, shm join is {}'.format(os.getpid(), shm['join']))
        if shm['join']:
            lock.acquire()
            join_list = shm['join']
            shm['join'] = []
            
            for join in join_list:
                print('join is {}'.format(join))
                os.waitpid(join, 0)
            lock.release()
        time.sleep(2)

    sys.exit(0)
'''