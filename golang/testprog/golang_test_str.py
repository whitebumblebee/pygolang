#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2022  Nexedi SA and Contributors.
#                     Kirill Smelkov <kirr@nexedi.com>
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
"""This program helps to verify _pystr and _pyunicode.

It complements golang_test.test_strings.
"""

from __future__ import print_function, absolute_import

from golang import b, u
from golang.gcompat import qq

def main():
    sb = b("привет b")
    su = u("привет u")
    print("print(qq(b)):", qq(sb))
    print("print(qq(u)):", qq(su))


if __name__ == '__main__':
    main()
