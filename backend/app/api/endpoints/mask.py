"""
File Masking router module for SecureData Web.
Exposes the endpoint to mask uploaded CSV or Excel files in memory,
stream the anonymized files back, and write job execution metadata to the audit log.
"""

import io
import os
import json
import logging
import zipfile
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
import pandas as pd
from sqlmodel import Session
from app.services.masker import mask_dataframe, revert_dataframe
from app.models.user import User
from app.services.auth import get_current_user
from app.db import get_session
from app.models.job import MaskingJob, JobDetail
from app.core.limiter import limiter


logger = logging.getLogger("app.api.endpoints.mask")
router = APIRouter()

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50MB

VALID_MIME_TYPES = {
    "text/csv",
    "application/vnd.ms-excel",
    "text/x-csv",
    "application/csv",
    "text/comma-separated-values",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
}

@router.post("/mask")
@limiter.limit("10/minute")
async def mask_file(
    request: Request,
    file: UploadFile = File(...),
    rules: str = Form(...),
    generate_key: bool = Form(False),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Applies the configured masking rules to an uploaded file.
    Performs all operations transiently in memory, streaming the masked file back immediately.
    Logs success or failure metadata to the database for audit tracking.
    Args:
        request (Request): FastAPI request object for rate limiting.
        file (UploadFile): The uploaded file to mask (CSV or XLSX).
        rules (str): Form parameter containing JSON-stringified column-to-rule mapping.
        generate_key (bool): Form parameter to also generate a reversion key.
        current_user (User): The authenticated user making the request.
        session (Session): SQLite database session.
    Raises:
        HTTPException 400: If file extension or MIME-type is unsupported or parsing fails.
        HTTPException 413: If file size exceeds the 50MB limit.
    Returns:
        StreamingResponse: Stream containing the newly masked file download or a ZIP.
    """

    # Validate extension and MIME-type
    filename = file.filename
    if not (filename.endswith('.csv') or filename.endswith('.xlsx')):
        raise HTTPException(
            status_code=400,
            detail="Format file tidak didukung. Hanya .csv dan .xlsx yang didukung."
        )
        
    if file.content_type not in VALID_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Tipe MIME file tidak valid."
        )
    
    # Quick content-length check
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="File terlalu besar. Maksimum ukuran file adalah 50MB."
        )
        
    # Read in chunks to prevent reading massive files into memory
    file_bytes = b""
    chunk_size = 8192
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        file_bytes += chunk
        if len(file_bytes) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail="File terlalu besar. Maksimum ukuran file adalah 50MB."
            )
    file_size = len(file_bytes)
        
    logger.info(f"File uploaded for masking: {filename} ({file_size} bytes)")
    
    file_buffer = io.BytesIO(file_bytes)
    
    try:
        rules_dict = json.loads(rules)
    except Exception as e:
        logger.error(f"Error parsing rules JSON: {str(e)}")
        # Log failed job
        try:
            job = MaskingJob(
                user_id=current_user.id,
                file_name=filename,
                file_size_bytes=file_size,
                row_count=None,
                status="FAILED",
                error_message="Format konfigurasi aturan masking tidak valid (JSON tidak valid)."
            )
            session.add(job)
            session.commit()
        except Exception as db_err:
            logger.error(f"Failed to log failed masking job: {str(db_err)}")
        raise HTTPException(
            status_code=400,
            detail="Format konfigurasi aturan masking tidak valid (JSON tidak valid)."
        )
        
    try:
        # Load full dataframe
        if filename.endswith('.csv'):
            try:
                df = pd.read_csv(file_buffer, dtype=str)
            except UnicodeDecodeError:
                file_buffer.seek(0)
                df = pd.read_csv(file_buffer, dtype=str, encoding='latin1')
        else:
            df = pd.read_excel(file_buffer, dtype=str)
            
        # Execute masking
        if generate_key:
            masked_df, mappings = mask_dataframe(df, rules_dict, return_mappings=True)
        else:
            masked_df = mask_dataframe(df, rules_dict)
        
        # Write to memory buffer
        output_buffer = io.BytesIO()
        if filename.endswith('.csv'):
            masked_df.to_csv(output_buffer, index=False, encoding='utf-8')
            media_type = "text/csv"
        else:
            with pd.ExcelWriter(output_buffer, engine='openpyxl') as writer:
                masked_df.to_excel(writer, index=False)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            
        output_buffer.seek(0)
        
        base_name, ext = os.path.splitext(filename)
        
        if generate_key:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                # Write masked file bytes
                masked_file_name = f"{base_name}_masked{ext}"
                zip_file.writestr(masked_file_name, output_buffer.getvalue())
                
                # Write key JSON file bytes
                key_file_name = f"{base_name}_reversion_key.json"
                key_json_bytes = json.dumps(mappings, indent=2).encode("utf-8")
                zip_file.writestr(key_file_name, key_json_bytes)
                
            zip_buffer.seek(0)
            output_buffer = zip_buffer
            media_type = "application/zip"
            download_filename = f"{base_name}_masked.zip"
        else:
            download_filename = f"{base_name}_masked{ext}"
        
        # Log SUCCESS
        job = MaskingJob(
            user_id=current_user.id,
            file_name=filename,
            file_size_bytes=file_size,
            row_count=len(df),
            status="SUCCESS"
        )
        session.add(job)
        session.flush()

        for col, rule in rules_dict.items():
            if rule != "No Masking" and col in df.columns:
                detail = JobDetail(
                    job_id=job.id,
                    column_name=col,
                    rule_name=rule
                )
                session.add(detail)
        session.commit()
        
    except Exception as e:
        logger.error(f"Error processing file masking for {filename}: {str(e)}", exc_info=True)
        # Log FAILED
        try:
            row_count = None
            try:
                if 'df' in locals():
                    row_count = len(df)
            except:
                pass
                
            err_msg = str(e)[:250]
            job = MaskingJob(
                user_id=current_user.id,
                file_name=filename,
                file_size_bytes=file_size,
                row_count=row_count,
                status="FAILED",
                error_message=err_msg
            )
            session.add(job)
            session.commit()
        except Exception as db_err:
            logger.error(f"Failed to log failed masking job: {str(db_err)}")

        # Clean up buffers
        try:
            file_buffer.close()
        except:
            pass
        raise HTTPException(
            status_code=400,
            detail=f"Gagal memproses penyamaran berkas: {str(e)}"
        )
        
    headers = {
        "Content-Disposition": f"attachment; filename={download_filename}",
        "Access-Control-Expose-Headers": "Content-Disposition"  # Important for frontend to read filename
    }
    
    return StreamingResponse(output_buffer, media_type=media_type, headers=headers)

MAX_KEY_SIZE_BYTES = 10 * 1024 * 1024  # 10MB

@router.post("/mask/revert")
@limiter.limit("10/minute")
async def revert_file(
    request: Request,
    file: UploadFile = File(...),
    key: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Restores the original values from a masked CSV or Excel file and its reversion key.
    Performs all operations transiently in memory, streaming the restored file back.
    Args:
        request (Request): FastAPI request object for rate limiting.
        file (UploadFile): The masked CSV or XLSX file.
        key (UploadFile): The JSON reversion key file.
        current_user (User): The authenticated user making the request.
        session (Session): SQLite database session.
    Raises:
        HTTPException 400: If parsing, validation, or reversion fails.
        HTTPException 413: If file or key size exceeds limit.
    Returns:
        StreamingResponse: Stream containing the restored file.
    """
    filename = file.filename or ""
    if not (filename.endswith('.csv') or filename.endswith('.xlsx')):
        raise HTTPException(
            status_code=400,
            detail="Format file tidak didukung. Hanya .csv dan .xlsx yang didukung."
        )

    if file.content_type not in VALID_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Tipe MIME file tidak valid."
        )

    key_filename = key.filename or ""
    if not key_filename.endswith('.json'):
        raise HTTPException(
            status_code=400,
            detail="Format kunci pemulihan tidak valid. Hanya berkas .json yang didukung."
        )

    # Validate file size is <= 50MB using the chunked reading loop
    file_bytes = b""
    chunk_size = 8192
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        file_bytes += chunk
        if len(file_bytes) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail="File terlalu besar. Maksimum ukuran file adalah 50MB."
            )
    file_size = len(file_bytes)

    # Validate key size is <= 10MB using the chunked reading loop
    key_bytes = b""
    while True:
        chunk = await key.read(chunk_size)
        if not chunk:
            break
        key_bytes += chunk
        if len(key_bytes) > MAX_KEY_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail="Berkas kunci terlalu besar. Maksimum ukuran berkas kunci adalah 10MB."
            )

    # Parse key JSON
    try:
        mappings = json.loads(key_bytes.decode('utf-8'))
    except Exception as e:
        logger.error(f"Error parsing key JSON: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="Format berkas kunci tidak valid (JSON tidak valid)."
        )

    # Parse masked file into DataFrame
    file_buffer = io.BytesIO(file_bytes)
    try:
        if filename.endswith('.csv'):
            try:
                df = pd.read_csv(file_buffer, dtype=str)
            except UnicodeDecodeError:
                file_buffer.seek(0)
                df = pd.read_csv(file_buffer, dtype=str, encoding='latin1')
        else:
            df = pd.read_excel(file_buffer, dtype=str)

        # Call revert_dataframe
        restored_df = revert_dataframe(df, mappings)

        # Write to memory buffer
        output_buffer = io.BytesIO()
        if filename.endswith('.csv'):
            restored_df.to_csv(output_buffer, index=False, encoding='utf-8')
            media_type = "text/csv"
        else:
            with pd.ExcelWriter(output_buffer, engine='openpyxl') as writer:
                restored_df.to_excel(writer, index=False)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            
        output_buffer.seek(0)
    except ValueError as val_err:
        logger.error(f"Validation failed during reversion: {str(val_err)}")
        raise HTTPException(
            status_code=400,
            detail=str(val_err)
        )
    except Exception as e:
        logger.error(f"Error processing file reversion: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Gagal memproses pemulihan data: {str(e)}"
        )

    base_name, ext = os.path.splitext(filename)
    if base_name.endswith('_masked'):
        base_name = base_name[:-7]
    reverted_filename = f"{base_name}_reverted{ext}"

    headers = {
        "Content-Disposition": f"attachment; filename={reverted_filename}",
        "Access-Control-Expose-Headers": "Content-Disposition"
    }

    return StreamingResponse(output_buffer, media_type=media_type, headers=headers)

