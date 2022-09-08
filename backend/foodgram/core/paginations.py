from rest_framework import pagination


class PageLimitPagination(pagination.PageNumberPagination):
    page_size_query_param = 'limit'
