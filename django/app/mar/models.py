from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.utils.timezone import now
from django.conf import settings

class Group(models.Model):
    name = models.CharField("Name", max_length=256, unique=True, null=False, blank=False)
    created_date = models.DateTimeField("Created Date", auto_created=True, auto_now=False, auto_now_add=True, editable=False, null=False, blank=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_user_created_by', on_delete=models.PROTECT, editable=False, blank=False, null=False)
    modified_date = models.DateTimeField("Modified Date", auto_created=True, auto_now=True, editable=False, null=False, blank=False)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_user_modified_by', on_delete=models.PROTECT, editable=False, blank=False, null=False)
    require_expiration = models.BooleanField("Require Expiration?", default=False, null=False, blank=False, editable=True)
    max_expire_days = models.PositiveSmallIntegerField("Max Expiration Date from Effective Date (in days)", null=True, blank=True)
    def __str__(self):
        return f'{self.name}'
    class Meta: 
        verbose_name = "MAC Address Group"
        verbose_name_plural = "MAC Address Groups"

class GroupUserAssignment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_user', on_delete=models.PROTECT, editable=True, blank=False, null=False)
    group = models.ForeignKey(Group, on_delete=models.PROTECT, editable=True, blank=False, null=False)
    create = models.BooleanField(default=False, null=False, blank=False, editable=True)
    read = models.BooleanField(default=False, null=False, blank=False, editable=True)
    update = models.BooleanField(default=False, null=False, blank=False, editable=True)
    delete = models.BooleanField(default=False, null=False, blank=False, editable=True)
    created_date = models.DateTimeField("Created Date", auto_created=True, auto_now=False, auto_now_add=True, editable=False, null=False, blank=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_user_created_by', on_delete=models.PROTECT, editable=False, blank=False, null=False)
    modified_date = models.DateTimeField("Modified Date", auto_created=True, auto_now=True, editable=False, null=False, blank=False)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_user_modified_by', on_delete=models.PROTECT, editable=False, blank=False, null=False)
    def __str__(self):
        return f'{self.group}'
    class Meta: 
        verbose_name = "MAC Address Group: User & Permissions Assignment"
        verbose_name_plural = "MAC Address Groups: User & Permissions Assignment"

class Category(models.Model):
    name = models.CharField("Name", max_length=256, unique=True, null=False, blank=False)
    created_date = models.DateTimeField("Created Date", auto_created=True, auto_now=False, auto_now_add=True, editable=False, null=False, blank=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_user_created_by', on_delete=models.PROTECT, editable=False, blank=False, null=False)
    modified_date = models.DateTimeField("Modified Date", auto_created=True, auto_now=True, editable=False, null=False, blank=False)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_user_modified_by', on_delete=models.PROTECT, editable=False, blank=False, null=False)
    def __str__(self):
        return f'{self.name}'
    class Meta: 
        verbose_name = "Category"
        verbose_name_plural = "Categories"

class Template(models.Model):
    name = models.CharField("Name", max_length=256, unique=True, null=False, blank=False)
    notes = models.TextField("Template Notes", null=True, blank=True)
    created_date = models.DateTimeField("Created Date", auto_created=True, auto_now=False, auto_now_add=True, editable=False, null=False, blank=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_user_created_by', on_delete=models.PROTECT, editable=False, blank=False, null=False)
    modified_date = models.DateTimeField("Modified Date", auto_created=True, auto_now=True, editable=False, null=False, blank=False)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_user_modified_by', on_delete=models.PROTECT, editable=False, blank=False, null=False)
    def __str__(self):
        return f'{self.name}'

class Mac(models.Model):
    mac = models.CharField("MAC Address", max_length=12, unique=False, null=False, blank=False, validators=[
            RegexValidator(
                regex=r'^([0-9a-f]){12}$',
                message="Enter a valid Forescout style MAC Address (lowercase, no spaces, no periods, no hyphens)",
                code="invalid_mac_address"
            )
        ])
    group = models.ForeignKey(Group, on_delete=models.PROTECT, editable=True, null=False, blank=False)
    created_date = models.DateTimeField("Created Date", auto_created=True, auto_now=False, auto_now_add=True, editable=False, null=False, blank=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_user_created_by', on_delete=models.PROTECT, editable=False, blank=False, null=False)
    modified_date = models.DateTimeField("Modified Date", auto_created=True, auto_now=True, editable=False, null=False, blank=False)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_user_modified_by', on_delete=models.PROTECT, editable=False, blank=False, null=False)
    comment = models.TextField("Entry Comment", null=True, blank=True)
    effective_date = models.DateTimeField("Effective Date", default=now, auto_created=False, auto_now=False, editable=True, null=False, blank=False)
    expire_date = models.DateTimeField("Expiration Date", auto_created=False, auto_now=False, editable=True, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, editable=True, null=True, blank=True)
    template = models.ForeignKey(Template, on_delete=models.PROTECT, editable=True, null=True, blank=True)
    # Note: These values match up to 802.1x Update MAR Action in Forescout, but they cannot be added by Tag to the Update MAR Action
    # These are just here to give the admin something to key off of that matches close to Forescout UI
    authorization_parameters = models.BooleanField("Authorization Parameters?", default=False, null=False, blank=False, editable=True)
    deny = models.BooleanField("Deny Access?", default=False, null=False, blank=False,editable=True)
    vlan_num = models.PositiveSmallIntegerField("VLAN Number", null=True, blank=True, validators=[
            MaxValueValidator(4095, message="4095 is the largest allowable VLAN number"),
            MinValueValidator(0, message="0 is the smallest allowable VLAN number")
        ])
    vlan_name = models.CharField("VLAN Name",max_length=128, null=True, blank=True)
    mar_comment = models.TextField("MAR Comment",null=True, blank=True)
    # Fields that Forescout can update via it's connect app
    # fsct_added_to_mar = models.BooleanField("Forescout: Added to MAR?", default=False, null=False, blank=False, editable=True)
    # fsct_first_auth = models.DateTimeField("Forescout: First Auth", auto_created=False, auto_now=False, editable=False, null=True, blank=True)
    def __str__(self):
        return f'{self.mac}'
    class Meta: 
        verbose_name = "MAC"
        verbose_name_plural = "MACs"