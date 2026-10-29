from django.core.management.base import BaseCommand
from PIL import Image, UnidentifiedImageError

from apps.recipes.catalog.serializers import IMAGE_EXTENSIONS
from apps.recipes.models import Recipe, RecipeSubmission
from apps.recipes.utils import encode_without_metadata, has_metadata


class Command(BaseCommand):
    help = (
        "Removes EXIF, XMP and IPTC metadata from stored recipe and revision images. "
        "Files without metadata stay untouched, so running it twice changes nothing."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Only list the files that still carry metadata.",
        )

    def handle(self, *args, dry_run, **options):
        files = [recipe.image for recipe in Recipe.objects.exclude(image="")]
        files += [
            submission.image
            for submission in RecipeSubmission.objects.exclude(image="")
        ]
        cleaned = 0

        for file in files:
            if not file.storage.exists(file.name):
                self.stderr.write(f"Missing: {file.name}")
                continue

            try:
                with file.storage.open(file.name, "rb") as stored:
                    with Image.open(stored) as image:
                        image_format = image.format
                        dirty = has_metadata(image)

                    if not dirty or image_format not in IMAGE_EXTENSIONS:
                        continue

                    if not dry_run:
                        data = encode_without_metadata(stored, image_format)
            except (OSError, UnidentifiedImageError) as exc:
                self.stderr.write(f"Unreadable: {file.name} ({exc})")
                continue

            cleaned += 1

            if dry_run:
                self.stdout.write(f"Has metadata: {file.name}")
                continue

            # Same name, so recipes and revisions keep pointing at the file.
            with file.storage.open(file.name, "wb") as stored:
                stored.write(data)

            self.stdout.write(f"Cleaned: {file.name}")

        verb = "carry metadata" if dry_run else "cleaned"
        self.stdout.write(
            self.style.SUCCESS(f"{cleaned} of {len(files)} images {verb}.")
        )
