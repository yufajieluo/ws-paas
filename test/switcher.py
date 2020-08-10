class A(object):
    def __init__(self):
        self.sequence = ['a', 'c', 'b']
        self.switcher = {
            'a': self.funca,
            'b': self.funcb,
            'c': self.funcc
        }
        return

    def funca(self, **kwargs):
        print('this is funca, args is {0}'.format(kwargs))
        return True

    def funcb(self, **kwargs):
        print('this is funcb')
        return 

    def funcc(self, **kwargs):
        print('this is funcc')
        return False
    
    def process(self):
        for case in self.sequence:
            print('begin process {0}'.format(case))
            re = self.switcher.get(case)(name = 'wshuai', age = 33)
            print(re)
            if re:
                print('end process {0}, continue'.format(case))
                continue
            else:
                print('failed process {0}, exit'.format(case))
                break
        return

if __name__ == '__main__':
    a = A()
    a.process()