from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session, init_db
from app.models import Recipe
from app.schemas import RecipeCreate, RecipeDetail, RecipeListItem


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await init_db()
    yield


app = FastAPI(
    title="Кулинарная книга API",
    description=(
        "REST API для кулинарной книги. Позволяет получать список рецептов, "
        "отсортированный по популярности, смотреть детальную информацию "
        "по конкретному рецепту и добавлять новые рецепты."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.get(
    "/recipes",
    response_model=list[RecipeListItem],
    summary="Получить список всех рецептов",
    description=(
        "Возвращает список рецептов, отсортированный по количеству просмотров "
        "(по убыванию — самые популярные рецепты первыми). При равном количестве "
        "просмотров рецепты сортируются по времени приготовления (по возрастанию)."
    ),
)
async def get_recipes(session: AsyncSession = Depends(get_session)) -> list[Recipe]:
    result = await session.execute(
        select(Recipe).order_by(Recipe.views.desc(), Recipe.cook_time.asc())
    )
    return list(result.scalars().all())


@app.get(
    "/recipes/{recipe_id}",
    response_model=RecipeDetail,
    summary="Получить детальную информацию о рецепте",
    description=(
        "Возвращает полную информацию о рецепте: название, время приготовления, "
        "список ингредиентов и текстовое описание. Каждый вызов этого эндпоинта "
        "увеличивает счётчик просмотров рецепта на 1."
    ),
    responses={404: {"description": "Рецепт с таким id не найден"}},
)
async def get_recipe(recipe_id: int, session: AsyncSession = Depends(get_session)) -> RecipeDetail:
    recipe = await session.get(Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Рецепт не найден")

    recipe.views += 1
    await session.commit()
    await session.refresh(recipe)
    return RecipeDetail(
        id=recipe.id,
        title=recipe.title,
        cook_time=recipe.cook_time,
        ingredients=recipe.ingredients.split(","),
        description=recipe.description,
    )


@app.post(
    "/recipes",
    response_model=RecipeDetail,
    status_code=201,
    summary="Создать новый рецепт",
    description=(
        "Добавляет новый рецепт в кулинарную книгу. "
        "Счётчик просмотров у нового рецепта всегда равен 0."
    ),
)
async def create_recipe(
    payload: RecipeCreate, session: AsyncSession = Depends(get_session)
) -> RecipeDetail:
    recipe = Recipe(
        title=payload.title,
        cook_time=payload.cook_time,
        ingredients=",".join(payload.ingredients),
        description=payload.description,
        views=0,
    )
    session.add(recipe)
    await session.commit()
    await session.refresh(recipe)
    return RecipeDetail(
        id=recipe.id,
        title=recipe.title,
        cook_time=recipe.cook_time,
        ingredients=payload.ingredients,
        description=recipe.description,
    )
