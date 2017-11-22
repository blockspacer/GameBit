# Copyright (c) 2013 The GameBit Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
from distutils.core import setup
setup(name='sysspendfrom',
      version='1.0',
      description='Command-line utility for GameBit "coin control"',
      author='Gavin Andresen',
      author_email='gavin@GameBitfoundation.org',
      requires=['jsonrpc'],
      scripts=['spendfrom.py'],
      )
