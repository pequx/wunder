#!/usr/bin/env python

import inspect
import os
import sys

from decouple import config
from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand


COVERAGE_XML = os.environ.get("HUNDI_COVERAGE_XML",
                              config("HUNDI_COVERAGE_XML", default=True, cast=bool))
COVERAGE_HTML = os.environ.get("HUNDI_COVERAGE_HTML",
                               config("HUNDI_COVERAGE_HTML", default=False, cast=bool))
JUNIT_XML = os.environ.get("HUNDI_JUNIT_XML",
                           config("HUNDI_JUNIT_XML", default=True, cast=bool))

# Add here all kinds of additional classifiers as defined under
# https://pypi.python.org/pypi?%3Aaction=list_classifiers
CLASSIFIERS = [
    "Development Status :: 2 - Pre-Alpha",
    "Environment :: Console",
    "Environment :: No Input/Output (Daemon)",
    "Environment :: Web Environment",
    "Framework :: Flask",
    "Framework :: Jupyter",
    "Framework :: Tornado",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "Intended Audience :: System Administrators",
    "License :: Other/Proprietary License",
    "Operating System :: Unix",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: Implementation :: CPython",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Scientific/Engineering :: Information Analysis",
    "Topic :: Scientific/Engineering :: Mathematics",
    "Topic :: Software Development :: Libraries :: Application Frameworks",
]

if sys.version_info < (3, 9, 0):
    sys.stderr.write(
        "FATAL: {} needs to be run with Python 3.9+\n".format(
            config("HUNDI_NAME", default=False)
        )
    )
    sys.exit(1)

__location__ = os.path.join(
    os.getcwd(), os.path.dirname(inspect.getfile(inspect.currentframe()))
)


class PyTest(TestCommand):
    user_options = [
        ("cov=", None, "Run coverage"),
        ("cov-xml=", None, "Generate junit xml report"),
        ("cov-html=", None, "Generate junit html report"),
        ("junitxml=", None, "Generate xml of test results"),
        ("pytest-args=", "a", "Arguments to pass to pytest"),
    ]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.cov = None
        self.cov_xml = False
        self.cov_html = False
        self.junitxml = None
        self.pytest_args = ""

    def finalize_options(self):
        TestCommand.finalize_options(self)
        if self.cov is not None:
            self.cov = ["--cov", self.cov, "--cov-report", "term-missing"]
            if self.cov_xml:
                self.cov.extend(["--cov-report", "xml"])
            if self.cov_html:
                self.cov.extend(["--cov-report", "html"])
        if self.junitxml is not None:
            self.junitxml = ["--junitxml", self.junitxml]

    def run_tests(self):
        try:
            import pytest
        except Exception:
            raise RuntimeError(
                "py.test is not installed, run: pip install pytest"
            )
        import shlex

        params = {"args": self.test_args}
        if self.cov:
            params["args"] += self.cov
        if self.junitxml:
            params["args"] += self.junitxml
        params["args"] += shlex.split(self.pytest_args)
        errno = pytest.main(**params)
        sys.exit(errno)


def get_install_requirements(path):
    content = open(os.path.join(__location__, path)).read()
    return [req for req in content.split("\\n") if req != ""]


def setup_package():
    # Assemble additional setup commands
    cmdclass = {}
    cmdclass["test"] = PyTest

    # install_reqs = get_install_requirements('requirements.txt')

    command_options = {
        "test": {
            "test_suite": ("setup.py", "tests"),
            "cov": ("setup.py", config("HUNDI_NAME", ""))
        }
    }

    if JUNIT_XML:
        command_options["test"]["junitxml"] = "setup.py", "junit.xml"
    if COVERAGE_XML:
        command_options["test"]["cov_xml"] = "setup.py", True
    if COVERAGE_HTML:
        command_options["test"]["cov_html"] = "setup.py", True

    setup(
        name=config("HUNDI_NAME", ""),
        author=config("HUNDI_AUTHOR", ""),
        author_email=config("HUNDI_EMAIL", ""),
        license=config("HUNDI_LICENSE", ""),
        classifiers=CLASSIFIERS,
        packages=find_packages(exclude=["tests", "tests.*"]),
        include_package_data=True,
        install_requires=[],
        cmdclass=cmdclass,
        command_options=command_options,
        test_suite="tests",
        setup_requires=["pytest-runner", "flake8", "isort", "black"],
        tests_require=[
            "pytest-cov",
            "pytest",
        ],
    )


if __name__ == "__main__":
    setup_package()
