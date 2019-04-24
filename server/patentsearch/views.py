
from django.shortcuts import render
from django.http import HttpResponse

# LUCENE SHIT
from .searchindex import SearchIndex
searcher = SearchIndex('../tools/patent.index/')
# END LUCENE SHIT


def index(request):

    regular_search = request.GET.get('regular_search', None)
    purpose_is = request.GET.get('purpose_is', None)
    purpose_is_not = request.GET.get('purpose_is_not', None)
    mechanics_is = request.GET.get('mechanics_is', None)
    mechanics_is_not = request.GET.get('mechanics_is_not', None)

    search_params = {'general_query': regular_search,
                     'purpose_is' : purpose_is,
                     'purpose_is_not': purpose_is_not,
                     'mechanics_is': mechanics_is,
                     'mechanics_is_not': mechanics_is_not}
    query={}
    for param in search_params:
        if search_params[param]:
            query[param] = search_params[param]
        else:
            query[param] = None


    if not query:
        return render(request, 'search.html', {})
    
    docs = searcher.search(query, topn=10)

    context = {'result': docs}
    return render(request, 'search.html', context)


# def index(request):
#     print(request.GET)
#     print(request.GET.keys())
#     print(request.GET.values())

#     if request.GET.get('query', ''):
#         context = {'result': 'aviv zaken'}
#     else:
#         context = {}

#     return render(request, 'search.html', context)


def about(request):
    PAGE = """<html><body><h1>About Us</h1><p>Aviv zaken isthe King! Naomi is the Queen and together they are King and Queen!</p>
</body></html>"""
    return HttpResponse(PAGE)
