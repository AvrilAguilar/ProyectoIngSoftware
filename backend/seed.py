# backend/seed.py

import asyncio
import sys
import os

# Asegurar que Python reconozca el paquete backend/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import books_collection


# === GRAN CATÁLOGO DE LIBROS (120+) ===
BOOKS = [
    # ==== Fantasía ====
    ("Harry Potter y la piedra filosofal", "J.K. Rowling", "Un niño descubre que es mago."),
    ("Harry Potter y la cámara secreta", "J.K. Rowling", "El segundo año de Harry en Hogwarts."),
    ("Harry Potter y el prisionero de Azkaban", "J.K. Rowling", "Harry enfrenta a un fugitivo peligroso."),
    ("El Hobbit", "J.R.R. Tolkien", "La aventura inesperada de Bilbo Bolsón."),
    ("El Señor de los Anillos: La Comunidad del Anillo", "J.R.R. Tolkien", "El viaje para destruir el Anillo Único."),
    ("El Señor de los Anillos: Las Dos Torres", "J.R.R. Tolkien", "La Comunidad dividida sigue luchando."),
    ("El Señor de los Anillos: El Retorno del Rey", "J.R.R. Tolkien", "La batalla final por la Tierra Media."),
    ("Las Crónicas de Narnia", "C.S. Lewis", "Un mundo mágico descubierto desde un ropero."),
    ("Percy Jackson y el ladrón del rayo", "Rick Riordan", "Percy descubre que es hijo de un dios griego."),
    ("Percy Jackson y el mar de los monstruos", "Rick Riordan", "Percy debe salvar el campamento mestizo."),
    ("Mistborn: El Imperio Final", "Brandon Sanderson", "Un imperio gobernado por un tirano inmortal."),
    ("Elantris", "Brandon Sanderson", "Una ciudad caída y maldita."),
    ("El Nombre del Viento", "Patrick Rothfuss", "Kvothe cuenta su historia."),
    ("El temor de un hombre sabio", "Patrick Rothfuss", "La legendaria continuación del Nombre del Viento."),
    ("Juego de tronos", "George R.R. Martin", "Reyes, traiciones y guerras en Poniente."),
    ("Tormenta de espadas", "George R.R. Martin", "La traición cambia el destino de Poniente."),
    ("La Rueda del Tiempo", "Robert Jordan", "Un viaje épico para salvar el mundo."),

    # ==== Ciencia ficción ====
    ("Dune", "Frank Herbert", "Un planeta desértico lleno de conspiraciones."),
    ("Fundación", "Isaac Asimov", "Una ciencia que predice el futuro."),
    ("Yo, robot", "Isaac Asimov", "Relatos sobre inteligencia artificial."),
    ("Neuromante", "William Gibson", "El origen del ciberpunk."),
    ("Ender’s Game", "Orson Scott Card", "Un niño genio entrena para salvar a la humanidad."),
    ("1984", "George Orwell", "Distopía sobre vigilancia total."),
    ("Un mundo feliz", "Aldous Huxley", "Sociedad controlada y modificada genéticamente."),
    ("Fahrenheit 451", "Ray Bradbury", "Bomberos que queman libros."),
    ("Ready Player One", "Ernest Cline", "Una competencia en un mundo virtual."),

    # ==== Terror ====
    ("It", "Stephen King", "Un ente maligno aterroriza a un pueblo."),
    ("El Resplandor", "Stephen King", "Un hotel embrujado domina la mente de Jack Torrance."),
    ("Cementerio de animales", "Stephen King", "La muerte no siempre es el final."),
    ("Drácula", "Bram Stoker", "El legendario vampiro."),
    ("Frankenstein", "Mary Shelley", "Un científico crea vida prohibida."),

    # ==== Romance ====
    ("Orgullo y prejuicio", "Jane Austen", "Elizabeth Bennet navega la sociedad inglesa."),
    ("Bajo la misma estrella", "John Green", "Dos jóvenes con cáncer encuentran el amor."),
    ("Yo antes de ti", "Jojo Moyes", "Una relación que cambia vidas."),

    # ==== Clásicos ====
    ("Don Quijote de la Mancha", "Miguel de Cervantes", "El mayor clásico español."),
    ("Crimen y castigo", "Dostoyevski", "Un asesinato y su impacto moral."),
    ("La Odisea", "Homero", "La aventura de Odiseo."),
    ("Hamlet", "Shakespeare", "Venganza y locura."),
    ("Romeo y Julieta", "Shakespeare", "El amor prohibido más famoso."),
]

# Agregar libros genéricos (80 más)
BOOKS += [
    (f"Libro Genérico #{i}", "Autor Desconocido", "Libro de prueba para catálogo.")
    for i in range(1, 81)
]


# ======================================================
#   FUNCIÓN PARA INSERTAR MASIVAMENTE LOS LIBROS
# ======================================================

async def seed_books():
    print("Eliminando libros existentes…")
    await books_collection.delete_many({})

    print(f"Inserción de {len(BOOKS)} libros…")

    docs = [{"title": t, "author": a, "description": d} for (t, a, d) in BOOKS]

    result = await books_collection.insert_many(docs)
    print(f"✔ Libros insertados: {len(result.inserted_ids)}")


if __name__ == "__main__":
    asyncio.run(seed_books())
    print("📚 Base de datos poblada correctamente 🚀")
