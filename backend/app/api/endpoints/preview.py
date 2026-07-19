"""
File Preview router module for SecureData Web.
Exposes the endpoint to parse uploaded CSV or Excel files, extracting
the headers, first 3 sample rows, and auto-detecting recommended masking rules.
"""

import io
import os
import logging
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Request
from app.services.parser import parse_csv_preview, parse_xlsx_preview
from app.services.detector import recommend_masking_rules
from app.models.user import User
from app.services.auth import get_current_user
from app.core.limiter import limiter


logger = logging.getLogger("app.api.endpoints.preview")
router = APIRouter()

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50MB

current_dir = os.path.dirname(os.path.abspath(__file__))
RULES_CONFIG_PATH = os.path.abspath(os.path.join(current_dir, "../../../config/regex_rules.json"))

@router.post("/preview")
@limiter.limit("10/minute")
async def get_file_preview(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Parses headers and 3 preview rows of an uploaded file.
    Suggests recommended masking rules based on regex matches of headers.
    Processes the file strictly in temporary RAM buffers.
    Args:
        request (Request): FastAPI request object for rate limiting.
        file (UploadFile): Uploaded CSV or Excel file (up to 50MB).
        current_user (User): Currently authenticated user.
    Raises:
        HTTPException 400: If file extension is unsupported or parsing fails.
        HTTPException 413: If file size exceeds the 50MB limit.
    Returns:
        dict: Filename, size_bytes, headers list, preview_rows list, and recommendations.
    """

    # Validate extension
    filename = file.filename
    if not (filename.endswith('.csv') or filename.endswith('.xlsx')):
        raise HTTPException(
            status_code=400,
            detail="Format file tidak didukung. Hanya .csv dan .xlsx yang didukung."
        )
    
    # Read entire content into memory (RAM buffer)
    file_bytes = await file.read()
    file_size = len(file_bytes)
    
    # Check size constraint
    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="File terlalu besar. Maksimum ukuran file adalah 50MB."
        )
    
    logger.info(f"File uploaded for preview: {filename} ({file_size} bytes)")
    
    file_buffer = io.BytesIO(file_bytes)
    
    try:
        if filename.endswith('.csv'):
            headers, preview_rows = parse_csv_preview(file_buffer)
        else:
            headers, preview_rows = parse_xlsx_preview(file_buffer)
    except Exception as e:
        logger.error(f"Error parsing file preview for {filename}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Gagal memproses pratinjau berkas: {str(e)}"
        )
        
    try:
        recommendations = recommend_masking_rules(headers, RULES_CONFIG_PATH)
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}", exc_info=True)
        recommendations = {header: "No Masking" for header in headers}
        
    return {
        "filename": filename,
        "size_bytes": file_size,
        "headers": headers,
        "preview_rows": preview_rows,
        "recommendations": recommendations
    }
