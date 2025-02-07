from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
import nltk
from nltk import word_tokenize, pos_tag, ne_chunk
from collections import Counter
from .models import NERText, NERResult
import pyperclip
import os
import PyPDF2
import mammoth
from .nlp.cosine_similarity import cosine_similarity_tfidf, merge_entities

def index(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        try:
            threshold = float(request.POST.get('threshold'))
        except Exception:
            threshold = 0.5
        allLabels = request.POST.get('allLabels')
        if allLabels=='true':
            labels=['PERSON', 'GPE', 'DATE', 'TIME', 'LOCATION', 'ORGANIZATION', 'MONEY', 'PERCENT', 'FACILITY']
        else:
            labels=['PERSON', 'GPE', 'DATE', 'TIME', 'LOCATION']
            
        try:
            with open("django_log.txt", "w", encoding='utf-8') as fid:
                fid.write(f"{text}\n")
                fid.write(f"{threshold}\n")
                fid.write(f"{allLabels}\n")
        except Exception:
            pass
            
        # Obtiene las entidades del análisis NER
        entities = perform_ner_analysis(text, labels=labels, threshold=threshold)
        
        # Create aggregate object
        aggregate_result = {
            'text': text,
            'entities': entities
        }
        
        return JsonResponse(aggregate_result)
    return render(request, 'ner_app/index.html')

def perform_ner_analysis(text, labels=['PERSON', 'GPE', 'DATE', 'TIME', 'LOCATION', 'ORGANIZATION', 'MONEY', 'PERCENT', 'FACILITY'], threshold=0.3):
    # Proceso principal del NER
    # Tokenization
    tokens = word_tokenize(text)
    # Part of Speech and Tagging
    tagged = pos_tag(tokens)
    # Recognition of entities
    entities = ne_chunk(tagged)
    # Process de NER results to the views
    entity_counter = Counter()
    for subtree in entities:
        if isinstance(subtree, nltk.Tree):
            entity_label = subtree.label()
            if entity_label in labels:
                entity_name = " ".join([token for token, pos in subtree.leaves()])
                entity_counter[(entity_name, entity_label)] += 1
    
    filtered_entities = [{'entity': name, 'type': label, 'count': count} for (name, label), count in entity_counter.items()]
    
    # Merge the entities using Tf-idf and cosine similarity
    merged_entities = merge_entities(filtered_entities, threshold=threshold)
    
    # Sort the filtered entities
    sorted_entities = sorted(merged_entities, key=lambda x: (-x['count'], x['entity'], x['type']))
    
    return sorted_entities


def save_results(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        try:
            threshold = float(request.POST.get('threshold'))
        except Exception:
            threshold = 0.5
        allLabels = request.POST.get('allLabels')
        if allLabels=='true':
            labels=['PERSON', 'GPE', 'DATE', 'TIME', 'LOCATION', 'ORGANIZATION', 'MONEY', 'PERCENT', 'FACILITY']
        else:
            labels=['PERSON', 'GPE', 'DATE', 'TIME', 'LOCATION']
            
        # try:
        #     with open("django_log.txt", "w", encoding='utf-8') as fid:
        #         fid.write(f"{text}\n")
        #         fid.write(f"{threshold}\n")
        #         fid.write(f"{allLabels}\n")
        # except Exception:
        #     pass
            
        # Obtiene las entidades del análisis NER
        entities = perform_ner_analysis(text, labels=labels, threshold=threshold)
               
        # Save NERText object
        ner_text = NERText.objects.create(text=text)
        
        # Save NERResult objects
        for entity in entities:
            NERResult.objects.create(
                ner_text=ner_text,
                entity=entity['entity'],
                entity_type=entity['type'],
                occurrences=entity['count'])
        
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'})


def results(request):
    # List to accumulate the matches
    list_results = []   
    # From a search
    if request.method == 'POST':
        search_text = request.POST.get('search_text')
        ner_texts = NERText.objects.filter(text__icontains=search_text)  
    # From the redirection
    else:
        ner_texts = NERText.objects.all()
    # Accumlate the results
    for ner_text in ner_texts:
        ner_results = NERResult.objects.filter(ner_text=ner_text)
        # Sort the ner_results
        sorted_ner_results = sorted(ner_results, key=lambda x: (-x.occurrences, x.entity, x.entity_type))
        list_results.append({'ner_text': ner_text, 'ner_results': sorted_ner_results})       
    
    # Return JSON object
    return render(request, 'ner_app/results.html', {'saved_results': list_results})


def delete_ner_text(request, id):
    if request.method == 'POST':
        ner_text = get_object_or_404(NERText, id=id)
        ner_text.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


def upload_file(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        file_content = ''

        if file_extension == '.pdf':
            file_content = extract_text_from_pdf(uploaded_file)
        elif file_extension == '.docx':
            file_content = extract_text_from_docx(uploaded_file)
        elif file_extension == '.txt':
            file_content = uploaded_file.read().decode('utf-8')
        else:
            return JsonResponse({'status': 'failed', 'message': 'Unsupported file type.'})

        return JsonResponse({'status': 'success', 'text': file_content})
    return JsonResponse({'status': 'failed', 'message': 'Invalid request method.'})

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ''
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
        utf8_text = text.encode('utf-8')
        utf8_text_str = utf8_text.decode('utf-8')
    return utf8_text_str

def extract_text_from_docx(docx_file):
    result = mammoth.extract_raw_text(docx_file)
    return result.value



