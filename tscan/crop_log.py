import subprocess
import datetime
import sqlalchemy as sa
import sqlalchemy.ext.declarative as sdec
import sqlalchemy.orm as sorm

Base = sdec.declarative_base()
Session = sorm.sessionmaker()

class SRegion(Base):
    __tablename__ = 'crop_regions'
    id = sa.Column(sa.Integer, primary_key=True)
    start_y = sa.Column(sa.Integer) # not DRY
    start_x = sa.Column(sa.Integer) # fewer joins
    stop_y = sa.Column(sa.Integer)
    stop_x = sa.Column(sa.Integer)

class SSample(Base):
    __tablename__ = 'samples'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    reference_crop_id = sa.Column(sa.Integer, sa.ForeignKey('crop_regions.id'))
    reference_crop = sorm.relationship("SRegion", uselist=False)  

class SCropLog(Base):
    __tablename__ = 'crop_logs'
    id = sa.Column(sa.Integer, primary_key=True)
    commit = sa.Column(sa.String(24), unique=True)
    date = sa.Column(sa.DateTime)
    method = sa.Column(sa.String(16))
    sample_id = sa.Column(sa.Integer, sa.ForeignKey('samples.id'))
    sample = sorm.relationship("SSample", uselist=False)
    generated_id = sa.Column(sa.Integer, sa.ForeignKey('crop_regions.id'))
    generated = sorm.relationship("SRegion", uselist=False)
    mean_distance = sa.Column(sa.Float) # violates normal form, but useful

class SQLog(object):
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
        sample = self.session.query(SSample).filter(SSample.name == meta.basename).first()
        if sample:
            return sample
        else:
            sample = SSample(name=meta.basename)
            self.session.add(sample)
            return sample
    
    def dump(self, method, generated, sample):
        SCropLog(
            commit=subprocess.check_output('git describe --tags'.split()).strip(),
            date=datetime.datetime.utcnow(),
            method=method,
            generated=self.dump_region(generated),
            reference=self.dump_sample(sample))

default = SQLog()
