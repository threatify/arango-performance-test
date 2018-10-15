"""Graph database client."""

from arango import ArangoClient
from arango_orm import Database, ConnectionPool


class Connection(object):
    """Code for accessing arangodb and utility functions."""

    def connect(self, host,  # pylint: disable=R0913
                port, username, password, dbname):

        client = ArangoClient(protocol='http', host=host, port=port)
        _db = client.db(dbname, username=username, password=password)

        self.db = Database(_db)

    def cluster_connect(self, hosts,  # pylint: disable=R0913
                        port, username, password, dbname):
        """Connect to a cluster using connection pooler."""
        clients = []
        for host in hosts:
            clients.append(ArangoClient(protocol='http', host=host, port=port))

        self.db = ConnectionPool(clients, dbname, username, password)

    def create_all(self, db_objects):
        self.db.create_all(db_objects)
