from django.core.paginator import Paginator as DjangoPaginator, Page


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