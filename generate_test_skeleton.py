import glob
import os
import inspect
import sys
import time
import datetime

def import_module(path, modulename):
    """Imports the module

    Imports the module grabbed from the filename in order to inspect its contents

    Args:
        path:       the path to the file where the test function will be written
        modulename: the name of the module, the filename without the trailing ".py"

    Returns:
        module, the python module object created by the __import__ statement

    Raises:
        none
    """
    try:
        sys.path.append(path)
        __import__(modulename)
        module = sys.modules[modulename]
        return module
    except:
        with open("{}/__init__.py".format(path), "w+") as f:
            f.write("")
        import_module(path, modulename)

def import_classes(modulename, classlist):
    """Import classes

    Procedurally import a list of classes to harvest info

    Args:
        modulename: the name of the module, the filename without the trailing ".py"
        classlist:  the list of classes found under the module in question

    Returns:
        mod, the module containing all the useful class info we want

    Raises:
        none
    """
    mod = __import__(modulename, fromlist=classlist)
    return mod


def teardown_module(path, modulename, module):
    """Tears down a module

    Tears down the imported module, this is to ensure we do not get overlaps on imports

    Args:
        path:       the path to the file where the test function will be written
        modulename: the name of the module, the filename without the trailing ".py"
        module:     the module object that was imported previously

    Returns:
        none

    Raises:
        none
    """
    sys.path.remove(path)
    del sys.modules[modulename]
    del module

def generate_test_file(path, filename, functions, classtree):
    """Generates the test file

    Procedurally generate the test file based on gathered resources

    Args:
        path:       the path to the file where the test function will be written
        filename:   the name of the file to generate a test case for
        functions:  a list containing all function names in the module
        classtree:  a dictionary containing all classes and their mapped functions

    Returns:
        none

    Raises:
        none
    """
    with open("{}/test_{}".format(path, filename), "w+") as f:
        f.write("import pytest\n")
        f.write("import {} as totest\n\n".format(filename))
        f.write("# Call this function if your function is under 5 lines and has a 0%\n")
        f.write("# chance of breaking\n")
        f.write("def i_am_sure_theres_no_issue():\n")
        f.write("\tassert 1\n\n")
        f.write("#--------------------#\n")
        f.write("# TESTING FUNCTIONS #\n")
        f.write("#--------------------#\n")
        for function in functions:
            f.write("def test_{}():\n".format(function))
            f.write("\t#output = totest.{}(*args_here*)\n".format(function))
            f.write("\t#expected = *expected_output_here*\n")
            f.write("\t#assert output == expected\n")
            f.write("\tassert 0\n\n")
        f.write("#------------------#\n")
        f.write("# TESTING CLASSES #\n")
        f.write("#------------------#\n")
        for classname, funcs in classtree.items():
            f.write("\"\"\" TESTING {} CLASS \"\"\"\n".format(classname))
            f.write("@pytest.fixture(scope=\"module\")\n")
            f.write("def setup_{}(request):\n".format(classname))
            f.write("\t#test_class = totest.{}(*args_here*)\n".format(classname))
            f.write("\t#return test_class #allows modules being tested to use one central class\n")
            f.write("\tdef teardown():\n")
            f.write("\t\t#place teardown stuff here\n")
            f.write("\t\tassert 0\n")
            f.write("\trequest.addfinalizer(teardown)\n")
            f.write("\tassert 0\n\n")
            for func in funcs:
                f.write("def test_{}_{}(setup_{}):\n".format(classname, func, classname))
                f.write("\t#output = setup_{}.{}(*args_here*)\n".format(classname, func))
                f.write("\t#expected = *expected_output_here*\n")
                f.write("\t#assert output == expected\n")
                f.write("\tassert 0\n\n")


def gather_file_info(path, filename):
    """Gather the file info

    Gathers the names of the functions and classes to auto-generate the procedurally 
    generated testing function

    Args:
        path:       the path to the file where the test function will be written
        filename:   the name of the file to generate a test case for

    Returns:
        none

    Raises:
        none
    """
    modulename = filename.split(".")[0]
    module = import_module(path, modulename)
    functions = [ x[0] for x in inspect.getmembers(module, inspect.isfunction) ]
    classes = [ x[0] for x in inspect.getmembers(module, inspect.isclass) ]
    classmod = import_classes(modulename, classes)
    classtree = {}
    for c in classes:
        classtree[c] = []
        klass = getattr(classmod, c)
        for v in inspect.getmembers(klass):
            if v[0] == "__dict__":
                for key,value in dict(v[1]).items():
                    if hasattr(value, "__call__"):
                        classtree[c].append(key)
    generate_test_file(path, filename, functions, classtree)
    teardown_module(path, modulename, module)

if __name__ == "__main__":
    path=""
    filename=""
    args = sys.argv
    if len(args) < 2:
        print("Parameters:")
        print("--path <path/to/dir> : REQUIRED - the directory where the file can be found")
        print("--filename <file.py> : REQUIRED - the filename inside the specified directory to generate a test for")
        sys.exit(0)
    i=1
    while i < len(args):
        arg=args[i]
        if arg == "--path":
            i+=1
            path = args[i]
        elif arg == "--filename":
            i+=1
            filename=args[i]
        i+=1
    gather_file_info(path, filename)

