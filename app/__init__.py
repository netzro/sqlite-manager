from flask import Flask, render_template, send_file, Response
from flask_admin import Admin
from .config import Config
from .models import db, init_models
from .views import CustomModelView
from sqlalchemy import inspect
from sqlalchemy.orm import scoped_session, sessionmaker
import os
from pathlib import Path
import sqlite3

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)
    
    # Check if any databases are configured
    if not app.config['SQLALCHEMY_BINDS'] and not app.config['SQLALCHEMY_DATABASE_URI']:
        @app.route('/')
        def home():
            return render_template('home.html', error="No SQLite databases found in /data directory.")
        @app.route('/check-db')
        def check_db():
            return render_template('db_check.html', db_info=[], error="No SQLite databases found in /data directory.")
        return app
    
    # Initialize database
    db.init_app(app)
    models = init_models(app)
    
    # Setup admin interface
    admin = Admin(app, name='Lotto Manager', template_mode='bootstrap4')
    
    with app.app_context():
        bind_keys = app.config['SQLALCHEMY_BINDS'].keys()
        
        for bind_key in bind_keys:
            engine = db.get_engine(bind=bind_key)
            session = scoped_session(sessionmaker(bind=engine))
            tables = inspect(engine).get_table_names()
            
            for table in tables:
                model_key = f"{bind_key}_{table.lower()}"
                if model_key in models:
                    admin.add_view(CustomModelView(
                        models[model_key],
                        session,
                        name=f"{table}",
                        category=bind_key.capitalize(),
                        endpoint=f"{bind_key}_{table.lower()}"
                    ))
                    print(f"Added table: {table} from {bind_key}")
    
    # Basic home route
    @app.route('/')
    def home():
        return render_template('home.html')
    
    # Database verification route
    @app.route('/check-db')
    def check_db():
        with app.app_context():
            try:
                db_info = []
                bind_keys = app.config['SQLALCHEMY_BINDS'].keys()
                for bind_key in bind_keys:
                    engine = db.get_engine(bind=bind_key)
                    tables = inspect(engine).get_table_names()
                    db_info.append({'name': bind_key, 'tables': tables})
                return render_template('db_check.html', db_info=db_info)
            except Exception as e:
                return render_template('db_check.html', db_info=[], error=str(e))
    
    # Database dump route
    @app.route('/dump-db/<bind_key>')
    def dump_db(bind_key):
        with app.app_context():
            if bind_key not in app.config['SQLALCHEMY_BINDS']:
                return f"Database {bind_key} not found", 404
            
            db_uri = app.config['SQLALCHEMY_BINDS'][bind_key]
            db_path = db_uri.replace('sqlite:///', '')
            
            try:
                # Connect to SQLite database
                conn = sqlite3.connect(db_path)
                # Generate SQL dump
                dump = '\n'.join(line for line in conn.iterdump())
                conn.close()
                
                # Return as downloadable file
                return Response(
                    dump,
                    mimetype='text/plain',
                    headers={'Content-Disposition': f'attachment; filename={bind_key}.sql'}
                )
            except Exception as e:
                return f"Error dumping database {bind_key}: {str(e)}", 500
    
    return app