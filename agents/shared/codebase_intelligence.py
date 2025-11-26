"""
Codebase Intelligence Layer - Enhanced RAG analysis for understanding code structure.

This module provides intelligent analysis of the codebase:
- Tech stack detection
- Architectural pattern recognition
- Dependency analysis
- File structure understanding
- Code pattern matching
"""

import re
import json
from typing import List, Dict, Optional, Set, Any
from dataclasses import dataclass
from collections import defaultdict, Counter


@dataclass
class TechStack:
    """Detected technology stack"""
    languages: List[str]
    frameworks: List[str]
    libraries: List[str]
    databases: List[str]
    tools: List[str]

    def __str__(self):
        return f"""TechStack(
    languages={self.languages},
    frameworks={self.frameworks},
    libraries={self.libraries[:5]}{'...' if len(self.libraries) > 5 else ''}
)"""


@dataclass
class CodebaseStructure:
    """Analyzed codebase structure"""
    tech_stack: TechStack
    file_patterns: Dict[str, List[str]]  # type -> file paths
    key_files: List[str]  # Important files (config, entry points)
    dependencies: Dict[str, int]  # library -> usage count
    patterns: List[str]  # Detected architectural patterns
    total_files: int

    def __str__(self):
        return f"""CodebaseStructure(
    tech_stack={self.tech_stack},
    file_patterns={list(self.file_patterns.keys())},
    key_files={len(self.key_files)},
    patterns={self.patterns}
)"""


@dataclass
class RelevantContext:
    """Relevant context for a specific task"""
    related_files: List[Dict[str, Any]]  # file path + content + relevance score
    similar_patterns: List[str]  # Similar code patterns found
    dependencies_to_consider: List[str]
    suggested_approach: str
    tech_stack_context: str

    def __str__(self):
        return f"""RelevantContext(
    related_files={len(self.related_files)} files,
    similar_patterns={len(self.similar_patterns)} patterns,
    dependencies={len(self.dependencies_to_consider)}
)"""


