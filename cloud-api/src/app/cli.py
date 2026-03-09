import argparse
import sys
from pathlib import Path


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='RF Site Telemetry Cloud API')
    parser.add_argument(
        '--config',
        default='/etc/rfsite-cloud-api/config.yaml',
        help='Path to configuration file (default: /etc/rfsite-cloud-api/config.yaml)'
    )
    return parser.parse_args()


def main():
    """Main entry point for the CLI"""
    args = parse_args()
    
    # Initialize settings with config file
    from .settings import initialize_settings
    settings = initialize_settings(args.config)
    
    # Import and run the FastAPI app
    import uvicorn
    from .main import app
    
    # Run uvicorn with configured host and port
    uvicorn.run(app, host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
