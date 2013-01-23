import urllib
from django.core.paginator import Paginator as DjangoPaginator, Page as DjangoPage, EmptyPage, InvalidPage


class Page(DjangoPage):

    def __init__(self, url, *args, **kwargs):
        self.url = url
        super(Page, self).__init__(*args, **kwargs)

    def next_page_number(self):
        return "%spage=%i" % (self.url, self.number + 1)

    def previous_page_number(self):
        return "%spage=%i" % (self.url, self.number - 1)

    def short_page_range(self):
        def item(i):
            return (i, "%spage=%i" % (self.url, i))
        RADIUS = 3
        COUNT = self.paginator.num_pages
        start = self.number - RADIUS if self.number > RADIUS else 1
        end = self.number + RADIUS if self.number < COUNT - RADIUS else COUNT
        range = [item(i) for i in xrange(start, end + 1)]
        front = 2 + RADIUS
        if self.number >= front:
            if self.number > front + RADIUS - 1:
                range.insert(0, ('...', item(1 + (self.number - RADIUS) / 2)[1]))
            range.insert(0, item(1))
        front = COUNT - front
        if self.number <= front:
            if self.number < front - RADIUS + 1:
                range.append(('...', item(self.number + RADIUS + (COUNT - (self.number + RADIUS)) / 2)[1]))
            range.append(item(COUNT))
        return range


class Paginator(DjangoPaginator):
    def __init__(self, object_list, per_page, count, orphans=0, allow_empty_first_page=True):
        super(Paginator, self).__init__(object_list, per_page, orphans=0, allow_empty_first_page=True)
        self._count = count

    def page(self, number, url):
        "Returns a Page object for the given 1-based page number."
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        if top + self.orphans >= self.count:
            top = self.count
        return Page(url, list(self.object_list[bottom:top]), number, self)


def paginate(request, query_list, query_count, on_page, url=''):
    page = request.GET.get('page', '1')
    if not page.isdigit():
        page = '1'
    paginator = Paginator(query_list, on_page, query_count)
    extra_params = dict(request.GET.items())
    if 'page' in extra_params:
        del extra_params['page']
    url = "%s?" % url
    if url:
        url += ''.join("%s=%s&" % (k, v) for k,v in extra_params.items())
    try:
        objects = paginator.page(page, url)
    except (EmptyPage, InvalidPage):
        objects = paginator.page(paginator.num_pages, url)
    return objects