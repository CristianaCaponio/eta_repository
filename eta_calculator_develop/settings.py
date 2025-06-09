"""Settings"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    General settings for the service
    """
    project_name: str = "eta_calculator"
    api_version_str: str = '1.0.0'
    host: str = "____"
    port: int = 0000
    error_topic: str = "Unknown-Messages"
    log_level: str = "debug"
    hot_reload: bool = False
