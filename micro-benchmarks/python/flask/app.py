import flask
from flask_sqlalchemy import SQLAlchemy
import random
from sqlalchemy.sql.expression import func
import os


app = flask.Flask(__name__)

ELASTIC_APM_ENABLED = os.getenv("ELASTIC_APM_ENABLED", "False")

if ELASTIC_APM_ENABLED == "True" or ELASTIC_APM_ENABLED == "true":
    from elasticapm.contrib.flask import ElasticAPM
    apm = ElasticAPM(app)


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PWD = os.getenv("DB_PWD", "postgres")
DB_NAME = os.getenv("DB_NAME", "world")

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{}:{}@{}/{}'.format(DB_USER, DB_PWD, DB_HOST, DB_NAME)
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
        return {'id': self.id, 'randomNumber': self.randomNumber}


@app.route('/json')
def json_serialization():
    return flask.jsonify({"message": "Hello, World!"})


@app.route("/db")
def single_db_query():
    print(app.config['SQLALCHEMY_DATABASE_URI'])
    random_id = random.randint(1, 10000)
    world = World.query.get(random_id)

    return flask.jsonify(world.serialize())


@app.route("/queries")
def multiple_db_queries():
    query_count_str = flask.request.args.get('queries', 1)

    try:
        query_count = max(min(int(query_count_str), 500), 1)
    except ValueError:
        query_count = 1

    worlds = [World.query.order_by(func.random()).first().serialize() for _ in range(query_count)]

    return flask.jsonify(worlds)


@app.route("/plaintext")
def plain_text():
    response_text = "Hello, World!"
    response = flask.Response(response_text)
    response.headers['Content-Type'] = 'text/plain'
    return response


@app.route('/updates', methods=['GET'])
def updates():
    query_count = flask.request.args.get('queries', 1, type=int)
    query_count = min(max(query_count, 1), 500)  # Query count should be between 1 and 500

    worlds = []
    for _ in range(query_count):
        # Select a random object
        random_id = random.randint(1, 10000)
        world = World.query.filter_by(id=random_id).first()

        # Update the random number of the World object
        world.randomNumber = random.randint(1, 10000)
        worlds.append(world.to_dict())

    db.session.commit()

    return flask.jsonify(worlds)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
