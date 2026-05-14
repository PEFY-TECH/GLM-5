import os
from dataclasses import dataclass, field


@dataclass
class Config:
    api_key: str = field(default_factory=lambda: os.environ.get("ZHIPU_API_KEY", ""))
    base_url: str = "https://open.bigmodel.cn/api/paas/v4/"
    model: str = field(default_factory=lambda: os.environ.get("GLM_MODEL", "glm-4-flash"))
    host: str = field(default_factory=lambda: os.environ.get("HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.environ.get("PORT", "8080")))


config = Config()
