from pydantic import BaseModel, ConfigDict, Field
from app.services.preprocessing import CLUSTER_DEFAULT, REGRESSION_DEFAULT


class ClusterRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    features: list[str] = Field(default_factory=lambda: CLUSTER_DEFAULT.copy(), min_length=2, max_length=6)
    k: int = Field(default=3, ge=2, le=4)
    sensitivity: bool = False


class RegressionRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    features: list[str] = Field(default_factory=lambda: REGRESSION_DEFAULT.copy(), min_length=1, max_length=4)

