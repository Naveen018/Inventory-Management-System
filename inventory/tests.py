from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import InventoryItem

class InventoryAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='Nav@3112000', email='test@gmail.com')
        self.client.force_authenticate(user=self.user)

        self.item_data = {
            "name": "Test Item",
            "description": "This is a test item",
            "quantity": 10,
            "price": "9.99"
        }

        self.item = InventoryItem.objects.create(**self.item_data)

    def test_create_item(self):
        self.assertTrue(InventoryItem.objects.filter(name=self.item_data['name']).exists())
        response = self.client.post('/api/inventory/items/', self.item_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print(response.data)
        self.assertIn('name', response.data)
        self.assertEqual(response.data['name'][0], 'inventory item with this name already exists.')

        new_item_data = self.item_data.copy()
        new_item_data['name'] = "New Test Item"
        response = self.client.post('/api/inventory/items/', new_item_data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(InventoryItem.objects.count(), 2)  # Assuming one item was created in setUp
        self.assertEqual(InventoryItem.objects.get(name="New Test Item").name, "New Test Item")

    def test_retrieve_item(self):
        response = self.client.get(f'/api/inventory/items/{self.item.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.item_data['name'])

    def test_update_item(self):
        updated_data = {
            "name": "Updated Test Item",
            "quantity": 20
        }
        response = self.client.patch(f'/api/inventory/items/{self.item.id}/', updated_data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], updated_data['name'])
        self.assertEqual(response.data['quantity'], updated_data['quantity'])

    def test_delete_item(self):
        response = self.client.delete(f'/api/inventory/items/{self.item.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Item deleted successfully")
        self.assertFalse(InventoryItem.objects.filter(id=self.item.id).exists())

    def test_retrieve_nonexistent_item(self):
        response = self.client.get('/api/inventory/items/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_nonexistent_item(self):
        response = self.client.put('/api/inventory/items/9999/', {"name": "Nonexistent Item"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_nonexistent_item(self):
        response = self.client.delete('/api/inventory/items/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)