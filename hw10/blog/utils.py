from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def paginate_objects(request, objects_list, num_per_page=2):
    paginator = Paginator(objects_list, num_per_page)
    page = request.GET.get('page')

    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)

    return objects
