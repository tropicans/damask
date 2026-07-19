import io
import os
import logging
from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.parser import parse_csv_preview, parse_xlsx_preview
from app.services.detector import recommend_masking_rules

logger = logging.getLogger("app.api.endpoints.preview")
router = APIRouter()

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50MB

current_dir = os.path.dirname(os.path.abspath(__file__))
RULES_CONFIG_PATH = os.path.abspath(os.path.join(current_dir, "../../../config/regex_rules.json"))

@router.post("/preview")
async def get_file_preview(file: UploadFile = File(...)):
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
