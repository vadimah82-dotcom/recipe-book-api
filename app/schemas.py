from pydantic import BaseModel, ConfigDict, Field


class RecipeListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str = Field(..., description="Название блюда")
    views: int = Field(..., description="Количество просмотров детального рецепта")
    cook_time: int = Field(..., description="Время приготовления в минутах")

class RecipeDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str = Field(..., description="Название блюда")
    cook_time: int = Field(..., description="Время приготовления в минутах")
    ingredients: list[str] = Field(..., description="Список ингредиентов")
    description: str = Field(..., description="Текстовое описание приготовления")

class RecipeCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Название блюда")
    cook_time: int = Field(..., gt=0, description="Время приготовления в минутах")
    ingredients: list[str] = Field(..., min_length=1, description="Список ингредиентов")
    description: str = Field(..., min_length=1, description="Текстовое описание приготовления")
