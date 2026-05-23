from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    """
    Paginación estándar para todos los listados de la API.
    Parámetros de query:
      - page      → número de página (default: 1)
      - page_size → registros por página (default: 10, max: 100)
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'

    def get_paginated_response(self, data):
        return Response({
            'total': self.page.paginator.count,
            'paginas': self.page.paginator.num_pages,
            'pagina_actual': self.page.number,
            'siguiente': self.get_next_link(),
            'anterior': self.get_previous_link(),
            'resultados': data,
        })

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'total':         {'type': 'integer'},
                'paginas':       {'type': 'integer'},
                'pagina_actual': {'type': 'integer'},
                'siguiente':     {'type': 'string', 'nullable': True},
                'anterior':      {'type': 'string', 'nullable': True},
                'resultados':    schema,
            }
        }

