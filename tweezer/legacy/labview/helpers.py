#!/usr/bin/env python
#-*- coding: utf-8 -*-


class Settings(object):
    """Settings or configuration data for various parts of the app """
    def __init__(self, cluster, file_path):
        self.cluster = cluster
        self.file_path = None

    def get_settings_file_path(self):
        pass

    def load_settings_from_json(self, file_path):
        pass

    def save_settings_to_json(self, file_path):
        pass

    def display_settings_dialog(self):
        pass
