#!/usr/bin/env python
"""
Debug script to identify test issues.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'advanced_api_project.settings')
django.setup()

from api.models import Author, Book
from django.test import Client
from django.urls import reverse

def debug_search_functionality():
    """Debug the search functionality."""
    print("🔍 Debugging Search Functionality")
    print("=" * 50)
    
    client = Client()
    url = reverse('book-list')
    
    # Test different search terms
    search_terms = ['harry', 'potter', 'rowling', 'tolkien', '1984']
    
    for term in search_terms:
        response = client.get(url, {'search': term})
        print(f"\nSearch term: '{term}'")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.data
            if isinstance(data, list):
                results = data
            elif 'results' in data:
                results = data['results']
            else:
                results = data
            
            print(f"Results found: {len(results)}")
            for i, book in enumerate(results[:3]):  # Show first 3 results
                print(f"  {i+1}. {book.get('title', 'N/A')} by {book.get('author_name', 'N/A')}")

if __name__ == "__main__":
    debug_search_functionality()