"""Compatibility CRUD views: arrays by default, opt-in pagination and scoped filters."""
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from player_profiles.permissions import IsAdmin


class ResourceView(APIView):
    permission_classes = [IsAdmin]
    scope_player = False
    search_fields = ()
    filter_fields = ()

    def queryset(self):
        rows = self.model.objects.all().order_by('id')
        if self.scope_player and self.request.user.role.name != 'Admin':
            rows = rows.filter(player_id=self.request.user.pk)
        for field in self.filter_fields:
            value = self.request.query_params.get(field)
            if value:
                try:
                    rows = rows.filter(**{field: int(value)})
                except ValueError:
                    raise serializers.ValidationError({field: 'Use a numeric ID.'})
        search = self.request.query_params.get('search', '').strip()
        if search and self.search_fields:
            condition = Q()
            for field in self.search_fields:
                condition |= Q(**{f'{field}__icontains': search})
            rows = rows.filter(condition)
        ordering = self.request.query_params.get('ordering')
        allowed = {field.name for field in self.model._meta.fields}
        if ordering and ordering.lstrip('-') in allowed:
            rows = rows.order_by(ordering, 'id')
        return rows

    def serialize(self, *args, **kwargs):
        return self.serializer_class(*args, context={'request': self.request}, **kwargs)


class ResourceList(ResourceView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rows = self.queryset()
        if 'page' not in request.query_params:
            return Response(self.serialize(rows, many=True).data)
        try:
            page = max(1, int(request.query_params['page']))
            size = min(100, max(1, int(request.query_params.get('page_size', 25))))
        except ValueError:
            raise serializers.ValidationError({'page': 'Use positive integers for pagination.'})
        count = rows.count()
        start = (page - 1) * size
        return Response({'count': count, 'next': page + 1 if start + size < count else None,
                         'previous': page - 1 if page > 1 else None,
                         'results': self.serialize(rows[start:start + size], many=True).data})


class ResourceCreate(ResourceView):
    success_status = 200

    def post(self, request):
        serializer = self.serialize(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                serializer.save()
        except IntegrityError:
            raise serializers.ValidationError({'non_field_errors': ['This assignment or value already exists.']})
        return Response(serializer.data, status=self.success_status)


class ResourceDetail(ResourceView):
    def get(self, request, pk):
        return Response(self.serialize(get_object_or_404(self.queryset(), pk=pk)).data)


class ResourceUpdate(ResourceView):
    def put(self, request, pk):
        serializer = self.serialize(get_object_or_404(self.queryset(), pk=pk), data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                serializer.save()
        except IntegrityError:
            raise serializers.ValidationError({'non_field_errors': ['This assignment or value already exists.']})
        return Response(serializer.data)


class ResourceDelete(ResourceView):
    def delete(self, request, pk):
        record = get_object_or_404(self.queryset(), pk=pk)
        try:
            record.delete()
        except ProtectedError as error:
            counts = {}
            for obj in error.protected_objects:
                label = str(obj._meta.verbose_name_plural)
                counts[label] = counts.get(label, 0) + 1
            return Response({'message': 'This record is still referenced. Review its dependencies before deleting.',
                             'dependencies': counts}, status=409)
        return Response(status=204)
