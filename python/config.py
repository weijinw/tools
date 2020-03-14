import yaml


def load_yml_conf(conf_file, profile):
    with open(conf_file, "r") as data:
        whole = yaml.load(data, Loader=yaml.FullLoader)
        config = whole["config"]
        return config[profile]
