"""
Background service to monitor for new conversation signals and process them.
This runs alongside the web UI to handle conversation continuation.
"""

import os
import time
import logging
from pathlib import Path
from dotenv import load_dotenv
from core.database import Database
from core.coordinator import Coordinator
from core.message import Role, Signal, Message, ConversationMode
from agents.glm_agent import GLMAgent
from agents.gemini_agent import GeminiAgent
from agents.planning_graph import TurnBasedPlanningWorkflow
from agents.shared.language_detector import LanguageDetector
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

STORAGE_DIR = Path(__file__).parent / 'storage'
SIGNAL_DIR = STORAGE_DIR


class ConversationProcessor:
    def __init__(self):
        self.db = Database()
        
        # Load API keys from environment variables
        z_ai_api_key = os.getenv('ZAI_API_KEY')
        z_ai_base_url = os.getenv('ZAI_BASE_URL', 'https://api.z.ai/api/coding/paas/v4')
        glm_model = os.getenv('GLM_MODEL', 'glm-4.5-air')

        gemini_api_key = os.getenv('GEMINI_API_KEY')
        gemini_model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')

        # openai_api_key = os.getenv('OPENAI_API_KEY')
        # openai_base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        # openai_model = os.getenv('OPENAI_MODEL', 'gpt-5')

        max_turn_length = int(os.getenv('MAX_TURN_LENGTH', '10000'))
        
        # Validate required API keys
        if not z_ai_api_key:
            raise ValueError("ZAI_API_KEY not found in environment variables. Please check your .env file.")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables. Please check your .env file.")
        # if not openai_api_key:
        #     raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")
        
        # GLM Configuration for Agent A
        glm_config = {
            "z_ai_api_key": z_ai_api_key,
            "z_ai_base_url": z_ai_base_url,
            "model": glm_model,
            "max_turn_length": max_turn_length
        }

        # openai_config = {
        #     "openai_api_key": openai_api_key,
        #     "openai_base_url": openai_base_url,
        #     "model": openai_model
        # }

        # Gemini Configuration for Agent B
        gemini_config = {
            "gemini_api_key": gemini_api_key,
            "model": gemini_model,
            "max_turn_length": max_turn_length
        }

        # Agent A uses OpenAI, Agent B uses Gemini
        self.agent_a = GLMAgent(Role.AGENT_A, self.db, glm_config)
        # self.agent_b = GeminiAgent(Role.AGENT_B, self.db, gemini_config)
        self.agent_b = GLMAgent(Role.AGENT_B, self.db, glm_config)

        logger.info(f"🤖 Agent A: {glm_model} from z.ai")
        logger.info(f"🤖 Agent B: {gemini_model} from Google")

        # Load RAG chain if codebase exists
        self._load_rag_chain()

        # Initialize LangGraph planning workflow
        self.planning_workflow = TurnBasedPlanningWorkflow(
            db=self.db,
            rag_chain=self.agent_a.rag_chain,
            agent_a=self.agent_a,
            agent_b=self.agent_b
        )
        logger.info("📊 LangGraph planning workflow initialized")

        self.coordinator = Coordinator(self.db)
        self.coordinator.register_agent(Role.AGENT_A, self.agent_a.respond_to)
        self.coordinator.register_agent(Role.AGENT_B, self.agent_b.respond_to)

    def _load_rag_chain(self):
        """Load RAG chain from codebase if it exists."""
        codebase_path = Path(__file__).parent / 'rag' / 'codebase.json'
        if codebase_path.exists():
            try:
                from rag.rag_system import create_rag_system

                logger.info(f"📚 Loading RAG chain from {codebase_path}")
                result = create_rag_system(str(codebase_path))

                rag_chain = result[0] if isinstance(result, tuple) else result

                if rag_chain:
                    self.agent_a.rag_chain = rag_chain
                    self.agent_b.rag_chain = rag_chain
                    self._codebase_mtime = codebase_path.stat().st_mtime
                    logger.info("✅ RAG chain loaded and assigned to both agents")
                else:
                    logger.warning("⚠️ RAG chain creation returned None")
            except Exception as e:
                logger.error(f"❌ Failed to load RAG chain: {e}")
        else:
            logger.info("📭 No codebase.json found, RAG disabled")
            self._codebase_mtime = None

    def _check_and_reload_rag(self):
        """Check if codebase was updated and reload RAG if needed."""
        codebase_path = Path(__file__).parent / 'rag' / 'codebase.json'
        if codebase_path.exists():
            current_mtime = codebase_path.stat().st_mtime
            if not hasattr(self, '_codebase_mtime') or self._codebase_mtime != current_mtime:
                logger.info("🔄 Codebase changed, reloading RAG chain...")
                self._load_rag_chain()
        elif hasattr(self, '_codebase_mtime') and self._codebase_mtime is not None:
            # Codebase was deleted
            logger.info("📭 Codebase removed, disabling RAG")
            self.agent_a.rag_chain = None
            self.agent_b.rag_chain = None
            self._codebase_mtime = None

    def process_signal_file(self, signal_path: Path) -> bool:
        """Process a signal file and start/continue conversation."""
        try:
            # Read and delete signal file
            signal_path.unlink()
            
            # Extract session ID from filename
            filename = signal_path.stem
            if filename.startswith('signal_'):
                session_id = filename.replace('signal_', '')
                logger.info(f"🚀 Starting new conversation for session {session_id}")
                return self._start_conversation(session_id)
            elif filename.startswith('continue_'):
                session_id = filename.replace('continue_', '')
                logger.info(f"💬 Continuing conversation for session {session_id}")
                return self._continue_conversation(session_id)
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing signal file {signal_path}: {e}")
            return False
    
    def _start_conversation(self, session_id: str) -> bool:
        """Start a new conversation - process ONLY ONE turn."""
        try:
            # Get session and initial message (session_id is already a string/UUID)
            session = self.db.get_session(session_id)
            if not session:
                logger.error(f"Session {session_id} not found")
                return False

            messages = self.db.get_messages(session_id)
            if not messages:
                logger.error(f"No messages found for session {session_id}")
                return False

            initial_message = messages[0]

            # Route based on mode
            if session.mode == ConversationMode.PLANNING:
                return self._run_planning_turn(session_id, initial_message, is_start=True)
            else:
                # DEBATE mode uses turn-based conversation via coordinator
                logger.info(f"📋 Debate mode: Processing one turn from: {initial_message.content[:50]}...")
                self.coordinator.auto_continue = False
                response = self.coordinator.process_turn(session.id, initial_message)
                if response:
                    logger.info(f"✅ Turn completed with signal: {response.signal.value}")
                return True

        except Exception as e:
            logger.error(f"Error starting conversation: {e}")
            return False

    def _continue_conversation(self, session_id: str) -> bool:
        """Continue an existing conversation - process ONLY ONE turn."""
        try:
            # Get session (session_id is already a string/UUID)
            session = self.db.get_session(session_id)
            if not session:
                logger.error(f"Session {session_id} not found")
                return False

            # Get all messages
            messages = self.db.get_messages(session_id)
            if not messages:
                logger.error(f"No messages found for session {session_id}")
                return False

            # Get the last message (could be from human or agent)
            last_message = messages[-1]

            # Route based on mode
            if session.mode == ConversationMode.PLANNING:
                # Check if last message is from human (interrupt)
                human_message = last_message if last_message.role == Role.HUMAN else None
                return self._run_planning_turn(session_id, last_message, is_start=False, human_message=human_message)
            else:
                # DEBATE mode - original logic
                is_stop_request = (
                    last_message.role == Role.HUMAN and
                    ('🛑 STOP' in last_message.content or 'stop' in last_message.content.lower())
                )

                if is_stop_request:
                    logger.info("🛑 Human requested STOP. Agents will summarize and conclude.")

                logger.info(f"🔄 Processing one turn from {last_message.role.value}...")
                self.coordinator.auto_continue = False

                response = self.coordinator.process_turn(session.id, last_message)

                if response:
                    logger.info(f"✅ Turn completed with signal: {response.signal.value}")

                    if is_stop_request and response.signal == Signal.HANDOVER:
                        logger.info("✅ Agent provided summary. Marking session as completed.")
                        self.db.update_session_status(session_id, 'completed')

                return True

        except Exception as e:
            logger.error(f"Error continuing conversation: {e}")
            return False

    def _run_planning_turn(self, session_id: str, trigger_message: Message, is_start: bool = False, human_message: Message = None) -> bool:
        """
        Run LangGraph planning workflow until checkpoint or completion.

        Auto-continues through nodes until hitting a HANDOVER signal (checkpoint).

        Args:
            session_id: Session ID
            trigger_message: The message that triggered this turn
            is_start: Whether this is the first turn
            human_message: Human message if this is a human interrupt
        """
        try:
            # Detect language from the trigger message
            language = LanguageDetector.detect(trigger_message.content)

            if is_start:
                # Initialize planning state
                logger.info(f"📊 LangGraph: Starting planning workflow for session {session_id}")
                self.planning_workflow.initialize_state(
                    session_id=session_id,
                    request=trigger_message.content,
                    language=language
                )

            # Execute nodes until we hit a checkpoint (HANDOVER) or complete
            max_iterations = 10  # Safety limit
            iteration = 0

            while iteration < max_iterations:
                iteration += 1

                # Execute one turn
                logger.info(f"📊 LangGraph: Executing turn {iteration} (human_interrupt={human_message is not None})")
                state, response = self.planning_workflow.execute_one_turn(
                    session_id=session_id,
                    human_message=human_message
                )

                # Clear human_message after first iteration (only applies to first node)
                human_message = None

                if response:
                    # Save response to database
                    saved_response = self.db.add_message(response)
                    logger.info(f"✅ [v2] LangGraph turn {iteration}: {response.role.value} - signal={response.signal.value}")
                    logger.info(f"📊 Current node: {state.get('current_node', 'unknown')}")
                    logger.info(f"📊 Response content length: {len(response.content)} chars")

                    # If planning completed, DON'T mark session as completed - allow human to continue
                    if state.get('current_node') == 'completed':
                        logger.info("✅ Planning workflow completed - waiting for human input to continue")
                        # Don't mark as completed - session stays active for continuous conversation
                        # self.db.update_session_status(session_id, 'completed')
                        break

                    # If HANDOVER, stop and wait for human
                    if response.signal == Signal.HANDOVER:
                        logger.info(f"🛑 Checkpoint reached after {iteration} turns. Waiting for human.")
                        break

                    # If CONTINUE, proceed to next node
                    if response.signal == Signal.CONTINUE:
                        logger.info(f"➡️ Auto-continuing to next node...")
                        continue
                else:
                    logger.warning("No response from workflow")
                    break

            return True

        except Exception as e:
            logger.error(f"Error in planning turn: {e}", exc_info=True)
            return False
    
    def run(self):
        """Main loop to monitor for signal files."""
        logger.info("🔍 Conversation processor started. Monitoring for signals...")
        logger.info(f"📁 Monitoring directory: {SIGNAL_DIR}")
        
        while True:
            try:
                # Check if codebase was updated and reload RAG if needed
                self._check_and_reload_rag()

                # Check for signal files
                signal_files = list(SIGNAL_DIR.glob('signal_*.txt')) + \
                              list(SIGNAL_DIR.glob('continue_*.txt'))

                for signal_file in signal_files:
                    logger.info(f"📨 Found signal: {signal_file.name}")
                    self.process_signal_file(signal_file)

                # Sleep before next check
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("👋 Shutting down conversation processor...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(5)  # Wait a bit longer on errors


if __name__ == '__main__':
    processor = ConversationProcessor()
    processor.run()

