from django.core.management.base import BaseCommand
from tracker.models import Activity
from collections import defaultdict
from django.db import transaction


class Command(BaseCommand):
    help = 'Merge activities whose names differ only by case for the same user'

    def handle(self, *args, **options):
        # Group activities by (telegram_chat_id, lowercased name)
        groups = defaultdict(list)
        for act in Activity.objects.all():
            key = (act.telegram_chat_id, act.name.lower())
            groups[key].append(act)

        merged_count = 0
        for (chat_id, lower_name), activities in groups.items():
            unique_casings = set(a.name for a in activities)
            if len(unique_casings) < 2:
                continue  # No duplicates for this group

            # Pick the most common casing. Tie-break by longest string.
            casing_counts = defaultdict(int)
            for a in activities:
                casing_counts[a.name] += 1
            max_count = max(casing_counts.values())
            candidates = [c for c, n in casing_counts.items() if n == max_count]
            if len(candidates) > 1:
                chosen_casing = max(candidates, key=lambda c: len(c))
            else:
                chosen_casing = candidates[0]

            self.stdout.write(
                f"Chat {chat_id}: merging {unique_casings} → '{chosen_casing}'"
            )

            # Update all activities with variant casings to use chosen_casing
            with transaction.atomic():
                updated = Activity.objects.filter(
                    telegram_chat_id=chat_id,
                    name__in=list(unique_casings - {chosen_casing}),
                ).update(name=chosen_casing)
                merged_count += updated

        self.stdout.write(self.style.SUCCESS(
            f"Merged {merged_count} activity record(s) to consistent casing."
        ))
