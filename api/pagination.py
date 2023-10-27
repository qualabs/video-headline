from django.core.paginator import Paginator, Page, InvalidPage, EmptyPage
from rest_framework.pagination import PageNumberPagination
from collections import OrderedDict

from rest_framework.response import Response


class PerformantPage(Page):
    def has_next(self):
        return self.paginator.has_next

    def has_previous(self):
        return self.paginator.has_previous


class PerformantPaginator(Paginator):
    num_pages = 0

    def __init__(
        self, object_list, per_page, orphans=0, allow_empty_first_page=True
    ):
        super(PerformantPaginator, self).__init__(
            object_list, per_page, orphans, allow_empty_first_page
        )
        self.has_next = False
        self.has_previous = False

    def count(self):
        """Counting the number of items is expensive, so by default it's not
        supported and None will be returned."""
        return None

    def validate_number(self, number):
        """
        Validates the given 1-based page number.
        """
        try:
            number = int(number)
        except (TypeError, ValueError):
            raise InvalidPage('That page number is not an integer')
        if number < 1:
            raise EmptyPage('That page number is less than 1')
        return number

    def page(self, number):
        """
        Returns a Page object for the given 1-based page number.
        """
        page_number = self.validate_number(number)

        bottom = (page_number - 1) * self.per_page
        top = bottom + self.per_page

        # Fetch one more item to check if we have next page
        queryset = self.object_list[bottom: top + 1]
        count = len(queryset)

        if page_number > 1:
            self.has_previous = True

        if count > self.per_page:
            queryset = queryset[0: count - 1]
            self.has_next = True

        return PerformantPage(queryset, page_number, self)


class PageNumberPaginationWithoutCount(PageNumberPagination):
    django_paginator_class = PerformantPaginator

    def get_paginated_response(self, data):
        response = OrderedDict(
            [
                ('next', self.get_next_link()),
                ('previous', self.get_previous_link()),
                ('results', data),
            ]
        )

        return Response(response)
