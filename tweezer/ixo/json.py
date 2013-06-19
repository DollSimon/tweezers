#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import re

try:
    import simplejson as json
except:
    import json

def parse_json(file_name):
    """ 
    Parse a JSON file
    First remove comments and then use the json module package
    Comments look like :
        // ...
    or
        /*
        ...
        */

    :param file_name: (path) to json file

    :return content: (dict)
    """
    # Regular expression for comments
    comment_re = re.compile(
        '(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
        re.DOTALL | re.MULTILINE
    )
    with open(file_name) as f:
        content = ''.join(f.readlines())

        ## Looking for comments
        match = comment_re.search(content)
        while match:
            # single line comment
            content = content[:match.start()] + content[match.end():]
            match = comment_re.search(content)

        # Return json file
        return json.loads(content)
