"""
Base class for LLM-powered agents with shared logic.
"""

import logging
from typing import List, Optional
from abc import abstractmethod

from agents.base_agent import BaseAgent
from agents.shared.prompts import get_system_prompt
from agents.shared.language_detector import LanguageDetector
from agents.shared.language_instructions import LanguageInstructions
from agents.shared.convergence_guidance import ConvergenceGuidanceService
from agents.shared.conversation_analyzer import ConversationAnalyzer
from core.message import Message, Role, Signal

# Import new planning system components
from agents.shared.task_analyzer import TaskAnalyzer, TaskContext
from agents.shared.codebase_intelligence import CodebaseIntelligence, CodebaseStructure, RelevantContext
from agents.shared.prompt_generator import PromptGenerator


logger = logging.getLogger(__name__)


class LLMAgentBase(BaseAgent):
    """
    Base class for LLM-powered agents with shared response generation logic.

    Subclasses only need to implement:
    - __init__: Initialize the specific LLM client
    - _call_llm: Make the actual API call to the LLM
    """

    def __init__(self, role: Role, db, config: dict = None):
        super().__init__(role, db, config)

        # Get system prompt based on role (will be dynamically generated)
        self.system_prompt = get_system_prompt(role)

        # Store detected language for the session
        self.detected_language: Optional[str] = None

        # Initialize planning system components
        self.codebase_intelligence: Optional[CodebaseIntelligence] = None
        self.task_context: Optional[TaskContext] = None
        self.use_dynamic_prompts: bool = config.get('use_dynamic_prompts', True) if config else True
        
    @abstractmethod
    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call the LLM API to generate a response.
        
        Args:
            system_prompt: The system prompt
            user_prompt: The user prompt
            
        Returns:
            Generated response text
            
        Raises:
            Exception: If the API call fails
        """
        pass
    
    def generate_response(self, previous_message: Message) -> str:
        """
        Generate response using the LLM model with dynamic planning prompts.

        This method contains all shared logic for:
        - Task analysis and classification
        - Codebase intelligence gathering
        - Dynamic prompt generation
        - Language detection
        - Context building
        - Human intervention detection
        - Convergence guidance

        Args:
            previous_message: The message to respond to

        Returns:
            Generated response text
        """
        # Get the full conversation history
        all_messages = self.db.get_messages(previous_message.session_id)

        # Check if human is requesting STOP/summary
        human_wants_stop = (
            previous_message.role == Role.HUMAN and
            any(keyword in previous_message.content.lower()
                for keyword in ['stop', 'dừng', 'summarize', 'tóm tắt', '🛑'])
        )

        # Determine how much context to load
        if human_wants_stop:
            # Get FULL conversation context for comprehensive summary
            context = self.get_conversation_context(
                previous_message.session_id,
                max_messages=None  # Get ALL messages
            )
            logger.info(
                f"{self.role.value}: Human requested STOP - using FULL conversation context "
                f"({len(all_messages)} messages)"
            )
        else:
            # Get recent context (last 10 messages)
            context = self.get_conversation_context(
                previous_message.session_id,
                max_messages=10
            )

        # Detect language from the first human message (the topic)
        if self.detected_language is None:
            topic = ConversationAnalyzer.extract_topic_from_messages(all_messages)
            if topic:
                self.detected_language = LanguageDetector.detect(topic)
                logger.info(f"{self.role.value}: Detected language = {self.detected_language}")

        # === NEW: Dynamic Planning System ===
        # Analyze task context on first human message
        if self.task_context is None and previous_message.role == Role.HUMAN:
            try:
                self.task_context = TaskAnalyzer.analyze(previous_message.content)
                logger.info(
                    f"{self.role.value}: Task analyzed - "
                    f"Type: {self.task_context.task_type.value}, "
                    f"Complexity: {self.task_context.complexity.value}"
                )
            except Exception as e:
                logger.warning(f"{self.role.value}: Task analysis failed: {e}")

        # Initialize codebase intelligence if RAG is available
        if self.codebase_intelligence is None and self.rag_chain:
            try:
                self.codebase_intelligence = CodebaseIntelligence(self.rag_chain)
                logger.info(f"{self.role.value}: Codebase intelligence initialized")
            except Exception as e:
                logger.warning(f"{self.role.value}: Codebase intelligence init failed: {e}")
        
        # Count agent exchanges
        exchange_count = ConversationAnalyzer.count_agent_exchanges(all_messages)
        
        # Detect human intervention
        human_just_intervened = previous_message.role == Role.HUMAN
        (
            human_wants_stop_flag,
            human_addressing_me,
            human_addressing_other,
            human_asks_to_summarize_other
        ) = ConversationAnalyzer.detect_human_intervention(previous_message, self.role)
        
        # Override human_wants_stop with the more detailed flag
        if human_just_intervened:
            human_wants_stop = human_wants_stop_flag
            
            if human_asks_to_summarize_other:
                other_agent_name = "Agent A" if self.role == Role.AGENT_B else "Agent B"
                logger.info(f"{self.role.value}: Human asks ME to summarize what {other_agent_name} proposed")
            elif human_addressing_me:
                logger.info(f"{self.role.value}: Human is addressing ME specifically")
            elif human_addressing_other:
                logger.info(f"{self.role.value}: Human is addressing the OTHER agent")
            else:
                logger.info(f"{self.role.value}: Human didn't mention specific agent")
        
        # Build language instruction
        language_instruction = LanguageInstructions.get_instructions(
            self.detected_language or 'english'
        )
        
        # Build convergence guidance
        convergence_guidance = ConvergenceGuidanceService.build_convergence_guidance(
            human_wants_stop=human_wants_stop,
            exchange_count=exchange_count,
            language=self.detected_language or 'english'
        )
        
        # Build addressing context
        addressing_context = ConvergenceGuidanceService.build_addressing_context(
            human_just_intervened=human_just_intervened,
            human_asks_to_summarize_other=human_asks_to_summarize_other,
            human_addressing_me=human_addressing_me,
            human_addressing_other=human_addressing_other,
            agent_role=self.role,
            language=self.detected_language or 'english'
        )
        
        # === NEW: Get relevant context using Codebase Intelligence ===
        relevant_context: Optional[RelevantContext] = None
        codebase_structure: Optional[CodebaseStructure] = None

        if self.codebase_intelligence and self.task_context:
            try:
                # Get task-specific relevant context
                relevant_context = self.codebase_intelligence.get_relevant_context(
                    previous_message.content,
                    self.task_context.task_type.value
                )
                logger.info(
                    f"{self.role.value}: Retrieved relevant context - "
                    f"{len(relevant_context.related_files)} files, "
                    f"{len(relevant_context.similar_patterns)} patterns"
                )

                # Analyze overall codebase structure (cached)
                codebase_structure = self.codebase_intelligence.analyze_codebase()
            except Exception as e:
                logger.warning(f"{self.role.value}: Codebase intelligence query failed: {e}")

        # Query RAG for codebase context if available (fallback/additional context)
        rag_context = ""
        if self.rag_chain:
            try:
                rag_result = self.query_rag(previous_message.content)
                if rag_result:
                    # Use PromptGenerator to build context addon
                    if self.use_dynamic_prompts and self.task_context and relevant_context:
                        rag_context = PromptGenerator.build_context_prompt_addon(
                            self.task_context,
                            relevant_context
                        )
                    else:
                        # Fallback to old format
                        rag_context = f"""
