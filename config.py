import configparser

config = configparser.ConfigParser()

config["PORT"] = {
    'device1': "8030",
    'device2': '8040'
}

config.read('config.ini')


def read_config(section, option):
    val = config.get(section, option)
    return val
