import io
import os
import json
import logging
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from fastapi.responses import StreamingResponse
import pandas as pd
from sqlmodel import Session
from app.services.masker import mask_dataframe
from app.models.user import User
from app.services.auth import get_current_user
from app.db import get_session
from app.models.job import MaskingJob, JobDetail


logger = logging.getLogger("app.api.endpoints.mask")
router = APIRouter()

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50MB

@router.post("/mask")
async def mask_file(
    file: UploadFile = File(...),
    rules: str = Form(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):

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
        
    # Generate download filename with suffix _masked
    base_name, ext = os.path.splitext(filename)
    masked_filename = f"{base_name}_masked{ext}"
    
    headers = {
        "Content-Disposition": f"attachment; filename={masked_filename}",
        "Access-Control-Expose-Headers": "Content-Disposition"  # Important for frontend to read filename
    }
    
    return StreamingResponse(output_buffer, media_type=media_type, headers=headers)
