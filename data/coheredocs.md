from langchain_cohere import ChatCohere
from langchain_core.prompts import ChatPromptTemplate
import base64
from langchain_cohere.react_multi_hop.parsing import parse_answer_with_prefixes
from langchain_core.callbacks import BaseCallbackHandler
import tempfile
import time
import json
from langchain_core.outputs import LLMResult
from langsmith import Client
from langsmith.run_helpers import traceable, trace
import asyncio
from .aws_services import S3Handler
import aiohttp
import os
import logging
from typing import Optional, Dict, Any, List
from .video_manager import VideoManager
from dotenv import load_dotenv
from pydantic import BaseModel, Field

logger = logging.getLogger(**name**)

load_dotenv()

# class ContentRequest(BaseModel):

# """Request model for story generation"""

# prompt: str = Field(..., description="User's content prompt")

# genre: str = Field(..., description="Content category/genre")

# iterations: int = Field(default=4, ge=1, le=10)

class ContentRequest(BaseModel):
"""Request model for story generation"""
prompt: str = Field(..., description="User's content prompt")
genre: str = Field(..., description="Content category/genre")
iterations: int = Field(default=3, ge=1, le=10)
backgroundVideo: str = Field(default="1", description="Background video type")
backgroundMusic: str = Field(default="1", description="Background music type")
voiceType: str = Field(default="v2/en_speaker_6", description="Voice type (male or female)")
subtitleColor: str = Field(default="#ff00ff", description="Subtitle text color")
guidance_scale: int = Field(default=5)
negative_prompt: str = Field(default="Bright tones, overexposed, static, blurred details, subtitles, style, works, paintings, images, static, overall gray, worst quality, low quality, JPEG compression residue, ugly, incomplete, extra fingers, poorly drawn hands, poorly drawn faces, deformed, disfigured, misshapen limbs, fused fingers, still picture, messy background, three legs, many people in the background, walking backwards") # useHfInference: bool = Field(default=False, description="Whether to use Hugging Face Inference API") # hfImageModel: str = Field(default="black-forest-labs/FLUX.1-schnell", description="HF model for image generation") # useHfVideo: bool = Field(default=False, description="Whether to use Hugging Face for video generation") # hfVideoModel: str = Field(default="Wan-AI/Wan2.1-T2V-14B", description="HF model for video generation")

class ContentResponse(BaseModel):
"""Response model for each story iteration"""
story: str
image_description: str
voice_data: Optional[str]
image_url: Optional[str]
iteration: int

class TokenUsageCallback(BaseCallbackHandler):
"""Callback handler to track token usage."""
def **init**(self):
super().**init**()
self.total_tokens = 0
self.prompt_tokens = 0
self.completion_tokens = 0
self.successful_requests = 0
self.failed_requests = 0

    def on_llm_start(self, *args, **kwargs) -> None:
        """Called when LLM starts processing."""
        pass

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Called when LLM ends processing."""
        if response.llm_output and "token_usage" in response.llm_output:
            usage = response.llm_output["token_usage"]
            self.total_tokens += usage.get("total_tokens", 0)
            self.prompt_tokens += usage.get("prompt_tokens", 0)
            self.completion_tokens += usage.get("completion_tokens", 0)
            self.successful_requests += 1
            logger.info(f"Token usage updated - Total: {self.total_tokens}")

    def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        """Called when LLM errors during processing."""
        self.failed_requests += 1
        logger.error(f"LLM error occurred: {str(error)}")

class StoryIterationChain:
def **init**(self, colab_url: Optional[str] = None, voice_url: Optional[str] = None, whisper_url: Optional[str] = None):
self.token_callback = TokenUsageCallback()
self.client = Client()

        self.llm = ChatCohere(
            cohere_api_key=os.getenv("CO_API_KEY"),
            temperature=0.7,
            max_tokens=150,
            callbacks=[self.token_callback]
        )

aiohappyeyeballs==2.4.4
aiohttp==3.11.10
aiosignal==1.3.2
annotated-types==0.7.0
anyio==4.5.0
asgiref==3.8.1
asyncio==3.4.3
attrs==24.2.0
boto3==1.35.22
botocore==1.35.22
certifi==2024.7.4
charset-normalizer==3.3.2
click==8.1.7
cohere==5.13.11
colorama==0.4.6
dataclasses-json==0.6.7
decorator==5.1.1
distro==1.9.0
Django==5.0.7
django-cors-headers==4.4.0
django-filter==24.2
djangorestframework==3.15.2
djangorestframework-simplejwt==5.3.1
fastapi==0.115.6
fastavro==1.9.7
filelock==3.16.1
frozenlist==1.5.0
fsspec==2024.9.0
greenlet==3.1.1
h11==0.14.0
httpcore==1.0.5
httpx==0.27.2
httpx-sse==0.4.0
huggingface-hub==0.25.0
idna==3.7
imageio==2.37.0
imageio-ffmpeg==0.6.0
jiter==0.8.2
jmespath==1.0.1
jsonpatch==1.33
jsonpointer==3.0.0
langchain==0.3.12
langchain-cohere==0.4.2
langchain-community==0.3.12
langchain-core==0.3.31
langchain-openai==0.2.12
langchain-text-splitters==0.3.3
langserve==0.3.0
langsmith==0.2.3
Markdown==3.6
marshmallow==3.23.1
moviepy==2.1.2
multidict==6.1.0
mypy-extensions==1.0.0
numpy==1.26.4
openai==1.57.4
orjson==3.10.12
packaging==24.1
parameterized==0.9.0
pillow==10.4.0
proglog==0.1.10
propcache==0.2.1
psycopg2==2.9.9
PyAudio==0.2.14
pydantic==2.9.2
pydantic-settings==2.7.0
pydantic_core==2.23.4
PyJWT==2.8.0
python-dateutil==2.9.0.post0
python-dotenv==1.0.1
PyYAML==6.0.2
regex==2024.11.6
requests==2.32.3
requests-toolbelt==1.0.0
s3transfer==0.10.2
six==1.16.0
sniffio==1.3.1
SQLAlchemy==2.0.36
sqlparse==0.5.1
sse-starlette==1.8.2
starlette==0.41.3
tenacity==9.0.0
tiktoken==0.8.0
tokenizers==0.20.0
tqdm==4.66.5
types-PyYAML==6.0.12.20241230
types-requests==2.32.0.20240914
typing-inspect==0.9.0
typing_extensions==4.12.2
tzdata==2024.1
urllib3==2.2.2
uvicorn==0.33.0
yarl==1.18.3
