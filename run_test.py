import os
import subprocess
import shlex
import xml.etree.ElementTree as ET
import numpy
from tqdm import tqdm

TESTLIST = "tests/testlist.txt"
PYTHON_COVERAGE_REPORT = "./misaka.xml"
CODE_ELEMENTS = []

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
                execute_command(f"gcov -p {os.path.join(dirpath, os.path.splitext(filename)[0] + '.c')}")
    # Analyse Coverage Results

    tree = ET.parse(PYTHON_COVERAGE_REPORT)
    root = tree.getroot()
    hits = {}
    source_files = root.findall("./packages/package/classes/class")
    for source_file in source_files:
        filepath = source_file.attrib['filename']
        hits[filepath] = {}
        for line in source_file.findall("./lines/line"):
            hits[filepath][int(line.attrib['number'])] = int(line.attrib['hits'])

    for filename in os.listdir('.'):
        if not os.path.splitext(filename)[1] == '.gcov':
            continue
        filepath = os.path.splitext(filename.replace('#', '/'))[0]
        hits[filepath] = {}
        with open(filename, 'r') as f:
            for line in f:
                count, number = line.split(':')[0].strip(), int(line.split(':')[1].strip())
                if number < 1 or count == '-':
                    continue
                hits[filepath][number] = 0 if count=='#####' else int(count)

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

    X = numpy.array(coverage)
    y = numpy.array(test_results)
    print(X.shape, y.shape)
