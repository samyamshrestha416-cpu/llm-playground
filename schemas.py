from pydantic import BaseModel , ValidationError


class Recipe(BaseModel):
    title: str
    ingredients: list[str]
    steps: list[str]