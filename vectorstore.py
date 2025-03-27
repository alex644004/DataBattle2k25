import json
import weaviate
import uuid
import numpy as np
import weaviate.classes.config as wc
import weaviate.classes as wvc
from weaviate.classes.config import Property, DataType, Configure, Tokenization
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
import os
from weaviate.classes.query import MetadataQuery


themes = {
    " Filing requirements and formalities": {
        " Minimum requirements for a filing date": 
            "Assessing the mandatory elements (e.g., description, claims) and their submission modes.",
        " Filing methods and locations": 
            "Addressing allowed filing modes (fax, online, physical) and relevant EPO sites.",
        " Formality examination": 
            "Checking if formal requirements (payment of fees, form usage, etc.) are met."
    },
    "Priority claims and right of priority": {
        " Substantive requirements for priority": 
            "Validity criteria, same invention requirement, earliest date, and partial priorities.",
        "Time limits and restoration": 
            "One-year priority period, procedures for requesting restoration, conditions for success.",
        "Multiple priorities and partial priority": 
            "Handling claims that rely on more than one earlier application."
    },
    "Divisional applications": {
        "Filing requirements": 
            "When a parent must still be pending, language options, and timing.",
        "Subject-matter and scope": 
            "Compliance with Article 76 EPC, no added subject-matter, and ensuring unity.",
        "Fees for divisionals": 
            "Payment of filing fees, renewal fees, examination fees, and other relevant costs."
    },
    "Fees, payment methods, and time limits": {
        " Types and calculation of fees": 
            "Understanding different fee types (filing, search, examination, renewal, claims).",
        "Payment mechanisms": 
            "Automatic debit orders, bank transfers, credit cards, and fee payment via third parties.",
        "Fee deadlines and late payment consequences": 
            "Additional fees, surcharges, and further processing if deadlines are missed."
    },
    "Languages and translations": {
        "Language of filing and procedural language": 
            "Filing in non-EPO official languages, subsequent translation deadlines, language-based fee reductions.",
        "Translation requirements on grant or other stages": 
            "Claim translations under Rule 71(3) EPC, translation for validation in national phases.",
        "Effects of language on costs and procedural rights": 
            "Fee reductions for certain languages, language-based rights of small entities or universities."
    },
    "Procedural remedies and legal effect": {
        "Further processing (Rule 135 EPC)": 
            "Available for missed deadlines in examination or other proceedings, scope of remedy, exceptions.",
        "Re-establishment of rights (Article 122 EPC)": 
            "Conditions (all due care), time limit for requesting, and required evidence.",
        "Loss of rights and remedies": 
            "Notices of loss of rights, deemed withdrawals, subsequent procedural options."
    },
    "PCT procedure and entry into the European phase": {
        "International filing and search": 
            "Filing at receiving offices, international search by EPO or other ISAs, invited corrections.",
        "Preliminary examination and amendments": 
            "Filing a demand, timing for Article 34 amendments, unity objections at IPER stage.",
        "European phase entry and requirements": 
            "Minimum actions to enter EP phase (translations, fees, etc.), optional actions (requesting examination)."
    },
    "Examination, amendments, and grant": {
        "Examination procedure and communications": 
            "Responding to Article 94(3) communications, telephone consultations with examiners, time limit extensions.",
        "Claim amendments and Article 123 EPC": 
            "No added subject-matter, no broadening after grant, clarity considerations.",
        "Grant stage (Rule 71(3) EPC) and post-grant publication": 
            "Paying the fee for grant and publishing, submitting claim translations, final text for publication."
    },
    "Opposition and appeals": {
        "Grounds for opposition (Article 100 EPC)": 
            "Novelty, inventive step, subject-matter not patentable, insufficiency of disclosure, extension beyond original filing.",
        "Opposition procedure and admissibility": 
            "Formal requirements (time limits, opponent identity), partial opposition, withdrawal of opposition.",
        "Appeal proceedings": 
            "Grounds of appeal, fresh evidence, remittal, boards’ powers, and procedures."
    },
    "Substantive patent law: novelty and inventive step": {
        "Novelty analysis": 
            "Defining prior art, comparing features, selection inventions, disclaimers.",
        "Inventive step analysis": 
            "Closest prior art selection, objective technical problem, and problem-solution approach.",
        "Special forms of claims (e.g., medical use)": 
            "Swiss-type, Article 54(5) EPC second medical use claims, allowable claim wording."
    },
    "Entitlement and transfers": {
        "Entitlement disputes (Article 61 EPC)": 
            "Disputes over who owns the right to a European patent application or patent.",
        "Transfers and assignments": 
            "Formalities for registering changes in ownership, partial transfers, and licensing.",
        "Procedural consequences": 
            "Impact on deadlines, actions that can/cannot be taken by a transferee before registration."
    },
    "Biotech and sequence listings": {
        "Sequence listing filing and format": 
            "Mandatory WIPO standard, electronic submission, late furnishing fees.",
        "Added subject-matter in biotech claims": 
            "Ensuring that no new sequences or mutations are introduced beyond the original disclosure.",
        "Specific patentability exceptions in biotech": 
            "Exclusions (plant/animal varieties, essentially biological processes), Rule 28 EPC."
    },
    "Unity of invention": {
        "Unity in European applications": 
            "Criteria for single general inventive concept, partial search where unity is lacking.",
        "Unity in PCT applications": 
            "International phase unity criteria, additional fees for multiple inventions, protest procedure.",
        "Strategies for overcoming lack of unity": 
            "Amendments, selecting one invention to proceed with, potential divisional filings."
    }
}



