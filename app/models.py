from app import db


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255))

    def __repr__(self):
        return f"Image {self.name}"
