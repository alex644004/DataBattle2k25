from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import random
from evaluation import semantic_similarity_with_negation,explain_answer  
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials, firestore
from google.cloud.firestore import FieldFilter
import time

app = Flask(__name__)
CORS(app)  



cred = credentials.Certificate("Votre fichier de connexion à Firebase.json")
firebase_admin.initialize_app(cred)
db = firestore.client()





@app.route("/api/themes", methods=["GET"])
def get_themes():
    themes_ref = db.collection("themes").stream()  # Récupère tous les documents de la collection "themes"
    
    themes_list = []
    
    for doc in themes_ref:
        theme_data = doc.to_dict()
        theme_name = theme_data.get("theme", doc.id)  # Récupère le nom du thème
        
        sous_themes = theme_data.get("sous_themes", [])  # Liste des sous-thèmes
        
        formatted_subthemes = [subtheme.get("nom", "") for subtheme in sous_themes]

        
        themes_list.append({
            "theme": theme_name,
            "subthemes": formatted_subthemes
        })


    return jsonify(themes_list)


@app.route("/api/quiz", methods=["POST"])
def start_quiz():
    data = request.json  # Récupérer les données envoyées en JSON
    subtheme = data.get("subtheme")

    return jsonify({"message": f"Démarrage du quiz pour {subtheme} dans le thème "}), 200




def get_questions_by_theme(theme):
    # Récupère uniquement les questions qui correspondent au thème dans Firestore

    questions_ref = db.collection("rag").where(filter=FieldFilter("Theme", "==", theme)).stream()
    questions = [q.to_dict() for q in questions_ref]  # Convertit les résultats en dictionnaires


    return questions


@app.route("/api/questions", methods=["POST"])
def get_questions():
    data = request.get_json()
    theme = data.get("theme")


    questions = get_questions_by_theme(theme)

    # if len(questions) < 10:
    #     return jsonify({"error": "Pas assez de questions disponibles pour ce thème"}), 400

    selected_questions = random.sample(questions, 2)

    return jsonify(selected_questions)



@app.route('/api/evaluate_justification', methods=['POST'])
def evaluate_justification():
    data = request.json  # Récupération des données envoyées par le frontend

    student_answer = data.get("student_answer", "")
    expected_answer = data.get("expected_answer", "")



    # Appel de la fonction de similarité
    result = semantic_similarity_with_negation(student_answer, expected_answer)

    return jsonify({
        "final_decision": result["final_decision"],
        "similarity_score": result["similarity_score"],
        "negation_mismatch": result["negation_mismatch"]
    })

@app.route('/api/explain_answer', methods=['POST'])
def explain_answer_api():
    data = request.json

    question = data.get("question", "")
    expected_answer = data.get("expected_answer", "")
    student_answer = data.get("student_answer", "")

    if not question or not expected_answer or not student_answer:
        return jsonify({"error": "Données manquantes"}), 400

    explanation = explain_answer(question, expected_answer, student_answer)

    return jsonify({"explanation": explanation})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
