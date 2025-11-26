"""
Task Analyzer - Classifies user requests and extracts key requirements.

This module analyzes user tasks to determine:
- Task type (feature, refactor, debug, architecture, review)
- Key entities (files, functions, components mentioned)
- Technical requirements
- Complexity level
"""

import re
from enum import Enum
from typing import List, Dict, Optional, Set
from dataclasses import dataclass


class TaskType(Enum):
    """Types of development tasks"""
    FEATURE = "feature"           # Adding new functionality
    REFACTOR = "refactor"         # Improving existing code
    DEBUG = "debug"               # Fixing bugs/errors
    ARCHITECTURE = "architecture" # System design decisions
    REVIEW = "review"             # Code review/analysis
    OPTIMIZATION = "optimization" # Performance improvements
    DOCUMENTATION = "documentation" # Writing docs
    TESTING = "testing"           # Adding/fixing tests
    UNKNOWN = "unknown"           # Cannot determine


class ComplexityLevel(Enum):
    """Complexity levels for tasks"""
    SIMPLE = "simple"       # Single file, straightforward change
    MODERATE = "moderate"   # Multiple files, some dependencies
    COMPLEX = "complex"     # Cross-cutting, architectural impact


@dataclass
class TaskContext:
    """Analyzed task context"""
    task_type: TaskType
    complexity: ComplexityLevel
    keywords: List[str]
    entities: Dict[str, List[str]]  # files, functions, components, etc.
    requirements: List[str]
    language: str  # detected language (vietnamese/english)
    original_request: str

    def __str__(self):
        return f"""TaskContext(
    type={self.task_type.value},
    complexity={self.complexity.value},
    keywords={self.keywords[:5]}...,
    entities={len(self.entities)} types,
    requirements={len(self.requirements)} items
)"""


