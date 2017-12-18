#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
"""
Check if a test page is accessible
"""
import sys
import json

def check():
    '''Check access'''
    print "Content-Type: application/json charset=utf-8"
    print ""
    print json.dumps({"connection": "successful"})


if __name__ == '__main__':
    check()
