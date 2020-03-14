import yaml
from pathlib import Path


def load_yml_conf(conf_file, profile):
    # Default configure file
    if not conf_file:
        conf_file = str(Path.home()) + "/ws/.secrets/appflows.yml"

    with open(conf_file, "r") as data:
        whole = yaml.load(data, Loader=yaml.FullLoader)
        config = whole["config"]
        return config[profile]
