import inspect
import os
import sys
from typing import Any, List, Set
from setuptools import Command, find_packages, setup
from setuptools.dist import Distribution

from hundi.meta import __version__, __name__, __url__, __author__, __email__, __license__, __classifiers__
from hundi.config.settings import EXTRAS_REQUIRE, COVERAGE_XML, COVERAGE_HTML, CONSOLE_SCRIPTS

__location__ = os.path.join(os.getcwd(), os.path.dirname(inspect.getfile(inspect.currentframe())))


class SetupFlake8(Command):
    def __init__(self, dist: Distribution, **kw: Any) -> None:
        super().__init__(dist, **kw)

    def initialize_options(self) -> None:
        try:
            from flake8.main import application

            self.flake8 = application.Application()
            self.flake8.initialize()
        except Exception as e:
            raise e
        self.user_options = []

    def finalize_options(self) -> None:
        pass

    def package_files(self) -> Set:
        seen_package_directories = ()
        directories = self.distribution.package_dir or {}
        empty_directory_exists = "" in directories

        packages = self.distribution.packages or []
        for package in packages:
            if package in directories:
                directory = directories[package]
            elif empty_directory_exists:
                directory = os.path.join(directories[""], package)
            else:
                directory = package

            if not directory.startswith(seen_package_directories):
                seen_package_directories += (directory + ".",)
                yield directory

    def targets(self) -> List:
        return [package for package in self.package_files()] + ['tests', 'setup.py']

    def run(self) -> None:
        self.flake8.run_checks(self.targets())
        self.flake8.formatter.start()
        self.flake8.report_errors()
        self.flake8.report_statistics()
        self.flake8.report_benchmarks()
        self.flake8.formatter.stop()
        try:
            self.flake8.exit()
        except SystemExit as e:
            if e.code:
                raise e


class SetupPyTest(Command):
    def initialize_options(self) -> None:
        self.user_options = [('cov=', None, 'Run coverage'), ('cov-xml=', None, 'Generate junit xml report'),
                             ('cov-html=', None, 'Generate junit html report')]
        self.cov = []
        self.cov_xml = False
        self.cov_html = False

    def finalize_options(self) -> None:
        if self.cov_xml or self.cov_html:
            self.cov = ['--cov', __name__, '--cov-report', 'term-missing']
            if self.cov_xml:
                self.cov.extend(['--cov-report', 'xml'])
            if self.cov_html:
                self.cov.extend(['--cov-report', 'html'])

    def run_tests(self) -> None:
        try:
            import pytest
        except Exception:
            raise RuntimeError('py.test is not installed, run: pip install pytest')

        import logging
        silence = logging.WARNING
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=os.getenv('LOGLEVEL', silence))

        args = ['--verbose', 'tests', '--doctest-modules', __name__] +\
            ['-s' if logging.getLogger().getEffectiveLevel() < silence else '--capture=fd']
        if self.cov:
            args += self.cov

        errno = pytest.main(args=args)
        sys.exit(errno)

    def run(self) -> None:
        from pkg_resources import evaluate_marker

        requirements = set(self.distribution.install_requires + ['mock>=2.0.0', 'pytest-cov', 'pytest'])
        for k, v in self.distribution.extras_require.items():
            if not k.startswith(':') or evaluate_marker(k[1:]):
                requirements.update(v)

        self.distribution.fetch_build_eggs(list(requirements))
        self.run_tests()


def read(fname: str) -> str:
    with open(os.path.join(__location__, fname)) as fd:
        return fd.read()


def get_install_requirements(path: str) -> Any:
    content = open(os.path.join(__location__, path)).read()
    return [req for req in content.split("\\n") if req != ""]


def setup_package(version: str) -> None:
    cmdclass = {'flake8': SetupFlake8, 'test': SetupPyTest}

    install = []
    for r in read('requirements.txt').split('\n'):
        r = r.strip()
        if r == '':
            continue
        extra = False
        for e, deps in EXTRAS_REQUIRE.items():
            for i, v in enumerate(deps):
                if r.startswith(v):
                    deps[i] = r
                    EXTRAS_REQUIRE[e] = deps
                    extra = True
                    break
            if extra:
                break
        if not extra:
            install.append(r)

    command_options = {'test': {}}
    if COVERAGE_XML:
        command_options['test']['cov_xml'] = 'setup.py', True
    if COVERAGE_HTML:
        command_options['test']['cov_html'] = 'setup.py', True

    setup(
        name=__name__,
        version=version,
        url=__url__,
        author=__author__,
        author_email=__email__,
        license=__license__,
        classifiers=__classifiers__,
        packages=find_packages(exclude=["test", "test.*", "tests", "tests.*"]),
        package_data={__name__: ["*.json"]},
        include_package_data=True,
        install_requires=install,
        extras_require=EXTRAS_REQUIRE,
        setup_requires='flake8',
        cmdclass=cmdclass,
        command_options=command_options,
        python_requires=">=3.10",
        entry_points={"console_scripts": CONSOLE_SCRIPTS}
    )


if __name__ == "__main__":
    old_modules = sys.modules.copy()

    sys.modules.clear()
    sys.modules.update(old_modules)

    if all(map(lambda i, j: i < j, sys.version_info, (3, 10, 0))):
        raise Exception('Patroni needs to be run with Python 3.10+')

    setup_package(__version__)
