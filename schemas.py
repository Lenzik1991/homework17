from marshmallow import Schema, fields

class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Str()
    director_id = fields.Str()

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)