📚 CODEBASE CONTEXT (from RAG search):
{rag_result}

Use this codebase context to inform your planning suggestions. Reference specific files/functions when relevant.
"""
                    logger.info(f"{self.role.value}: Retrieved RAG context ({len(rag_result)} chars)")
            except Exception as e:
                logger.warning(f"{self.role.value}: RAG query failed: {e}")

        # Build the user prompt
        user_prompt = f"""Previous conversation:
{context}

Latest message from {previous_message.role.value}:
{previous_message.content}
{rag_context}
Exchange count: {exchange_count} (Total messages: {len(all_messages)})
{addressing_context}

Respond naturally in your characteristic style as {self.role.value}.{language_instruction}{convergence_guidance}"""
        
        try:
            # === NEW: Generate dynamic system prompt if enabled ===
            system_prompt_to_use = self.system_prompt  # Default

            if self.use_dynamic_prompts and self.task_context:
                try:
                    # Generate dynamic prompt based on task context and codebase
                    dynamic_prompt = PromptGenerator.generate_planning_prompt(
                        role=self.role,
                        task_context=self.task_context,
                        codebase_structure=codebase_structure,
                        relevant_context=relevant_context
                    )
                    system_prompt_to_use = dynamic_prompt
                    logger.info(
                        f"{self.role.value}: Using dynamic prompt for "
                        f"{self.task_context.task_type.value} task "
                        f"(complexity: {self.task_context.complexity.value})"
                    )
                except Exception as e:
                    logger.warning(f"{self.role.value}: Dynamic prompt generation failed, using default: {e}")

            # Call the LLM (implemented by subclass)
            generated_text = self._call_llm(system_prompt_to_use, user_prompt)

            logger.info(
                f"{self.role.value} generated {len(generated_text)} chars "
                f"(exchange {exchange_count}) in {self.detected_language or 'english'}"
            )

            return generated_text
            
        except Exception as e:
            logger.error(f"Error calling LLM API: {e}", exc_info=True)
            
            # Get agent type name for better error message
            agent_type = self.__class__.__name__.replace("Agent", "")
            
            # Fallback response if API fails
            if self.detected_language == 'vietnamese':
                return f"⚠️ Xin lỗi, tôi gặp sự cố với {agent_type} API. Lỗi: {str(e)[:100]}... \n\nVui lòng thử lại hoặc chuyển sang agent khác."
            else:
                return f"⚠️ I apologize, I'm having trouble with {agent_type} API. Error: {str(e)[:100]}... \n\nPlease try again or switch to another agent."
    
    def decide_signal(self, response_content: str, conversation_history: List[Message]) -> Signal:
        """
        Decide what signal to send with the response.
        
        🚨 IMPORTANT: Agents can NEVER send STOP signal. Only human can stop the conversation.
        Agents can only send CONTINUE or HANDOVER.
        
        Args:
            response_content: The response that will be sent
            conversation_history: List of previous messages
            
        Returns:
            Signal (CONTINUE or HANDOVER only)
        """
        # Count agent exchanges
        exchange_count = ConversationAnalyzer.count_agent_exchanges(conversation_history)
        
        # Count exchanges since last human input
        exchanges_since_human = ConversationAnalyzer.count_exchanges_since_human(conversation_history)
        
        # Vietnamese agreement/conclusion keywords
        vietnamese_conclusion = [
            "tóm lại", "kết luận", "thống nhất rồi", "quyết định là", 
            "vậy là xong", "oke như vậy", "ok đó là xong", "ổn rồi nhé", 
            "đã rõ ràng", "rõ ràng rồi nhé", "như vậy là tốt", "xong rồi",
            "📌 tóm tắt", "📌 summary"
        ]
        
        vietnamese_agreement = [
            "hoàn toàn đồng ý", "chính xác luôn", "chuẩn không cần chỉnh",
            "tốt lắm", "hay lắm", "ý hay đấy", "được luôn"
        ]
        
        # English agreement/conclusion keywords
        english_conclusion = [
            "in conclusion", "to summarize", "in summary", "final thought", 
            "to conclude", "alright, that's it", "sounds perfect", "let's ship it", 
            "that's our decision", "we're done", "that's settled", "agreed on that",
            "cool, we're aligned", "perfect, let's go"
        ]
        
        english_agreement = [
            "completely agree", "absolutely right", "spot on", "couldn't agree more",
            "that's perfect", "love that approach"
        ]
        
        content_lower = response_content.lower()
        
        # Check for conclusion/agreement signals
        has_strong_conclusion = any(
            keyword in content_lower 
            for keyword in (vietnamese_conclusion + english_conclusion)
        )
        has_strong_agreement = any(
            keyword in content_lower 
            for keyword in (vietnamese_agreement + english_agreement)
        )
        
        # ✋ HANDOVER to human after every 2-3 exchanges (more human involvement)
        if exchanges_since_human >= 2:
            logger.info(
                f"{self.role.value}: 2+ exchanges since human input ({exchanges_since_human}), "
                f"sending HANDOVER for human involvement"
            )
            return Signal.HANDOVER
        
        # If 6+ total exchanges, handover to let human decide next steps
        if exchange_count >= 6:
            logger.info(
                f"{self.role.value}: 6+ exchanges ({exchange_count}), "
                f"sending HANDOVER to let human decide"
            )
            return Signal.HANDOVER
        
        # If showing strong conclusion, handover to let human confirm or continue
        if has_strong_conclusion and exchange_count >= 2:
            logger.info(
                f"{self.role.value}: Strong conclusion detected after {exchange_count} exchanges, "
                f"sending HANDOVER for human confirmation"
            )
            return Signal.HANDOVER
        
        # If strong agreement, handover to let human approve or add thoughts
        if has_strong_agreement and exchange_count >= 2:
            logger.info(
                f"{self.role.value}: Strong agreement detected, "
                f"sending HANDOVER for human input"
            )
            return Signal.HANDOVER
        
        # If explicitly asking for human input
        if "human" in content_lower or "moderator" in content_lower:
            logger.info(f"{self.role.value}: Requesting human input")
            return Signal.HANDOVER
        
        # Default: continue the conversation
        return Signal.CONTINUE

