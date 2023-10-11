from clickhouse_driver import Client

class ClickHouseConnection:
    connection = None

    def get_connection(connection_name='clickhouse'):
        if ClickHouseConnection.connection:
            return connection
        db_props = BaseHook.get_connection(connection_name)
        ClickHouseConnection.connection = Client(db_props.host)
        return ClickHouseConnection.connection