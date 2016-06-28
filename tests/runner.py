#!/usr/bin/python

import optparse
import os
import sys
import unittest

USAGE = """%prog
Run unit tests for this project. If there were any parameters there'd be a description here for them as well."""


def main(test_path="./"):
    # Discover and run tests, anything that starts with test
    sys.path.insert(0, test_path)
    suite = unittest.TestLoader().discover(test_path)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else -1


if __name__ == '__main__':
    # Parsing args here even though there aren't any
    parser = optparse.OptionParser(USAGE)
    options, args = parser.parse_args()
    ret_val = main()
    sys.exit(ret_val)
