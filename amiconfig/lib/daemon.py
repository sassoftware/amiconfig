#
# Copyright (c) SAS Institute Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import os
import sys
import time

class Daemon(object):
    def start(self):
        """ Stub for subclasses to implement. """
        pass

    def daemonize(self):
        pid = os.fork()
        if pid == 0:
            null = os.open(os.devnull, os.O_RDONLY)
            os.dup2(null, sys.stdin.fileno())
            os.close(null)

            pid = os.fork()
            if pid == 0:
                os.setsid()
                sys.stdout.flush()
                sys.stderr.flush()

                self.start()
            else:
                time.sleep(1)
                timeSlept = 1
                while timeSlept < 60:
                    foundPid, status = os.waitpid(pid, os.WNOHANG)
                    if foundPid:
                        os._exit(0)
                    else:
                        time.sleep(.5)
                        timeSlept += .5
                os._exit(1)
        else:
            time.sleep(2)
            pid, status = os.waitpid(pid, 0)
            if os.WIFEXITED(status):
                rc = os.WEXITSTATUS(status)
                return rc
            else:
                print 'process killed with signal %s' % os.WTERMSIG(status)
                return 1
