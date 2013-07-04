#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os

def get_subdirs(path, is_file=True):
    """
    Splits a path into its subdirectories and returns a list of those

    :param path: file path
    :param is_file: (Boolean) defaults to True for a complete file_name

    :return subdirs: List of subdirectories that make up a path
    """
    if is_file:
        _path = os.path.dirname(path)
    else:
        _path = path

    subdirs = []
    while True:
        _path, folder = os.path.split(_path)

        if folder!="":
            subdirs.append(folder)
        else:
            if _path!="":
                subdirs.append(_path)
            break

    subdirs.reverse()

    return subdirs


def get_parent_directory(file_name):
    """
    Extracts the parent directory of a file from an absolute path

    :param file_name: (Path)

    :return parent_dir: (String) name of parent directory
    """
    return get_subdirs(file_name)[-1]


def generate_file_tree_of(directory):
    """
    Generator for all files contained in a directory
    
    :param directory: (path) root directory
    """
    for paths, dirs, files in os.walk(directory):
        for f in files:
            yield os.path.abspath(os.path.join(paths, f))
    

