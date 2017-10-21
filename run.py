# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from app import run_app
from sys import exit, exc_info, argv

try:
    run_app(argv)
except Exception:
    print(exc_info()[1])
    print('Error runtime: please, help us improve by reporting to us on :')
    print("\n\thttps://chrome-cut.github.io/")
    exit(0)
