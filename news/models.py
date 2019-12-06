from django.db import models

# Create your models here.


class News(models.Model):
    title = models.CharField(max_length=200, unique=True, db_index=True)
    abstract = models.TextField()
    url = models.TextField()
    source = models.CharField(max_length=20, blank=True, null=True)
    savedate = models.DateTimeField(db_index=True)
    keyword = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        db_table = "t_ff_news"
        ordering = ['id']
        verbose_name = '新闻'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title
