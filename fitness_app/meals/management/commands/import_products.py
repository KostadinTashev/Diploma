import re
import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.db import transaction
from fitness_app.meals.models import Product  # ⇦ коригирай ако пътят е различен

# ──────────────────────────────────────────────────────────────────────────────
GROUPS_URL = "https://www.bb-team.org/hrani"
GROUP_LINK_RE = re.compile(r"^/hrani/[^/]+$")  # /hrani/агнешки-продукти …

CYRILLIC_NAME_RE = re.compile(r"^[\u0400-\u04FF\d\s\-\(\)\.,\"']+$")

NUTR_KEYS = {
    "Ккал": "calories_per_100g",
    "Въглехидрати": "carbohydrates_per_100g",
    "Мазнини": "fats_per_100g",
    "Белтъчини": "proteins_per_100g",
}


# ──────────────────────────────────────────────────────────────────────────────


class Command(BaseCommand):
    help = (
        "Импортира или обновява хранителни продукти от bb-team.org/hrani "
        "директно в таблицата Product."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Презаписва вече съществуващите продукти.",
        )

    # ──────────────────────────────────────────────────────────────────────────
    def handle(self, *args, **opts):
        overwrite = opts["overwrite"]
        session = requests.Session()
        self.stdout.write("→ Чета списъка с групи …")

        group_slugs = self._get_group_slugs(session)
        if not group_slugs:
            self.stderr.write("❌   Не намерих групи! Вероятно HTML структурата се е променила.")
            return

        self.stdout.write(f"✔︎ Намерени групи: {len(group_slugs)}\n")

        new_count = updated_count = skipped_bad_name = 0

        for slug in group_slugs:
            url = f"https://www.bb-team.org{slug}"
            self.stdout.write(f"  → Сканирам {url}")
            html = session.get(url, timeout=30).text
            soup = BeautifulSoup(html, "lxml")

            # таблицата е единствената <table class="composition-table">
            table = soup.find("table")
            if not table:
                continue

            for tr in table.select("tbody > tr"):
                cols = [c.get_text(strip=True).replace(",", ".") for c in tr("td")]
                if len(cols) < 5:
                    continue

                name = cols[0]
                if not CYRILLIC_NAME_RE.match(name):
                    skipped_bad_name += 1
                    continue

                data = {
                    "calories_per_100g": self._to_float(cols[1]),
                    "carbohydrates_per_100g": self._to_float(cols[2]),
                    "fats_per_100g": self._to_float(cols[3]),
                    "proteins_per_100g": self._to_float(cols[4]),
                }

                # ако всички макро­стойности са 0 или None – пропусни
                if all(v in (0, None) for v in data.values()):
                    continue

                with transaction.atomic():
                    obj, created = Product.objects.update_or_create(
                        name=name,
                        defaults=data if overwrite or created else {},
                    )
                    if created:
                        new_count += 1
                    elif overwrite:
                        updated_count += 1

        self.stdout.write("\n──── Резултат ────")
        self.stdout.write(f"  ▸ Нови продукти:         {new_count}")
        self.stdout.write(f"  ▸ Обновени продукти:     {updated_count}")
        self.stdout.write(f"  ▸ Пропуснати (име ≠ BG): {skipped_bad_name}")
        self.stdout.write("Готово!")

    # ──────────────────────────────────────────────────────────────────────────
    def _get_group_slugs(self, session):
        """Връща списък от URL пътища към всяка група /hrani/<slug>."""
        html = session.get(GROUPS_URL, timeout=30).text
        soup = BeautifulSoup(html, "lxml")
        # Всяка група е <a href="/hrani/<slug>"> …
        return [
            a["href"]
            for a in soup.find_all("a", href=GROUP_LINK_RE)
            if "/hrani/" in a["href"] and a["href"].count("/") == 2
        ]

    @staticmethod
    def _to_float(value):
        try:
            return float(value)
        except ValueError:
            return None
