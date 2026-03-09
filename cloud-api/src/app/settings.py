import yaml
import logging
import logging.handlers
from pathlib import Path
from pydantic import BaseModel


class LoggingConfig(BaseModel):
    level: str = "INFO"
    file_path: str = "/var/log/rfsite/cloud-api.log"
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 30  # 30 días de rotación


class Settings(BaseModel):
    # Database
    db_dsn: str = "postgresql://rftelemetry:rftelemetry@localhost:5432/rftelemetry"
    
    # Authentication
    auth_required: bool = True
    public_readonly_tenant: str | None = None
    
    # Server
    host: str = "127.0.0.1"
    port: int = 8001
    
    # Logging
    logging: LoggingConfig = LoggingConfig()

    def __init__(self, config_file: str = "/etc/rfsite-cloud-api/config.yaml", **kwargs):
        # Load from config file
        config_data = {}
        
        if Path(config_file).exists():
            print(f"Loading configuration from: {config_file}")
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f) or {}
                print(f"Successfully loaded configuration from: {config_file}")
            except Exception as e:
                print(f"Error: Could not load config file {config_file}: {e}")
                raise
        else:
            print(f"Warning: Config file not found: {config_file}")
            print("Using default configuration")
        
        # Store the config file path for later reference
        self._config_file_used = config_file if Path(config_file).exists() else None
        
        # Handle nested logging config
        if 'logging' in config_data and isinstance(config_data['logging'], dict):
            config_data['logging'] = LoggingConfig(**config_data['logging'])
        
        # Initialize with config data
        super().__init__(**config_data)
        
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


# Global settings instance - will be initialized in main.py
settings: Settings | None = None

def initialize_settings(config_file: str = "/etc/rfsite-cloud-api/config.yaml") -> Settings:
    """Initialize global settings with specified config file"""
    global settings
    settings = Settings(config_file=config_file)
    
    # Create application logger and log startup info
    app_logger = logging.getLogger('app')
    app_logger.info("RF Site Telemetry Cloud API starting up")
    if settings._config_file_used:
        app_logger.info(f"Configuration loaded from: {settings._config_file_used}")
    else:
        app_logger.info("Using default configuration")
    app_logger.info(f"Database DSN: {settings.db_dsn}")
    app_logger.info(f"Auth required: {settings.auth_required}")
    app_logger.info(f"Server: {settings.host}:{settings.port}")
    app_logger.info(f"Log file: {settings.logging.file_path}")
    app_logger.info(f"Log level: {settings.logging.level}")
    
    return settings
