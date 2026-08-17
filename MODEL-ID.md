# MODEL_ID.md - FORGE Model IDs (Single Source of Truth)
# Your Free Tier: Groq + Nvidia + Gemini + OpenRouter
# Agents MUST read this file, never hardcode models

# ========================================
# PLANNER - Reasoning + DAG Generation (Needs strongest reasoning)
# ========================================
planner: groq/openai/gpt-oss-120b
# 120B reasoning beast on Groq - fastest inference for complex planning
# Alternatives you have:
# - nvidia/nemotron-3-ultra-550b-a55b (550B ultra - best for ultra-complex DAGs)
# - gemini/gemini-3.7-flash (Google latest, great function calling)
# - openrouter/google/gemma-4-31b-it:free (free backup)

# ========================================
# VISION - Screenshot Understanding + Self-Healing (Needs vision)
# ========================================
vision: gemini/gemini-3.7-flash
# Gemini Flash has best vision + speed for self-heal (re-locating elements)
# Alternatives you have:
# - nvidia/meta/muse-glimmer-30b (Nvidia vision model)
# - groq/qwen/qwen3.6-27b (Qwen has strong visual grounding)
# - nvidia/google/diffusiongemma-26b-a4b-it (vision + diffusion)

# ========================================
# CODEGEN - Generate FastMCP Python Server Code (Needs code specialist)
# ========================================
codegen: nvidia/poolside/laguna-xs-2.1
# Laguna XS is code-specialized (trained for code generation)
# Alternatives you have:
# - groq/qwen/qwen3.6-27b (Qwen Coder strong)
# - nvidia/minimaxai/minimax-m3 (M3 code + reasoning)
# - nvidia/stepfun-ai/step-3.7-flash (fast code flash)

# ========================================
# EXECUTOR - Fast Tool Calls (Runs 100s of times, needs speed)
# ========================================
executor: groq/llama-3.3-70b-versatile
# Groq 70B versatile - best balance speed + smart for tool execution
# Alternatives you have:
# - groq/qwen/qwen3.6-27b (faster, cheaper)
# - gemini/gemini-3.5-flash-lite (ultra cheap for simple calls)
# - openrouter/google/gemma-4-31b-it:free (free backup)
# - nvidia/nemotron-3.5-lightning-30b-a3b (fast reasoning for re-plans)

# ========================================
# EMBEDDINGS - Chroma Memory
# ========================================
embeddings: nvidia/nv-embed-qa-4
# Alt: gemini/text-embedding-004
# Alt: openrouter/text-embedding-3-small

# ========================================
# EXTRA MODELS YOU HAVE (For experiments / fallbacks)
# ========================================
# - nvidia/nemotron-3.5-lightning-30b-a3b (fast re-planning)
# - nvidia/stepfun-ai/step-3.7-flash (fast code)
# - nvidia/google/diffusiongemma-26b-a4b-it
# - nvidia/meta/muse-glimmer-30b
# - openrouter/dots-studio/dots-3-note-preview:free (long context)
# - openrouter/fish-audio/s2.1-pro-free:free (audio)

# ========================================
# PROVIDER INIT (How to use in code)
# ========================================
# Format: "provider/model/path" -> split first "/" = provider, rest = model ID

# GEMINI:
#   import google.generativeai as genai
#   genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
#   model = genai.GenerativeModel("gemini-3.7-flash")  # strip "gemini/" prefix

# GROQ:
#   from groq import Groq
#   client = Groq(api_key=os.getenv("GROQ_API_KEY"))
#   client.chat.completions.create(model="openai/gpt-oss-120b", ...)  # strip "groq/" prefix

# NVIDIA:
#   from openai import OpenAI
#   client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=os.getenv("NVIDIA_API_KEY"))
#   client.chat.completions.create(model="nvidia/nemotron-3-ultra-550b-a55b", ...)

# OPENROUTER:
#   from openai import OpenAI
#   client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))
#   client.chat.completions.create(model="google/gemma-4-31b-it:free", ...)

# ========================================
# CODE SNIPPET TO LOAD THIS FILE
# ========================================
# def load_model(role):
#     for line in Path("MODEL_ID.md").read_text().splitlines():
#         if line.strip().startswith(f"{role}:"):
#             return line.split(":",1)[1].split("#")[0].strip()
#     return "gemini/gemini-3.7-flash"
