import oslo_messaging as om
import conf
import config
from app.models import Url
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


CONF = conf.CONF
transport = om.get_transport(CONF)
target = om.Target(topic='shortener', server="10.164.178.141")
engine = create_engine(config.SQLALCHEMY_DATABASE_URI, echo=True)


class InteractDB(object):

    def __init__(self):
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()

    def insert_database(self, cctx, record):
        rc = Url(org_link=record['org_link'],
                 short_link=record['short_link'])
        try:
            self.session.add(rc)
            self.session.commit()
        except Exception as e:
            raise e

    def query_database(self, cctx, short_link):
        origin_link = self.session.query(Url).filter(
            Url.short_link == short_link).one()
        return {
            'org_link': origin_link.org_link
        }


def main():
    endpoints = [InteractDB(), ]
    server_rpc = om.get_rpc_server(transport, target,
                                   endpoints, executor='blocking')
    server_rpc.start()
    server_rpc.wait()
