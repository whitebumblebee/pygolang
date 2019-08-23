# pygolang | pythonic package setup
# Copyright (C) 2018-2019  Nexedi SA and Contributors.
#                          Kirill Smelkov <kirr@nexedi.com>
#
# This program is free software: you can Use, Study, Modify and Redistribute
# it under the terms of the GNU General Public License version 3, or (at your
# option) any later version, as published by the Free Software Foundation.
#
# You can also Link and Combine this program with other software covered by
# the terms of any of the Free Software licenses or any of the Open Source
# Initiative approved licenses and Convey the resulting work. Corresponding
# source of such a combination shall include the source code for all other
# software used.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See COPYING file for full licensing terms.
# See https://www.nexedi.com/licensing for rationale and options.
from setuptools import setup, find_packages
from setuptools.command.install_scripts import install_scripts as _install_scripts
from setuptools.command.develop import develop as _develop
from os.path import dirname, join
import sys, re

# read file content
def readfile(path):
    with open(path, 'r') as f:
        return f.read()

# grep searches text for pattern.
# return re.Match object or raises if pattern was not found.
def grep1(pattern, text):
    rex = re.compile(pattern, re.MULTILINE)
    m = rex.search(text)
    if m is None:
        raise RuntimeError('%r not found' % pattern)
    return m

# find our version
_ = readfile(join(dirname(__file__), 'golang/__init__.py'))
_ = grep1('^__version__ = "(.*)"$', _)
version = _.group(1)

# XInstallGPython customly installs bin/gpython.
#
# console_scripts generated by setuptools do lots of imports. However we need
# gevent.monkey.patch_all() to be done first - before all other imports. We
# could use plain scripts for gpython, however even for plain scripts
# setuptools wants to inject pkg_resources import for develop install, and
# pkg_resources does import lots of modules.
#
# -> generate the script via our custom install, but keep gpython listed as
# console_scripts entry point, so that pip knows to remove the file on develop
# uninstall.
#
# NOTE in some cases (see below e.g. about bdist_wheel) we accept for gpython
# to be generated not via XInstallGPython - becuase in those cases pkg_resources
# and entry points are not used - just plain `import gpython`.
class XInstallGPython:
    gpython_installed = 0

    # NOTE cannot override write_script, because base class - _install_scripts
    # or _develop, is old-style and super does not work with it.
    #def write_script(self, script_name, script, mode="t", blockers=()):
    #    script_name, script = self.transform_script(script_name, script)
    #    super(XInstallGPython, self).write_script(script_name, script, mode, blockers)

    # transform_script transform to-be installed script to override installed gpython content.
    #
    # (script_name, script) -> (script_name, script)
    def transform_script(self, script_name, script):
        # on windows setuptools installs 3 files:
        #   gpython-script.py
        #   gpython.exe
        #   gpython.exe.manifest
        # we want to override .py only.
        #
        # for-windows build could be cross - e.g. from linux via bdist_wininst -
        # -> we can't rely on os.name. Rely on just script name.
        if script_name in ('gpython', 'gpython-script.py'):
            script  = '#!%s\n' % sys.executable
            script += '\nfrom gpython import main; main()\n'
            self.gpython_installed += 1

        return script_name, script


# install_scripts is custom scripts installer that takes gpython into account.
class install_scripts(XInstallGPython, _install_scripts):
    def write_script(self, script_name, script, mode="t", blockers=()):
        script_name, script = self.transform_script(script_name, script)
        _install_scripts.write_script(self, script_name, script, mode, blockers)

    def run(self):
        _install_scripts.run(self)
        # bdist_wheel disables generation of scripts for entry-points[1]
        # and pip/setuptools regenerate them when installing the wheel[2].
        #
        #   [1] https://github.com/pypa/wheel/commit/0d7f398b
        #   [2] https://github.com/pypa/wheel/commit/9aaa6628
        #
        # since setup.py is not included into the wheel, we cannot control
        # entry-point installation when the wheel is installed. However,
        # console script generated when installing the wheel looks like:
        #
        #   #!/path/to/python
        #   # -*- coding: utf-8 -*-
        #   import re
        #   import sys
        #
        #   from gpython import main
        #
        #   if __name__ == '__main__':
        #       sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
        #       sys.exit(main())
        #
        # which does not import pkg_resources. Since we also double-check in
        # gpython itself that pkg_resources and other modules are not imported,
        # we are ok with this.
        if not self.no_ep:
            # regular install
            assert self.gpython_installed == 1
        else:
            # bdist_wheel
            assert self.gpython_installed == 0
            assert len(self.outfiles) == 0


# develop, similarly to install_scripts, is used to handle gpython in `pip install -e` mode.
class develop(XInstallGPython, _develop):
    def write_script(self, script_name, script, mode="t", blockers=()):
        script_name, script = self.transform_script(script_name, script)
        _develop.write_script(self, script_name, script, mode, blockers)

    def install_egg_scripts(self, dist):
        _develop.install_egg_scripts(self, dist)
        assert self.gpython_installed == 1


# requirements of packages under "golang." namespace
R = {
    'cmd.pybench':      {'pytest'},
    'x.perf.benchlib':  {'numpy'},
}
# TODO generate `a.b -> a`, e.g. x.perf = join(x.perf.*); x = join(x.*)
Rall = set()
for pkg in R:
    Rall.update(R[pkg])
R['all'] = Rall

# extras_require <- R
extras_require = {}
for k in sorted(R.keys()):
    extras_require[k] = list(sorted(R[k]))


setup(
    name        = 'pygolang',
    version     = version,
    description = 'Go-like features for Python',
    long_description = '%s\n----\n\n%s' % (
                            readfile('README.rst'), readfile('CHANGELOG.rst')),
    long_description_content_type  = 'text/x-rst',
    url         = 'https://lab.nexedi.com/kirr/pygolang',
    license     = 'GPLv3+ with wide exception for Open-Source',
    author      = 'Kirill Smelkov',
    author_email= 'kirr@nexedi.com',

    keywords    = 'golang go channel goroutine concurrency GOPATH python import gpython gevent',

    packages    = find_packages(),
    include_package_data = True,

    install_requires = ['gevent', 'six', 'decorator'],
    extras_require   = extras_require,

    entry_points= {'console_scripts': [
                        # NOTE gpython is handled specially - see XInstallGPython.
                        'gpython  = gpython:main',

                        'py.bench = golang.cmd.pybench:main',
                      ]
                  },

    cmdclass    = {
        'install_scripts':  install_scripts,
        'develop':          develop,
    },

    classifiers = [_.strip() for _ in """\
        Development Status :: 3 - Alpha
        Intended Audience :: Developers
        Programming Language :: Python :: 2
        Programming Language :: Python :: 2.7
        Programming Language :: Python :: 3
        Programming Language :: Python :: 3.5
        Programming Language :: Python :: 3.6
        Programming Language :: Python :: 3.7
        Programming Language :: Python :: Implementation :: CPython
        Programming Language :: Python :: Implementation :: PyPy
        Topic :: Software Development :: Interpreters
        Topic :: Software Development :: Libraries :: Python Modules\
    """.splitlines()]
)
