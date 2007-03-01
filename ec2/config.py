#
# Copyright (c) 2007 rPath, Inc.
#

class config:
    def __init__(self, file):
        for line in open(file):
            line = line.strip()
            if line.startswith('#') or line == '':
                continue
            lst = line.split()
            key = lst[0]
            if len(lst) == 2:
                val = lst[1]
            elif len(lst) == 1:
                val = ''
            else:
                val = ' '.join(lst[1:])
            if key not in self.__dict__:
                self.__dict__[key] = val
