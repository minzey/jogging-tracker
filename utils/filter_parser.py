from pyparsing import nestedExpr
from rest_framework import filters


class QueryParser:

    def combine_q_filters(self, qfilter):
        if isinstance(qfilter, list):
            try:
                operator = "&" if qfilter[1] == "AND" else "|"
                return "(" + self.combine_q_filters(qfilter[0]) + f" {operator} " + self.combine_q_filters(qfilter[2]) + ")"
            except IndexError:
                return self.combine_q_filters(qfilter[0])
        else:
            return qfilter

    def construct_q_filter(self, lookup_list):
        for index, token in enumerate(lookup_list):
            if token == "AND" or token == "OR":
                continue
            if isinstance(token, list):
                lookup_list[index] = self.construct_q_filter(token)
            else:
                if lookup_list[1] == "ne":
                    return f"~Q({lookup_list[0]}__iexact={lookup_list[2]})"
                elif lookup_list[1] == "eq":
                    return f"Q({lookup_list[0]}__iexact={lookup_list[2]})"
                return f"Q({lookup_list[0]}__{lookup_list[1]}={lookup_list[2]})"

        return lookup_list

    def transform_to_q_filter(self, expr_string):
        expr_string = '(' + expr_string + ')'
        parsed = nestedExpr('(', ')').parseString(expr_string).asList()
        qfilters = self.combine_q_filters(self.construct_q_filter(parsed)[0])
        return qfilters


# if __name__ == "__main__":
#     transformed = QueryParser().transform_to_qfilter("(date eq '2016-05-01') AND ((distance ne 20) OR ((distance lt 10) AND (time gt 300)))")
#     print(transformed)

class PrecedenceQueryFilter(filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """
    def filter_queryset(self, request, queryset, view):
        filter_string = request.query_params.get("filter", None)
        if filter_string:
            transformed_q_filter_string = QueryParser().transform_to_q_filter(filter_string)
            queryset = queryset.filter(eval(transformed_q_filter_string))
        return queryset
