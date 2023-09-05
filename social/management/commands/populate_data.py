from django.core.management.base import BaseCommand
from social.models import *
import json


def search_catg(data_obj, search_item):
    for category, items in data_obj.items():
        if search_item in items:
            return [category, True]
    return [None, False]


class Command(BaseCommand):
    help = 'Populate data from JSON file into models'

    def handle(self, *args, **options):
        json_file_path = '/home/shreedhar/mysocial/social/management/commands/iconData.json'

        with open(json_file_path, 'r') as file:
            data = json.load(file)

        icons_data = data.get("icons", {})
        categories_data = data.get("categories", {})

        cat_count = 0
        for cat in categories_data:
            cat_count += 1
            Category.objects.get_or_create(name=cat, internal_name=cat)

        obj_list = []
        tot_found = 0
        i = 0
        for object_key, object_data in icons_data.items():
            i += 1
            if "body" in object_data:
                tot_found += 1
                item_body = object_data["body"]
                body_title = f"<title>{object_key}</title>"
                item_body = item_body + body_title
                curr_category, found = search_catg(categories_data, object_key)
                curr_category = str(curr_category)
                if found:
                    temp_category = Category.objects.get(name=curr_category)
                else:
                    temp_category = None
                model_instance = Icon(
                    category=temp_category,
                    internal_name=object_key,
                    html=item_body,
                    name=object_key
                )
                obj_list.append(model_instance)
                
        self.stdout.write(self.style.SUCCESS(
            f'Total {i} icons Found'))
        self.stdout.write(self.style.SUCCESS(
            f'Total {tot_found} icons created in DataBase'))
        self.stdout.write(self.style.SUCCESS(
            f'Total {cat_count} categories created in DataBase'))

        Icon.objects.bulk_create(obj_list)
        