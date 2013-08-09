#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os

def get_subdirs(directory):
    """
    Returns a list of directories contained in the parent directory

    :param directory: (path)

    :return subdirs: (list) of directories
    """
    try:
        dirs = [d[0] for d in os.walk(directory)]
    except TypeError:
        print("You need to provide a directory path as a string, not {}".format(directory))

    subdirs = [d for d in dirs if d != directory]

    return subdirs


def get_new_subdirs(old_directory_list, new_directory_list):
    """
    Gets new directories by comparing old and new stage of this directory.
    This assumes that there are new directories added and none deleted from the the old ones.
     
    :param old_directory_list: (list) of directory at an earlier stage
    :param new_directory_list: (list) of directory at a later stage
    """
    return list(set(new_directory_list) - set(old_directory_list))


def split_path(path, is_file=True):
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
    return split_path(file_name)[-1]


def generate_file_tree_of(directory):
    """
    Generator for all files contained in a directory
    
    :param directory: (path) root directory
    """
    for paths, dirs, files in os.walk(directory):
        for f in files:
            yield os.path.abspath(os.path.join(paths, f))
    

