from httpx import AsyncClient


async def test_get_recipes_empty(client: AsyncClient) -> None:
    response = await client.get("/recipes")
    assert response.status_code == 200
    assert response.json() == []

async def test_create_recipe(client: AsyncClient) -> None:
    payload = {
        "title": "Омлет",
        "cook_time": 10,
        "ingredients": ["яйца", "молоко", "соль"],
        "description": "Взбить яйца с молоком, посолить, обжарить.",
    }
    response = await client.post("/recipes", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == payload["title"]
    assert data["ingredients"] == payload["ingredients"]
    assert "id" in data

async def test_get_recipe_detail_increments_views(client: AsyncClient) -> None:
    create_response = await client.post(
        "/recipes",
        json={
            "title": "Салат",
            "cook_time": 15,
            "ingredients": ["огурцы", "помидоры"],
            "description": "Нарезать и смешать.",
        },
    )
    recipe_id = create_response.json()["id"]

    first_view = await client.get(f"/recipes/{recipe_id}")
    assert first_view.status_code == 200

    second_view = await client.get(f"/recipes/{recipe_id}")
    assert second_view.json()["ingredients"] == ["огурцы", "помидоры"]

    list_response = await client.get("/recipes")
    recipe_in_list = next(r for r in list_response.json() if r["id"] == recipe_id)
    assert recipe_in_list["views"] == 2


async def test_get_recipe_not_found(client: AsyncClient) -> None:
    response = await client.get("/recipes/999")
    assert response.status_code == 404


async def test_recipes_sorted_by_views_then_cook_time(client: AsyncClient) -> None:
    slow = await client.post(
        "/recipes",
        json={
            "title": "Долгий рецепт",
            "cook_time": 60,
            "ingredients": ["мясо"],
            "description": "Долго готовить.",
        },
    )
    fast = await client.post(
        "/recipes",
        json={
            "title": "Быстрый рецепт",
            "cook_time": 5,
            "ingredients": ["яйцо"],
            "description": "Быстро готовить.",
        },
    )

    slow_id = slow.json()["id"]
    fast_id = fast.json()["id"]
    response = await client.get("/recipes")
    data = response.json()
    assert data[0]["id"] == fast_id
    assert data[1]["id"] == slow_id
    await client.get(f"/recipes/{slow_id}")

    response = await client.get("/recipes")
    data = response.json()
    assert data[0]["id"] == slow_id
