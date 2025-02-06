from django.http import JsonResponse
from django.shortcuts import render
import nltk
from nltk import word_tokenize, pos_tag, ne_chunk
from collections import Counter
from .models import NERText, NERResult

def index(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        # Lo principal
        tokens = word_tokenize(text)
        tagged = pos_tag(tokens)
        entities = ne_chunk(tagged)
        
        
        
        
        
        entity_counter = Counter()
        for subtree in entities:
            if isinstance(subtree, nltk.Tree):
                entity_label = subtree.label()
                if entity_label in ['PERSON', 'GPE', 'DATE', 'TIME', 'LOCATION', 'ORGANIZATION', 'MONEY', 'PERCENT', 'FACILITY']:
                    entity_name = " ".join([token for token, pos in subtree.leaves()])
                    entity_counter[(entity_name, entity_label)] += 1
        
        filtered_entities = [{'entity': name, 'type': label, 'count': count} for (name, label), count in entity_counter.items()]
        
        # Create aggregate object
        aggregate_result = {
            'text': text,
            'entities': filtered_entities
        }
        
        return JsonResponse(aggregate_result)
    return render(request, 'ner_app/index.html')

def save_results(request):
       
    with open("C:/Users/jorge/OneDrive - FERCEL/Python/DataScience/artificial_intelligence/proyecto_final/django_log.txt", "w") as fid:
        fid.write(f"{request.POST.get('text')}\n")
        fid.write(f"{request.POST.getlist('entities')}\n")
       
    # if request.method == 'POST':
    text = request.POST.get('text')
    entities = request.POST.getlist('entities')
    
    # Save text and results to the database
    ner_text = NERText.objects.create(text=text)
    for entity in entities:
        entity_data = entity.split('|')
        NERResult.objects.create(
            ner_text=ner_text,
            entity=entity_data[0],
            entity_type=entity_data[1],
            occurrences=int(entity_data[2])
        )
    
    return JsonResponse({'status': 'success'})
    # return JsonResponse({'status': 'error'}, status=400)


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
        list_results.append({'ner_text':ner_text, 'ner_results':ner_results})       
    
    # Return JSON object
    return render(request, 'ner_app/results.html', {'saved_results': list_results})
        