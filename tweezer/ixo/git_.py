#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import shutil

import envoy
from tempfile import mkdtemp


def get_latest_file_from_git_repo(file_name, repo_name='tweezer', 
    host='bitbucket', user='majahn', saving_directory=os.getcwd()):
    """
    Retrieve one file from a remote git repository
    
    :param file_name: (path) file to retrieve from the repo_name

    :param repo_name: (url) of the git repo

    :param saving_directory: (path) where the file should be saved to; default is the current directory
    """
    DIR = os.getcwd()

    # create tempdir and change into it
    temp_dir = mkdtemp()
    os.chdir(temp_dir)

    if 'bitbucket' in host:
        repo_address = 'git@bitbucket.org:{}/{}.git'.format(user, repo_name)
    elif 'github' in host:
        repo_address = 'gitgit@github.com:{}/{}.git'.format(user, repo_name)
    else:
        repo_address = '{}{}/{}.git'.format(host, user, repo_name)

    # clone repo and get file 
    clone = envoy.run('git clone -n {} --depth 1'.format(repo_address))

    if not clone.status_code:
        os.chdir(repo_name)
        checkout_call = envoy.run('git checkout HEAD {}'.format(file_name))
        if not checkout_call.status_code:
            src = os.path.join(os.getcwd(), file_name)
            dst = os.path.join(saving_directory, os.path.basename(file_name))
            try:
                shutil.copy2(src, dst)
            except:
                raise StandardError('Copying {} to {} did not work...'.format(src, dst))
        else:
            raise StandardError('Checking out {} from {} did not work...'.format(file_name, repo_address)) 
    else:
        raise StandardError('Cloning of {} did not work...'.format(repo_address))

    # clean up
    os.chdir(DIR)
    
    # remove temp_dir
    shutil.rmtree(temp_dir)
