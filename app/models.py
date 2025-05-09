from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import inspect

db = SQLAlchemy()

def init_models(app):
    with app.app_context():
        # Reflect states.db (primary database)
        StatesBase = automap_base()
        StatesBase.prepare(db.engine, reflect=True)
        
        # Reflect past_results.db
        PastResultsBase = automap_base()
        PastResultsBase.prepare(db.get_engine(bind='past_results'), reflect=True)
        
        # Combine models
        models = {}
        models.update({f"state_{cls.__name__.lower()}": cls for cls in StatesBase.classes})
        models.update({f"past_{cls.__name__.lower()}": cls for cls in PastResultsBase.classes})
        
        #print(f"Loaded models: {list(models.keys())}")
        return models