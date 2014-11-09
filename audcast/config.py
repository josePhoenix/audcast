from ConfigParser import RawConfigParser, NoSectionError
import os.path

class Configuration(object):
    """
    Configuration wraps the stdlib ConfigParser to allow dict-like
    access, and includes a class-level attribute LOCATIONS
    specifying where to search for the audcast config file.
    """
    LOCATIONS = (
        './audcast.cfg',
        '/usr/local/etc/audcast.cfg'
    )

    def _find_config_file(self, config_file):
        if config_file is not None:
            return config_file
        for path in self.LOCATIONS:
            if os.path.exists(path):
                return path
        raise RuntimeError("Couldn't find a config file,"
                           "tried {}".format(self.LOCATIONS))
    def __init__(self, config_file=None):
        self.config_file = self._find_config_file(config_file)
        self.config = RawConfigParser()
        self.config.read(self.config_file)
    def __getitem__(self, key):
        section, key = key.split('.', 1)
        return self.config.get(section, key)
    def __setitem__(self, key, value):
        section, key = key.split('.', 1)
        try:
            self.config.set(section, key, value)
        except NoSectionError:
            self.config.add_section(section)
            self.config.set(section, key, value)
    def write(self):
        with open(self.config_file, 'w') as f:
            self.config.write(f)

settings = Configuration()

import logging
_log_levels = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}
_log_level = settings['log.level'].upper()
logging.basicConfig(level=_log_level)

if __name__ == '__main__':
    conf = Configuration('./audcast.cfg')
    conf['database.path'] = '/Users/josephoenix/dev/audcast/audcast.sqlite3'
    conf['speech.helper'] = 'say'
    conf.write()