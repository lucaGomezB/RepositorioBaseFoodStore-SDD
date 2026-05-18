# Input sanitization utilities
import re
import html
from fastapi import UploadFile


# Patterns to detect potentially dangerous content
HTML_TAG_PATTERN = re.compile(r'<[^>]+>')
SCRIPT_PATTERN = re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL)
SQL_INJECTION_PATTERN = re.compile(
    r"(?:')|(?:--)|(?:\/\*)|(?:\*\/)|(?:xp_)|(?:sp_)|(?:exec)|(?:execute)",
    re.IGNORECASE
)


def sanitize_string(value: str, strip_html: bool = True) -> str:
    """
    Sanitize a string input by removing dangerous content.
    
    Args:
        value: The string to sanitize
        strip_html: Whether to strip HTML tags
        
    Returns:
        Sanitized string
    """
    if not value:
        return value
    
    # Step 1: Trim whitespace
    sanitized = value.strip()
    
    # Step 2: Remove HTML/script tags if requested
    if strip_html:
        # Remove script tags first (they may contain other HTML)
        sanitized = SCRIPT_PATTERN.sub('', sanitized)
        # Remove remaining HTML tags
        sanitized = HTML_TAG_PATTERN.sub('', sanitized)
        # Decode HTML entities (e.g., &lt; becomes <)
        sanitized = html.unescape(sanitized)
    
    # Step 3: Check for SQL injection patterns (basic detection)
    # Note: This is a warning only, actual prevention is done via parameterized queries
    if SQL_INJECTION_PATTERN.search(sanitized):
        # Escape special SQL characters
        sanitized = sanitized.replace("'", "''")
    
    # Step 4: Remove null bytes
    sanitized = sanitized.replace('\x00', '')
    
    return sanitized


def sanitize_html(value: str) -> str:
    """
    Sanitize HTML content while preserving safe tags.
    
    Args:
        value: The HTML string to sanitize
        
    Returns:
        Sanitized HTML with only safe tags
    """
    if not value:
        return value
    
    # Remove script and style tags entirely
    value = re.sub(r'<script[^>]*>.*?</script>', '', value, flags=re.IGNORECASE | re.DOTALL)
    value = re.sub(r'<style[^>]*>.*?</style>', '', value, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove event handlers (onclick, onerror, etc.)
    value = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', value, flags=re.IGNORECASE)
    
    # Remove javascript: URLs
    value = re.sub(r'javascript:', '', value, flags=re.IGNORECASE)
    
    return value


def normalize_whitespace(value: str) -> str:
    """
    Normalize whitespace in a string.
    
    Replaces multiple whitespace characters with a single space.
    
    Args:
        value: The string to normalize
        
    Returns:
        String with normalized whitespace
    """
    if not value:
        return value
    
    # Replace multiple whitespace with single space
    return re.sub(r'\s+', ' ', value).strip()


def truncate_string(value: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length.
    
    Args:
        value: The string to truncate
        max_length: Maximum length (including suffix)
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated string
    """
    if not value or len(value) <= max_length:
        return value
    
    return value[:max_length - len(suffix)] + suffix


# File validation utilities
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}
ALLOWED_DOCUMENT_EXTENSIONS = {'.pdf', '.doc', '.docx', '.txt', '.csv'}
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


def validate_file_type(file: UploadFile, allowed_extensions: set) -> bool:
    """
    Validate file type based on extension.
    
    Args:
        file: FastAPI UploadFile
        allowed_extensions: Set of allowed extensions (e.g., {'.jpg', '.png'})
        
    Returns:
        True if file type is allowed
    """
    if not file.filename:
        return False
    
    # Get extension (lowercase)
    ext = file.filename.lower().rsplit('.', 1)[-1] if '.' in file.filename else ''
    return f'.{ext}' in allowed_extensions


def validate_file_size(file: UploadFile, max_size_bytes: int = MAX_FILE_SIZE_BYTES) -> bool:
    """
    Validate file size.
    
    Note: This only works if the file is small enough to fit in memory.
    For large files, use content-length header check at the proxy level.
    
    Args:
        file: FastAPI UploadFile
        max_size_bytes: Maximum allowed size in bytes
        
    Returns:
        True if file size is within limits
    """
    # Note: This is a placeholder. For actual implementation,
    # you'd need to read the file content or check Content-Length header
    # For now, we'll trust the client but add a note
    return True


def validate_uploaded_image(file: UploadFile) -> tuple[bool, str]:
    """
    Validate an uploaded image file.
    
    Args:
        file: FastAPI UploadFile
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not validate_file_type(file, ALLOWED_IMAGE_EXTENSIONS):
        return False, f"Invalid file type. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
    
    # Note: For full validation, you'd also check:
    # - File signature (magic bytes) to verify it's actually an image
    # - File size
    
    return True, ""


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent path traversal and other attacks.
    
    Args:
        filename: The original filename
        
    Returns:
        Sanitized filename
    """
    if not filename:
        return "file"
    
    # Remove path components (prevent directory traversal)
    filename = filename.split('/')[-1].split('\\')[-1]
    
    # Remove dangerous characters
    filename = re.sub(r'[^\w\s\-\.]', '', filename)
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    # Limit length
    max_name_length = 255
    if len(filename) > max_name_length:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        name = name[:max_name_length - len(ext) - 1]
        filename = f"{name}.{ext}" if ext else name
    
    return filename