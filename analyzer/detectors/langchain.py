"""
LangChain framework detector
Time estimate: 3 hours
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import ast

from .base import (
    BaseDetector, 
    Component, 
    FilePattern, 
    CodePattern,
    DetectionResult,
    FrameworkConfidence
)


@dataclass
class LangChainComponent:
    """Represents a LangChain component"""
    name: str
    component_type: str  # chain, agent, tool, memory, etc
    model: Optional[str] = None
    prompt_template: Optional[str] = None
    tools: List[str] = None


class LangChainDetector(BaseDetector):
    """Detector for LangChain framework"""
    
    def get_framework_name(self) -> str:
        return "langchain"
    
    def _setup_patterns(self):
        """Setup LangChain-specific patterns"""
        
        # File patterns
        self.file_patterns = [
            FilePattern("**/langchain*.py", description="LangChain-named files"),
            FilePattern("**/chain*.py", description="Chain files"),
            FilePattern("**/agent*.py", description="Agent files"),
            FilePattern("**/prompt*.py", description="Prompt files"),
            FilePattern("**/memory*.py", description="Memory files"),
        ]
        
        # Code patterns
        self.code_patterns = [
            CodePattern(
                r"LLMChain\s*\(",
                [".py"],
                weight=2.0,
                description="LLMChain usage"
            ),
            CodePattern(
                r"ChatOpenAI\s*\(",
                [".py"],
                weight=2.0,
                description="ChatOpenAI model"
            ),
            CodePattern(
                r"OpenAI\s*\(",
                [".py"],
                weight=2.0,
                description="OpenAI model"
            ),
            CodePattern(
                r"PromptTemplate\s*\(",
                [".py"],
                weight=1.5,
                description="PromptTemplate usage"
            ),
            CodePattern(
                r"ChatPromptTemplate\s*\(",
                [".py"],
                weight=1.5,
                description="ChatPromptTemplate usage"
            ),
            CodePattern(
                r"ConversationChain\s*\(",
                [".py"],
                weight=1.5,
                description="ConversationChain usage"
            ),
            CodePattern(
                r"RetrievalQA\s*\(",
                [".py"],
                weight=1.5,
                description="RetrievalQA chain"
            ),
            CodePattern(
                r"create_.*_agent\s*\(",
                [".py"],
                weight=1.5,
                description="Agent creation"
            ),
            CodePattern(
                r"Tool\s*\(",
                [".py"],
                weight=1.0,
                description="Tool definition"
            ),
            CodePattern(
                r"ConversationBufferMemory\s*\(",
                [".py"],
                weight=1.0,
                description="Memory usage"
            ),
        ]
        
        # Import patterns
        self.import_patterns = [
            "langchain",
            "langchain.llms",
            "langchain.chat_models",
            "langchain.chains",
            "langchain.agents",
            "langchain.prompts",
            "langchain.memory",
            "langchain.tools",
            "langchain.vectorstores",
            "langchain.embeddings",
            "langchain_community",
            "langchain_openai",
        ]
        
        # Config files
        self.config_files = [
            ".env",  # Often contains API keys
            "langchain.yaml",
            "config.yaml",
        ]
    
    def extract_components(self, file_content: str, file_path: str) -> List[Component]:
        """Extract LangChain components"""
        components = []
        
        if not file_path.endswith('.py'):
            return components
        
        try:
            # Parse the Python AST
            tree = ast.parse(file_content)
            
            # Find component instantiations
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    component = self._extract_component_from_call(node, file_path, file_content)
                    if component:
                        components.append(component)
        
        except (SyntaxError, ValueError):
            # If AST parsing fails, fall back to regex
            components.extend(self._regex_extract_components(file_content, file_path))
        
        return components
    
    def _extract_component_from_call(self, node: ast.Call, file_path: str, 
                                   file_content: str) -> Optional[Component]:
        """Extract component information from AST call node"""
        
        # Get function name
        func_name = None
        if hasattr(node.func, 'id'):
            func_name = node.func.id
        elif hasattr(node.func, 'attr'):
            func_name = node.func.attr
        else:
            return None
        
        # Map function names to component types
        component_map = {
            'LLMChain': 'chain',
            'ConversationChain': 'chain',
            'RetrievalQA': 'chain',
            'ChatOpenAI': 'llm',
            'OpenAI': 'llm',
            'PromptTemplate': 'prompt',
            'ChatPromptTemplate': 'prompt',
            'ConversationBufferMemory': 'memory',
            'Tool': 'tool',
        }
        
        if func_name not in component_map:
            # Check for agent creation
            if 'agent' in func_name.lower():
                component_type = 'agent'
            else:
                return None
        else:
            component_type = component_map[func_name]
        
        # Get line number
        line_number = node.lineno if hasattr(node, 'lineno') else 0
        
        # Extract relevant information
        component_info = {
            'type': component_type,
            'function': func_name,
            'model': None,
            'template': None,
            'tokens': 0
        }
        
        # Parse arguments based on component type
        if component_type == 'llm':
            component_info.update(self._parse_llm_args(node))
        elif component_type == 'prompt':
            component_info.update(self._parse_prompt_args(node))
        elif component_type == 'chain':
            component_info.update(self._parse_chain_args(node))
        
        # Generate component name
        component_name = f"{func_name}_{line_number}"
        
        return Component(
            name=component_name,
            type=component_type,
            file_path=file_path,
            line_number=line_number,
            model=component_info.get('model'),
            estimated_tokens=component_info.get('tokens', 0),
            metadata=component_info
        )
    
    def _parse_llm_args(self, node: ast.Call) -> Dict[str, Any]:
        """Parse LLM-specific arguments"""
        info = {'model': None, 'temperature': None}
        
        for keyword in node.keywords:
            if keyword.arg == 'model' and isinstance(keyword.value, ast.Str):
                info['model'] = keyword.value.s
            elif keyword.arg == 'model_name' and isinstance(keyword.value, ast.Str):
                info['model'] = keyword.value.s
            elif keyword.arg == 'temperature' and isinstance(keyword.value, ast.Num):
                info['temperature'] = keyword.value.n
        
        # Default models if not specified
        if not info['model']:
            if 'ChatOpenAI' in str(node.func):
                info['model'] = 'gpt-3.5-turbo'
            elif 'OpenAI' in str(node.func):
                info['model'] = 'text-davinci-003'
        
        return info
    
    def _parse_prompt_args(self, node: ast.Call) -> Dict[str, Any]:
        """Parse prompt template arguments"""
        info = {'template': None, 'tokens': 0}
        
        # Try to get template from arguments
        if node.args and isinstance(node.args[0], ast.Str):
            info['template'] = node.args[0].s
            info['tokens'] = self.estimate_tokens(node.args[0].s)
        
        # Check keywords
        for keyword in node.keywords:
            if keyword.arg == 'template' and isinstance(keyword.value, ast.Str):
                info['template'] = keyword.value.s
                info['tokens'] = self.estimate_tokens(keyword.value.s)
        
        return info
    
    def _parse_chain_args(self, node: ast.Call) -> Dict[str, Any]:
        """Parse chain arguments"""
        info = {'llm': None, 'prompt': None}
        
        for keyword in node.keywords:
            if keyword.arg == 'llm':
                # Try to get model info from llm
                if hasattr(keyword.value, 'id'):
                    info['llm'] = keyword.value.id
            elif keyword.arg == 'prompt':
                if hasattr(keyword.value, 'id'):
                    info['prompt'] = keyword.value.id
        
        return info
    
    def _regex_extract_components(self, file_content: str, file_path: str) -> List[Component]:
        """Fallback regex-based extraction"""
        components = []
        lines = file_content.split('\n')
        
        # Patterns for different components
        patterns = [
            (r'(\w+)\s*=\s*LLMChain\s*\(', 'chain'),
            (r'(\w+)\s*=\s*ChatOpenAI\s*\(', 'llm'),
            (r'(\w+)\s*=\s*OpenAI\s*\(', 'llm'),
            (r'(\w+)\s*=\s*PromptTemplate\s*\(', 'prompt'),
            (r'(\w+)\s*=\s*ConversationChain\s*\(', 'chain'),
            (r'(\w+)\s*=\s*RetrievalQA\s*\(', 'chain'),
        ]
        
        for i, line in enumerate(lines):
            for pattern, comp_type in patterns:
                match = re.search(pattern, line)
                if match:
                    comp_name = match.group(1)
                    
                    # Try to extract model info
                    model = None
                    if comp_type == 'llm':
                        # Look for model parameter
                        for j in range(i, min(i + 5, len(lines))):
                            model_match = re.search(r'model\s*=\s*["\'](.+?)["\']', lines[j])
                            if model_match:
                                model = model_match.group(1)
                                break
                    
                    components.append(Component(
                        name=comp_name,
                        type=comp_type,
                        file_path=file_path,
                        line_number=i + 1,
                        model=model,
                        metadata={'component_class': pattern.split('=')[1].strip()}
                    ))
        
        return components
    
    def analyze_chain_flow(self, components: List[Component], 
                         file_contents: Dict[str, str]) -> List[Dict[str, Any]]:
        """Analyze how chains are connected"""
        flows = []
        
        # Look for chain execution patterns
        run_patterns = [
            re.compile(r'(\w+)\.run\s*\('),
            re.compile(r'(\w+)\.invoke\s*\('),
            re.compile(r'(\w+)\.call\s*\('),
            re.compile(r'(\w+)\.predict\s*\('),
        ]
        
        for file_path, content in file_contents.items():
            for pattern in run_patterns:
                matches = pattern.findall(content)
                for chain_name in matches:
                    # Check if this matches a known component
                    matching_comp = next((c for c in components if c.name == chain_name), None)
                    if matching_comp:
                        flows.append({
                            'type': 'execution',
                            'component': chain_name,
                            'component_type': matching_comp.type,
                            'file': file_path
                        })
        
        # Look for sequential chains
        seq_pattern = re.compile(r'SequentialChain\s*\([^)]*chains\s*=\s*\[([^\]]+)\]')
        for file_path, content in file_contents.items():
            matches = seq_pattern.findall(content)
            for match in matches:
                # Extract chain names
                chain_names = [n.strip() for n in match.split(',')]
                flows.append({
                    'type': 'sequential',
                    'chains': chain_names,
                    'file': file_path
                })
        
        return flows
    
    def detect(self, file_paths: List[str], file_contents: Dict[str, str]) -> DetectionResult:
        """Enhanced detection for LangChain"""
        # Get base detection
        result = super().detect(file_paths, file_contents)
        
        # Add workflow analysis
        if result.components:
            result.workflow_patterns = self.analyze_chain_flow(
                result.components, file_contents
            )
        
        # Check for LangChain-specific patterns
        for content in file_contents.values():
            # Check for LCEL (LangChain Expression Language)
            if '|' in content and ('invoke' in content or 'stream' in content):
                result.confidence_score += 10
            
            # Check for typical LangChain patterns
            if 'RunnablePassthrough' in content or 'RunnableParallel' in content:
                result.confidence_score += 15
            
            # Vector store usage
            if any(vs in content for vs in ['FAISS', 'Chroma', 'Pinecone', 'Weaviate']):
                result.confidence_score += 5
        
        # Recalculate confidence
        if result.confidence_score >= 75:
            result.confidence = FrameworkConfidence.HIGH
        elif result.confidence_score >= 40:
            result.confidence = FrameworkConfidence.MEDIUM
        elif result.confidence_score >= 10:
            result.confidence = FrameworkConfidence.LOW
        
        return result