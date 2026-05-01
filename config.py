from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    model: str = "claude-sonnet-4-6"
    # When true, route Claude calls through the local `claude` CLI / Claude Max
    # subscription via claude-agent-sdk instead of the Anthropic REST API.
    use_subscription: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
