from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Target links file path
    TARGET_LINKS_FILE_PATH: str = "target_links.txt"

    # Proxies file path
    PROXIES_FILE_PATH: str = "proxies.txt"

    # Application
    DEBUG: bool = True

    # Browser
    HEADLESS: bool = False
    BROWSER_VERSION: str = ""
    LICENSE_KEY: str = ""

    @property
    def TARGET_LINKS(self) -> list[str]:
        with open(self.TARGET_LINKS_FILE_PATH, "r", encoding="utf-8") as file:
            return [line.strip() for line in file if line.strip()]

    @property
    def PROXIES(self) -> list[str]:
        with open(self.PROXIES_FILE_PATH, "r", encoding="utf-8") as file:
            return [line.strip() for line in file if line.strip()]


settings = Settings()
