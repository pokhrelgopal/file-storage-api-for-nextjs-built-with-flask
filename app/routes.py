from flask import Blueprint, request, jsonify, render_template, current_app, abort
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from app.models import Image
from app import db
from app.utils import (
    allowed_file,
    validate_file_size,
    generate_filename,
    ensure_upload_directory,
    create_file_url,
    get_file_size_mb
)
import os
import mimetypes
from datetime import datetime
from functools import wraps

# Create Blueprint
main_bp = Blueprint('main', __name__)


def require_api_key(f):
    """Decorator to require API key authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != current_app.config['API_KEY']:
            return jsonify({
                "error": "Unauthorized",
                "message": "Valid API key required. Include 'X-API-Key' header with your request."
            }), 401
        return f(*args, **kwargs)
    return decorated_function


@main_bp.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    max_size_mb = current_app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024)
    return jsonify({
        "error": "File too large",
        "message": f"File size exceeds the maximum allowed size of {max_size_mb}MB"
    }), 413


@main_bp.errorhandler(400)
def bad_request(error):
    """Handle bad request errors."""
    return jsonify({
        "error": "Bad request",
        "message": str(error.description) if hasattr(error, 'description') else "Invalid request"
    }), 400


@main_bp.errorhandler(500)
def internal_server_error(error):
    """Handle internal server errors."""
    db.session.rollback()
    current_app.logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred. Please try again later."
    }), 500


@main_bp.route("/file", methods=["POST"])
@require_api_key
def upload_file():
    """Upload a media file and store its information in the database.

    Returns:
        JSON response with file information or error message
    """
    try:
        # Ensure upload directory exists
        ensure_upload_directory()

        # Check if file is in request
        if "file" not in request.files:
            return jsonify({"error": "No file provided", "message": "No file part in the request"}), 400

        file = request.files["file"]

        # Check if file was selected
        if file.filename == "":
            return jsonify({"error": "No file selected", "message": "No file was selected for upload"}), 400

        # Validate file size
        if not validate_file_size():
            max_size_mb = current_app.config['MAX_CONTENT_LENGTH'] / \
                (1024 * 1024)
            return jsonify({
                "error": "File too large",
                "message": f"File size exceeds the maximum allowed size of {max_size_mb}MB"
            }), 400

        # Validate file type
        if not allowed_file(file.filename):
            allowed_extensions = ', '.join(
                current_app.config['ALLOWED_EXTENSIONS'])
            return jsonify({
                "error": "Invalid file type",
                "message": f"File type not allowed. Allowed types: {allowed_extensions}"
            }), 400

        # Generate secure filename
        filename = generate_filename(file.filename)
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)

        # Get file information
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning

        # Get MIME type and extension
        mime_type, _ = mimetypes.guess_type(file.filename)
        file_extension = file.filename.rsplit(
            '.', 1)[1].lower() if '.' in file.filename else ''

        # Save file
        file.save(file_path)

        # Create file URL
        file_url = create_file_url(filename)

        # Save to database
        image = Image(
            filename=filename,
            original_filename=file.filename,
            file_size=file_size,
            file_type=mime_type or 'application/octet-stream',
            file_extension=file_extension,
            image_url=file_url,
            upload_date=datetime.utcnow()
        )

        db.session.add(image)
        db.session.commit()

        current_app.logger.info(
            f"File uploaded successfully: {filename} ({get_file_size_mb(file_size)}MB)")

        return jsonify({
            "success": True,
            "message": "File uploaded successfully",
            "file": image.to_dict()
        }), 201

    except RequestEntityTooLarge:
        max_size_mb = current_app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024)
        return jsonify({
            "error": "File too large",
            "message": f"File size exceeds the maximum allowed size of {max_size_mb}MB"
        }), 413
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"File upload error: {str(e)}")
        return jsonify({
            "error": "Upload failed",
            "message": "An error occurred while uploading the file. Please try again."
        }), 500


@main_bp.route("/files", methods=["GET"])
@require_api_key
def list_files():
    """Get a list of all uploaded files.

    Returns:
        JSON response with list of files
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # Limit per_page to prevent abuse
        per_page = min(per_page, 100)

        files_query = Image.get_active_files()
        files_paginated = files_query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        files_list = [file.to_dict() for file in files_paginated.items]

        return jsonify({
            "success": True,
            "files": files_list,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": files_paginated.total,
                "pages": files_paginated.pages,
                "has_next": files_paginated.has_next,
                "has_prev": files_paginated.has_prev
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error listing files: {str(e)}")
        return jsonify({
            "error": "Failed to retrieve files",
            "message": "An error occurred while retrieving the file list."
        }), 500


@main_bp.route("/file/<int:file_id>", methods=["DELETE"])
@require_api_key
def delete_file(file_id):
    """Soft delete a file by ID.

    Args:
        file_id: ID of the file to delete

    Returns:
        JSON response confirming deletion
    """
    try:
        file_record = Image.query.get_or_404(file_id)

        if not file_record.is_active:
            return jsonify({
                "error": "File not found",
                "message": "File has already been deleted or does not exist"
            }), 404

        # Soft delete
        file_record.soft_delete()

        current_app.logger.info(f"File soft deleted: {file_record.filename}")

        return jsonify({
            "success": True,
            "message": "File deleted successfully"
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting file {file_id}: {str(e)}")
        return jsonify({
            "error": "Failed to delete file",
            "message": "An error occurred while deleting the file."
        }), 500


@main_bp.route("/file/<int:file_id>/info", methods=["GET"])
@require_api_key
def get_file_info(file_id):
    """Get information about a specific file.

    Args:
        file_id: ID of the file

    Returns:
        JSON response with file information
    """
    try:
        file_record = Image.query.filter_by(
            id=file_id, is_active=True).first_or_404()

        return jsonify({
            "success": True,
            "file": file_record.to_dict()
        }), 200

    except Exception as e:
        current_app.logger.error(
            f"Error getting file info {file_id}: {str(e)}")
        return jsonify({
            "error": "File not found",
            "message": "The requested file could not be found."
        }), 404


@main_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint.

    Returns:
        JSON response with service status
    """
    try:
        # Test database connection
        db.session.execute('SELECT 1')

        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }), 200

    except Exception as e:
        current_app.logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": "Database connection failed"
        }), 503


# Template routes
@main_bp.route("/", methods=["GET"])
def index():
    """Render the main index page with API documentation."""
    return render_template("index.html")
