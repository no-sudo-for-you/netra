import os
import time
from pathlib import Path
from threading import Lock

class ModelManager:
    """Manager for local LLM models"""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls, config=None):
        """Singleton pattern to ensure only one model is loaded"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ModelManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self, config=None):
        """Initialize model manager"""
        if self._initialized:
            return
        
        self.config = config or {}
        self.model = None
        self.model_path = self.config.get("llm", {}).get("model_path", "")
        self.model_loaded = False
        self.last_error = None
        
        # Lazy loading - don't load the model until it's needed
        self._initialized = True
    
    def load_model(self, force=False):
        """Load the LLM model"""
        if self.model_loaded and not force:
            return True
        
        try:
            # Only import llama_cpp when we need it
            from llama_cpp import Llama
            
            # Check if model file exists
            if not os.path.exists(self.model_path):
                self.last_error = f"Model file not found: {self.model_path}"
                return False
            
            # Get model parameters from config
            context_size = self.config.get("llm", {}).get("context_size", 4096)
            gpu_layers = self.config.get("llm", {}).get("gpu_layers", 0)
            threads = self.config.get("llm", {}).get("threads", 4)
            
            # Load the model
            start_time = time.time()
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=context_size,
                n_gpu_layers=gpu_layers,
                n_threads=threads,
            )
            load_time = time.time() - start_time
            
            self.model_loaded = True
            print(f"Model loaded in {load_time:.2f} seconds")
            return True
            
        except Exception as e:
            self.last_error = str(e)
            print(f"Error loading model: {e}")
            self.model_loaded = False
            return False
    
    def unload_model(self):
        """Unload the model to free memory"""
        if self.model_loaded:
            self.model = None
            self.model_loaded = False
    
    def get_model(self):
        """Get the loaded model, loading it if necessary"""
        if not self.model_loaded:
            self.load_model()
        return self.model
    
    def generate_text(self, prompt, max_tokens=512, temperature=0.7, stop=None):
        """Generate text from prompt using the model"""
        if not self.model_loaded:
            if not self.load_model():
                return f"Error: {self.last_error}"
        
        try:
            response = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=stop or [],
                echo=False
            )
            
            return response["choices"][0]["text"].strip()
        except Exception as e:
            print(f"Error generating text: {e}")
            return f"Error generating text: {e}"
    
    def is_model_available(self):
        """Check if the model is available"""
        if self.model_loaded:
            return True
        
        return os.path.exists(self.model_path)