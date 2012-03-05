# Copyright (C) 2011,2012 Colin Walters <walters@verbum.org>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

# ostbuild-compile-one-make wraps systems that implement the GNOME build API:
# http://people.gnome.org/~walters/docs/build-api.txt

import os,sys,stat,subprocess,tempfile,re,shutil
import argparse
from StringIO import StringIO
import json

from . import builtins
from .ostbuildlog import log, fatal
from .subprocess_helpers import run_sync, run_sync_get_output
from . import buildutil

class OstbuildStatus(builtins.Builtin):
    name = "status"
    short_description = "Show build status"

    def __init__(self):
        builtins.Builtin.__init__(self)

    def execute(self, argv):
        parser = argparse.ArgumentParser(description=self.short_description)
        parser.add_argument('--manifest', required=True)

        args = parser.parse_args(argv)

        self.parse_config()
        self.manifest = json.load(open(args.manifest))

        for component in self.manifest['components']:
            branch = buildutil.manifest_buildname(self.manifest, component)
            build_revision = run_sync_get_output(['ostree', '--repo=' + self.repo,
                                                  'show',
                                                  '--print-metadata-key=ostbuild-artifact-version',
                                                  branch],
                                                 none_on_error=True)
            if build_revision is None:
                build_revision = '(not built)'
            if build_revision != component['revision']:
                build_status = '(needs build)'
            else:
                build_status = 'ok'
            sys.stdout.write('{:<40} {:<95} {:<10}\n'.format(component['name'],
                                                             build_revision, build_status))
    
builtins.register(OstbuildStatus)
