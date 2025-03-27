import spacy
from sentence_transformers import SentenceTransformer, util
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="Votre clé API OPEN ROUTER",
)

modele = "mistralai/mistral-7b-instruct:free"

# Charger le modèle NLP et le modèle de similarité
nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer('all-MiniLM-L6-v2')

def detect_negation(sentence):
    """Détecte la présence de négations dans une phrase."""
    doc = nlp(sentence)
    negations = {token.text.lower() for token in doc if token.dep_ == "neg"}
    return negations

def semantic_similarity_with_negation(student_answer, expected_answer):
    # Encoder les phrases en vecteurs

        
    embeddings = model.encode([student_answer, expected_answer])

    # Calcul de la similarité cosinus
    similarity = util.cos_sim(embeddings[0], embeddings[1]).item()

    # Détection des négations
    student_negations = detect_negation(student_answer)
    expected_negations = detect_negation(expected_answer)

    # Vérifier si la négation est différente entre les deux phrases
    negation_mismatch = (bool(student_negations) != bool(expected_negations))

    # Ajuster la validation : si la similarité est élevée mais la négation est opposée, c'est faux
    is_correct = similarity > 0.75 and not negation_mismatch

    return {
        "similarity_score": similarity,
        "student_negations": student_negations,
        "expected_negations": expected_negations,
        "negation_mismatch": negation_mismatch,
        "final_decision": is_correct
    }

def explain_answer(question, expected_answer, student_answer, modele=modele):
    """Génère une réponse en utilisant les documents et le contexte."""
    
    message = [
        {
            "role": "system",
            "content": f"""
    You are an expert patent law professor, known for your clear and direct teaching style. I am a patent law student. Your task is to evaluate my answer by identifying only the major errors. 
    You MUST Adopt an informal tone and address to me directly.

    Here is the exam question:
    "{question}"

    My answer is:
    "{student_answer}"

    The expected answer is:
    "{expected_answer}"

    In your explanation, follow the order of my answer and, for each part, indicate:

    1. **Missing elements**: What should have been included for a complete response.
    2. **Incorrect or misinterpreted elements**: What I misunderstood or misformulated.

    Explain what were the key points to have maximum grading.

    I can't see the expected answer, so make sure to provide enough detail for me to understand my mistakes.
    """
        }
    ]



    # Appeler le modèle pour générer une réponse
    response = client.chat.completions.create(model=modele, messages=message)

    # Retourner le contenu de la réponse générée
    return response.choices[0].message.content

