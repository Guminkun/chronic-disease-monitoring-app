from minio import Minio
from minio.error import S3Error
from app.config import settings
from app.logging_config import get_logger
import io
import uuid
import hashlib
import datetime
from typing import Optional, Tuple
from pathlib import Path
from PIL import Image
import tempfile

logger = get_logger(__name__)


class MinioService:
    def __init__(self):
        endpoint = settings.MINIO_ENDPOINT
        if endpoint.startswith("http://"):
            endpoint = endpoint.replace("http://", "")
        elif endpoint.startswith("https://"):
            endpoint = endpoint.replace("https://", "")
            
        self.client = Minio(
            endpoint,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
            region="cn-north-1"
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self.presigned_url_expiration = 600  # 10 minutes
        
    def _generate_file_key(
        self,
        user_id: str,
        member_id: str,
        file_type: str,
        extension: str,
        filename_prefix: Optional[str] = None
    ) -> str:
        """
        Generate a secure file key path following production standards.
        
        Path format: {bucket}/user_{user_id}/member_{member_id}/{timestamp}_{uuid}.{ext}
        
        Args:
            user_id: User UUID
            member_id: Member UUID
            file_type: Type of file (reports, medical_records, avatars, guides)
            extension: File extension (jpg, png, etc.)
            filename_prefix: Optional prefix for filename (e.g., 'avatar', 'thumbnail')
        
        Returns:
            File key path
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        file_uuid = uuid.uuid4().hex[:8]
        
        if filename_prefix:
            filename = f"{timestamp}_{file_uuid}_{filename_prefix}.{extension}"
        else:
            filename = f"{timestamp}_{file_uuid}.{extension}"
        
        key = f"user_{user_id}/member_{member_id}/{file_type}/{filename}"
        
        return key
    
    def _calculate_md5(self, file_data: bytes) -> str:
        """Calculate MD5 hash of file data."""
        return hashlib.md5(file_data).hexdigest()
    
    def _compress_image(
        self,
        file_data: bytes,
        max_width: int = 1920,
        max_height: int = 1920,
        quality: int = 85,
        max_size_kb: int = 500
    ) -> Tuple[bytes, str]:
        """
        Compress image to reduce file size.
        
        Args:
            file_data: Original image bytes
            max_width: Maximum width
            max_height: Maximum height
            quality: JPEG quality (1-100)
            max_size_kb: Maximum file size in KB
        
        Returns:
            Tuple of (compressed_data, format)
        """
        try:
            img = Image.open(io.BytesIO(file_data))
            
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Resize if too large
            if img.width > max_width or img.height > max_height:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Compress
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            compressed_data = output.getvalue()
            
            # If still too large, reduce quality
            current_quality = quality
            while len(compressed_data) > max_size_kb * 1024 and current_quality > 20:
                current_quality -= 10
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=current_quality, optimize=True)
                compressed_data = output.getvalue()
            
            logger.info(f"Image compressed: {len(file_data)} -> {len(compressed_data)} bytes")
            return compressed_data, 'jpeg'
            
        except Exception as e:
            logger.warning(f"Image compression failed, using original: {e}")
            return file_data, 'jpeg'
    
    def _create_thumbnail(
        self,
        file_data: bytes,
        width: int = 200,
        height: int = 200,
        quality: int = 70
    ) -> bytes:
        """
        Create a thumbnail for image.
        
        Args:
            file_data: Original image bytes
            width: Thumbnail width
            height: Thumbnail height
            quality: JPEG quality
        
        Returns:
            Thumbnail bytes
        """
        try:
            img = Image.open(io.BytesIO(file_data))
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Create thumbnail
            img.thumbnail((width, height), Image.Resampling.LANCZOS)
            
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            
            logger.info(f"Thumbnail created: {len(output.getvalue())} bytes")
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Thumbnail creation failed: {e}")
            raise
    
    def check_file_exists_by_md5(
        self,
        md5_hash: str,
        bucket_name: str
    ) -> Optional[str]:
        """
        Check if file with same MD5 already exists.
        
        Returns:
            File key if exists, None otherwise
        """
        try:
            objects = self.client.list_objects(bucket_name, recursive=True)
            for obj in objects:
                # We would need to download and check MD5, which is expensive
                # For now, we'll use a metadata approach in upload_file
                pass
        except Exception as e:
            logger.error(f"Error checking file by MD5: {e}")
        
        return None
    
    def upload_file(
        self,
        file_data: bytes,
        user_id: str,
        member_id: str,
        file_type: str,
        content_type: str,
        bucket_name: Optional[str] = None,
        compress: bool = True,
        create_thumbnail: bool = False,
        filename_prefix: Optional[str] = None
    ) -> Tuple[str, str, Optional[str]]:
        try:
            target_bucket = bucket_name or self.bucket_name
            
            # Calculate MD5 before any processing
            md5_hash = self._calculate_md5(file_data)
            
            # Determine extension
            extension = content_type.split('/')[-1] if '/' in content_type else 'jpg'
            if extension == 'jpeg':
                extension = 'jpg'
            
            # Compress if needed
            if compress and content_type.startswith('image/'):
                file_data, _ = self._compress_image(file_data)
                content_type = 'image/jpeg'
                extension = 'jpg'
            
            # Generate secure file key
            file_key = self._generate_file_key(
                user_id,
                member_id,
                file_type,
                extension,
                filename_prefix
            )
            
            # Upload with metadata
            self.client.put_object(
                target_bucket,
                file_key,
                io.BytesIO(file_data),
                len(file_data),
                content_type=content_type,
                metadata={
                    'md5': md5_hash,
                    'user-id': user_id,
                    'member-id': member_id,
                    'upload-time': datetime.datetime.now().isoformat()
                }
            )
            
            logger.info(f"File uploaded successfully: {file_key} (MD5: {md5_hash[:8]}...)")
            
            # Create thumbnail if requested
            thumbnail_key = None
            if create_thumbnail and content_type.startswith('image/'):
                try:
                    thumbnail_data = self._create_thumbnail(file_data)
                    thumbnail_key = self._generate_file_key(
                        user_id,
                        member_id,
                        f"{file_type}_thumbnails",
                        'jpg',
                        'thumbnail'
                    )
                    
                    self.client.put_object(
                        target_bucket,
                        thumbnail_key,
                        io.BytesIO(thumbnail_data),
                        len(thumbnail_data),
                        content_type='image/jpeg',
                        metadata={
                            'md5': self._calculate_md5(thumbnail_data),
                            'user-id': user_id,
                            'member-id': member_id,
                            'original-key': file_key
                        }
                    )
                    
                    logger.info(f"Thumbnail uploaded: {thumbnail_key}")
                except Exception as e:
                    logger.error(f"Failed to create thumbnail: {e}")
            
            return file_key, md5_hash, thumbnail_key
            
        except S3Error as e:
            logger.error(f"MinIO S3 Error: {e}")
            raise Exception(f"Failed to upload file: {str(e)}")
        except Exception as e:
            logger.error(f"Upload error: {e}")
            raise
    
    def get_presigned_url(
        self,
        file_key: str,
        bucket_name: Optional[str] = None
    ) -> str:
        """
        Generate a presigned URL for temporary file access.
        
        Args:
            file_key: File key path
            bucket_name: Bucket name (optional)
        
        Returns:
            Presigned URL valid for 10 minutes
        """
        try:
            target_bucket = bucket_name or self.bucket_name
            
            url = self.client.presigned_get_object(
                target_bucket,
                file_key,
                expires=datetime.timedelta(seconds=self.presigned_url_expiration)
            )
            
            logger.debug(f"Generated presigned URL for: {file_key}")
            return url
            
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise
    
    def delete_file(
        self,
        file_key: str,
        bucket_name: Optional[str] = None
    ) -> bool:
        """
        Delete a file from MinIO.
        
        Args:
            file_key: File key path
            bucket_name: Bucket name (optional)
        
        Returns:
            True if successful
        """
        try:
            target_bucket = bucket_name or self.bucket_name
            
            self.client.remove_object(target_bucket, file_key)
            logger.info(f"File deleted: {file_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False
    
    def delete_files_by_prefix(
        self,
        prefix: str,
        bucket_name: Optional[str] = None
    ) -> int:
        """
        Delete all files with a given prefix (for cascade deletion).
        
        Args:
            prefix: Key prefix (e.g., user_123/member_456/)
            bucket_name: Bucket name (optional)
        
        Returns:
            Number of files deleted
        """
        try:
            target_bucket = bucket_name or self.bucket_name
            deleted_count = 0
            
            objects = self.client.list_objects(target_bucket, prefix=prefix, recursive=True)
            for obj in objects:
                try:
                    self.client.remove_object(target_bucket, obj.object_name)
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Failed to delete {obj.object_name}: {e}")
            
            logger.info(f"Deleted {deleted_count} files with prefix: {prefix}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to delete files by prefix: {e}")
            return 0
    
    def get_file_metadata(
        self,
        file_key: str,
        bucket_name: Optional[str] = None
    ) -> Optional[dict]:
        """
        Get file metadata.
        
        Args:
            file_key: File key path
            bucket_name: Bucket name (optional)
        
        Returns:
            Metadata dict or None
        """
        try:
            target_bucket = bucket_name or self.bucket_name
            
            stat = self.client.stat_object(target_bucket, file_key)
            return {
                'size': stat.size,
                'content_type': stat.content_type,
                'last_modified': stat.last_modified,
                'metadata': stat.metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to get file metadata: {e}")
            return None


minio_service = MinioService()
