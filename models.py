from django.db import models
from django.contrib.postgres.fields import ArrayField, HStoreField, JSONField  # if Postgres is used
import uuid

class AllFields(models.Model):
    # Text-based
    char_field = models.CharField("CharField", max_length=50, choices=[("a", "Option A"), ("b", "Option B")])
    text_field = models.TextField("TextField", blank=True)

    # Numbers
    integer_field = models.IntegerField("IntegerField", default=0)
    big_integer_field = models.BigIntegerField("BigIntegerField", default=0)
    small_integer_field = models.SmallIntegerField("SmallIntegerField", default=0)
    positive_integer_field = models.PositiveIntegerField("PositiveIntegerField", default=0)
    positive_small_integer_field = models.PositiveSmallIntegerField("PositiveSmallIntegerField", default=0)
    float_field = models.FloatField("FloatField", default=0.0)
    decimal_field = models.DecimalField("DecimalField", max_digits=10, decimal_places=2, default=0.00)

    # Boolean
    boolean_field = models.BooleanField("BooleanField", default=False)
    null_boolean_field = models.BooleanField("NullBooleanField (deprecated, test only)", null=True)

    # Date & Time
    date_field = models.DateField("DateField", auto_now=False, auto_now_add=False, null=True, blank=True)
    datetime_field = models.DateTimeField("DateTimeField", null=True, blank=True)
    time_field = models.TimeField("TimeField", null=True, blank=True)
    duration_field = models.DurationField("DurationField", null=True, blank=True)

    # Files & Images
    file_field = models.FileField("FileField", upload_to="files/", null=True, blank=True)
    image_field = models.ImageField("ImageField", upload_to="images/", null=True, blank=True)

    # Relationships
    foreign_key = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="fk_related")
    one_to_one = models.OneToOneField("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="oto_related")
    many_to_many = models.ManyToManyField("self", blank=True, related_name="m2m_related")

    # UUID / Slug / Generic
    slug_field = models.SlugField("SlugField", max_length=50, unique=True)
    uuid_field = models.UUIDField("UUIDField", unique=True, default=uuid.uuid4)

    # Email, URL, IP
    email_field = models.EmailField("EmailField", max_length=100, blank=True)
    url_field = models.URLField("URLField", max_length=200, blank=True)
    ip_field = models.GenericIPAddressField("IPAddressField", protocol="both", unpack_ipv4=True, null=True, blank=True)

    # Binary & JSON
    binary_field = models.BinaryField("BinaryField", blank=True, null=True)
    json_field = models.JSONField("JSONField", default=dict, blank=True, null=True)

    # Postgres-specific (optional, safe to remove if not using Postgres)
    array_field = ArrayField(models.CharField(max_length=20), size=5, null=True, blank=True)
    hstore_field = HStoreField(null=True, blank=True)

    # Choices using TextChoices
    class StatusChoices(models.TextChoices):
        ACTIVE = "A", "Active"
        INACTIVE = "I", "Inactive"

    status_choice = models.CharField(
        "Status Choice",
        max_length=1,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
    )

    def __str__(self):
        return f"AllFields #{self.id}"