# Téléchargement des stopwords (une seule fois)
nltk.download('punkt')
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))


def clean_text(text):
    """Nettoyer le texte : enlever les stopwords et tokeniser."""
    if not text:  # Vérifie si text est None ou vide
        return ""  # Retourne une chaîne vide au lieu de lever une erreur
    tokens = word_tokenize(text.lower())  # Tokenisation et mise en minuscule
    filtered_tokens = [word for word in tokens if word not in stop_words and word.isalnum()]
    return ' '.join(filtered_tokens)                  

# A changer pour déploiement sur AWS ou autre
def connect_to_db():
    """Connexion à la base de données Weaviate."""
    return weaviate.connect_to_local()

def create_class_Chunk():
    """Créer la classe Chunk dans Weaviate."""

    # Connexion à Weaviate
    client = connect_to_db()

    if not client.collections.exists("Chunk"):
        # Créer la classe Chunk si elle n'existe pas
        client.collections.create(
            name="Chunk",
            properties=[
                wc.Property(name="title", data_type=wc.DataType.TEXT),
                wc.Property(name="section", data_type=wc.DataType.TEXT),
                wc.Property(name="subsection", data_type=wc.DataType.TEXT),
                wc.Property(name="text", data_type=wc.DataType.TEXT, tokenization=wvc.config.Tokenization.WORD),
                wc.Property(name="level", data_type=wc.DataType.INT),
                wc.Property(name="references", data_type=wc.DataType.TEXT_ARRAY),  
                wc.Property(name="original_filename", data_type=wc.DataType.TEXT),
                wc.Property(name="theme", data_type=wc.DataType.TEXT_ARRAY)
            ],
            vectorizer_config=wvc.config.Configure.Vectorizer.none(),
        )
        print("Classe 'Chunk' créée avec succès")

    client.close()

def get_weighted_embedding(embedder, chunk):
    """Calcule un embedding pondéré pour le chunk."""
    # Vérifier que les valeurs existent avant d'encoder
    title_embedding = embedder.encode(chunk['title']).tolist() if chunk.get('title') else [0] * 384  
    section_embedding = embedder.encode(chunk['section']).tolist() if chunk.get('section') else [0] * 384
    text_embedding = embedder.encode(chunk['text']).tolist() if chunk.get('text') else [0] * 384
    # Convertir la liste de références en une seule chaîne de texte
    references_text = " ".join(chunk['references']) if chunk.get('references') else ""
    references_embedding = embedder.encode(references_text).tolist() if references_text else [0] * 384


    # Pondération : 60% `text`, 20% `title`, 10% `section`, 10% `subsection`
    final_embedding = np.array(title_embedding) * 0.2 + np.array(section_embedding) * 0.05 + np.array(references_embedding) * 0.25 + np.array(text_embedding) * 0.5

    return final_embedding.tolist()

