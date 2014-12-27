'''
textvxpatcher
*************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

A temporary file for development with the VX patcher.
'''
from librpgmakertrans.controllers.coreprotocol import CoreRunner
from librpgmakertrans.controllers.headlessvx import HeadlessVX

runner = CoreRunner()
tester = runner.initialise(HeadlessVX)
tester.go('/home/habisain/LiliumUnion', '/tmp/LiliumUnionPatch', '/tmp/LiliumUnion', False, 3)
runner.run()