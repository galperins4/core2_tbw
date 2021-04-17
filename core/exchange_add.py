from config.config import Config
from util.sql import SnekDB

if __name__ == '__main__':

    # get config data
    data = Config()
    snekdb = SnekDB(data.database_user, data.network, data.delegate)
    snekdb.setup()
