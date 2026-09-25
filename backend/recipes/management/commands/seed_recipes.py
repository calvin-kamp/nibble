"""Management command that fills the database with the example recipes.

Contents:
  * RECIPES           -- the 50 recipes; each names only its strictest diet and
                         the values that can't be derived. Units as label, macros
                         per serving.
  * derive_diets      -- adds the looser diets to the strictest one.
  * derive_attributes -- attributes that follow from the recipe values.
  * TAXONOMIES        -- diets, meal types etc., created before the recipes.
  * Command           -- the command itself, run with ``manage.py seed_recipes``.

The recipes get no owner, so they are read-only in the API. The command is safe
to run repeatedly: a recipe whose name already exists without owner is skipped.
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from recipes.models import (
    Attribute,
    CookingStep,
    Diet,
    Equipment,
    Ingredient,
    Intolerance,
    MealType,
    Recipe,
    RecipeIngredient,
)

FRUEHSTUECK = "fruehstueck"
MITTAG = "mittagessen"
ABEND = "abendessen"
SNACK = "snack"
DESSERT = "dessert"

VEGAN = "vegan"
VEGETARISCH = "vegetarisch"
PESCETARISCH = "pescetarisch"

BACKOFEN = "backofen"
HERD = "herd"
AIRFRYER = "airfryer"
MIXER = "mixer"
OHNE_KOCHEN = "ohne-kochen"


def recipe(
    name,
    description,
    *,
    servings,
    minutes,
    macros,
    meals,
    equipment,
    ingredients,
    steps,
    diet=None,
    glutenfree=False,
    lactosefree=False,
    meal_prep=False,
):
    protein, carbs, fat = macros

    return {
        "name": name,
        "description": description,
        "servings": servings,
        "duration_minutes": minutes,
        "protein_per_serving": protein,
        "carbs_per_serving": carbs,
        "fat_per_serving": fat,
        "meal_types": meals,
        "equipment": equipment,
        "diet": diet,
        "glutenfree": glutenfree,
        "lactosefree": lactosefree,
        "meal_prep": meal_prep,
        "ingredients": ingredients,
        "steps": steps,
    }


RECIPES = [
    # ── Frühstück ────────────────────────────────────────────────────────────
    recipe(
        "Overnight Oats mit Beeren",
        "Haferflocken über Nacht in Milch und Joghurt quellen lassen, morgens nur noch Beeren darauf.",
        servings=2,
        minutes=10,
        macros=(16, 52, 9),
        meals=[FRUEHSTUECK],
        equipment=[OHNE_KOCHEN],
        diet=VEGETARISCH,
        meal_prep=True,
        ingredients=[
            (120, "g", "Haferflocken"),
            (250, "ml", "Milch"),
            (150, "g", "Naturjoghurt"),
            (1, "EL", "Chiasamen"),
            (150, "g", "gemischte Beeren"),
            (1, "TL", "Honig"),
        ],
        steps=[
            "Haferflocken, Milch, Joghurt und Chiasamen in einer Schüssel verrühren.",
            "Auf zwei Gläser verteilen, abdecken und über Nacht in den Kühlschrank stellen.",
            "Morgens die Beeren darauf geben und mit Honig beträufeln.",
        ],
    ),
    recipe(
        "Rührei mit Spinat",
        "Cremiges Rührei mit frischem Blattspinat, fertig in zehn Minuten.",
        servings=1,
        minutes=10,
        macros=(20, 3, 16),
        meals=[FRUEHSTUECK],
        equipment=[HERD],
        diet=VEGETARISCH,
        glutenfree=True,
        ingredients=[
            (3, "Stück", "Eier"),
            (50, "g", "Blattspinat"),
            (1, "TL", "Butter"),
            (1, "Prise", "Salz"),
            (1, "Prise", "Pfeffer"),
        ],
        steps=[
            "Butter in einer Pfanne bei mittlerer Hitze schmelzen, Spinat darin zusammenfallen lassen.",
            "Eier verquirlen, mit Salz und Pfeffer würzen und in die Pfanne geben.",
            "Unter langsamem Rühren stocken lassen, solange das Ei noch leicht glänzt vom Herd nehmen.",
        ],
    ),
    recipe(
        "Apfel-Zimt-Porridge",
        "Warmer Haferbrei mit Haferdrink, geriebenem Apfel und Zimt.",
        servings=2,
        minutes=15,
        macros=(9, 58, 7),
        meals=[FRUEHSTUECK],
        equipment=[HERD],
        diet=VEGAN,
        ingredients=[
            (100, "g", "Haferflocken"),
            (400, "ml", "Haferdrink"),
            (1, "Stück", "Apfel"),
            (1, "TL", "Zimt"),
            (1, "EL", "Walnüsse"),
        ],
        steps=[
            "Haferflocken mit dem Haferdrink aufkochen und bei kleiner Hitze fünf Minuten köcheln lassen.",
            "Den Apfel grob reiben und mit dem Zimt unterrühren.",
            "In Schalen füllen und mit gehackten Walnüssen bestreuen.",
        ],
    ),
    recipe(
        "Avocado-Brot mit pochiertem Ei",
        "Vollkornbrot mit zerdrückter Avocado, Zitrone und einem weichen Ei.",
        servings=1,
        minutes=15,
        macros=(14, 30, 20),
        meals=[FRUEHSTUECK],
        equipment=[HERD],
        diet=VEGETARISCH,
        lactosefree=True,
        ingredients=[
            (2, "Scheibe", "Vollkornbrot"),
            (0.5, "Stück", "Avocado"),
            (1, "Stück", "Ei"),
            (1, "TL", "Zitronensaft"),
            (1, "Prise", "Chiliflocken"),
        ],
        steps=[
            "Wasser in einem kleinen Topf zum Sieden bringen, das Ei hineingleiten lassen und vier Minuten garen.",
            "Avocado mit Zitronensaft zerdrücken und auf das geröstete Brot streichen.",
            "Das Ei darauf setzen und mit Chiliflocken bestreuen.",
        ],
    ),
    recipe(
        "Skyr-Bowl mit Nüssen und Honig",
        "Proteinreiches Frühstück ohne Kochen.",
        servings=1,
        minutes=5,
        macros=(27, 30, 12),
        meals=[FRUEHSTUECK, SNACK],
        equipment=[OHNE_KOCHEN],
        diet=VEGETARISCH,
        glutenfree=True,
        ingredients=[
            (250, "g", "Skyr"),
            (20, "g", "Mandeln"),
            (1, "TL", "Honig"),
            (80, "g", "Heidelbeeren"),
        ],
        steps=[
            "Skyr in eine Schale geben und glatt rühren.",
            "Mandeln grob hacken und mit den Heidelbeeren darauf verteilen.",
            "Mit Honig beträufeln.",
        ],
    ),
    recipe(
        "Pfannkuchen",
        "Klassische Pfannkuchen, dazu passen Apfelmus oder Beeren.",
        servings=2,
        minutes=25,
        macros=(15, 55, 12),
        meals=[FRUEHSTUECK, DESSERT],
        equipment=[HERD],
        diet=VEGETARISCH,
        ingredients=[
            (125, "g", "Weizenmehl"),
            (250, "ml", "Milch"),
            (2, "Stück", "Eier"),
            (1, "Prise", "Salz"),
            (1, "EL", "Rapsöl"),
        ],
        steps=[
            "Mehl, Milch, Eier und Salz zu einem glatten Teig verrühren und zehn Minuten ruhen lassen.",
            "Wenig Öl in einer Pfanne erhitzen, eine Kelle Teig hineingeben und dünn verteilen.",
            "Von beiden Seiten goldbraun backen, mit dem restlichen Teig ebenso verfahren.",
        ],
    ),
    recipe(
        "Chia-Pudding mit Mango",
        "Chiasamen in Kokosdrink quellen lassen, mit frischer Mango.",
        servings=2,
        minutes=10,
        macros=(6, 28, 13),
        meals=[FRUEHSTUECK, DESSERT],
        equipment=[OHNE_KOCHEN],
        diet=VEGAN,
        glutenfree=True,
        meal_prep=True,
        ingredients=[
            (50, "g", "Chiasamen"),
            (300, "ml", "Kokosdrink"),
            (1, "Stück", "Mango"),
            (1, "TL", "Ahornsirup"),
        ],
        steps=[
            "Chiasamen, Kokosdrink und Ahornsirup verrühren, nach zehn Minuten noch einmal umrühren.",
            "Abgedeckt mindestens vier Stunden kühlen.",
            "Mango würfeln und auf dem Pudding verteilen.",
        ],
    ),
    recipe(
        "Shakshuka",
        "In würziger Tomaten-Paprika-Sauce gegarte Eier.",
        servings=2,
        minutes=30,
        macros=(17, 18, 15),
        meals=[FRUEHSTUECK, ABEND],
        equipment=[HERD],
        diet=VEGETARISCH,
        glutenfree=True,
        lactosefree=True,
        ingredients=[
            (1, "EL", "Olivenöl"),
            (1, "Stück", "Zwiebel"),
            (1, "Stück", "rote Paprika"),
            (2, "Zehe", "Knoblauch"),
            (1, "Dose", "gehackte Tomaten"),
            (1, "TL", "Kreuzkümmel"),
            (4, "Stück", "Eier"),
            (0.5, "Bund", "Petersilie"),
        ],
        steps=[
            "Zwiebel, Paprika und Knoblauch würfeln und im Olivenöl fünf Minuten andünsten.",
            "Tomaten und Kreuzkümmel dazugeben und zehn Minuten einköcheln lassen.",
            "Vier Mulden in die Sauce drücken, die Eier hineinschlagen und zugedeckt sechs Minuten stocken lassen.",
            "Mit gehackter Petersilie bestreuen.",
        ],
    ),
    recipe(
        "Bananen-Hafer-Smoothie",
        "Sättigender Smoothie mit Banane, Haferflocken und Sojadrink.",
        servings=1,
        minutes=5,
        macros=(12, 60, 7),
        meals=[FRUEHSTUECK, SNACK],
        equipment=[MIXER],
        diet=VEGAN,
        ingredients=[
            (1, "Stück", "Banane"),
            (30, "g", "Haferflocken"),
            (250, "ml", "Sojadrink"),
            (1, "TL", "Erdnussmus"),
        ],
        steps=[
            "Alle Zutaten in den Mixer geben.",
            "Eine Minute fein pürieren und sofort trinken.",
        ],
    ),
    recipe(
        "Gemüse-Ei-Muffins",
        "Herzhafte Muffins aus Ei und Gemüse, halten im Kühlschrank vier Tage.",
        servings=6,
        minutes=35,
        macros=(12, 3, 9),
        meals=[FRUEHSTUECK, SNACK],
        equipment=[BACKOFEN],
        diet=VEGETARISCH,
        glutenfree=True,
        meal_prep=True,
        ingredients=[
            (8, "Stück", "Eier"),
            (1, "Stück", "rote Paprika"),
            (60, "g", "Blattspinat"),
            (50, "g", "Feta"),
            (1, "Prise", "Salz"),
            (1, "Prise", "Pfeffer"),
        ],
        steps=[
            "Backofen auf 180 °C Ober- und Unterhitze vorheizen, ein Muffinblech einfetten.",
            "Paprika fein würfeln, Spinat hacken und beides auf zwölf Mulden verteilen.",
            "Eier mit Salz und Pfeffer verquirlen, darüber gießen und Feta darauf bröseln.",
            "20 Minuten backen, bis die Eimasse fest ist.",
        ],
    ),
    recipe(
        "Tofu-Rührei",
        "Veganes Rührei aus zerbröseltem Tofu mit Kurkuma.",
        servings=2,
        minutes=15,
        macros=(18, 5, 12),
        meals=[FRUEHSTUECK],
        equipment=[HERD],
        diet=VEGAN,
        glutenfree=True,
        ingredients=[
            (300, "g", "Naturtofu"),
            (1, "EL", "Olivenöl"),
            (0.5, "TL", "Kurkuma"),
            (1, "Stück", "Frühlingszwiebel"),
            (1, "Prise", "Kala Namak"),
        ],
        steps=[
            "Tofu mit einer Gabel grob zerbröseln.",
            "Im heißen Öl mit Kurkuma fünf Minuten braten, bis er leicht Farbe nimmt.",
            "Mit Kala Namak würzen und mit Frühlingszwiebelringen bestreuen.",
        ],
    ),
    # ── Mittag- und Abendessen ───────────────────────────────────────────────
    recipe(
        "Spaghetti Bolognese",
        "Langsam geköchelte Hackfleischsauce mit Spaghetti.",
        servings=4,
        minutes=60,
        macros=(32, 78, 18),
        meals=[MITTAG, ABEND],
        equipment=[HERD],
        lactosefree=True,
        meal_prep=True,
        ingredients=[
            (400, "g", "Rinderhackfleisch"),
            (1, "Stück", "Zwiebel"),
            (1, "Stück", "Karotte"),
            (2, "Zehe", "Knoblauch"),
            (2, "EL", "Tomatenmark"),
            (2, "Dose", "passierte Tomaten"),
            (400, "g", "Spaghetti"),
            (1, "EL", "Olivenöl"),
        ],
        steps=[
            "Zwiebel, Karotte und Knoblauch fein würfeln und im Olivenöl andünsten.",
            "Hackfleisch dazugeben und krümelig braten, dann das Tomatenmark kurz mitrösten.",
            "Passierte Tomaten zugeben und die Sauce 40 Minuten bei kleiner Hitze köcheln lassen.",
            "Spaghetti nach Packungsangabe kochen und mit der Sauce servieren.",
        ],
    ),
    recipe(
        "Linsen-Dal mit Reis",
        "Rote Linsen in Kokosmilch mit Ingwer und Kurkuma.",
        servings=4,
        minutes=35,
        macros=(19, 72, 13),
        meals=[MITTAG, ABEND],
        equipment=[HERD],
        diet=VEGAN,
        glutenfree=True,
        meal_prep=True,
        ingredients=[
            (250, "g", "rote Linsen"),
            (200, "ml", "Kokosmilch"),
            (1, "Stück", "Zwiebel"),
            (1, "Stück", "Ingwer, daumengroß"),
            (1, "TL", "Kurkuma"),
            (1, "TL", "Garam Masala"),
            (1, "Dose", "gehackte Tomaten"),
            (200, "g", "Basmatireis"),
        ],
        steps=[
            "Zwiebel und Ingwer fein hacken und in einem Topf anschwitzen, Gewürze kurz mitrösten.",
            "Linsen, Tomaten, Kokosmilch und 500 ml Wasser zugeben und 20 Minuten köcheln lassen.",
            "Parallel den Reis nach Packungsangabe garen.",
            "Das Dal mit Salz abschmecken und mit dem Reis servieren.",
        ],
    ),
    recipe(
        "Chili sin Carne",
        "Bohnen, Mais und Paprika in rauchiger Tomatensauce.",
        servings=4,
        minutes=45,
        macros=(16, 50, 7),
        meals=[MITTAG, ABEND],
        equipment=[HERD],
        diet=VEGAN,
        glutenfree=True,
        meal_prep=True,
        ingredients=[
            (1, "Dose", "Kidneybohnen"),
            (1, "Dose", "schwarze Bohnen"),
            (1, "Dose", "Mais"),
            (2, "Stück", "rote Paprika"),
            (1, "Stück", "Zwiebel"),
            (2, "Dose", "gehackte Tomaten"),
            (1, "TL", "geräuchertes Paprikapulver"),
            (1, "TL", "Kreuzkümmel"),
        ],
        steps=[
            "Zwiebel und Paprika würfeln und in etwas Öl anbraten.",
            "Gewürze kurz mitrösten, dann die Tomaten zugeben.",
            "Bohnen und Mais abspülen, dazugeben und 30 Minuten köcheln lassen.",
        ],
    ),
    recipe(
        "Chili con Carne",
        "Klassisches Chili mit Rinderhack und Kidneybohnen.",
        servings=4,
        minutes=50,
        macros=(30, 30, 16),
        meals=[MITTAG, ABEND],
        equipment=[HERD],
        glutenfree=True,
        lactosefree=True,
        meal_prep=True,
        ingredients=[
            (500, "g", "Rinderhackfleisch"),
            (1, "Stück", "Zwiebel"),
            (2, "Zehe", "Knoblauch"),
            (2, "Dose", "gehackte Tomaten"),
            (1, "Dose", "Kidneybohnen"),
            (1, "Dose", "Mais"),
            (1, "TL", "Chilipulver"),
            (1, "TL", "Kreuzkümmel"),
        ],
        steps=[
            "Zwiebel und Knoblauch hacken und mit dem Hackfleisch krümelig anbraten.",
            "Gewürze zugeben und eine Minute mitrösten.",
            "Tomaten, abgespülte Bohnen und Mais zugeben und 35 Minuten köcheln lassen.",
        ],
    ),
    recipe(
        "Hähnchen-Curry mit Reis",
        "Mildes Curry mit Hähnchenbrust, Kokosmilch und Gemüse.",
        servings=4,
        minutes=35,
        macros=(34, 55, 16),
        meals=[MITTAG, ABEND],
        equipment=[HERD],
        glutenfree=True,
        lactosefree=True,
        meal_prep=True,
        ingredients=[
            (500, "g", "Hähnchenbrust"),
            (400, "ml", "Kokosmilch"),
            (2, "EL", "rote Currypaste"),
            (1, "Stück", "rote Paprika"),
            (1, "Stück", "Zucchini"),
            (250, "g", "Jasminreis"),
            (1, "EL", "Rapsöl"),
        ],
        steps=[
            "Reis nach Packungsangabe garen.",
            "Hähnchen in Würfel schneiden und im Öl rundum anbraten.",
            "Currypaste kurz mitrösten, Gemüse und Kokosmilch zugeben.",
            "Zehn Minuten köcheln lassen und mit dem Reis servieren.",
        ],
    ),
    recipe(
        "Lachs mit Ofengemüse",
        "Lachsfilet und buntes Gemüse vom Blech.",
        servings=2,
        minutes=35,
        macros=(34, 22, 24),
        meals=[MITTAG, ABEND],
        equipment=[BACKOFEN],
        diet=PESCETARISCH,
        glutenfree=True,
        lactosefree=True,
        ingredients=[
            (2, "Stück", "Lachsfilets"),
            (300, "g", "Brokkoli"),
            (1, "Stück", "rote Paprika"),
            (1, "Stück", "rote Zwiebel"),
            (2, "EL", "Olivenöl"),
            (1, "Stück", "Zitrone"),
        ],
        steps=[
            "Backofen auf 200 °C Ober- und Unterhitze vorheizen.",
            "Gemüse klein schneiden, mit Öl und Salz mischen und 15 Minuten backen.",
            "Lachs dazulegen, mit Zitronensaft beträufeln und weitere 12 Minuten backen.",
        ],
    ),
    recipe(
        "Gemüse-Lasagne",
        "Lasagne mit Zucchini, Aubergine und Tomatensauce.",
        servings=6,
        minutes=75,
        macros=(20, 45, 17),
        meals=[MITTAG, ABEND],
        equipment=[BACKOFEN, HERD],
        diet=VEGETARISCH,
        meal_prep=True,
        ingredients=[
            (250, "g", "Lasagneplatten"),
            (2, "Stück", "Zucchini"),
            (1, "Stück", "Aubergine"),
            (2, "Dose", "passierte Tomaten"),
            (250, "g", "Ricotta"),
            (150, "g", "geriebener Mozzarella"),
            (1, "Stück", "Zwiebel"),
        ],
        steps=[
            "Zwiebel, Zucchini und Aubergine würfeln, anbraten und mit den Tomaten zehn Minuten köcheln lassen.",
            "Backofen auf 180 °C vorheizen.",
            "Sauce, Lasagneplatten und Ricotta abwechselnd in eine Form schichten, mit Sauce abschließen.",
            "Mozzarella darüber streuen und 40 Minuten backen.",
        ],
    ),
    recipe(
        "Griechischer Salat",
        "Tomaten, Gurke, Oliven und Feta mit Oregano.",
        servings=2,
        minutes=15,
        macros=(10, 12, 22),
        meals=[MITTAG, ABEND],
        equipment=[OHNE_KOCHEN],
        diet=VEGETARISCH,
        glutenfree=True,
        ingredients=[
            (3, "Stück", "Tomaten"),
            (1, "Stück", "Salatgurke"),
            (1, "Stück", "rote Zwiebel"),
            (100, "g", "Feta"),
            (50, "g", "Kalamata-Oliven"),
            (2, "EL", "Olivenöl"),
            (1, "TL", "Oregano"),
        ],
        steps=[
            "Tomaten und Gurke in grobe Stücke, Zwiebel in feine Ringe schneiden.",
            "Mit Oliven, Olivenöl und Oregano mischen.",
            "Feta in Scheiben darauf legen.",
        ],
    ),
    recipe(
        "Kichererbsen-Salat",
        "Frischer Salat mit Kichererbsen, Gurke und Zitronen-Dressing.",
        servings=3,
        minutes=15,
        macros=(12, 32, 10),
        meals=[MITTAG],
        equipment=[OHNE_KOCHEN],
        diet=VEGAN,
        glutenfree=True,
        meal_prep=True,
        ingredients=[
            (2, "Dose", "Kichererbsen"),
            (1, "Stück", "Salatgurke"),
            (200, "g", "Kirschtomaten"),
            (0.5, "Bund", "Petersilie"),
            (2, "EL", "Olivenöl"),
            (1, "Stück", "Zitrone"),
        ],
        steps=[
            "Kichererbsen abspülen und abtropfen lassen.",
            "Gurke würfeln, Tomaten halbieren, Petersilie hacken.",
            "Alles mit Olivenöl, Zitronensaft und Salz mischen.",
        ],
    ),
    recipe(
        "Tomatensuppe",
        "Samtige Suppe aus Tomaten und Paprika.",
        servings=4,
        minutes=30,
        macros=(4, 16, 5),
        meals=[MITTAG, ABEND],
        equipment=[HERD, MIXER],
        diet=VEGAN,
        glutenfree=True,
        ingredients=[
            (2, "Dose", "gehackte Tomaten"),
            (1, "Stück", "rote Paprika"),
            (1, "Stück", "Zwiebel"),
            (500, "ml", "Gemüsebrühe"),
            (1, "EL", "Olivenöl"),
            (0.5, "Bund", "Basilikum"),
        ],
        steps=[
            "Zwiebel und Paprika würfeln und im Öl andünsten.",
            "Tomaten und Brühe zugeben und 15 Minuten köcheln lassen.",
            "Mit dem Basilikum fein pürieren und abschmecken.",
        ],
    ),
    recipe(
        "Kürbissuppe",
        "Hokkaido-Suppe mit Ingwer und Kokosmilch.",
        servings=4,
        minutes=35,
        macros=(4, 20, 10),
        meals=[MITTAG, ABEND],
        equipment=[HERD, MIXER],
        diet=VEGAN,
        glutenfree=True,
        meal_prep=True,
        ingredients=[
            (1, "kg", "Hokkaido-Kürbis"),
            (1, "Stück", "Zwiebel"),
            (1, "Stück", "Ingwer, daumengroß"),
            (750, "ml", "Gemüsebrühe"),
            (200, "ml", "Kokosmilch"),
        ],
        steps=[
            "Kürbis entkernen und mit Schale würfeln, Zwiebel und Ingwer hacken.",
            "Alles kurz andünsten, mit Brühe aufgießen und 20 Minuten köcheln lassen.",
            "Kokosmilch zugeben und fein pürieren.",
        ],
    ),
    recipe(
        "Hähnchen mit Brokkoli und Reis",
        "Schlichtes Meal-Prep-Gericht für mehrere Tage.",
        servings=4,
        minutes=30,
        macros=(42, 55, 8),
        meals=[MITTAG, ABEND],
        equipment=[HERD],
        glutenfree=True,
        lactosefree=True,
        meal_prep=True,
        ingredients=[
            (600, "g", "Hähnchenbrust"),
            (500, "g", "Brokkoli"),
            (250, "g", "Basmatireis"),
            (1, "EL", "Rapsöl"),
            (1, "TL", "Paprikapulver"),
        ],
        steps=[
            "Reis nach Packungsangabe kochen.",
            "Hähnchen in Streifen schneiden, mit Paprikapulver würzen und im Öl durchbraten.",
            "Brokkoli in Röschen teilen und fünf Minuten dämpfen.",
            "Alles auf vier Dosen verteilen.",
        ],
    ),
    recipe(
        "Hähnchenschenkel mit Kartoffeln aus dem Airfryer",
        "Knusprige Hähnchenschenkel und Kartoffelspalten in einem Durchgang.",
        servings=2,
        minutes=40,
        macros=(36, 40, 20),
        meals=[MITTAG, ABEND],
        equipment=[AIRFRYER],
        glutenfree=True,
        lactosefree=True,
        ingredients=[
            (4, "Stück", "Hähnchenunterschenkel"),
            (500, "g", "festkochende Kartoffeln"),
            (1, "EL", "Olivenöl"),
            (1, "TL", "Paprikapulver"),
            (1, "TL", "Rosmarin"),
        ],
        steps=[
            "Kartoffeln in Spalten schneiden, mit Öl, Rosmarin und Salz mischen.",
            "Hähnchen mit Paprikapulver und Salz einreiben.",
            "Alles in den Airfryer legen und bei 190 °C 30 Minuten garen, nach der Hälfte wenden.",
        ],
    ),
    recipe(
        "Falafel aus dem Airfryer",
        "Falafel aus eingeweichten Kichererbsen, ohne Frittieren.",
        servings=4,
        minutes=30,
        macros=(12, 30, 8),
        meals=[MITTAG, ABEND, SNACK],
        equipment=[AIRFRYER, MIXER],
        diet=VEGAN,
        glutenfree=True,
        meal_prep=True,
        ingredients=[
            (250, "g", "getrocknete Kichererbsen, eingeweicht"),
            (1, "Stück", "Zwiebel"),
            (2, "Zehe", "Knoblauch"),
            (1, "Bund", "Petersilie"),
            (1, "TL", "Kreuzkümmel"),
            (1, "EL", "Olivenöl"),
        ],
        steps=[
            "Kichererbsen abgießen und mit Zwiebel, Knoblauch, Petersilie und Kreuzkümmel grob mixen.",
            "Mit Salz abschmecken und zu kleinen Bällchen formen.",
            "Mit Öl bepinseln und bei 190 °C 15 Minuten im Airfryer garen, nach der Hälfte wenden.",
        ],
    ),
    recipe(
        "Gebratener Reis mit Ei",
        "Reste-Reis aus der Pfanne mit Erbsen und Ei.",
        servings=2,
        minutes=20,
        macros=(15, 65, 12),
        meals=[MITTAG, ABEND],
        equipment=[HERD],
        diet=VEGETARISCH,
        lactosefree=True,
        ingredients=[
            (400, "g", "gekochter Reis vom Vortag"),
            (2, "Stück", "Eier"),
            (150, "g", "TK-Erbsen"),
            (2, "Stück", "Frühlingszwiebeln"),
            (2, "EL", "Sojasauce"),
            (1, "EL", "Rapsöl"),
        ],
        steps=[
            "Öl in einer großen Pfanne stark erhitzen, Erbsen zwei Minuten braten.",
            "Reis zugeben und unter Rühren fünf Minuten braten.",
            "Reis zur Seite schieben, die Eier daneben verquirlen und stocken lassen, dann alles mischen.",
            "Mit Sojasauce würzen und Frühlingszwiebeln darüber geben.",
        ],
    ),
    recipe(
        "Thunfisch-Pasta",
        "Schnelle Pasta mit Thunfisch, Tomaten und Kapern.",
        servings=2,
        minutes=20,
        macros=(33, 80, 10),
        meals=[MITTAG, ABEND],
        equipment=[HERD],
        diet=PESCETARISCH,
        lactosefree=True,
        ingredients=[
            (200, "g", "Penne"),
            (1, "Dose", "Thunfisch im eigenen Saft"),
            (1, "Dose", "gehackte Tomaten"),
            (1, "EL", "Kapern"),
            (1, "Zehe", "Knoblauch"),
            (1, "EL", "Olivenöl"),
        ],
        steps=[
            "Penne nach Packungsangabe kochen.",
            "Knoblauch im Öl andünsten, Tomaten und Kapern zugeben und fünf Minuten köcheln lassen.",
            "Thunfisch zerpflücken, unterheben und mit der Pasta mischen.",
        ],
    ),
    recipe(
        "Kartoffel-Gemüse-Pfanne",
        "Bratkartoffeln mit Paprika, Zucchini und Kräutern.",
        servings=2,
        minutes=30,
        macros=(7, 45, 11),
        meals=[MITTAG, ABEND],
        equipment=[HERD],
        diet=VEGAN,
        glutenfree=True,
        ingredients=[
            (600, "g", "festkochende Kartoffeln"),
            (1, "Stück", "rote Paprika"),
            (1, "Stück", "Zucchini"),
            (1, "Stück", "Zwiebel"),
            (2, "EL", "Rapsöl"),
            (1, "TL", "Thymian"),
        ],
        steps=[
            "Kartoffeln in kleine Würfel schneiden und im Öl 15 Minuten braten.",
            "Zwiebel, Paprika und Zucchini würfeln, zugeben und weitere acht Minuten braten.",
            "Mit Thymian, Salz und Pfeffer abschmecken.",
        ],
    ),
    recipe(
        "Ofenkartoffel mit Kräuterquark",
        "Große Backkartoffeln mit Quark und frischen Kräutern.",
        servings=2,
        minutes=60,
        macros=(22, 55, 6),
        meals=[MITTAG, ABEND],
        equipment=[BACKOFEN],
        diet=VEGETARISCH,
        glutenfree=True,
        ingredients=[
            (4, "Stück", "große mehligkochende Kartoffeln"),
            (250, "g", "Magerquark"),
            (100, "g", "Naturjoghurt"),
            (1, "Bund", "Schnittlauch"),
            (1, "EL", "Olivenöl"),
        ],
        steps=[
            "Backofen auf 200 °C vorheizen, Kartoffeln waschen, mit Öl einreiben und einstechen.",
            "50 Minuten backen, bis sie weich sind.",
            "Quark, Joghurt und gehackten Schnittlauch verrühren und salzen.",
            "Kartoffeln aufschneiden und mit dem Quark füllen.",
        ],
    ),
    recipe(
        "Quinoa-Bowl mit Ofengemüse",
        "Quinoa, Süßkartoffel, Kichererbsen und Tahin-Sauce.",
        servings=2,
        minutes=40,
        macros=(18, 75, 18),
        meals=[MITTAG, ABEND],
        equipment=[BACKOFEN, HERD],
        diet=VEGAN,
        glutenfree=True,
        meal_prep=True,
        ingredients=[
            (150, "g", "Quinoa"),
            (1, "Stück", "Süßkartoffel"),
            (1, "Dose", "Kichererbsen"),
            (100, "g", "Babyspinat"),
            (2, "EL", "Tahin"),
            (1, "Stück", "Zitrone"),
            (1, "EL", "Olivenöl"),
        ],
        steps=[
            "Backofen auf 200 °C vorheizen, Süßkartoffel würfeln, mit Kichererbsen und Öl mischen und 25 Minuten backen.",
            "Quinoa nach Packungsangabe kochen.",
            "Tahin mit Zitronensaft und etwas Wasser glatt rühren.",
            "Quinoa, Spinat und Ofengemüse in Schalen anrichten und mit der Sauce beträufeln.",
        ],
    ),
    recipe(
        "Garnelen-Zucchini-Pfanne",
        "Garnelen mit Zucchini, Knoblauch und Zitrone.",
        servings=2,
        minutes=15,
        macros=(26, 6, 9),
        meals=[MITTAG, ABEND],
        equipment=[HERD],
        diet=PESCETARISCH,
        glutenfree=True,
        lactosefree=True,
        ingredients=[
            (300, "g", "Garnelen, geschält"),
            (2, "Stück", "Zucchini"),
            (2, "Zehe", "Knoblauch"),
            (1, "EL", "Olivenöl"),
            (1, "Stück", "Zitrone"),
        ],
        steps=[
            "Zucchini in Halbmonde schneiden und im Öl vier Minuten braten.",
            "Knoblauch und Garnelen zugeben und braten, bis die Garnelen rosa sind.",
            "Mit Zitronensaft, Salz und Pfeffer abschmecken.",
        ],
    ),
    recipe(
        "Rindergeschnetzeltes mit Paprika",
        "Zarte Rinderstreifen mit Paprika und Zwiebeln.",
        servings=3,
        minutes=25,
        macros=(35, 10, 14),
        meals=[MITTAG, ABEND],
        equipment=[HERD],
        glutenfree=True,
        lactosefree=True,
        ingredients=[
            (500, "g", "Rinderhüfte"),
            (2, "Stück", "rote Paprika"),
            (1, "Stück", "Zwiebel"),
            (1, "EL", "Rapsöl"),
            (1, "TL", "Paprikapulver"),
            (150, "ml", "Rinderbrühe"),
        ],
        steps=[
            "Fleisch in feine Streifen schneiden und portionsweise im heißen Öl scharf anbraten.",
            "Zwiebel und Paprika in Streifen schneiden und in derselben Pfanne fünf Minuten braten.",
            "Fleisch zurückgeben, mit Brühe ablöschen, würzen und kurz einkochen lassen.",
        ],
    ),
    recipe(
        "Pilzrisotto",
        "Cremiges Risotto mit braunen Champignons und Parmesan.",
        servings=3,
        minutes=40,
        macros=(14, 70, 13),
        meals=[MITTAG, ABEND],
        equipment=[HERD],
        diet=VEGETARISCH,
        glutenfree=True,
        ingredients=[
            (250, "g", "Risottoreis"),
            (300, "g", "braune Champignons"),
            (1, "Stück", "Zwiebel"),
            (1, "l", "Gemüsebrühe"),
            (40, "g", "Parmesan"),
            (1, "EL", "Butter"),
        ],
        steps=[
            "Pilze in Scheiben schneiden und in der Hälfte der Butter anbraten, dann herausnehmen.",
            "Zwiebel würfeln und im Topf andünsten, Reis zugeben und glasig werden lassen.",
            "Nach und nach heiße Brühe angießen und unter Rühren 18 Minuten garen.",
            "Pilze, restliche Butter und Parmesan unterrühren.",
        ],
    ),
    recipe(
        "Spinat-Feta-Quiche",
        "Quiche mit Mürbeteig, Blattspinat und Feta.",
        servings=6,
        minutes=70,
        macros=(14, 25, 24),
        meals=[MITTAG, ABEND],
        equipment=[BACKOFEN],
        diet=VEGETARISCH,
        ingredients=[
            (1, "Packung", "Mürbeteig aus dem Kühlregal"),
            (300, "g", "Blattspinat"),
            (150, "g", "Feta"),
            (4, "Stück", "Eier"),
            (200, "ml", "Milch"),
            (1, "Prise", "Muskatnuss"),
        ],
        steps=[
            "Backofen auf 190 °C vorheizen und eine Tarteform mit dem Teig auslegen.",
            "Spinat in einer Pfanne zusammenfallen lassen und gut ausdrücken.",
            "Eier mit Milch, Muskat und Salz verquirlen, Spinat und zerbröselten Feta unterheben.",
            "Auf den Teig gießen und 40 Minuten backen.",
        ],
    ),
    recipe(
        "Hähnchen-Wraps",
        "Weizen-Wraps mit gebratenem Hähnchen, Salat und Joghurtsauce.",
        servings=2,
        minutes=20,
        macros=(35, 45, 12),
        meals=[MITTAG, ABEND],
        equipment=[HERD],
        ingredients=[
            (300, "g", "Hähnchenbrust"),
            (4, "Stück", "Weizentortillas"),
            (100, "g", "Eisbergsalat"),
            (2, "Stück", "Tomaten"),
            (150, "g", "Naturjoghurt"),
            (1, "TL", "Paprikapulver"),
        ],
        steps=[
            "Hähnchen in Streifen schneiden, mit Paprikapulver würzen und durchbraten.",
            "Joghurt mit Salz und Pfeffer verrühren, Salat und Tomaten klein schneiden.",
            "Tortillas kurz erwärmen, belegen und einrollen.",
        ],
    ),
    recipe(
        "Kabeljau mit Senfsauce und Kartoffeln",
        "Gedünsteter Kabeljau mit heller Senfsauce.",
        servings=2,
        minutes=30,
        macros=(35, 40, 9),
        meals=[MITTAG, ABEND],
        equipment=[HERD],
        diet=PESCETARISCH,
        glutenfree=True,
        ingredients=[
            (2, "Stück", "Kabeljaufilets"),
            (500, "g", "Kartoffeln"),
            (150, "ml", "Kochsahne 15 %"),
            (1, "EL", "mittelscharfer Senf"),
            (0.5, "Bund", "Dill"),
        ],
        steps=[
            "Kartoffeln schälen und in Salzwasser 20 Minuten kochen.",
            "Sahne mit Senf aufkochen, den Fisch hineinlegen und zugedeckt acht Minuten ziehen lassen.",
            "Mit gehacktem Dill bestreuen und mit den Kartoffeln servieren.",
        ],
    ),
    recipe(
        "Tofu-Gemüse-Wok mit Reisnudeln",
        "Knuspriger Tofu mit Pak Choi und Karotten.",
        servings=2,
        minutes=25,
        macros=(20, 60, 14),
        meals=[MITTAG, ABEND],
        equipment=[HERD],
        diet=VEGAN,
        glutenfree=True,
        ingredients=[
            (200, "g", "Naturtofu"),
            (150, "g", "Reisnudeln"),
            (2, "Stück", "Pak Choi"),
            (2, "Stück", "Karotten"),
            (3, "EL", "Tamari"),
            (1, "EL", "Sesamöl"),
        ],
        steps=[
            "Reisnudeln nach Packungsangabe einweichen.",
            "Tofu würfeln und im Sesamöl knusprig braten, dann herausnehmen.",
            "Karotten in Streifen, Pak Choi in Stücke schneiden und drei Minuten im Wok braten.",
            "Nudeln, Tofu und Tamari zugeben und alles durchschwenken.",
        ],
    ),
    recipe(
        "Putenbällchen in Tomatensauce",
        "Saftige Hackbällchen aus Pute in Tomatensauce.",
        servings=4,
        minutes=40,
        macros=(30, 14, 10),
        meals=[MITTAG, ABEND],
        equipment=[HERD],
        lactosefree=True,
        meal_prep=True,
        ingredients=[
            (500, "g", "Putenhackfleisch"),
            (1, "Stück", "Ei"),
            (3, "EL", "Semmelbrösel"),
            (1, "Stück", "Zwiebel"),
            (2, "Dose", "passierte Tomaten"),
            (1, "TL", "Oregano"),
        ],
        steps=[
            "Hackfleisch mit Ei, Semmelbröseln, der Hälfte der gehackten Zwiebel und Salz verkneten.",
            "Walnussgroße Bällchen formen und rundum anbraten.",
            "Restliche Zwiebel dazugeben, mit Tomaten ablöschen und mit Oregano 20 Minuten köcheln lassen.",
        ],
    ),
    recipe(
        "Süßkartoffel mit schwarzen Bohnen",
        "Gefüllte Ofen-Süßkartoffel mit Bohnen, Mais und Limette.",
        servings=2,
        minutes=50,
        macros=(14, 80, 6),
        meals=[MITTAG, ABEND],
        equipment=[BACKOFEN],
        diet=VEGAN,
        glutenfree=True,
        ingredients=[
            (2, "Stück", "Süßkartoffeln"),
            (1, "Dose", "schwarze Bohnen"),
            (0.5, "Dose", "Mais"),
            (1, "Stück", "Limette"),
            (0.5, "Bund", "Koriander"),
        ],
        steps=[
            "Backofen auf 200 °C vorheizen, Süßkartoffeln einstechen und 45 Minuten backen.",
            "Bohnen und Mais abspülen und mit Limettensaft und Salz mischen.",
            "Süßkartoffeln längs aufschneiden, füllen und mit Koriander bestreuen.",
        ],
    ),
    recipe(
        "Ofen-Hähnchenbrust mit Gemüse",
        "Hähnchen und Gemüse vom Blech mit Kräutern.",
        servings=3,
        minutes=35,
        macros=(40, 14, 10),
        meals=[MITTAG, ABEND],
        equipment=[BACKOFEN],
        glutenfree=True,
        lactosefree=True,
        meal_prep=True,
        ingredients=[
            (600, "g", "Hähnchenbrust"),
            (2, "Stück", "Zucchini"),
            (250, "g", "Kirschtomaten"),
            (1, "Stück", "rote Zwiebel"),
            (1, "EL", "Olivenöl"),
            (1, "TL", "italienische Kräuter"),
        ],
        steps=[
            "Backofen auf 200 °C vorheizen.",
            "Gemüse klein schneiden, mit Öl, Kräutern und Salz auf einem Blech verteilen.",
            "Hähnchenbrust würzen, dazulegen und 25 Minuten backen.",
        ],
    ),
    recipe(
        "Linsen-Bolognese",
        "Vegane Bolognese mit Berglinsen und Vollkornspaghetti.",
        servings=4,
        minutes=40,
        macros=(22, 80, 6),
        meals=[MITTAG, ABEND],
        equipment=[HERD],
        diet=VEGAN,
        meal_prep=True,
        ingredients=[
            (200, "g", "Berglinsen"),
            (1, "Stück", "Zwiebel"),
            (1, "Stück", "Karotte"),
            (2, "EL", "Tomatenmark"),
            (2, "Dose", "passierte Tomaten"),
            (400, "g", "Vollkornspaghetti"),
        ],
        steps=[
            "Zwiebel und Karotte fein würfeln und andünsten, Tomatenmark kurz mitrösten.",
            "Linsen, Tomaten und 300 ml Wasser zugeben und 25 Minuten köcheln lassen.",
            "Spaghetti nach Packungsangabe kochen und mit der Sauce servieren.",
        ],
    ),
    # ── Snacks ───────────────────────────────────────────────────────────────
    recipe(
        "Hummus mit Gemüsesticks",
        "Selbst gemachter Hummus mit Karotten und Gurke zum Dippen.",
        servings=4,
        minutes=15,
        macros=(8, 20, 10),
        meals=[SNACK],
        equipment=[MIXER],
        diet=VEGAN,
        glutenfree=True,
        meal_prep=True,
        ingredients=[
            (1, "Dose", "Kichererbsen"),
            (2, "EL", "Tahin"),
            (1, "Stück", "Zitrone"),
            (1, "Zehe", "Knoblauch"),
            (3, "Stück", "Karotten"),
            (1, "Stück", "Salatgurke"),
        ],
        steps=[
            "Kichererbsen abgießen, das Wasser auffangen.",
            "Mit Tahin, Zitronensaft, Knoblauch und etwas Kichererbsenwasser cremig mixen.",
            "Karotten und Gurke in Sticks schneiden und dazu servieren.",
        ],
    ),
    recipe(
        "Dattel-Energiebällchen",
        "Kleine Bällchen aus Datteln, Haferflocken und Kakao.",
        servings=6,
        minutes=15,
        macros=(4, 28, 7),
        meals=[SNACK],
        equipment=[MIXER, OHNE_KOCHEN],
        diet=VEGAN,
        meal_prep=True,
        ingredients=[
            (200, "g", "entsteinte Datteln"),
            (80, "g", "Haferflocken"),
            (50, "g", "Mandeln"),
            (1, "EL", "Kakaopulver"),
        ],
        steps=[
            "Alle Zutaten im Mixer zu einer klebrigen Masse verarbeiten.",
            "Mit feuchten Händen 18 Bällchen formen.",
            "Im Kühlschrank fest werden lassen.",
        ],
    ),
    recipe(
        "Quark mit Beeren",
        "Schneller Eiweißsnack aus Magerquark und Beeren.",
        servings=1,
        minutes=5,
        macros=(30, 18, 1),
        meals=[SNACK, DESSERT],
        equipment=[OHNE_KOCHEN],
        diet=VEGETARISCH,
        glutenfree=True,
        ingredients=[
            (250, "g", "Magerquark"),
            (100, "g", "Himbeeren"),
            (1, "TL", "Honig"),
        ],
        steps=[
            "Quark mit einem Schuss Wasser glatt rühren.",
            "Himbeeren darauf geben und mit Honig beträufeln.",
        ],
    ),
    recipe(
        "Geröstete Kichererbsen",
        "Knusprige Kichererbsen mit Paprika aus dem Ofen.",
        servings=3,
        minutes=35,
        macros=(8, 20, 6),
        meals=[SNACK],
        equipment=[BACKOFEN],
        diet=VEGAN,
        glutenfree=True,
        meal_prep=True,
        ingredients=[
            (2, "Dose", "Kichererbsen"),
            (1, "EL", "Olivenöl"),
            (1, "TL", "geräuchertes Paprikapulver"),
            (1, "Prise", "Salz"),
        ],
        steps=[
            "Backofen auf 200 °C vorheizen, Kichererbsen abspülen und gut trocken tupfen.",
            "Mit Öl, Paprikapulver und Salz mischen.",
            "Auf einem Blech 30 Minuten rösten, zwischendurch einmal wenden.",
        ],
    ),
    recipe(
        "Edamame mit Meersalz",
        "Gekochte Sojabohnen in der Schote.",
        servings=2,
        minutes=10,
        macros=(12, 9, 6),
        meals=[SNACK],
        equipment=[HERD],
        diet=VEGAN,
        glutenfree=True,
        ingredients=[
            (300, "g", "TK-Edamame"),
            (1, "TL", "grobes Meersalz"),
        ],
        steps=[
            "Edamame in kochendem Salzwasser fünf Minuten garen.",
            "Abgießen und mit Meersalz bestreuen.",
        ],
    ),
    # ── Desserts ─────────────────────────────────────────────────────────────
    recipe(
        "Schoko-Avocado-Mousse",
        "Cremige Mousse aus Avocado, Kakao und Ahornsirup.",
        servings=2,
        minutes=10,
        macros=(4, 24, 18),
        meals=[DESSERT],
        equipment=[MIXER, OHNE_KOCHEN],
        diet=VEGAN,
        glutenfree=True,
        ingredients=[
            (2, "Stück", "reife Avocados"),
            (3, "EL", "Kakaopulver"),
            (3, "EL", "Ahornsirup"),
            (50, "ml", "Haferdrink"),
        ],
        steps=[
            "Avocados halbieren und das Fruchtfleisch herauslösen.",
            "Mit Kakao, Ahornsirup und Haferdrink glatt mixen.",
            "Mindestens 30 Minuten kalt stellen.",
        ],
    ),
    recipe(
        "Apfel-Crumble",
        "Warme Äpfel unter knusprigen Butterstreuseln.",
        servings=4,
        minutes=45,
        macros=(4, 48, 12),
        meals=[DESSERT],
        equipment=[BACKOFEN],
        diet=VEGETARISCH,
        ingredients=[
            (4, "Stück", "Äpfel"),
            (100, "g", "Weizenmehl"),
            (60, "g", "Butter"),
            (50, "g", "brauner Zucker"),
            (1, "TL", "Zimt"),
        ],
        steps=[
            "Backofen auf 180 °C vorheizen, Äpfel würfeln und mit Zimt in eine Auflaufform geben.",
            "Mehl, kalte Butter und Zucker zu Streuseln verkneten und darüber verteilen.",
            "30 Minuten goldbraun backen.",
        ],
    ),
    recipe(
        "Bananen-Eis",
        "Eis aus gefrorenen Bananen, ohne Zucker.",
        servings=2,
        minutes=5,
        macros=(2, 32, 1),
        meals=[DESSERT, SNACK],
        equipment=[MIXER],
        diet=VEGAN,
        glutenfree=True,
        ingredients=[
            (3, "Stück", "gefrorene Bananen"),
            (2, "EL", "Haferdrink"),
        ],
        steps=[
            "Gefrorene Bananen in Stücke brechen.",
            "Mit dem Haferdrink im Mixer cremig pürieren und sofort essen.",
        ],
    ),
    recipe(
        "Protein-Käsekuchen",
        "Käsekuchen aus Magerquark ohne Boden.",
        servings=8,
        minutes=70,
        macros=(18, 16, 4),
        meals=[DESSERT],
        equipment=[BACKOFEN],
        diet=VEGETARISCH,
        meal_prep=True,
        ingredients=[
            (1, "kg", "Magerquark"),
            (3, "Stück", "Eier"),
            (80, "g", "Zucker"),
            (1, "Packung", "Vanillepuddingpulver"),
            (1, "Stück", "Zitrone"),
        ],
        steps=[
            "Backofen auf 170 °C vorheizen und eine Springform auslegen.",
            "Quark, Eier, Zucker, Puddingpulver und Zitronenabrieb glatt rühren.",
            "In die Form füllen und 50 Minuten backen.",
            "Im ausgeschalteten Ofen bei leicht geöffneter Tür abkühlen lassen.",
        ],
    ),
]


# A vegan recipe also fits the vegetarian and pescetarian filter, and so on.
DIET_INCLUDES = {
    "vegan": ["vegan", "vegetarisch", "pescetarisch"],
    "vegetarisch": ["vegetarisch", "pescetarisch"],
    "pescetarisch": ["pescetarisch"],
}

TAXONOMIES = [
    (Diet, "diet"),
    (Intolerance, "intolerance"),
    (MealType, "meal_type"),
    (Equipment, "equipment"),
    (Attribute, "attribute"),
]

UNDER_MINUTES = 30
FEW_INGREDIENTS = 5
LOW_KCAL = 300
PROTEIN_MIN_GRAMS = 20
PROTEIN_MIN_SHARE = Decimal("0.25")

UNITS = {unit.label: unit for unit in RecipeIngredient.UnitChoice}


def derive_diets(data):
    return DIET_INCLUDES.get(data["diet"], [])


def derive_intolerances(data):
    values = []

    if data["glutenfree"]:
        values.append("glutenfrei")

    # Vegan recipes contain no milk products by definition.
    if data["lactosefree"] or data["diet"] == "vegan":
        values.append("laktosefrei")

    return values


def derive_attributes(recipe, data):
    values = []
    protein_share = recipe.protein_per_serving * 4 / recipe.kcal_per_serving

    if (
        recipe.protein_per_serving >= PROTEIN_MIN_GRAMS
        and protein_share >= PROTEIN_MIN_SHARE
    ):
        values.append("proteinreich")

    if recipe.kcal_per_serving <= LOW_KCAL:
        values.append("kalorienarm")

    if data["meal_prep"]:
        values.append("meal-prep")

    if recipe.duration_minutes < UNDER_MINUTES:
        values.append("unter-30-min")

    if len(data["ingredients"]) <= FEW_INGREDIENTS:
        values.append("wenig-zutaten")

    return values


class Command(BaseCommand):
    """Seeds the example recipes and the taxonomy values they rely on."""

    help = "Seeds the example recipes (without owner, read-only in the API)."

    def handle(self, *args, **options):
        self.seed_taxonomies()

        existing = set(
            Recipe.objects.filter(owner__isnull=True).values_list("name", flat=True)
        )
        created = 0

        for data in RECIPES:
            if data["name"] in existing:
                continue

            self.create_recipe(data)
            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Recipes: {created} new, {len(RECIPES) - created} skipped."
            )
        )

    def seed_taxonomies(self):
        """One row per choice value, so the recipes can reference them."""
        for model, field_name in TAXONOMIES:
            for value, _label in model._meta.get_field(field_name).choices:
                model.objects.get_or_create(**{field_name: value})

    @transaction.atomic
    def create_recipe(self, data):
        # save() calculates kcal_per_serving from the macros.
        recipe = Recipe.objects.create(
            name=data["name"],
            description=data["description"],
            servings=data["servings"],
            duration_minutes=data["duration_minutes"],
            protein_per_serving=Decimal(str(data["protein_per_serving"])),
            carbs_per_serving=Decimal(str(data["carbs_per_serving"])),
            fat_per_serving=Decimal(str(data["fat_per_serving"])),
        )

        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=self.get_or_create_ingredient(name),
                amount=Decimal(str(amount)),
                unit=UNITS[unit],
            )
            for amount, unit, name in data["ingredients"]
        )

        CookingStep.objects.bulk_create(
            CookingStep(recipe=recipe, step=number, text=text)
            for number, text in enumerate(data["steps"], start=1)
        )

        recipe.meal_types.set(MealType.objects.filter(meal_type__in=data["meal_types"]))
        recipe.equipment.set(Equipment.objects.filter(equipment__in=data["equipment"]))
        recipe.diets.set(Diet.objects.filter(diet__in=derive_diets(data)))
        recipe.intolerances.set(
            Intolerance.objects.filter(intolerance__in=derive_intolerances(data))
        )
        recipe.attributes.set(
            Attribute.objects.filter(attribute__in=derive_attributes(recipe, data))
        )

    def get_or_create_ingredient(self, name):
        """Case-insensitive, like the serializer, so both share one entry."""
        ingredient = Ingredient.objects.filter(name__iexact=name).first()

        return ingredient or Ingredient.objects.create(name=name)
