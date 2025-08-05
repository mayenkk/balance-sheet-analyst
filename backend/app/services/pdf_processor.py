import os
import re
import fitz  # PyMuPDF
import pdfplumber
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.company import Company
import logging

logger = logging.getLogger(__name__)

@dataclass
class PDFChunk:
    """Represents a chunk of text from PDF with metadata"""
    content: str
    page_number: int
    start_char: int
    end_char: int
    company_vertical: str
    confidence_score: float
    metadata: Dict[str, Any]

class PDFProcessor:
    """Service for processing PDF balance sheets and extracting company-specific data"""
    
    def __init__(self):
        self.vertical_keywords = settings.VERTICAL_KEYWORDS
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
    
    def process_balance_sheet_pdf(self, pdf_path: str, db: Session) -> Dict[str, List[PDFChunk]]:
        """
        Process a balance sheet PDF and extract chunks by company vertical
        Returns: Dict[company_vertical, List[PDFChunk]]
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        logger.info(f"Processing PDF: {pdf_path}")
        
        # Extract text from PDF
        full_text = self._extract_text_from_pdf(pdf_path)
        
        # Identify company verticals in the text
        vertical_sections = self._identify_vertical_sections(full_text)
        
        # Chunk text by vertical
        vertical_chunks = {}
        
        for vertical, sections in vertical_sections.items():
            chunks = []
            for section in sections:
                section_chunks = self._chunk_text(section['text'], section['page'])
                for chunk in section_chunks:
                    chunk.company_vertical = vertical
                    chunk.confidence_score = section['confidence']
                    chunks.append(chunk)
            
            vertical_chunks[vertical] = chunks
            logger.info(f"Extracted {len(chunks)} chunks for vertical: {vertical}")
        
        return vertical_chunks
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using PyMuPDF for better text extraction"""
        try:
            doc = fitz.open(pdf_path)
            full_text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                full_text += f"\n--- PAGE {page_num + 1} ---\n{text}\n"
            
            doc.close()
            return full_text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            # Fallback to pdfplumber
            return self._extract_text_with_pdfplumber(pdf_path)
    
    def _extract_text_with_pdfplumber(self, pdf_path: str) -> str:
        """Fallback text extraction using pdfplumber"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        full_text += f"\n--- PAGE {page_num + 1} ---\n{text}\n"
                return full_text
        except Exception as e:
            logger.error(f"Error with pdfplumber: {e}")
            raise Exception(f"Failed to extract text from PDF: {e}")
    
    def _identify_vertical_sections(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Identify sections of text that belong to different company verticals
        Returns: Dict[vertical_name, List[section_data]]
        """
        vertical_sections = {vertical: [] for vertical in self.vertical_keywords.keys()}
        
        # Split text into pages
        pages = text.split("--- PAGE")
        
        for page_text in pages:
            if not page_text.strip():
                continue
            
            # Extract page number
            page_match = re.search(r'(\d+) ---', page_text)
            page_num = int(page_match.group(1)) if page_match else 1
            
            # Find verticals in this page
            page_verticals = self._find_verticals_in_text(page_text)
            
            for vertical, confidence in page_verticals.items():
                if confidence > 0.3:  # Minimum confidence threshold
                    vertical_sections[vertical].append({
                        'text': page_text,
                        'page': page_num,
                        'confidence': confidence
                    })
        
        return vertical_sections
    
    def _find_verticals_in_text(self, text: str) -> Dict[str, float]:
        """
        Find which verticals are mentioned in the text with confidence scores
        Returns: Dict[vertical_name, confidence_score]
        """
        text_lower = text.lower()
        vertical_scores = {}
        
        for vertical, keywords in self.vertical_keywords.items():
            score = 0
            total_keywords = len(keywords)
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                # Count occurrences and weight by proximity
                occurrences = text_lower.count(keyword_lower)
                if occurrences > 0:
                    # Higher score for more occurrences and longer keywords
                    score += (occurrences * len(keyword)) / total_keywords
            
            # Normalize score
            if score > 0:
                vertical_scores[vertical] = min(score / 10, 1.0)  # Cap at 1.0
        
        return vertical_scores
    
    def _chunk_text(self, text: str, page_number: int) -> List[PDFChunk]:
        """
        Split text into overlapping chunks
        Returns: List[PDFChunk]
        """
        chunks = []
        words = text.split()
        
        if len(words) <= self.chunk_size:
            # Single chunk for short text
            chunk = PDFChunk(
                content=text,
                page_number=page_number,
                start_char=0,
                end_char=len(text),
                company_vertical="",
                confidence_score=0.0,
                metadata={"word_count": len(words)}
            )
            chunks.append(chunk)
        else:
            # Create overlapping chunks
            for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
                chunk_words = words[i:i + self.chunk_size]
                chunk_text = " ".join(chunk_words)
                
                chunk = PDFChunk(
                    content=chunk_text,
                    page_number=page_number,
                    start_char=i,
                    end_char=i + len(chunk_text),
                    company_vertical="",
                    confidence_score=0.0,
                    metadata={
                        "word_count": len(chunk_words),
                        "chunk_index": i // (self.chunk_size - self.chunk_overlap)
                    }
                )
                chunks.append(chunk)
        
        return chunks
    
    def get_company_access_chunks(
        self, 
        user_verticals: List[str], 
        all_chunks: Dict[str, List[PDFChunk]]
    ) -> List[PDFChunk]:
        """
        Filter chunks based on user's company access
        Returns: List[PDFChunk] that user has access to
        """
        accessible_chunks = []
        
        for vertical in user_verticals:
            if vertical in all_chunks:
                accessible_chunks.extend(all_chunks[vertical])
        
        return accessible_chunks
    
    def validate_pdf_structure(self, pdf_path: str) -> Dict[str, Any]:
        """
        Validate PDF structure and extract metadata
        Returns: Dict with validation results and metadata
        """
        try:
            doc = fitz.open(pdf_path)
            
            validation_result = {
                "is_valid": True,
                "total_pages": len(doc),
                "file_size_mb": os.path.getsize(pdf_path) / (1024 * 1024),
                "text_present": False,
                "verticals_found": [],
                "errors": []
            }
            
            # Check if text is extractable
            sample_text = ""
            for page_num in range(min(3, len(doc))):  # Check first 3 pages
                page = doc.load_page(page_num)
                sample_text += page.get_text()
            
            if sample_text.strip():
                validation_result["text_present"] = True
                
                # Check for verticals in sample
                verticals = self._find_verticals_in_text(sample_text)
                validation_result["verticals_found"] = [
                    v for v, score in verticals.items() if score > 0.3
                ]
            else:
                validation_result["is_valid"] = False
                validation_result["errors"].append("No extractable text found")
            
            doc.close()
            return validation_result
            
        except Exception as e:
            return {
                "is_valid": False,
                "errors": [str(e)]
            } 