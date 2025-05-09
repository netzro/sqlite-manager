from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask import Response
import csv
import io
from . import db

class CustomModelView(ModelView):
    can_export = True
    export_types = ['csv']
    column_exclude_list = ['id']  # Hide ID column by default
    page_size = 20  # Pagination for mobile
    can_view_details = True
    column_display_pk = True
    
class QueryView(BaseView):
    def __init__(self, app):
        super().__init__('SQL Query', endpoint='query', category='Tools')
        self.app = app

    @expose('/', methods=['GET', 'POST'])
    def index(self):
        from flask import request, render_template
        databases = ['results'] + list(self.app.config['SQLALCHEMY_BINDS'].keys())
        result = None
        error = None
        query = ''
        
        if request.method == 'POST':
            db_name = request.form.get('db_name')
            query = request.form.get('query', '').strip()
            export = request.form.get('export')

            try:
                engine = db.get_engine(self.app, db_name if db_name != 'results' else None)
                with engine.connect() as conn:
                    result_set = conn.execute(query).fetchall()
                    columns = result_set[0].keys() if result_set else []
                    result = [dict(zip(columns, row)) for row in result_set]

                if export:
                    output = io.StringIO()
                    writer = csv.DictWriter(output, fieldnames=columns)
                    writer.writeheader()
                    for row in result:
                        writer.writerow(row)
                    return Response(
                        output.getvalue(),
                        mimetype='text/csv',
                        headers={'Content-Disposition': 'attachment;filename=query_result.csv'}
                    )
            except Exception as e:
                error = str(e)

        return self.render('admin/query.html', databases=databases, result=result, error=error, query=query)