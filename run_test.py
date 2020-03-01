import os
import subprocess
import shlex
import xml.etree.ElementTree as ET
import numpy as np
from tqdm import tqdm
from sbfl import ochiai
from sbfl.utils import ranking
from cov_parser import cobertura, gcov

TESTLIST = "tests/testlist.txt"
PYTHON_COVERAGE_REPORT = "./misaka.xml"
CODE_ELEMENTS = []
F_LINES = {}

def get_py_f_lines(filepath):
    f_lines = {}
    function = None
    cls = None
    with open(filepath, 'r') as f:
        for i, line in enumerate(f):
            if line.startswith('def '):
                function = line.split()[1].split('(')[0]
                f_lines[function] = []
                cls = None
                continue
            if line.startswith('class'):
                cls = line.split()[1].split('(')[0].split(':')[0]
                function = None
                continue
            if cls is not None and line.strip().startswith('def '):
                function = f"{cls}${line.strip().split()[1].split('(')[0]}"
                f_lines[function] = []
                continue
            lineno = i+1
            if function is not None:
                f_lines[function].append(lineno)
    print(f_lines)
    return f_lines

def execute_command(cmd, timeout=60):
    #print(f"$ {cmd}")
    sprocess = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    stdout, stderr = sprocess.communicate(timeout=timeout)
    return stdout.decode("ascii"), stderr.decode("ascii")

def load_testlist():
    with open(TESTLIST, 'r') as f:
        return f.read().splitlines()

def cleanup():
    if os.path.exists('.coverage'):
        execute_command("rm .coverage")
    for dirpath, dirnames, filenames in os.walk('misaka/'):
        for filename in filenames:
            if os.path.splitext(filename)[1] == '.gcda':
                execute_command(f"rm {os.path.join(dirpath, filename)}")
    for filename in os.listdir('.'):
        if os.path.splitext(filename)[1] == '.gcov':
            execute_command(f"rm {filename}")

def run_testcase(testname):
    cleanup() 

    stdout, _ = execute_command(f"coverage run tests/run_tests.py -s {testname}")
    test_result = stdout.split('\n')[1].split()[-1]
    
    execute_command(f"coverage xml -o {PYTHON_COVERAGE_REPORT} --omit \"tests/*\"")
    
    for dirpath, dirnames, filenames in os.walk('misaka/'):
        for filename in filenames:
            if os.path.splitext(filename)[1] == '.gcno':
                execute_command(f"gcov -pfb {os.path.join(dirpath, os.path.splitext(filename)[0] + '.c')}")
    # Analyse Coverage Results

    hits = cobertura(PYTHON_COVERAGE_REPORT)
    for filepath in hits:
        if filepath.endswith('.py') and filepath not in F_LINES:
            F_LINES[filepath] = get_py_f_lines(filepath)
    for filename in os.listdir('.'):
        if not os.path.splitext(filename)[1] == '.gcov':
            continue
        filepath = os.path.splitext(filename.replace('#', '/'))[0]
        f_lines = {} if filepath not in F_LINES else None
        hits[filepath] = gcov(filename, f_lines=f_lines)
        if filepath not in F_LINES:
            F_LINES[filepath] = f_lines
    return test_result, hits

if __name__ == "__main__":
    tests = load_testlist()
    print(f"Found {len(tests)} test cases")

    test_results = []
    code_elements = []
    coverage = []
    for test in tqdm(tests):
        test_result, hits = run_testcase(test)
        if not code_elements:
            for filepath in hits:
                for lineno in hits[filepath]:
                    code_elements.append((filepath, lineno))
            code_elements.sort()
        coverage.append([ hits[f][l] for f, l in code_elements ])
        test_results.append(1 if test_result == 'PASSED' else 0)

    if 0 in test_results:
        X = np.array(coverage)
        y = np.array(test_results)
        for i in np.where(y == 0)[0]:
            print("FAILED: ", tests[i])
        print(ochiai(X, y))
        scores = ochiai(X, y)
        line_scores = { elem: scores[i] for i, elem in enumerate(code_elements) }
        method_scores = {}
        for filepath in F_LINES:
            for function in F_LINES[filepath]:
                method_scores[(filepath, function)] = 0.0
                for lineno in F_LINES[filepath][function]:
                    key = (filepath, lineno)
                    if key in code_elements:
                        score = line_scores[key]
                        if not np.isnan(score) and score > method_scores[(filepath, function)]:
                            method_scores[(filepath, function)] = score
                #print((filepath, function), method_scores[(filepath, function)])
        
        methods = list(sorted(list(method_scores.keys())))
        ranks = ranking([ method_scores[method] for method in methods])
        results = [ (ranks[i], method, method_scores[method]) for i, method in enumerate(methods) ]
        results.sort()
        print(results)
    else:
        print("no failing test cases")
