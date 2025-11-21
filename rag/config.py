"""
Configuration module for RAG Codebase Search App
Handles all environment variables and application settings
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Flask configuration
SECRET_KEY = 'your-secret-key-here'
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'md', 'json'}

# Ollama configuration
USE_OLLAMA = os.getenv("USE_OLLAMA", "true").lower() == "true"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Embeddings configuration
USE_LOCAL_EMBEDDINGS = os.getenv("USE_LOCAL_EMBEDDINGS", "true").lower() == "true"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Ollama generation configuration
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "8000"))

# GLM configuration
USE_GLM = os.getenv("USE_GLM", "false").lower() == "true"
GLM_API_KEY = os.getenv("GLM_API_KEY", os.getenv("ZAI_API_KEY"))
GLM_MODEL = os.getenv("GLM_MODEL", "glm-4.6")
GLM_BASE_URL = os.getenv("GLM_BASE_URL", os.getenv("ZAI_BASE_URL", "https://api.z.ai/api/coding/paas/v4"))
GLM_MAX_TOKENS = int(os.getenv("GLM_MAX_TOKENS", "32768"))
GLM_TEMPERATURE = float(os.getenv("GLM_TEMPERATURE", "0.7"))

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

