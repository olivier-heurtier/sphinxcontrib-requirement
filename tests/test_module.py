
import unittest

import sphinxcontrib.requirement.__main__ as main

#_______________________________________________________________________________
class TestReq(unittest.TestCase):

    def test_withid(self):
        S = """
A req with already an ID

.. req:req:: This is req 01-01
    :reqid: REQ-0101

"""

        mo = main.rReq.search(S)
        assert mo is not None
        assert mo['optionkey'] == 'reqid'

    def test_withid_and(self):
        S = """
A req with already an ID

.. req:req:: This is req 01-01
    :reqid: REQ-0101
    :priority: 2
"""

        mo = main.rReq.search(S)
        assert mo is not None
        # assert mo['optionkey'] == 'reqid'

    def test_withnoid(self):
        S = """
A req with already an ID

.. req:req:: This is req 01-01
    :priority: 2
"""

        mo = main.rReq.search(S)
        assert mo is not None
        assert mo['optionkey'] != 'reqid'

    def test_nooption(self):
        S = """
A req with already an ID

.. req:req:: This is req 01-01

"""

        mo = main.rReq.search(S)
        assert mo is None

    def test_withid_second(self):
        S = """
A req with already an ID

.. req:req:: This is req 01-01
    :priority: 2
    :reqid: 001
"""

        mo = main.rReq.search(S)
        assert mo is not None
        assert mo.groups() is not None
        assert mo['options'] == '\n'.join(S.splitlines()[-2:])+'\n'

# _____________________________________________________________________________
if __name__ == '__main__':
    unittest.main()
    