import urllib
from django.core.paginator import Paginator as DjangoPaginator, Page as DjangoPage, EmptyPage, InvalidPage


class Page(DjangoPage):

    def __init__(self, extra_params, *args, **kwargs):
        if extra_params:
            self.extra_params = ''.join("%s=%s&" % (k, v) for k,v in extra_params.items())
        else:
            self.extra_params = ''
        super(Page, self).__init__(*args, **kwargs)

    def next_page_number(self):
        return "?%spage=%i" % (self.extra_params, self.number + 1)

    def previous_page_number(self):
        return "?%spage=%i" % (self.extra_params, self.number - 1)

    def short_page_range(self):
        RADIUS = 3
        start = self.number - RADIUS if self.number > RADIUS else 1
        end = self.number + RADIUS if self.number < self.paginator.num_pages - RADIUS else self.paginator.num_pages
        return [(i, "?%spage=%i" % (self.extra_params, i)) for i in xrange(start, end + 1)]


class Paginator(DjangoPaginator):
    def __init__(self, object_list, per_page, count, orphans=0, allow_empty_first_page=True):
        super(Paginator, self).__init__(object_list, per_page, orphans=0, allow_empty_first_page=True)
        self._count = count

    def page(self, number, extra_params):
        "Returns a Page object for the given 1-based page number."
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        if top + self.orphans >= self.count:
            top = self.count
        return Page(extra_params, list(self.object_list[bottom:top]), number, self)


def paginate(request, query_list, query_count, on_page):
    page = request.GET.get('page', '1')
    if not page.isdigit():
        page = '1'
    paginator = Paginator(query_list, on_page, query_count)
    extra_params = dict(request.GET.items())
    if 'page' in extra_params:
        del extra_params['page']
    try:
        objects = paginator.page(page, extra_params)
    except (EmptyPage, InvalidPage):
        objects = paginator.page(paginator.num_pages, extra_params)
    return objects