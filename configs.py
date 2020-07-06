class BaseConfig(object):
    TEMP_FOLDER = 'tmp_data/'
    OUTPUT_FOLDER = 'out/'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///hidden_faces.db'

class ProductionConfig(BaseConfig):
    pass 