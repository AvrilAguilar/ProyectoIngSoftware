from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer


def extract_keywords(texts: List[str], top_k: int = 5) -> List[str]:
    """
    Extrae las palabras clave más importantes usando TF-IDF.
    
    Parámetros:
        texts (List[str]): Lista de textos (reseñas) del libro.
        top_k (int): Número de palabras clave a devolver.

    Returns:
        List[str]: Lista de palabras clave ordenadas por relevancia.
    """
    if not texts:
        return []

    # Stopwords personalizadas (puedes agregar más si quieres)
    stop_words = [
        "el", "la", "los", "las", "y", "de", "que", "en", "un", "una",
        "es", "muy", "por", "para", "con", "lo", "como", "al", "se",
        "del", "más", "menos", "su", "sus", "le", "les", "me", "mi",
        "te", "tu", "yo", "nos", "pero", "si", "porque", "esta", "este"
    ]

    # Inicializamos TF-IDF
    vectorizer = TfidfVectorizer(
        max_features=1000,
        stop_words=stop_words
    )

    # Matriz TF-IDF
    tfidf_matrix = vectorizer.fit_transform(texts)

    # Sumamos pesos por palabra
    scores = tfidf_matrix.sum(axis=0).A1

    # Lista de palabras
    feature_names = vectorizer.get_feature_names_out()

    # Ordenar por relevancia
    sorted_idx = scores.argsort()[::-1]

    # Tomar las top_k
    top_terms = [feature_names[i] for i in sorted_idx[:top_k]]

    return top_terms
