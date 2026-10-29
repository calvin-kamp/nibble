from django.utils import timezone

# A few columns of the export besides the ones the import reads, as in the real file
EXPORT_COLUMNS = (
    "code",
    "url",
    "product_name",
    "quantity",
    "brands",
    "countries_tags",
    "serving_size",
    "serving_quantity",
    "product_quantity",
    "popularity_tags",
    "energy-kcal_100g",
    "fat_100g",
    "carbohydrates_100g",
    "proteins_100g",
)


def export_line(code, **overrides):
    year = timezone.now().year
    product = {
        "code": code,
        "url": f"https://world.openfoodfacts.org/product/{code}",
        "product_name": "Haferflocken",
        "quantity": "500 g",
        "brands": "Kölln, Peter Kölln KGaA",
        "countries_tags": "en:germany,en:austria",
        "serving_size": "40 g",
        "serving_quantity": "40",
        "product_quantity": "500",
        "popularity_tags": f"top-75-percent-scans-{year - 1},top-de-scans-{year - 1}",
        "energy-kcal_100g": "372",
        "fat_100g": "7",
        "carbohydrates_100g": "58.7",
        "proteins_100g": "13.5",
    }
    product.update(overrides)

    return "\t".join(product[column] for column in EXPORT_COLUMNS)
