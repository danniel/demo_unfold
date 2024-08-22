from django.db import models
from django.utils import timezone
from fossil_delta import create_delta, apply_delta


class Notebook(models.Model):
    title = models.CharField(default="", max_length=100, blank=True, null=False)
    content = models.JSONField(default=dict)
    updated_on = models.DateTimeField(auto_now=timezone.now, editable=False)

    class Meta:
        ordering = ("-updated_on",)
        get_latest_by = "updated_on"

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        # TODO: All this stuff should be in a transaction
        if self.pk:
            # Generate a new revision for the Notebook and save the content delta
            previous = Notebook.objects.get(pk=self.pk)
            delta = create_delta(
                str(self.content).encode("utf8"), str(previous.content).encode("utf8")
            )
            revision = ContentRevision(notebook=previous, content_delta=delta)
            revision.save()
        return super().save(*args, **kwargs)


class ContentRevision(models.Model):
    notebook = models.ForeignKey(
        Notebook, on_delete=models.CASCADE, blank=False, null=False
    )
    content_delta = models.BinaryField(blank=True, null=True, editable=False)
    created_on = models.DateTimeField(auto_now_add=timezone.now, editable=False)

    class Meta:
        ordering = ("-created_on",)
        get_latest_by = "created_on"

    def __str__(self) -> str:
        # We start from the Notebook's current content
        content = self.notebook.content

        # Retrieve this revision all the NEWER revisions of the current Notebook
        newer_revisions = self.notebook.contentrevision_set.exclude(
            created_on__lt=self.created_on
        ).order_by("-created_on")

        # Build the previous content by applying the chain of revision deltas to the current content
        for revision in newer_revisions:
            content = apply_delta(
                str(content).encode("utf8"), revision.content_delta
            ).decode("utf8")

        # For now just show that old content as str
        return content
