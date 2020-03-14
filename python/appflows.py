from gql import gql, Client
import json
import requests
from gql.transport.requests import RequestsHTTPTransport

import config


def load_gql_query(gql_name):
    with open("./gql/{}".format(gql_name)) as f:
        return gql(f.read())


def create_gql_client(config):
    resp = requests.post(
        "{}/api/session".format(config["url"]),
        headers={"Content-type": "application/json"},
        data=json.dumps({
            "username": config["username"],
            "password": config["password"]
        }))
    token = resp.json()["access_token"]

    _transport = RequestsHTTPTransport(
        url='{}/api/graphql'.format(config["url"]),
        use_json=True,
        headers={"authorization": "Bearer {}".format(token)}
    )
    return Client(
        transport=_transport,
        fetch_schema_from_transport=True,
    )


if __name__ == "__main__":
    conf = config.load_yml_conf('', 'dev-066')
    client = create_gql_client(conf)

    query = '''
query{
    blueprintConnection {
        count
        edges {
            node {
                id
                name
            }
        }
    }
}
'''
    res = client.execute(gql(query))
    blueprints = res["blueprintConnection"]["edges"]
    for bp_node in blueprints:
        bp = bp_node["node"]
        print("{} {}".format(bp["id"], bp["name"]))
