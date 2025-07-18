"""
AutoGen framework detector
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
class AutoGenAgent:
    """Represents an AutoGen agent"""
    name: str
    agent_type: str  # AssistantAgent, UserProxyAgent, etc
    model: Optional[str] = None
    system_message: Optional[str] = None
    max_consecutive_auto_reply: int = 10
    human_input_mode: str = "NEVER"
    code_execution_config: Optional[Dict[str, Any]] = None


class AutoGenDetector(BaseDetector):
    """Detector for Microsoft AutoGen framework"""
    
    def get_framework_name(self) -> str:
        return "autogen"
    
    def _setup_patterns(self):
        """Setup AutoGen-specific patterns"""
        
        # File patterns
        self.file_patterns = [
            FilePattern("**/autogen*.py", description="AutoGen-named files"),
            FilePattern("**/agent*.py", description="Agent files"),
            FilePattern("**/groupchat*.py", description="Group chat files"),
            FilePattern(".cache/", description="AutoGen cache directory"),
        ]
        
        # Code patterns
        self.code_patterns = [
            CodePattern(
                r"AssistantAgent\s*\(",
                [".py"],
                weight=2.0,
                description="AssistantAgent initialization"
            ),
            CodePattern(
                r"UserProxyAgent\s*\(",
                [".py"],
                weight=2.0,
                description="UserProxyAgent initialization"
            ),
            CodePattern(
                r"GroupChat\s*\(",
                [".py"],
                weight=1.5,
                description="GroupChat usage"
            ),
            CodePattern(
                r"GroupChatManager\s*\(",
                [".py"],
                weight=1.5,
                description="GroupChatManager usage"
            ),
            CodePattern(
                r"initiate_chat\s*\(",
                [".py"],
                weight=1.0,
                description="Chat initiation"
            ),
            CodePattern(
                r"register_reply\s*\(",
                [".py"],
                weight=1.0,
                description="Reply registration"
            ),
            CodePattern(
                r"ConversableAgent\s*\(",
                [".py"],
                weight=1.5,
                description="ConversableAgent usage"
            ),
        ]
        
        # Import patterns
        self.import_patterns = [
            "autogen",
            "autogen.agentchat",
            "autogen.oai",
            "ag2",
        ]
        
        # Config files
        self.config_files = [
            "OAI_CONFIG_LIST",
            ".env",  # Often contains OpenAI keys for AutoGen
            "config_list.json",
        ]
    
    def extract_components(self, file_content: str, file_path: str) -> List[Component]:
        """Extract AutoGen agents and components"""
        components = []
        
        if not file_path.endswith('.py'):
            return components
        
        try:
            # Parse the Python AST
            tree = ast.parse(file_content)
            
            # Find agent instantiations
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if hasattr(node.func, 'id'):
                        # Direct function call
                        func_name = node.func.id
                    elif hasattr(node.func, 'attr'):
                        # Method call
                        func_name = node.func.attr
                    else:
                        continue
                    
                    # Check if it's an agent creation
                    if func_name in ['AssistantAgent', 'UserProxyAgent', 'ConversableAgent']:
                        component = self._extract_agent_info(node, func_name, file_path, file_content)
                        if component:
                            components.append(component)
                    
                    # Check for GroupChat
                    elif func_name == 'GroupChat':
                        component = self._extract_groupchat_info(node, file_path, file_content)
                        if component:
                            components.append(component)
        
        except (SyntaxError, ValueError):
            # If AST parsing fails, fall back to regex
            components.extend(self._regex_extract_components(file_content, file_path))
        
        return components
    
    def _extract_agent_info(self, node: ast.Call, agent_type: str, 
                          file_path: str, file_content: str) -> Optional[Component]:
        """Extract information from agent creation node"""
        
        # Get line number
        line_number = node.lineno if hasattr(node, 'lineno') else 0
        
        # Extract arguments
        agent_info = {
            'type': agent_type,
            'llm_config': None,
            'system_message': None,
            'name': None,
        }
        
        # Parse keyword arguments
        for keyword in node.keywords:
            if keyword.arg == 'name' and isinstance(keyword.value, ast.Str):
                agent_info['name'] = keyword.value.s
            elif keyword.arg == 'system_message' and isinstance(keyword.value, ast.Str):
                agent_info['system_message'] = keyword.value.s
            elif keyword.arg == 'llm_config' and isinstance(keyword.value, ast.Dict):
                agent_info['llm_config'] = self._parse_llm_config(keyword.value)
        
        # If no name found, try first positional argument
        if not agent_info['name'] and node.args and isinstance(node.args[0], ast.Str):
            agent_info['name'] = node.args[0].s
        
        # Generate name if still not found
        if not agent_info['name']:
            agent_info['name'] = f"{agent_type}_{line_number}"
        
        # Estimate tokens
        tokens = 0
        if agent_info['system_message']:
            tokens += self.estimate_tokens(agent_info['system_message'])
        
        # Extract model from llm_config
        model = None
        if agent_info['llm_config'] and 'model' in agent_info['llm_config']:
            model = agent_info['llm_config']['model']
        
        return Component(
            name=agent_info['name'],
            type='agent',
            file_path=file_path,
            line_number=line_number,
            model=model,
            estimated_tokens=tokens,
            metadata={
                'agent_type': agent_type,
                'system_message': agent_info['system_message'],
                'llm_config': agent_info['llm_config']
            }
        )
    
    def _parse_llm_config(self, dict_node: ast.Dict) -> Dict[str, Any]:
        """Parse llm_config dictionary from AST"""
        config = {}
        
        for key, value in zip(dict_node.keys, dict_node.values):
            if isinstance(key, ast.Str):
                key_name = key.s
                
                if isinstance(value, ast.Str):
                    config[key_name] = value.s
                elif isinstance(value, ast.Num):
                    config[key_name] = value.n
                elif isinstance(value, ast.List):
                    # Handle model list
                    if key_name == 'model' and value.elts:
                        models = []
                        for elt in value.elts:
                            if isinstance(elt, ast.Str):
                                models.append(elt.s)
                        if models:
                            config[key_name] = models[0]  # Take first model
                
        return config
    
    def _extract_groupchat_info(self, node: ast.Call, file_path: str, 
                              file_content: str) -> Optional[Component]:
        """Extract GroupChat information"""
        line_number = node.lineno if hasattr(node, 'lineno') else 0
        
        # Extract agents list
        agents_count = 0
        for keyword in node.keywords:
            if keyword.arg == 'agents' and isinstance(keyword.value, ast.List):
                agents_count = len(keyword.value.elts)
        
        return Component(
            name=f"GroupChat_{line_number}",
            type='groupchat',
            file_path=file_path,
            line_number=line_number,
            metadata={
                'agents_count': agents_count
            }
        )
    
    def _regex_extract_components(self, file_content: str, file_path: str) -> List[Component]:
        """Fallback regex-based extraction"""
        components = []
        lines = file_content.split('\n')
        
        # Pattern for agent creation
        agent_pattern = re.compile(
            r'(\w+)\s*=\s*(AssistantAgent|UserProxyAgent|ConversableAgent)\s*\('
        )
        
        for i, line in enumerate(lines):
            match = agent_pattern.search(line)
            if match:
                agent_name = match.group(1)
                agent_type = match.group(2)
                
                # Try to find system message in next few lines
                system_message = None
                for j in range(i, min(i + 20, len(lines))):
                    if 'system_message' in lines[j]:
                        # Simple extraction
                        msg_match = re.search(r'system_message\s*=\s*["\'](.+?)["\']', 
                                            lines[j], re.DOTALL)
                        if msg_match:
                            system_message = msg_match.group(1)
                            break
                
                tokens = self.estimate_tokens(system_message) if system_message else 0
                
                components.append(Component(
                    name=agent_name,
                    type='agent',
                    file_path=file_path,
                    line_number=i + 1,
                    estimated_tokens=tokens,
                    metadata={
                        'agent_type': agent_type,
                        'system_message': system_message
                    }
                ))
        
        return components
    
    def analyze_conversation_flow(self, components: List[Component], 
                                file_contents: Dict[str, str]) -> List[Dict[str, Any]]:
        """Analyze conversation patterns between agents"""
        flows = []
        
        # Look for initiate_chat patterns
        chat_pattern = re.compile(
            r'(\w+)\.initiate_chat\s*\(\s*(\w+)'
        )
        
        for file_path, content in file_contents.items():
            matches = chat_pattern.findall(content)
            for initiator, recipient in matches:
                flows.append({
                    'type': 'chat',
                    'from': initiator,
                    'to': recipient,
                    'file': file_path
                })
        
        # Look for group chat patterns
        groupchat_components = [c for c in components if c.type == 'groupchat']
        for gc in groupchat_components:
            if 'agents_count' in gc.metadata:
                flows.append({
                    'type': 'groupchat',
                    'agents_count': gc.metadata['agents_count'],
                    'file': gc.file_path
                })
        
        return flows
    
    def detect(self, file_paths: List[str], file_contents: Dict[str, str]) -> DetectionResult:
        """Enhanced detection for AutoGen"""
        # Get base detection
        result = super().detect(file_paths, file_contents)
        
        # Add workflow analysis
        if result.components:
            result.workflow_patterns = self.analyze_conversation_flow(
                result.components, file_contents
            )
        
        # Check for AutoGen-specific patterns that increase confidence
        for content in file_contents.values():
            # Check for config list pattern
            if 'config_list' in content and ('gpt-4' in content or 'gpt-3' in content):
                result.confidence_score += 10
            
            # Check for typical AutoGen patterns
            if 'TERMINATE' in content and 'initiate_chat' in content:
                result.confidence_score += 5
        
        # Recalculate confidence
        if result.confidence_score >= 75:
            result.confidence = FrameworkConfidence.HIGH
        elif result.confidence_score >= 40:
            result.confidence = FrameworkConfidence.MEDIUM
        elif result.confidence_score >= 10:
            result.confidence = FrameworkConfidence.LOW
        
        return result