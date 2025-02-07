from django.db import models

class NERText(models.Model):
    text = models.TextField(default="Default text")

    def __str__(self):
        return self.text

class NERResult(models.Model):
    ner_text = models.ForeignKey(NERText, related_name='results', on_delete=models.CASCADE)
    entity = models.CharField(max_length=255, default="Unknown entity")
    entity_type = models.CharField(max_length=255, default="Unknown type")
    occurrences = models.IntegerField(default=0)

    def __str__(self):
        # return f"{self.entity} ({self.entity_type}) - {self.occurrences}"
        return f"{self.entity}|{self.entity_type}|{self.occurrences}"