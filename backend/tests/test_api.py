import pytest
from httpx import AsyncClient
from backend.app.main import app



@pytest.mark.asyncio
async def test_create_book():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "title": "Harry Potter",
            "author": "Rowling",
            "description": "Magia, aventura y amistad."
        }
        response = await ac.post("/books", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["title"] == "Harry Potter"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_review():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Crear libro
        book = await ac.post("/books", json={
            "title": "El Hobbit",
            "author": "Tolkien",
            "description": "Un viaje inesperado."
        })
        book_id = book.json()["id"]

        # Crear reseña
        review_res = await ac.post(f"/books/{book_id}/reviews", json={
            "username": "Vicente",
            "text": "Muy emocionante y divertido."
        })

    assert review_res.status_code == 200
    data = review_res.json()
    assert data["sentiment_label"] in ["positive", "negative"]
    assert isinstance(data["sentiment_score"], float)


@pytest.mark.asyncio
async def test_summary():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Crear libro
        book = await ac.post("/books", json={
            "title": "Percy Jackson",
            "author": "Rick Riordan",
            "description": "Mitología griega moderna."
        })
        book_id = book.json()["id"]

        # Crear reseñas
        await ac.post(f"/books/{book_id}/reviews", json={
            "username": "usuario1",
            "text": "Muy divertido y emocionante."
        })

        await ac.post(f"/books/{book_id}/reviews", json={
            "username": "usuario2",
            "text": "Un poco aburrido al principio."
        })

        # Probar summary
        summary_res = await ac.get(f"/books/{book_id}/summary")

    assert summary_res.status_code == 200
    data = summary_res.json()

    assert "positive" in data
    assert "negative" in data
    assert "keywords" in data
    assert data["total_reviews"] == 2


@pytest.mark.asyncio
async def test_recommendations():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Crear libros
        b1 = await ac.post("/books", json={
            "title": "Libro A",
            "author": "Autor X",
            "description": "Magia y aventuras en un mundo misterioso."
        })

        b2 = await ac.post("/books", json={
            "title": "Libro B",
            "author": "Autor Y",
            "description": "Aventuras mágicas con criaturas fantásticas."
        })

        b3 = await ac.post("/books", json={
            "title": "Libro C",
            "author": "Autor Z",
            "description": "Historia triste y dramática, sin magia."
        })

        id1 = b1.json()["id"]

        # Probar recomendaciones
        rec_res = await ac.get(f"/books/{id1}/recommendations")

    assert rec_res.status_code == 200
    data = rec_res.json()

    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)
