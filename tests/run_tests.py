# -*- coding: utf-8 -*-

import importlib
import inspect
import os
import sys
import argparse
from itertools import chain
from os.path import dirname, join as jp, splitext

CWD = dirname(sys.modules[__name__].__file__)
sys.path.insert(0, jp(CWD, '..'))

from chibitest import runner, TestCase, Benchmark


def get_test_modules():
    modules = []

    for n in os.listdir(CWD):
        if n.startswith('test_') and n.endswith('.py'):
            n, _ = splitext(n)
            modules.append(importlib.import_module(n))

    return modules


def is_testcase(n):
    return inspect.isclass(n) \
        and issubclass(n, TestCase) \
        and not n is TestCase \
        and not n is Benchmark


def is_benchmark(n):
    return inspect.isclass(n) \
        and issubclass(n, Benchmark) \
        and not n is Benchmark


def get_testcases(module):
    return [(testcase.__name__, testcase) \
        for _, testcase in inspect.getmembers(module, is_testcase)]


def run_testcases(testcases, benchmark=False, include=[], exclude=[], single=None):
    if include:
        testcases = [n for n in testcases if n[0] in include]
    if exclude:
        testcases = [n for n in testcases if not n[0] in exclude]

    if benchmark:
        testcases = [n[1] for n in testcases if is_benchmark(n[1])]
    else:
        testcases = [n[1] for n in testcases if not is_benchmark(n[1])]

    runner(testcases, method_name=single)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    parser.add_argument("-l", "--list", help="list all testcases",
                        action="store_true")
    parser.add_argument("-b", "--benchmark", help="run benchmarks",
                        action="store_true")
    group.add_argument("-s", "--single", type=str, default=None,
                        help="single test function to run")
    group.add_argument("-i", "--include", type=str, default='',
                        help="comma separated list of testcases to include")
    group.add_argument("-e", "--exclude", type=str, default='',
                        help="comma separated list of testcases to exclude")

    args = parser.parse_args()
    
    testcases = list(chain(*map(get_testcases, get_test_modules())))
    include = []
    exclude = []
    benchmark = False

    if args.list:
        for name, testcase in testcases:
            print(name)
        sys.exit(0)

    if args.include:
        include=args.include.split(',')
    elif args.exclude:
        exclude=args.exclude.split(',')

    run_testcases(testcases, benchmark, include, exclude, args.single)
