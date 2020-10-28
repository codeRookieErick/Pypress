import re


class TestClass:
    classes = {}

    def __init__(self):
        pass

    @staticmethod
    def decorate(name):
        def factory(function):
            .classes[name] = function
            return function
        return factory


class TestChid(TestClass):
    def __init__(self):
        TestClass.__init__(self)

    @TestClass.decorate('manure')
    def noHacer(self):
        print('noHacer')


class TestChid2(TestClass):
    def __init__(self):
        TestClass.__init__(self)

    @TestClass.decorate('manure')
    def noHacer(self):
        print('noHacer')


t = TestChid()
