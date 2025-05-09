from flask import Flask, render_template
from flask_admin import Admin
from .config import Config
from .models import db, init_models
from .views import CustomModelView
from sqlalchemy import inspect
from sqlalchemy.orm import scoped_session, sessionmaker

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)
    
    # Initialize database
    db.init_app(app)
    models = init_models(app)
    
    # Setup admin interface
    admin = Admin(app, name='Lotto Manager', template_mode='bootstrap4')
    
    with app.app_context():
        # Create a separate session for past_results.db
        past_engine = db.get_engine(bind='past_results')
        past_session = scoped_session(sessionmaker(bind=past_engine))
        
        # Add states tables
        states_tables = inspect(db.engine).get_table_names()
        for table in states_tables:
            model_key = f"state_{table.lower()}"
            if model_key in models:
                admin.add_view(CustomModelView(
                    models[model_key], 
                    db.session, 
                    name=f"{table}",
                    category="States",
                    endpoint=f"state_{table.lower()}"
                ))
                print(f"Added State table: {table}")
        
        # Add past results tables
        past_tables = inspect(past_engine).get_table_names()
        for table in past_tables:
            model_key = f"past_{table.lower()}"
            if model_key in models:
                admin.add_view(CustomModelView(
                    models[model_key],
                    past_session,  # Use separate session
                    name=f"{table}",
                    category="Past Results",
                    endpoint=f"past_{table.lower()}"
                ))
                print(f"Added Past Results table: {table}")
    
    # Basic home route
    @app.route('/')
    def home():
        return render_template('home.html')
    
    # Database verification route
    @app.route('/check-db')
    def check_db():
        with app.app_context():
            output = []
            try:
                states_tables = inspect(db.engine).get_table_names()
                output.append(f"States.db tables: {states_tables}")
                past_engine = db.get_engine(bind='past_results')
                past_tables = inspect(past_engine).get_table_names()
                output.append(f"PastResults.db tables: {past_tables}")
                return '<br>'.join(output)
            except Exception as e:
                return f"Database check failed: {str(e)}"
    
    return app