class CodebaseIntelligence:
    """Intelligent analysis of codebase structure and patterns"""

    # Technology detection patterns
    TECH_PATTERNS = {
        'languages': {
            'python': [r'\.py$', r'import \w+', r'def \w+', r'class \w+'],
            'javascript': [r'\.js$', r'const \w+', r'function \w+', r'require\('],
            'typescript': [r'\.ts$', r'\.tsx$', r'interface \w+', r'type \w+'],
            'go': [r'\.go$', r'package \w+', r'func \w+'],
            'rust': [r'\.rs$', r'fn \w+', r'impl \w+'],
        },
        'frameworks': {
            'react': [r'import.*react', r'useState', r'useEffect', r'<[A-Z]\w+'],
            'nextjs': [r'next/\w+', r'getServerSideProps', r'getStaticProps', r'app/page\.tsx'],
            'vue': [r'import.*vue', r'<template>', r'<script setup>'],
            'django': [r'from django', r'models\.Model', r'views\.'],
            'fastapi': [r'from fastapi', r'@app\.', r'APIRouter'],
            'flask': [r'from flask', r'@app\.route'],
            'express': [r'express\(\)', r'app\.get', r'app\.post'],
        },
        'databases': {
            'sqlite': [r'sqlite3?', r'\.db$', r'\.sqlite$'],
            'postgres': [r'postgresql', r'psycopg2', r'pg_'],
            'mysql': [r'mysql', r'pymysql'],
            'mongodb': [r'mongodb', r'mongoose', r'mongo'],
            'redis': [r'redis', r'ioredis'],
        },
        'tools': {
            'docker': [r'Dockerfile', r'docker-compose'],
            'webpack': [r'webpack\.config', r'webpackConfig'],
            'vite': [r'vite\.config', r'import\.meta'],
            'git': [r'\.git/', r'\.gitignore'],
        }
    }

    # Architectural patterns
    ARCHITECTURE_PATTERNS = {
        'mvc': ['models/', 'views/', 'controllers/'],
        'mvvm': ['models/', 'viewmodels/', 'views/'],
        'microservices': ['services/', 'api/', 'gateway/'],
        'layered': ['domain/', 'application/', 'infrastructure/', 'presentation/'],
        'component-based': ['components/', 'containers/', 'hooks/'],
        'rag': ['rag/', 'embeddings/', 'vectorstore'],
    }

    def __init__(self, rag_chain=None):
        """
        Initialize codebase intelligence.

        Args:
            rag_chain: Optional RAG chain for querying codebase
        """
        self.rag_chain = rag_chain
        self._structure_cache: Optional[CodebaseStructure] = None

    def analyze_codebase(self, rag_results: str = None) -> CodebaseStructure:
        """
        Analyze entire codebase structure.

        Args:
            rag_results: Optional RAG query results to analyze

        Returns:
            CodebaseStructure with detected information
        """
        if self._structure_cache:
            return self._structure_cache

        # If no RAG results provided, query for general structure
        if rag_results is None and self.rag_chain:
            rag_results = self._query_rag_for_structure()

        if not rag_results:
            # Return minimal structure
            return CodebaseStructure(
                tech_stack=TechStack([], [], [], [], []),
                file_patterns={},
                key_files=[],
                dependencies={},
                patterns=[],
                total_files=0
            )

        # Detect tech stack
        tech_stack = self._detect_tech_stack(rag_results)

        # Extract file patterns
        file_patterns = self._extract_file_patterns(rag_results)

        # Identify key files
        key_files = self._identify_key_files(rag_results, tech_stack)

        # Analyze dependencies
        dependencies = self._analyze_dependencies(rag_results)

        # Detect architectural patterns
        patterns = self._detect_patterns(rag_results, file_patterns)

        # Count total files
        total_files = sum(len(files) for files in file_patterns.values())

        structure = CodebaseStructure(
            tech_stack=tech_stack,
            file_patterns=file_patterns,
            key_files=key_files,
            dependencies=dependencies,
            patterns=patterns,
            total_files=total_files
        )

        # Cache the result
        self._structure_cache = structure

        return structure

    def get_relevant_context(self, task_description: str, task_type: str) -> RelevantContext:
        """
        Get relevant context for a specific task.

        Args:
            task_description: Description of the task
            task_type: Type of task (feature, refactor, etc.)

        Returns:
            RelevantContext with task-specific information
        """
        # Query RAG for relevant files
        rag_results = ""
        if self.rag_chain:
            try:
                # Use retriever to get documents directly (no LLM call)
                # Try invoke() first (LangChain new API), fallback to get_relevant_documents() (old API)
                try:
                    docs = self.rag_chain.invoke(task_description)
                except AttributeError:
                    docs = self.rag_chain.get_relevant_documents(task_description)

                # Format documents into readable context
                context_parts = []
                for doc in docs:
                    context_parts.append(doc.page_content)
                rag_results = "\n\n".join(context_parts) if context_parts else ""
            except Exception as e:
                print(f"RAG query error: {e}")

        # Parse RAG results to extract files
        related_files = self._parse_related_files(rag_results)

        # Find similar patterns
        similar_patterns = self._find_similar_patterns(task_description, rag_results)

        # Get relevant dependencies
        dependencies = self._extract_relevant_dependencies(task_description, rag_results)

        # Generate suggested approach
        structure = self.analyze_codebase(rag_results)
        suggested_approach = self._generate_suggested_approach(
            task_description, task_type, structure, related_files
        )

        # Build tech stack context
        tech_context = self._build_tech_stack_context(structure.tech_stack)

        return RelevantContext(
            related_files=related_files,
            similar_patterns=similar_patterns,
            dependencies_to_consider=dependencies,
            suggested_approach=suggested_approach,
            tech_stack_context=tech_context
        )

    def _query_rag_for_structure(self) -> str:
        """Query RAG for general codebase structure"""
        queries = [
            "package.json requirements.txt dependencies",
            "main entry point app configuration",
            "folder structure directory layout",
        ]

        results = []
        for query in queries:
            try:
                # Use retriever to get documents directly (no LLM call)
                # Try invoke() first (LangChain new API), fallback to get_relevant_documents() (old API)
                try:
                    docs = self.rag_chain.invoke(query)
                except AttributeError:
                    docs = self.rag_chain.get_relevant_documents(query)

                for doc in docs:
                    results.append(doc.page_content)
            except:
                pass

        return "\n\n".join(results)

    def _detect_tech_stack(self, text: str) -> TechStack:
        """Detect technology stack from code/config"""
        detected = {
            'languages': set(),
            'frameworks': set(),
            'databases': set(),
            'tools': set(),
            'libraries': set(),
        }

        for category, techs in self.TECH_PATTERNS.items():
            for tech_name, patterns in techs.items():
                for pattern in patterns:
                    if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                        detected[category].add(tech_name)
                        break

        # Extract libraries from imports
        libraries = self._extract_libraries(text)
        detected['libraries'] = libraries

        return TechStack(
            languages=sorted(list(detected['languages'])),
            frameworks=sorted(list(detected['frameworks'])),
            libraries=sorted(list(detected['libraries']))[:20],  # Top 20
            databases=sorted(list(detected['databases'])),
            tools=sorted(list(detected['tools']))
        )

    def _extract_libraries(self, text: str) -> Set[str]:
        """Extract library names from imports"""
        libraries = set()

        # Python imports
        python_imports = re.findall(r'(?:from|import)\s+([a-zA-Z_][a-zA-Z0-9_]*)', text)
        libraries.update(python_imports)

        # JS/TS imports
        js_imports = re.findall(r'import.*?from\s+["\']([^"\']+)["\']', text)
        libraries.update([lib.split('/')[0] for lib in js_imports])

        # Package.json dependencies
        package_deps = re.findall(r'"([^"]+)":\s*"[^"]+"', text)
        libraries.update(package_deps)

        # Filter out relative imports and common words
        filtered = {
            lib for lib in libraries
            if not lib.startswith('.') and len(lib) > 2
            and lib not in {'from', 'import', 'as', 'name', 'version'}
        }

        return filtered

    def _extract_file_patterns(self, text: str) -> Dict[str, List[str]]:
        """Extract file patterns by type"""
        patterns = defaultdict(list)

        # Find file paths
        file_paths = re.findall(r'([a-zA-Z0-9_/\-]+\.[a-zA-Z]+)', text)

        for path in file_paths:
            ext = path.split('.')[-1]
            patterns[ext].append(path)

        # Remove duplicates
        return {k: list(set(v)) for k, v in patterns.items()}

    def _identify_key_files(self, text: str, tech_stack: TechStack) -> List[str]:
        """Identify important files in the codebase"""
        key_patterns = [
            r'package\.json',
            r'requirements\.txt',
            r'Dockerfile',
            r'docker-compose\.yml',
            r'\.env',
            r'config\.[jt]s',
            r'settings\.py',
            r'main\.[jt]s',
            r'app\.[jt]s',
            r'index\.[jt]sx?',
            r'README\.md',
        ]

        key_files = []
        for pattern in key_patterns:
            matches = re.findall(rf'([a-zA-Z0-9_/\-]*{pattern})', text)
            key_files.extend(matches)

        return list(set(key_files))[:15]  # Top 15

    def _analyze_dependencies(self, text: str) -> Dict[str, int]:
        """Analyze library usage frequency"""
        libraries = self._extract_libraries(text)

        # Count occurrences
        dependency_count = {}
        for lib in libraries:
            count = len(re.findall(rf'\b{re.escape(lib)}\b', text))
            dependency_count[lib] = count

        # Return top dependencies
        return dict(sorted(dependency_count.items(), key=lambda x: x[1], reverse=True)[:20])

    def _detect_patterns(self, text: str, file_patterns: Dict[str, List[str]]) -> List[str]:
        """Detect architectural patterns"""
        detected_patterns = []

        # Get all file paths
        all_paths = []
        for files in file_patterns.values():
            all_paths.extend(files)

        paths_text = ' '.join(all_paths).lower()

        for pattern_name, indicators in self.ARCHITECTURE_PATTERNS.items():
            matches = sum(1 for indicator in indicators if indicator.lower() in paths_text)
            if matches >= len(indicators) * 0.5:  # At least 50% match
                detected_patterns.append(pattern_name)

        return detected_patterns

    def _parse_related_files(self, rag_results: str) -> List[Dict[str, Any]]:
        """Parse related files from RAG results"""
        files = []

        # Extract file mentions with context
        file_pattern = r'([a-zA-Z0-9_/\-]+\.[a-zA-Z]+)'
        matches = re.finditer(file_pattern, rag_results)

        seen = set()
        for match in matches:
            file_path = match.group(1)
            if file_path not in seen:
                # Get surrounding context
                start = max(0, match.start() - 100)
                end = min(len(rag_results), match.end() + 100)
                context = rag_results[start:end]

                files.append({
                    'path': file_path,
                    'context': context,
                    'relevance_score': 0.8  # Could be enhanced with actual scoring
                })
                seen.add(file_path)

        return files[:10]  # Top 10 most relevant

    def _find_similar_patterns(self, task: str, rag_results: str) -> List[str]:
        """Find similar code patterns in the codebase"""
        patterns = []

        # Look for class definitions
        classes = re.findall(r'class\s+([A-Z][a-zA-Z0-9_]*)', rag_results)
        if classes:
            patterns.append(f"Existing classes: {', '.join(list(set(classes))[:5])}")

        # Look for function patterns
        functions = re.findall(r'(?:def|function)\s+([a-zA-Z_][a-zA-Z0-9_]*)', rag_results)
        if functions:
            patterns.append(f"Function patterns: {', '.join(list(set(functions))[:5])}")

        # Look for React hooks
        hooks = re.findall(r'use[A-Z]\w+', rag_results)
        if hooks:
            patterns.append(f"React hooks used: {', '.join(list(set(hooks))[:5])}")

        return patterns[:5]

    def _extract_relevant_dependencies(self, task: str, rag_results: str) -> List[str]:
        """Extract dependencies relevant to the task"""
        task_lower = task.lower()

        # Map task keywords to libraries
        keyword_lib_map = {
            'auth': ['passport', 'jwt', 'bcrypt', 'next-auth'],
            'database': ['sequelize', 'prisma', 'mongoose', 'typeorm'],
            'api': ['axios', 'fetch', 'express', 'fastapi'],
            'state': ['redux', 'zustand', 'recoil', 'jotai'],
            'form': ['formik', 'react-hook-form', 'yup', 'zod'],
            'ui': ['tailwind', 'mui', 'antd', 'shadcn'],
        }

        relevant = []
        for keyword, libs in keyword_lib_map.items():
            if keyword in task_lower:
                # Check which libs are actually in the codebase
                for lib in libs:
                    if lib in rag_results.lower():
                        relevant.append(lib)

        return list(set(relevant))[:5]

    def _generate_suggested_approach(
        self,
        task: str,
        task_type: str,
        structure: CodebaseStructure,
        related_files: List[Dict[str, Any]]
    ) -> str:
        """Generate a suggested approach based on codebase analysis"""
        suggestions = []

        # Based on tech stack
        if 'react' in structure.tech_stack.frameworks or 'nextjs' in structure.tech_stack.frameworks:
            suggestions.append("Consider React component patterns found in the codebase")

        if 'python' in structure.tech_stack.languages:
            suggestions.append("Follow Python class and function patterns used in existing code")

        # Based on patterns
        if 'component-based' in structure.patterns:
            suggestions.append("Use component-based architecture consistent with existing structure")

        if 'rag' in structure.patterns:
            suggestions.append("Leverage existing RAG system for context-aware features")

        # Based on related files
        if related_files:
            file_dirs = [f['path'].split('/')[0] for f in related_files if '/' in f['path']]
            if file_dirs:
                most_common_dir = Counter(file_dirs).most_common(1)[0][0]
                suggestions.append(f"Place new code in or near '{most_common_dir}/' directory")

        return " | ".join(suggestions) if suggestions else "Follow existing code conventions"

    def _build_tech_stack_context(self, tech_stack: TechStack) -> str:
        """Build a human-readable tech stack context"""
        parts = []

        if tech_stack.languages:
            parts.append(f"Languages: {', '.join(tech_stack.languages)}")

        if tech_stack.frameworks:
            parts.append(f"Frameworks: {', '.join(tech_stack.frameworks)}")

        if tech_stack.databases:
            parts.append(f"Databases: {', '.join(tech_stack.databases)}")

        return " | ".join(parts) if parts else "Tech stack not fully detected"


# Example usage
if __name__ == "__main__":
    # Test with sample RAG results
    sample_rag = """
    File: web/app/page.tsx
    import React from 'react'
    import { useState } from 'react'

    File: package.json
    {
        "dependencies": {
            "react": "^18.0.0",
            "next": "^14.0.0",
            "tailwindcss": "^3.0.0"
        }
    }

    File: agents/base_agent.py
    class BaseAgent:
        def __init__(self):
            pass
    """

    intel = CodebaseIntelligence()
    structure = intel.analyze_codebase(sample_rag)
    print(structure)
    print("\nTech Stack:")
    print(structure.tech_stack)
