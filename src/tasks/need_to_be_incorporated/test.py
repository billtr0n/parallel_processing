class test( object ):
    def __init__(self, func):
        self.func = func
        self.func()

    def exec_func(self):
        self.func()


def fun():
    print 'hello world'

t = test(fun)
t.exec_func()
