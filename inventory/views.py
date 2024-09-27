from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import InventoryItem
from .serializers import InventoryItemSerializer
from django.core.cache import cache
import logging

logger = logging.getLogger('django')

class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if InventoryItem.objects.filter(name=serializer.validated_data['name']).exists():
                logger.warning(f"User {request.user} attempted to create an item that already exists")
                return Response({"error": "Item already exists"}, status=status.HTTP_400_BAD_REQUEST)
            self.perform_create(serializer)
            logger.info(f"User {request.user} created a new inventory item")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        cache_key = f'inventory_item_{instance.id}'
        logger.debug(f"Checking cache for item {instance.id}")
        cached_data = cache.get(cache_key)

        if cached_data is None:
            # Data not in cache, retrieving from database
            logger.info(f"Data for item {instance.id} not found in cache. Retrieving from database.")
            serializer = self.get_serializer(instance)
            cached_data = serializer.data
            cache.set(cache_key, cached_data, timeout=60 * 15)  # Cache for 15 minutes
        else:
            # Data retrieved from cache
            logger.info(f"Data for item {instance.id} retrieved from cache.")
            
        logger.info(f"User {request.user} retrieved item {instance.id}")
        return Response(cached_data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            logger.info(f"User {request.user} updated item {instance.id}")
            cache_key = f'inventory_item_{instance.id}'
            cache.delete(cache_key)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        logger.info(f"User {request.user} deleted item {instance.id}")
        cache_key = f'inventory_item_{instance.id}'
        cache.delete(cache_key)
        return Response({"message": "Item deleted successfully"}, status=status.HTTP_200_OK)