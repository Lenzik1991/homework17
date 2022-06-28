# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy

from models import *
from schemas import movie_schema, movies_schema, director_schema, directors_schema, genre_schema, genres_schema

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['JSON_AS_ASCII'] = False
app.config['RESTX_JSON'] = { 'ensure_ascii': False, 'indent': 3}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


@movie_ns.route("/")
class MovieView(Resource):

    def get(self):
        movie_with_genre_and_director = db.session.query(
            Movie.id, Movie.title, Movie.description, Movie.rating, Movie.trailer,
            Genre.name.label('genre'), Director.name.label('director')).join(Genre).join(Director)
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        if director_id:
            movie_with_genre_and_director = movie_with_genre_and_director.filter(Movie.director_id == director_id)
        if genre_id:
            movie_with_genre_and_director = movie_with_genre_and_director.filter(Movie.genre_id == genre_id)

        movies_list = movie_with_genre_and_director.all()

        return movies_schema.dump(movies_list), 200

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return f" Новый объект c id {new_movie.id} создан", 201


@movie_ns.route("/<int:movie_id>")
class MovieView(Resource):

    def get(self, movie_id: int):
        movie = db.session.query(
            Movie.id, Movie.title, Movie.description, Movie.rating, Movie.trailer,
            Genre.name.label('genre'), Director.name.label('director')).join(Genre).join(Director).filter(
            Movie.id == movie_id).first()
        if movie:
            return movie_schema.dump(movie)
        return "Нет такого фильма", 404

    def patch(self, movie_id: int):
        movie = db.session.query(Movie).get(movie_id)
        if not movie:
            return "Нет такого фильма", 404

        req_json = request.json
        if 'title' in req_json:
            movie.title = req_json['title']
        elif 'description' in req_json:
            movie.description = req_json['description']
        elif 'trailer' in req_json:
            movie.trailer = req_json['trailer']
        elif 'year' in req_json:
            movie.year = req_json['year']
        elif 'rating' in req_json:
            movie.rating = req_json['rating']
        elif 'genre_id' in req_json:
            movie.genre_id = req_json['genre_id']
        elif 'director_id' in req_json:
            movie.director_id = req_json['director_id']
        db.session.add(movie)
        db.session.commit()
        return f"Oбъект c id {movie_id} обновлен", 204

    def put(self, movie_id):
        movie = db.session.query(Movie).get(movie_id)
        if not movie:
            return "Нет такого фильма", 404
        req_json = request.json

        movie.title = req_json['title']
        movie.description = req_json['description']
        movie.trailer = req_json['trailer']
        movie.year = req_json['year']
        movie.rating = req_json['rating']
        movie.genre_id = req_json['genre_id']
        movie.director_id = req_json['director_id']
        db.session.add(movie)
        db.session.commit()
        return f"Oбъект c id {movie_id} обновлен", 204

    def delete(self, movie_id):
        movie = db.session.query(Movie).get(movie_id)
        if not movie:
            return "Нет такого фильма", 404
        db.session.delete(movie)
        db.session.commit()
        return f"Oбъект c id {movie_id} удален", 204


@director_ns.route("/")
class DirectorView(Resource):
    def get(self):
        all_directors = db.session.query(Director).all()
        return directors_schema.dump(all_directors), 200


@director_ns.route("/<int:director_id>")
class DirectorView(Resource):

    def get(self, director_id: int):
        try:
            director = db.session.query(Director).filter(Director.id == director_id).one()
            return director_schema.dump(director), 200
        except Exception as e:
            return str(e), 404


@genre_ns.route("/")
class GenreView(Resource):
    def get(self):
        all_genres = db.session.query(Genre).all()
        return genres_schema.dump(all_genres), 200


@genre_ns.route("/<int:genre_id>")
class GenreView(Resource):

    def get(self, genre_id: int):
        try:
            genre = db.session.query(Genre).filter(Genre.id == genre_id).one()
            return genre_schema.dump(genre), 200
        except Exception as e:
            return str(e), 404


if __name__ == '__main__':
    app.run(debug=True)
