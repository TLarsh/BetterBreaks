from typing import Optional
import logging

from django.db import transaction

from core.models.break_execution import BreakExecution

logger = logging.getLogger(__name__)


class BreakExecutionService:
    @staticmethod
    def upsert_execution(
        user,
        recommended_start,
        recommended_end,
        *,
        status: Optional[str] = None,
        actual_start: Optional[object] = None,
        actual_end: Optional[object] = None,
    ):
        """
        Create or update a BreakExecution for the given recommended date range.
        Returns the BreakExecution instance or None on failure.
        """
        try:
            with transaction.atomic():
                exec_obj, created = BreakExecution.objects.get_or_create(
                    user=user,
                    recommended_start=recommended_start,
                    recommended_end=recommended_end,
                    defaults={
                        "status": status or BreakExecution.STATUS_CHOICES[0][0],
                        "actual_start": actual_start,
                        "actual_end": actual_end,
                    },
                )

                if not created:
                    update_fields = []
                    if status and exec_obj.status != status:
                        exec_obj.status = status
                        update_fields.append("status")
                    if actual_start is not None and exec_obj.actual_start != actual_start:
                        exec_obj.actual_start = actual_start
                        update_fields.append("actual_start")
                    if actual_end is not None and exec_obj.actual_end != actual_end:
                        exec_obj.actual_end = actual_end
                        update_fields.append("actual_end")
                    if update_fields:
                        exec_obj.save(update_fields=update_fields)

                return exec_obj
        except Exception:
            logger.exception("Failed to upsert BreakExecution")
            return None