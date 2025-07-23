from datetime import datetime
from app import db


class Image(db.Model):
    """Model for storing uploaded media files information."""

    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False, index=True)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    file_extension = db.Column(db.String(10), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    upload_date = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<Image {self.filename}>"

    def to_dict(self):
        """Convert the model to a dictionary."""
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'file_size_mb': round(self.file_size / (1024 * 1024), 2),
            'file_type': self.file_type,
            'file_extension': self.file_extension,
            'image_url': self.image_url,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'is_active': self.is_active
        }

    @classmethod
    def get_active_files(cls):
        """Get all active files."""
        return cls.query.filter_by(is_active=True).order_by(cls.upload_date.desc())

    def soft_delete(self):
        """Soft delete the file record."""
        self.is_active = False
        db.session.commit()
