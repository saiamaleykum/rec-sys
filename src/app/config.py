from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    w_click: int
    w_cart: int
    w_purchase: int
    items_limit: int
    brand_limit: int
    csv_data_path: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
