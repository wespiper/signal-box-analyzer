"""
Base detector interface for framework detection
Time estimate: 2 hours
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from enum import Enum
import re
from pathlib import Path


class FrameworkConfidence(Enum):
    """Confidence levels for framework detection"""
    HIGH = "high"  # Definitive markers found (imports, config files)
    MEDIUM = "medium"  # Strong indicators (patterns, naming)
    LOW = "low"  # Weak indicators (generic patterns)
    NONE = "none"  # No indicators found


@dataclass
class FilePattern:
    """Pattern for matching files"""
    pattern: str  # Glob pattern or regex
    is_regex: bool = False
    weight: float = 1.0  # Importance of this pattern
    description: str = ""


@dataclass
class CodePattern:
    """Pattern for matching code content"""
    pattern: str  # Regex pattern
    file_types: List[str] = field(default_factory=list)  # [".py", ".js", etc]
    weight: float = 1.0
    description: str = ""


@dataclass
class Component:
    """Detected AI component"""
    name: str
    type: str  # agent, chain, tool, model, etc
    file_path: str
    line_number: int
    model: Optional[str] = None
    estimated_tokens: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DetectionResult:
    """Result of framework detection"""
    framework: str
    confidence: FrameworkConfidence
    version: Optional[str] = None
    components: List[Component] = field(default_factory=list)
    file_patterns_matched: List[str] = field(default_factory=list)
    code_patterns_matched: List[str] = field(default_factory=list)
    imports_found: List[str] = field(default_factory=list)
    config_files: List[str] = field(default_factory=list)
    workflow_patterns: List[Dict[str, Any]] = field(default_factory=list)
    confidence_score: float = 0.0  # 0-100
    
    def merge(self, other: 'DetectionResult') -> 'DetectionResult':
        """Merge another detection result into this one"""
        self.components.extend(other.components)
        self.file_patterns_matched.extend(other.file_patterns_matched)
        self.code_patterns_matched.extend(other.code_patterns_matched)
        self.imports_found.extend(other.imports_found)
        self.config_files.extend(other.config_files)
        self.workflow_patterns.extend(other.workflow_patterns)
        
        # Update confidence if needed
        if other.confidence_score > self.confidence_score:
            self.confidence = other.confidence
            self.confidence_score = other.confidence_score
            
        return self


class BaseDetector(ABC):
    """Base class for all framework detectors"""
    
    def __init__(self):
        self.file_patterns: List[FilePattern] = []
        self.code_patterns: List[CodePattern] = []
        self.import_patterns: List[str] = []
        self.config_files: List[str] = []
        self._setup_patterns()
    
    @abstractmethod
    def _setup_patterns(self):
        """Setup detection patterns specific to this framework"""
        pass
    
    @abstractmethod
    def get_framework_name(self) -> str:
        """Return the name of the framework this detector handles"""
        pass
    
    def calculate_confidence(self, 
                           file_matches: int, 
                           code_matches: int, 
                           import_matches: int,
                           config_matches: int) -> tuple[FrameworkConfidence, float]:
        """Calculate confidence level based on matches"""
        # Weighted scoring
        score = 0.0
        
        # Config files are strongest indicator
        if config_matches > 0:
            score += 40
            
        # Imports are very strong
        if import_matches > 0:
            score += 35
            
        # Code patterns are good indicators
        if code_matches > 0:
            score += min(20, code_matches * 5)
            
        # File patterns are supporting evidence
        if file_matches > 0:
            score += min(5, file_matches * 1)
        
        # Determine confidence level
        if score >= 75:
            confidence = FrameworkConfidence.HIGH
        elif score >= 40:
            confidence = FrameworkConfidence.MEDIUM
        elif score >= 10:
            confidence = FrameworkConfidence.LOW
        else:
            confidence = FrameworkConfidence.NONE
            
        return confidence, min(100, score)
    
    def match_file_patterns(self, file_paths: List[str]) -> List[str]:
        """Match file patterns against provided paths"""
        matched = []
        
        for file_path in file_paths:
            path = Path(file_path)
            
            for pattern in self.file_patterns:
                if pattern.is_regex:
                    if re.match(pattern.pattern, str(path)):
                        matched.append(f"{pattern.description or pattern.pattern}")
                else:
                    # Use glob-style matching
                    if path.match(pattern.pattern):
                        matched.append(f"{pattern.description or pattern.pattern}")
                        
        return list(set(matched))  # Remove duplicates
    
    def match_code_patterns(self, file_content: str, file_path: str) -> List[str]:
        """Match code patterns in file content"""
        matched = []
        path = Path(file_path)
        
        for pattern in self.code_patterns:
            # Check if file type matches
            if pattern.file_types and path.suffix not in pattern.file_types:
                continue
                
            # Search for pattern
            if re.search(pattern.pattern, file_content, re.MULTILINE | re.IGNORECASE):
                matched.append(pattern.description or pattern.pattern)
                
        return matched
    
    def find_imports(self, file_content: str, file_path: str) -> List[str]:
        """Find framework-specific imports"""
        imports = []
        
        # Only check Python files for now
        if not file_path.endswith('.py'):
            return imports
            
        for import_pattern in self.import_patterns:
            # Match both 'import X' and 'from X import Y' patterns
            import_regex = rf"(?:^import\s+{import_pattern}|^from\s+{import_pattern}\s+import)"
            
            if re.search(import_regex, file_content, re.MULTILINE):
                imports.append(import_pattern)
                
        return imports
    
    def check_config_files(self, file_paths: List[str]) -> List[str]:
        """Check for framework-specific config files"""
        config_found = []
        
        for file_path in file_paths:
            path = Path(file_path)
            
            for config_file in self.config_files:
                if path.name == config_file or path.match(f"**/{config_file}"):
                    config_found.append(config_file)
                    
        return config_found
    
    @abstractmethod
    def extract_components(self, file_content: str, file_path: str) -> List[Component]:
        """Extract framework-specific components from code"""
        pass
    
    def detect(self, file_paths: List[str], file_contents: Dict[str, str]) -> DetectionResult:
        """
        Main detection method
        
        Args:
            file_paths: List of all file paths in the repository
            file_contents: Dict mapping file paths to their content
            
        Returns:
            DetectionResult with confidence and detected components
        """
        result = DetectionResult(
            framework=self.get_framework_name(),
            confidence=FrameworkConfidence.NONE
        )
        
        # Check file patterns
        result.file_patterns_matched = self.match_file_patterns(file_paths)
        
        # Check config files
        result.config_files = self.check_config_files(file_paths)
        
        # Check code patterns and imports
        for file_path, content in file_contents.items():
            # Find imports
            imports = self.find_imports(content, file_path)
            result.imports_found.extend(imports)
            
            # Match code patterns
            patterns = self.match_code_patterns(content, file_path)
            result.code_patterns_matched.extend(patterns)
            
            # Extract components
            components = self.extract_components(content, file_path)
            result.components.extend(components)
        
        # Remove duplicates
        result.imports_found = list(set(result.imports_found))
        result.code_patterns_matched = list(set(result.code_patterns_matched))
        
        # Calculate confidence
        confidence, score = self.calculate_confidence(
            len(result.file_patterns_matched),
            len(result.code_patterns_matched),
            len(result.imports_found),
            len(result.config_files)
        )
        
        result.confidence = confidence
        result.confidence_score = score
        
        return result
    
    def estimate_tokens(self, text: str, is_prompt: bool = True) -> int:
        """Estimate token count for text"""
        # Simple estimation: ~4 characters per token
        # More accurate would use tiktoken or similar
        base_tokens = len(text) // 4
        
        # System prompts tend to be more token-dense
        if is_prompt:
            base_tokens = int(base_tokens * 1.2)
            
        return base_tokens