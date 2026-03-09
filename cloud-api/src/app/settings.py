import os
import yaml
import logging
import logging.handlers
from pathlib import Path
from typing import Dict, Any
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingConfig(BaseModel):
    level: str = "INFO"
    file_path: str = "/var/log/rfsite/cloud-api.log"
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 30  # 30 días de rotación


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    db_dsn: str = "postgresql://rftelemetry:rftelemetry@localhost:5432/rftelemetry"
    
    # Authentication
    auth_required: bool = True  # in cloud: keep True; in local dev you can set AUTH_REQUIRED=0
    public_readonly_tenant: str | None = None  # e.g. "demo"
    
    # Logging
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    # Config file path (can be set via env var CONFIG_FILE)
    config_file: str | None = None

    def __init__(self, **kwargs):
        # First load from config file if specified
        config_data = {}
        config_file = kwargs.get('config_file') or os.getenv('CONFIG_FILE')
        
        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Warning: Could not load config file {config_file}: {e}")
        
        # Merge config file data with kwargs, giving precedence to kwargs (env vars)
        merged_data = {**config_data, **kwargs}
        
        # Handle nested logging config
        if 'logging' in config_data and isinstance(config_data['logging'], dict):
            logging_config = LoggingConfig(**config_data['logging'])
            merged_data['logging'] = logging_config
        
        super().__init__(**merged_data)
        
        # Setup logging after initialization
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging with daily rotation"""
        # Create log directory if it doesn't exist
        log_path = Path(self.logging.file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure specific loggers instead of root logger to avoid conflicts with uvicorn
        log_level = getattr(logging, self.logging.level.upper(), logging.INFO)
        
        # File handler with daily rotation
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=self.logging.file_path,
            when='midnight',
            interval=1,
            backupCount=self.logging.backup_count,
            encoding='utf-8'
        )
        file_handler.suffix = '%Y-%m-%d'
        file_handler.setLevel(log_level)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Configure application loggers
        app_loggers = [
            'app',
            'app.main',
            'app.auth',
            'app.db',
            'uvicorn.access',
            'uvicorn.error'
        ]
        
        for logger_name in app_loggers:
            logger = logging.getLogger(logger_name)
            logger.setLevel(log_level)
            
            # Remove existing file handlers to avoid duplicates
            for handler in logger.handlers[:]:
                if isinstance(handler, (logging.FileHandler, logging.handlers.TimedRotatingFileHandler)):
                    logger.removeHandler(handler)
            
            # Add our file handler
            logger.addHandler(file_handler)
            
            # Ensure logs propagate to parent (for console output)
            logger.propagate = True
        
        # Also configure root logger for any other logs
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Add file handler to root logger if not already present
        has_file_handler = any(
            isinstance(h, (logging.FileHandler, logging.handlers.TimedRotatingFileHandler))
            for h in root_logger.handlers
        )
        if not has_file_handler:
            root_logger.addHandler(file_handler)


# Global settings instance
settings = Settings()

# Create application logger
app_logger = logging.getLogger('app')
app_logger.info("RF Site Telemetry Cloud API starting up")
