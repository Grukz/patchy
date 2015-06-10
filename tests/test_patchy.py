#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import six
import unittest

import pytest

import patchy


class PatchTests(unittest.TestCase):

    def test_patch(self):
        def sample():
            return 1

        patchy.patch(sample, """\
            @@ -1,2 +1,2 @@
             def sample():
            -    return 1
            +    return 9001
            """)
        assert sample() == 9001

    def test_patch_simple(self):
        def sample():
            return 1

        patchy.patch(sample, """\
            @@ -2,2 +2,2 @@
            -    return 1
            +    return 2
            """)
        assert sample() == 2

    def test_patch_simple_no_newline(self):
        def sample():
            return 1

        patchy.patch(sample, """\
            @@ -2,2 +2,2 @@
            -    return 1
            +    return 2""")
        assert sample() == 2

    def test_patch_invalid(self):
        """
        We need to balk on empty patches
        """
        def sample():
            return 1

        bad_patch = """
            """
        with pytest.raises(ValueError) as excinfo:
            patchy.patch(sample, bad_patch)

        msg = str(excinfo.value)
        assert msg.startswith("Could not apply the patch to 'sample'.")
        assert "Only garbage was found in the patch input."
        assert sample() == 1

    def test_patch_invalid_hunk(self):
        """
        We need to balk on patches that fail on application
        """
        def sample():
            return 1

        bad_patch = """\
            @@ -1,2 +1,2 @@
             def sample():
            -    return 2
            +    return 23"""
        with pytest.raises(ValueError) as excinfo:
            patchy.patch(sample, bad_patch)

        assert "Hunk #1 FAILED" in str(excinfo.value)
        assert sample() == 1

    def test_patch_invalid_hunk_2(self):
        """
        We need to balk on patches that fail on application
        """
        def sample():
            if True:
                print("yes")
            if False:
                print("no")
            return 1

        bad_patch = """\
            @@ -1,2 +1,2 @@
             def sample():
            -    if True:
            +    if False:
            @@ -3,5 +3,5 @@
                     print("yes")
            -    if Falsy:
            +    if Truey:
                     print("no")
            """
        with pytest.raises(ValueError) as excinfo:
            patchy.patch(sample, bad_patch)

        print(excinfo.value)
        assert "Hunk #2 FAILED" in str(excinfo.value)
        assert sample() == 1

    def test_patch_twice(self):
        def sample():
            return 1

        patchy.patch(sample, """\
            @@ -1,2 +1,2 @@
             def sample():
            -    return 1
            +    return 2""")
        patchy.patch(sample, """\
            @@ -1,2 +1,2 @@
             def sample():
            -    return 2
            +    return 3
            """)

        assert sample() == 3

    def test_patch_mutable_default_arg(self):
        def foo(append=None, mutable=[]):
            if append is not None:
                mutable.append(append)
            return len(mutable)

        assert foo() == 0
        assert foo('v1') == 1
        assert foo('v2') == 2
        assert foo(mutable=[]) == 0

        patchy.patch(foo, """\
            @@ -1,2 +1,3 @@
             def foo(append=None, mutable=[]):
            +    len(mutable)
                 if append is not None:
            """)

        assert foo() == 2
        assert foo('v3') == 3
        assert foo(mutable=[]) == 0

    def test_patch_instancemethod(self):
        class Artist(object):
            def method(self):
                return 'Chalk'

        patchy.patch(Artist.method, """\
            @@ -1,2 +1,2 @@
             def method(self):
            -    return 'Chalk'
            +    return 'Cheese'
            """)

        assert Artist().method() == "Cheese"

    def test_patch_instancemethod_twice(self):
        class Artist(object):
            def method(self):
                return 'Chalk'

        patchy.patch(Artist.method, """\
            @@ -1,2 +1,2 @@
             def method(self):
            -    return 'Chalk'
            +    return 'Cheese'""")

        patchy.patch(Artist.method, """\
            @@ -1,2 +1,2 @@
             def method(self):
            -    return 'Cheese'
            +    return 'Crackers'""")

        assert Artist().method() == "Crackers"

    def test_patch_classmethod(self):
        class Emotion(object):
            def __init__(self, name):
                self.name = name

            @classmethod
            def create(cls, name):
                return cls(name)

        patchy.patch(Emotion.create, """\
            @@ -1,2 +1,3 @@
             @classmethod
             def create(cls, name):
            +    name = name.title()
                 return cls(name)""")

        assert Emotion.create("Happy").name == "Happy"
        assert Emotion.create("happy").name == "Happy"

    def test_patch_classmethod_twice(self):
        class Emotion(object):
            def __init__(self, name):
                self.name = name

            @classmethod
            def create(cls, name):
                return cls(name)

        patchy.patch(Emotion.create, """\
            @@ -1,2 +1,3 @@
             @classmethod
             def create(cls, name):
            +    name = name.title()
                 return cls(name)""")

        patchy.patch(Emotion.create, """\
            @@ -1,3 +1,3 @@
             @classmethod
             def create(cls, name):
            -    name = name.title()
            +    name = name.lower()
                 return cls(name)""")

        assert Emotion.create("happy").name == "happy"
        assert Emotion.create("Happy").name == "happy"
        assert Emotion.create("HAPPY").name == "happy"

    def test_patch_staticmethod(self):
        class Doge(object):
            @staticmethod
            def bark():
                return "Woof"

        patchy.patch(Doge.bark, """\
            @@ -1,3 +1,3 @@
             @staticmethod
             def bark():
            -    return "Woof"
            +    return "Wow\"""")

        assert Doge.bark() == "Wow"

    def test_patch_staticmethod_twice(self):
        class Doge(object):
            @staticmethod
            def bark():
                return "Woof"

        patchy.patch(Doge.bark, """\
            @@ -1,3 +1,3 @@
             @staticmethod
             def bark():
            -    return "Woof"
            +    return "Wow\"""")

        patchy.patch(Doge.bark, """\
            @@ -1,3 +1,3 @@
             @staticmethod
             def bark():
            -    return "Wow"
            +    return "Wowowow\"""")

        assert Doge.bark() == "Wowowow"

    @unittest.skipUnless(six.PY3, "Python 3")
    def test_patch_nonlocal_fails(self):
        # Kept in separate file since it would SyntaxError on Python 2
        from py3_nonlocal import sample

        with pytest.raises(SyntaxError) as excinfo:
            patchy.patch(sample, """\
                @@ -2,3 +2,3 @@
                     nonlocal variab
                -    multiple = 3
                +    multiple = 4
                """)
        assert "no binding for nonlocal 'variab' found" in str(excinfo.value)
