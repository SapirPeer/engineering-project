
from django.shortcuts import render
from django.http import HttpResponse

# LUCENE SHIT
from .searchindex import SearchIndex
searcher = SearchIndex('../tools/patent.index/')
# END LUCENE SHIT


def index(request):

    query = request.GET.get('query', None)

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
