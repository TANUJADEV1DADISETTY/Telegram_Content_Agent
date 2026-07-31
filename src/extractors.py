import os
import hashlib
import trafilatura
from markitdown import MarkItDown
from src.config import logger

def extract_from_url(url: str) -> str:
    logger.info(f"Extracting content from URL: {url}")
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            raise ValueError(f"Failed to fetch content from URL: {url}")
        
        result = trafilatura.extract(downloaded, output_format="markdown", with_metadata=True)
        if not result:
            raise ValueError(f"Failed to extract readable text from URL: {url}")
            
        return result
    except Exception as e:
        logger.error(f"Error during HTML extraction: {str(e)}")
        raise

def extract_from_pdf(pdf_path: str) -> str:
    logger.info(f"Extracting content from PDF: {pdf_path}")
    try:
        md_converter = MarkItDown()
        result = md_converter.convert(pdf_path)
        if not result or not result.text_content:
            raise ValueError(f"No content extracted from PDF: {pdf_path}")
        return result.text_content
    except Exception as e:
        logger.error(f"Error during PDF extraction with markitdown: {str(e)}")
        raise

def compute_hash(text: str) -> str:
    """Compute SHA-256 hash of text for unique identifier."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
