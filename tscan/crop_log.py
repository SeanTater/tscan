# TODO: Maybe we shouldn't require this - fallback to a dummy maybe?
import tables
import subprocess
import time
import sqlite3
import os
import sqlalchemy as sa
import sqlalchemy.ext.declarative as sdec
import sqlalchemy.orm as sorm

'''
class H5Point(tables.IsDescription):
    y = tables.IntCol()
    x = tables.IntCol()

class H5Region(tables.IsDescription):
    start = H5Point()
    stop = H5Point()

class H5Record(tables.IsDescription):
    commit = tables.StringCol(24)
    date = tables.TimeCol()
    method = tables.StringCol(16)
    generated = H5Region()
    reference = H5Region()
    mean_distance = tables.FloatCol()
    
class H5(object):   
    def __init__(self):
        self.engine = tables.openFile("tscan_perf.h5", mode="a", title="tscan performance")
        print H5Record
        
        # Create or use existing group
        if not hasattr(self.engine.root, 'crop'):
            self.engine.createGroup("/", "crop", "Crop performance")
            self.engine.createTable("/crop", "log", H5Record, "Crop unit test log")

        self.log = self.engine.root.crop.log
    
    def __del__(self):
        self.engine.close()
    
    def dump_point(self, point):
        p = H5Point(
            y = point.y,
            x = point.x
        )
        return p
    
    def dump_region(self, region):
        r = H5Region()
        r['start'] = self.dump_point(region.start)
        r['stop'] = self.dump_point(region.stop)
        return r

    def dump(self, method, generated, reference):
        r = self.log.row
        r['commit'] = subprocess.check_output('git describe --tags'.split()).strip()
        r['date'] = time.time()
        r['method'] = method
        r['generated'] = self.dump_region(generated)
        r['reference'] = self.dump_region(reference)
        r['mean_distance'] = generated.mean_distance(reference)
        self.log.append(r)
'''
Base = sdec.declarative_base()
Session = sorm.sessionmaker()

class SRegion(Base):
    __tablename__ = 'crop_regions'
    id = sa.Column(sa.Integer, primary_key=True)
    crop_log = sa.Column(sa.Integer, sa.ForeignKey('crop_logs.id'))
    start_y = sa.Column(sa.Integer) # not DRY
    start_x = sa.Column(sa.Integer) # fewer joins
    stop_y = sa.Column(sa.Integer)
    stop_x = sa.Column(sa.Integer)

class SSample(Base):
    __tablename__ = 'samples'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    crop_logs = sorm.relationship("SCropLog")    

class SCropLog(Base):
    __tablename__ = 'crop_logs'
    id = sa.Column(sa.Integer, primary_key=True)
    commit = sa.Column(sa.String(24), unique=True)
    date = sa.Column(sa.DateTime)
    method = sa.Column(sa.String(16))
    sample_id = sa.Column(sa.Integer, sa.ForeignKey('samples.id'))
    generated = sorm.relationship("SRegion")
    mean_distance = sa.Column(sa.Float) # violates normal form; but useful

class SQA(object):
    def __init__(self):
        self.engine = sa.create_engine("sqlite:///tscan_perf.sqlite3")
        SSample.metadata.create_all(self.engine)
        SCropLog.metadata.create_all(self.engine)
        SRegion.metadata.create_all(self.engine)
        Session.configure(bind=self.engine)
        self.session = Session()
    
    def dump_region(self, region):
        sr = SRegion(
            start_y = region.start.y,
            start_x = region.start.x,
            stop_y = region.stop.y,
            stop_x = region.stop.x)
        self.session.add(sr)
        return sr
    
    def dump_sample(self, meta):
        # We know this is a SampleImageMeta so we can use basename
        q = session.query(SSample).filter(SSample.name == meta.basename)
        
        ss = SSample(name=meta.basename)
        self.session.add(ss)
        return ss
    
    def dump(self, method, generated, reference):
        SCropLog(
            commit=subprocess.check_output('git describe --tags'.split()).strip(),
            date=datetime.datetime.utcnow(),
            method=method,
            generated=self.dump_region(generated),
            reference=None)

default = SQA()