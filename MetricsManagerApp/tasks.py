import pandas as pd
import os
from django.db import transaction
from .models import Company, City, State, Country, Industry
from celery import shared_task

def to_int(value):
    """Convert value to int, handling NaN and None."""
    if pd.isna(value) or value is None:
        return 0
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

def get_or_create_country(name):
    """Get or create a country."""
    return Country.objects.get_or_create(name=name)[0] if name else None

def get_or_create_state(name, country=None):
    """Get or create a state."""
    return State.objects.get_or_create(name=name, country=country)[0] if name else None

def get_or_create_city(name, state=None):
    """Get or create a city."""
    return City.objects.get_or_create(name=name, state=state)[0] if name else None

@shared_task
def process_csv(file_path):
    chunk_size = 1000  # Adjust based on your system's memory capacity

    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        company_records = []

        for _, row in chunk.iterrows():
            locality_value = row.get('locality', '')

            # Skip rows with NaN or empty locality values
            if pd.isna(locality_value) or not str(locality_value).strip() or locality_value.lower() == "nan":
                locality_value = ""

            locality_parts = [part.strip() for part in str(locality_value).split(',') if part.strip()]

            city = None
            state = None
            country = None

            if len(locality_parts) == 3:
                city_name, state_name, country_name = locality_parts
                country = get_or_create_country(country_name)
                state = get_or_create_state(state_name, country)
                city = get_or_create_city(city_name, state)
            elif len(locality_parts) == 2:
                city_name, state_name = locality_parts
                state = get_or_create_state(state_name)
                city = get_or_create_city(city_name, state)
            elif len(locality_parts) == 1:
                city_name = locality_parts[0]
                city = get_or_create_city(city_name)

            industry_name = row.get('industry', '')
            size_range_name = row.get('size range', '')

            company_records.append({
                'name': row.get("name", ""),
                'domain': row.get('domain', ''),
                'year_founded': to_int(row.get('year founded')),
                'industry': Industry.objects.get_or_create(name=industry_name)[0] if industry_name else None,
                'size_range': size_range_name,
                'city': city,
                'linkedin_url': row.get('linkedin url', ''),
                'current_employee_estimate': to_int(row.get('current employee estimate')),
                'total_employee_estimate': to_int(row.get('total employee estimate'))
            })

        # Perform bulk operations
        with transaction.atomic():
            for record in company_records:
                Company.objects.update_or_create(
                    name=record['name'],
                    defaults={
                        'domain': record['domain'],
                        'year_founded': record['year_founded'],
                        'industry': record['industry'],
                        'size_range': record['size_range'],
                        'city': record['city'],
                        'linkedin_url': record['linkedin_url'],
                        'current_employee_estimate': record['current_employee_estimate'],
                        'total_employee_estimate': record['total_employee_estimate']
                    }
                )

    # Optionally delete the file after processing
    os.remove(file_path)