class TaskAnalyzer:
    """Analyzes user requests to extract task context"""

    # Task type patterns
    TASK_PATTERNS = {
        TaskType.FEATURE: [
            r'\b(add|implement|create|build|new|thêm|tạo|xây dựng)\b',
            r'\b(feature|functionality|tính năng|chức năng)\b',
        ],
        TaskType.REFACTOR: [
            r'\b(refactor|restructure|reorganize|improve|clean|tái cấu trúc|cải thiện)\b',
            r'\b(better|cleaner|simpler|đơn giản hơn|tốt hơn)\b',
        ],
        TaskType.DEBUG: [
            r'\b(fix|bug|error|issue|problem|sửa|lỗi|vấn đề)\b',
            r'\b(not working|broken|fails|không hoạt động|bị lỗi)\b',
        ],
        TaskType.ARCHITECTURE: [
            r'\b(design|architecture|structure|pattern|thiết kế|kiến trúc|cấu trúc)\b',
            r'\b(should we|how to|what\'s the best|nên|tốt nhất)\b',
        ],
        TaskType.REVIEW: [
            r'\b(review|analyze|check|evaluate|đánh giá|kiểm tra)\b',
            r'\b(opinion|thoughts|perspective|ý kiến|suy nghĩ)\b',
        ],
        TaskType.OPTIMIZATION: [
            r'\b(optimize|performance|faster|slow|tối ưu|hiệu năng|nhanh hơn)\b',
            r'\b(memory|cache|latency|bộ nhớ|độ trễ)\b',
        ],
        TaskType.TESTING: [
            r'\b(test|testing|unit test|integration|kiểm thử)\b',
            r'\b(coverage|assertion|mock)\b',
        ],
    }

    # Entity extraction patterns
    ENTITY_PATTERNS = {
        'files': r'`([^`]+\.(py|js|tsx|ts|json|md|yml|yaml))`|([a-zA-Z0-9_/\-]+\.(py|js|tsx|ts|json|md))',
        'functions': r'\b(function|def|class|method|hàm|lớp)\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        'components': r'<([A-Z][a-zA-Z0-9]*)|([A-Z][a-zA-Z0-9]*Component)',
        'apis': r'\b(api|endpoint|route|API)\b.*?([/a-z\-]+)',
        'databases': r'\b(database|table|collection|schema|db|bảng|cơ sở dữ liệu)\b\s*:?\s*([a-zA-Z_][a-zA-Z0-9_]*)',
    }

    @classmethod
    def analyze(cls, user_request: str) -> TaskContext:
        """
        Analyze user request and extract task context.

        Args:
            user_request: The user's task description

        Returns:
            TaskContext with analyzed information
        """
        # Detect language
        language = cls._detect_language(user_request)

        # Classify task type
        task_type = cls._classify_task_type(user_request)

        # Extract keywords
        keywords = cls._extract_keywords(user_request)

        # Extract entities (files, functions, components, etc.)
        entities = cls._extract_entities(user_request)

        # Extract requirements
        requirements = cls._extract_requirements(user_request)

        # Estimate complexity
        complexity = cls._estimate_complexity(user_request, entities, requirements)

        return TaskContext(
            task_type=task_type,
            complexity=complexity,
            keywords=keywords,
            entities=entities,
            requirements=requirements,
            language=language,
            original_request=user_request
        )

    @classmethod
    def _detect_language(cls, text: str) -> str:
        """Detect if text is Vietnamese or English"""
        vietnamese_chars = re.findall(r'[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]', text.lower())
        return 'vietnamese' if len(vietnamese_chars) > 3 else 'english'

    @classmethod
    def _classify_task_type(cls, text: str) -> TaskType:
        """Classify the type of task based on keywords"""
        text_lower = text.lower()

        scores = {}
        for task_type, patterns in cls.TASK_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                score += len(matches)
            scores[task_type] = score

        # Get task type with highest score
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)

        return TaskType.UNKNOWN

    @classmethod
    def _extract_keywords(cls, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'của', 'và', 'hoặc', 'trong', 'trên', 'tại', 'cho', 'với'}

        # Extract words
        words = re.findall(r'\b[a-zA-Zàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]{3,}\b', text.lower())

        # Filter stop words and get unique
        keywords = [w for w in words if w not in stop_words]

        # Return top keywords (by frequency)
        from collections import Counter
        counter = Counter(keywords)
        return [word for word, count in counter.most_common(20)]

    @classmethod
    def _extract_entities(cls, text: str) -> Dict[str, List[str]]:
        """Extract entities like files, functions, components, etc."""
        entities = {}

        for entity_type, pattern in cls.ENTITY_PATTERNS.items():
            matches = re.findall(pattern, text)

            # Flatten tuples from regex groups
            flattened = []
            for match in matches:
                if isinstance(match, tuple):
                    # Get first non-empty group
                    flattened.extend([m for m in match if m and len(m) > 0])
                else:
                    flattened.append(match)

            # Remove duplicates and clean
            unique = list(set([m.strip() for m in flattened if m and len(m.strip()) > 0]))

            if unique:
                entities[entity_type] = unique

        return entities

    @classmethod
    def _extract_requirements(cls, text: str) -> List[str]:
        """Extract specific requirements from text"""
        requirements = []

        # Look for bullet points
        bullets = re.findall(r'[-•\*]\s*(.+)', text)
        requirements.extend(bullets)

        # Look for numbered lists
        numbered = re.findall(r'\d+[\.)]\s*(.+)', text)
        requirements.extend(numbered)

        # Look for "need to", "should", "must" statements
        need_patterns = [
            r'(?:need to|needs to|cần phải)\s+(.+?)(?:\.|,|\n|$)',
            r'(?:should|nên)\s+(.+?)(?:\.|,|\n|$)',
            r'(?:must|phải)\s+(.+?)(?:\.|,|\n|$)',
        ]

        for pattern in need_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            requirements.extend(matches)

        # Clean and deduplicate
        cleaned = [req.strip() for req in requirements if len(req.strip()) > 5]
        return list(set(cleaned))[:10]  # Top 10 requirements

    @classmethod
    def _estimate_complexity(cls, text: str, entities: Dict[str, List[str]],
                           requirements: List[str]) -> ComplexityLevel:
        """Estimate task complexity"""
        score = 0

        # More entities = more complex
        total_entities = sum(len(items) for items in entities.values())
        if total_entities > 5:
            score += 2
        elif total_entities > 2:
            score += 1

        # More requirements = more complex
        if len(requirements) > 5:
            score += 2
        elif len(requirements) > 2:
            score += 1

        # Complexity keywords
        complex_keywords = [
            'architecture', 'system', 'integration', 'multiple', 'across',
            'kiến trúc', 'hệ thống', 'tích hợp', 'nhiều', 'toàn bộ'
        ]

        text_lower = text.lower()
        for keyword in complex_keywords:
            if keyword in text_lower:
                score += 1

        # Determine level
        if score >= 4:
            return ComplexityLevel.COMPLEX
        elif score >= 2:
            return ComplexityLevel.MODERATE
        else:
            return ComplexityLevel.SIMPLE


# Example usage and testing
if __name__ == "__main__":
    # Test cases
    test_requests = [
        "Add authentication to the app using NextAuth.js",
        "Refactor the UserService.py to use dependency injection",
        "Fix the bug in api/users endpoint where it returns 500",
        "What's the best architecture for implementing real-time notifications?",
        "Thêm tính năng upload file với preview cho component UploadForm",
    ]

    for req in test_requests:
        print(f"\n{'='*60}")
        print(f"Request: {req}")
        print(f"{'='*60}")
        context = TaskAnalyzer.analyze(req)
        print(context)
        print(f"\nEntities found: {context.entities}")
        print(f"Requirements: {context.requirements}")
