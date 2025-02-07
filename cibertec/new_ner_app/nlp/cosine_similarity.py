import nltk
# Download stopwords and punkt if not already downloaded
# nltk.download('stopwords')
# nltk.download('punkt')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine_similarity

# Function to calculate cosine similarity using TF-IDF
def cosine_similarity_tfidf(str1, str2):
    
    import re

    def limpiar_texto(texto):
        texto = texto.lower()
        texto = re.sub(r'[^a-zA-Z0-9\n ]', '', texto)
        return texto
    
    # Remove unwanted characters
    str1 = limpiar_texto(str1)
    str2 = limpiar_texto(str2)
    
    # Tokenize and remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens1 = ' '.join([word for word in word_tokenize(str1.lower()) if word not in stop_words])
    tokens2 = ' '.join([word for word in word_tokenize(str2.lower()) if word not in stop_words])
    
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer().fit_transform([tokens1, tokens2])
    vectors = vectorizer.toarray()
    
    # Calculate cosine similarity
    cosine_sim = sklearn_cosine_similarity(vectors)
    
    return cosine_sim[0][1]

# Function to merge dictionaries based on cosine similarity using TF-IDF
def merge_entities(entity_list, threshold=0.3):
    merged_list = []
    while entity_list:
        entity = entity_list.pop(0)
        name, entity_type, occurrences = entity['entity'], entity['type'], entity['count']
        merged = False
        
        for i, merged_entity in enumerate(merged_list):
            m_name, m_type, m_occurrences = merged_entity['entity'], merged_entity['type'], merged_entity['count']
            if m_type == entity_type:
                if cosine_similarity_tfidf(name, m_name) >= threshold:
                    # Update the name to be the largest among the similar entities
                    new_name = max(name, m_name, key=len)
                    merged_list[i] = {'entity': new_name, 'type': m_type, 'count': m_occurrences + occurrences}
                    merged = True
                    break
        
        if not merged:
            merged_list.append(entity)
    
    return merged_list