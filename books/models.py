from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=255,default = '')
    author = models.CharField(max_length=255, default = '')
    price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class BaseQuerySet(models.QuerySet):
    def delete(self):
        count = self.update(is_deleted = True)
        model_label = f"{self.model._meta.app_label}.{self.model.__name__}"
        return count, {model_label: count}
    

class DeletedManager(models.Manager):
    def get_queryset(self):
        return BaseQuerySet(self.model, using=self._db).filter(is_deleted = False)
    
class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at =models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    objects = DeletedManager()
    all_objects = BaseQuerySet.as_manager()

    def __str__(self):
        return self.title
    
    def delete(self, using = None, keep_parents = False):
        self.is_deleted = True
        self.save(update_fields=["is_deleted", "updated_at"])
        model_label = f"{self._meta.app_label}.{self.__class__.__name__}"
        return 1, {model_label:1}