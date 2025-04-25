from pydantic import ConfigDict, BaseModel


class ExtraBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
