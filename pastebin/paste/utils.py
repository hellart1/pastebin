from django.views.generic.detail import SingleObjectMixin


class StrObjectMixin(SingleObjectMixin):
    str_field = 'data'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        str = self.kwargs.get(self.str_field)

        if not str:
            raise AttributeError("Str is required to get an object")

        return queryset.filter(**{self.str_field: str}).get()
