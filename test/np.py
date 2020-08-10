from multiprocessing import Process, Manager

def f(d, l):
    print('f--{0}'.format(l))
    d['qingren'] = 'wtt'
    l.append(2)
    print('f--{0}'.format(l))
    
def nf(d, l):
    print('nf--{0}'.format(l))
    d['qingren'] = 'wtt'
    print('nf--{0}'.format(l))

if __name__ == '__main__':
    with Manager() as manager:
        d = manager.dict()
        l = manager.list(range(10))
        d = {'name': 'wshuai'}
        l = [1]
        print('main--{0}'.format(l))
        p = Process(target=f, args=(d, l))
        p.start()
        #p.join()

        #nf(d)
        print('main--{0}'.format(l))