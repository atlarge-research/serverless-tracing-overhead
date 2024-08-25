from flask import Flask, jsonify, request, Response, current_app
from flask_sqlalchemy import SQLAlchemy
import random
from sqlalchemy.sql.expression import func
import os
from cprofiler import profile_route

from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter

def configure_opentelemetry(app, db):
    """
    Configure OpenTelemetry for the Flask application and SQLAlchemy.
    """
    with app.app_context():  # Ensure the application context is active
        # Set up OpenTelemetry Tracer
        trace.set_tracer_provider(TracerProvider())
        tracer = trace.get_tracer(__name__)

        # Set up the span processor and exporter
        span_processor = SimpleSpanProcessor(ConsoleSpanExporter())
        trace.get_tracer_provider().add_span_processor(span_processor)

        # Instrument the Flask app with OpenTelemetry
        FlaskInstrumentor().instrument_app(app)

        # Instrument SQLAlchemy with OpenTelemetry
        SQLAlchemyInstrumentor().instrument(engine=db.engine)

        return tracer

def create_app(profiling_data):
    app = Flask(__name__)

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PWD = os.getenv("DB_PWD", "postgres")
    DB_NAME = os.getenv("DB_NAME", "world")

    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PWD}@{DB_HOST}/{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db = SQLAlchemy(app)

    class World(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        randomnumber = db.Column(db.Integer)

        def serialize(self):
            return {
                "id": self.id,
                "randomNumber": self.randomnumber
            }

        def to_dict(self):
            return {'id': self.id, 'randomNumber': self.randomnumber}

    @app.route('/json')
    def json_serialization():
        return jsonify({"message": "Hello, World!"})

    @app.route("/db")
    def single_db_query():
        random_id = random.randint(1, 10000)
        world = World.query.get(random_id)
        return jsonify(world.serialize())

    @app.route("/queries")
    def multiple_db_queries():
        query_count_str = request.args.get('queries', 1)
        try:
            query_count = max(min(int(query_count_str), 500), 1)
        except ValueError:
            query_count = 1

        worlds = [World.query.order_by(func.random()).first().serialize() for _ in range(query_count)]
        return jsonify(worlds)

    @app.route("/plaintext")
    def plain_text():
        response_text = "Hello, World!"
        response = Response(response_text)
        response.headers['Content-Type'] = 'text/plain'
        return response

    @app.route('/updates', methods=['GET'])
    @profile_route(profiling_data, "updates")
    def updates():
        tracer = trace.get_tracer(__name__)
        query_count = request.args.get('queries', 1, type=int)
        query_count = min(max(query_count, 1), 500)

        worlds = []
        # span = tracer.start_span("updates-endpoint")
        span = start_span_custom(tracer, "updates-endpoint")

        span.set_attribute("query_count", query_count)

        for _ in range(query_count):
            random_id = random.randint(1, 10000)

            # Instrument the database query
            query_span = tracer.start_span("db-query")
            world = World.query.filter_by(id=random_id).first()
            query_span.set_attribute("random_id", random_id)

            update_span = tracer.start_span("db-update")
            world.randomNumber = random.randint(1, 10000)
            worlds.append(world.to_dict())
            update_span.set_attribute("new_random_number", world.randomNumber)

        db.session.commit()

        return jsonify(worlds)

    return app, db

def start_span_custom(tracer, name):
    return tracer.start_span(name)

if __name__ == "__main__":
    profiling_data = []  # Just for standalone testing
    app, db = create_app(profiling_data)
    configure_opentelemetry(app, db)
    app.run(host="0.0.0.0", port=8080, debug=True)
