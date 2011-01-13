from django.core.paginator import Paginator as DjangoPaginator, Page as DjangoPage, EmptyPage, InvalidPage


class Page(DjangoPage):

    def short_page_range(self):
        RADIUS = 3
        start = self.number - RADIUS if self.number > RADIUS else 1
        end = self.number + RADIUS if self.number < self.paginator.num_pages - RADIUS else self.paginator.num_pages
        return range(start, end + 1)


class Paginator(DjangoPaginator):
    def __init__(self, object_list, per_page, count, orphans=0, allow_empty_first_page=True):
        super(Paginator, self).__init__(object_list, per_page, orphans=0, allow_empty_first_page=True)
        self._count = count

    def page(self, number):
        "Returns a Page object for the given 1-based page number."
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        if top + self.orphans >= self.count:
            top = self.count
        return Page(list(self.object_list[bottom:top]), number, self)


def paginate(request, query_list, query_count, on_page):
    page = request.GET.get('page', '1')
    if not page.isdigit():
        page = '1'
    paginator = Paginator(query_list, on_page, query_count)
    try:
        objects = paginator.page(page)
    except (EmptyPage, InvalidPage):
        objects = paginator.page(paginator.num_pages)
    return objects