def get_subthemes_for_chunk(chunk_embedding, themes, embedding_model):
    """ Associe plusieurs sous-thèmes à un chunk selon la similarité."""
    assigned_subthemes = []
    
    for theme, subthemes in themes.items():
        for subtheme, description in subthemes.items():
            theme_embedding = embedding_model.encode(subtheme, normalize_embeddings=True)
            similarity = np.dot(chunk_embedding, theme_embedding)
            
            if similarity > 0.6:
                assigned_subthemes.append(subtheme)
    
    return assigned_subthemes

    
def extract_and_store_chunks(chunks,embedder):
    """Stocker les chunks dans Weaviate."""

    # Connexion à Weaviate
    client = connect_to_db()

    # Get the collection
    collection = client.collections.get("Chunk")
    with collection.batch.dynamic() as batch:
        # Ajouter les documents dans Weaviate
        for chunk in chunks:
                title = clean_text(chunk["title"])
                section = clean_text(chunk["section"])
                subsection = clean_text(chunk["subsection"])
                text = clean_text(chunk["text"])
                level = chunk["level"]
                references = chunk["references"]
                original_filename = chunk["original_filename"]

                embedding = get_weighted_embedding(embedder, chunk)

                theme = get_subthemes_for_chunk(embedding, themes, embedder)

                # Créer un ID unique
                doc_id = str(uuid.uuid4())

                # Construire l'objet à envoyer à Weaviate
                document_data = {
                    "title": title,
                    "section": section,
                    "subsection": subsection,
                    "text": text,
                    "level": level,
                    "references": references,
                    "original_filename": original_filename,
                    "theme": theme
                }

                # Ajouter l'objet au client Weaviate
                batch.add_object(
                    properties=document_data,
                    vector=embedding,
                    uuid=doc_id,
                )

                # Check for failed objects
                if len(collection.batch.failed_objects) > 0:
                    print(f"Failed to import {len(collection.batch.failed_objects)} objects")
                    for failed in collection.batch.failed_objects:
                        print(f"e.g. Failed to import object with error: {failed.message}")

    client.close()        

def process_and_add_chunks_from_json(file_path,embedder):
    """Ouverture du fichier et ajout des chunkss à la base de données."""

    #  Ouvrir le fichier JSON
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            chunks = json.load(f)  # Charger les données JSON
    except Exception as e:
        print(f" Erreur lors de la lecture du fichier JSON : {e}")
        return
    
    #  Appliquer la fonction d'ajout des chunks à ChromaDB
    extract_and_store_chunks(chunks,embedder)

def process_all_json_files(directory, embedder):
    """Parcourt récursivement un dossier et traite tous les fichiers JSON."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                print(f"Traitement du fichier : {file_path}")
                process_and_add_chunks_from_json(file_path, embedder)


def verify_stored_chunks():
    """Vérifie si des chunks sont bien stockés dans Weaviate."""
    client = connect_to_db()
    collection = client.collections.get("Chunk")

    # Récupérer les 5 premiers objets stockés
    results = collection.query.fetch_objects(limit=5)
    
    if results.objects:
        print("Chunks stockés dans Weaviate :")
        for obj in results.objects:
            print(obj)
    else:
        print("Aucun chunk trouvé dans Weaviate.")

    client.close()

def more_relevant_chunks(query, embedder, top_k):
    """Récupère les chunks stockés dans Weaviate."""
    client = connect_to_db()

    query_results = client.collections.get("Chunk")
    
    querryEmbbed = embedder.encode(query).tolist()

    # Perform query
    response = query_results.query.near_vector(
        near_vector=querryEmbbed,
        limit=top_k
    )

    chunks = []
    for doc in response.objects:
        properties = doc.properties
        chunks.append({
        "title": properties.get('title'),
        "section": properties.get('section'),
        "subsection": properties.get('subsection'),
        "text": properties.get('text'),
        "level": properties.get('level'),
        "references": properties.get('references'),
        "original_filename": properties.get('original_filename'),
        "theme": properties.get('theme')
    })
    
    return chunks[:top_k]