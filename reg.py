#! /usr/bin/python

import re

targ  = "the 1337 brown 420 jumped over the lazy dog"
search = re.search(r".*([0-9]*).*", targ)
