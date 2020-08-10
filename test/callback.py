class Test():
    def __init__(self):
        self.callback = None
        return

    def register_callback(self, *args, **kwargs):
        def _register_callback(func):
            self.callback = func
        return _register_callback

    def run(self, **kwargs):
        print('run kwargs is {0}'.format(kwargs))
        print('run get from redis')
        self.callback(**kwargs)

    # /**将foo注册为回调函数**/
    @register_callback()
    def foo(self, **kwargs):
        print('kwargs is {0}'.format(kwargs))

test = Test()


# /**调用feature将触发回调函数,可以在某个合适的时机调用**/
test.run(name = 'wshuai')