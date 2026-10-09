from django.conf import settings
from django.db import models


class Group(models.Model):
    """
    A performance group / ukulele club (e.g. FWC, I-Ukes).
    Acts as the tenant that board/assets/setlists content belongs to.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, help_text="Used in URLs, e.g. /board/i-ukes/")
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="subgroups",
        help_text="Leave empty for a top-level club. Set this for a performance "
                   "subgroup that belongs to a club (e.g. 'I-Ukes Performers' -> parent 'I-Ukes').",
    )
    logo = models.ImageField(upload_to="group_logos/", blank=True, null=True)
    landing_image = models.ImageField(
        upload_to="group_landing/", blank=True, null=True,
        help_text="Square image (e.g. 600×600 px) shown on the landing page card.",
    )
    contact_email = models.EmailField(blank=True)
    description   = models.TextField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    facebook_url  = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

from django.core.exceptions import ValidationError


class GroupContact(models.Model):
    """A contact person shown on a group's Contact page (max 3 per group)."""
    MAX_PER_GROUP = 3

    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="contacts",
    )
    name = models.CharField(max_length=100)
    role = models.CharField(
        max_length=100, blank=True,
        help_text="e.g. Leader, Treasurer, Membership",
    )
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    order = models.PositiveSmallIntegerField(
        default=0, help_text="Lower numbers are shown first."
    )

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.name} ({self.group})"

    def clean(self):
        super().clean()
        if self.group_id:
            others = GroupContact.objects.filter(group_id=self.group_id)
            if self.pk:
                others = others.exclude(pk=self.pk)
            if others.count() >= self.MAX_PER_GROUP:
                raise ValidationError(
                    f"A group can have at most {self.MAX_PER_GROUP} contacts."
                )

class GroupMembership(models.Model):
    """
    Links a user to a group with a role. A user can belong to more than
    one group (e.g. someone who performs with both FWC and I-Ukes).
    """
    ROLE_CHOICES = [
        ("performer", "Performer"),
        ("leader", "Leader"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="group_memberships",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="performer")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "group")
        ordering = ["group__name", "user__username"]

    def __str__(self):
        return f"{self.user} @ {self.group} ({self.get_role_display()})"