from django.db.models import Case, IntegerField, Value, When


def ordered_members(queryset):
    return queryset.annotate(
        _membership_rank=Case(
            When(graduation_date__isnull=True, then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        ),
        _role_rank=Case(
            When(role_type__icontains="导师", then=Value(0)),
            When(role_type__iexact="PI", then=Value(0)),
            When(role_type__icontains="博士后", then=Value(1)),
            When(role_type__iexact="postdoc", then=Value(1)),
            When(role_type__icontains="博士", then=Value(2)),
            When(role_type__iexact="phd", then=Value(2)),
            When(role_type__icontains="硕士", then=Value(3)),
            When(role_type__iexact="master", then=Value(3)),
            When(role_type__icontains="本科", then=Value(4)),
            When(role_type__iexact="undergraduate", then=Value(4)),
            default=Value(5),
            output_field=IntegerField(),
        ),
    ).order_by("_membership_rank", "_role_rank", "sort_order", "name")
