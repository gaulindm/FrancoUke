from django.conf import settings
from django.db import models


class Group(models.Model):
    """
    A performance group / ukulele club (e.g. Uke4ia, I-Ukes).
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
    contact_email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class GroupMembership(models.Model):
    """
    Links a user to a group with a role. A user can belong to more than
    one group (e.g. someone who performs with both Uke4ia and I-Ukes).
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