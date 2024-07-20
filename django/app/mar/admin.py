from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from datetime import date
import logging
logger = logging.getLogger('console')

# Register your models here.
from .models import Mac
from .models import Template
from .models import Category
from .models import Group
from .models import GroupUserAssignment

class MacAdminForm(forms.ModelForm):
    def clean_expire_date(self):
        # Safety check to make sure Effective Date is present
        if "effective_date" not in self.cleaned_data:
            raise ValidationError(f'Effctive Date is mandatory!')
        # Check if selected MAC Group required Expiration Date / Max days
        effective_date = self.cleaned_data["effective_date"]
        expire_date = self.cleaned_data["expire_date"]
        
        if 'group' not in self.cleaned_data:
            raise ValidationError(f'You must assign a Group for the MAC Address')
        elif self.cleaned_data["group"].max_expire_days and expire_date and (expire_date-effective_date).days > self.cleaned_data["group"].max_expire_days:
                raise ValidationError(f'MAC Group "{self.cleaned_data["group"].name}" requires an expiration date less than {self.cleaned_data["group"].max_expire_days} days!')
        elif self.cleaned_data["group"].require_expiration and expire_date is None:
            raise ValidationError(f'MAC Group "{self.cleaned_data["group"].name}" requires an expiration date!')
        return self.cleaned_data["expire_date"]

@admin.register(Mac)
class MacAdmin(admin.ModelAdmin):
    readonly_fields = ('created_by', 'created_date', 'modified_by', 'modified_date')
    list_display = ('mac', 'group', 'category', 'template', 'effective_date', 'expire_date', 'created_by', 'created_date', 'modified_by', 'modified_date')
    list_display_links = ('mac',)
    ordering = ('-effective_date', 'expire_date')
    form = MacAdminForm
    def save_model(self, request, obj, form, change):
        # Set modified and created properties
        obj.modified_by = request.user
        if not obj.pk:
            obj.created_by = request.user
        obj.save()
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            # Return all if super admin
            logger.debug(f'User {request.user} is Super Admin and can read all MACs')
            return qs
        else:
            # Otherwise filter to just MACs that are part of a Group that the User (by GroupUserAssignment) has Read to
            # Get list of Groups the User has GroupUserAssignment:Read
            read_groups = list(GroupUserAssignment.objects.filter(user=request.user).filter(read=True).all().values_list('group', flat=True))
            logger.debug(f'User {request.user} can read MACs from Group(s): {read_groups}')
            return qs.filter(group__in=read_groups)
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.is_superuser:
            return super().formfield_for_foreignkey(db_field, request, **kwargs)
        else:
            # Filter the Group FK relationship to only those the user has access to
            if db_field.name == "group":
                # which groups can the user create in?
                create_groups = list(GroupUserAssignment.objects.filter(user=request.user).filter(create=True).all().values_list('group', flat=True))
                logger.debug(f'Can create in: {create_groups}')
                # Filter Group list if changing or creating new
                if "object_id" in request.resolver_match.kwargs:
                    # Changing record: must have delete in previous group and create in new group permissions
                    # Get MAC user is editing
                    mac = Mac.objects.get(pk=request.resolver_match.kwargs["object_id"])
                    # Check if user can delete from this Group
                    delete_groups = list(GroupUserAssignment.objects.filter(user=request.user).filter(delete=True).filter(group=mac.group).all().values_list('group', flat=True))
                    if len(delete_groups) == 0:
                        # can't make any changes
                        mac = Mac.objects.get(pk=request.resolver_match.kwargs["object_id"])
                        kwargs["queryset"] = Group.objects.filter(id=mac.group.id)
                    else:
                        kwargs["queryset"] = Group.objects.filter(id__in=create_groups)
                else:
                    # Creating record: must have create in group permission
                    kwargs["queryset"] = Group.objects.filter(id__in=create_groups)
            return super().formfield_for_foreignkey(db_field, request, **kwargs)
    def has_change_permission(self, request, obj=None):
        if obj is not None and not request.user.is_superuser:
            # check if user has update for Group
            update_groups = list(GroupUserAssignment.objects.filter(user=request.user).filter(update=True).all().values_list('group', flat=True))
            if obj.group.id not in update_groups:
                return False
        return super().has_change_permission(request, obj=obj)
    def has_delete_permission(self, request, obj=None):
        if obj is not None and not request.user.is_superuser:
            # check if user has update for Group
            del_groups = list(GroupUserAssignment.objects.filter(user=request.user).filter(delete=True).all().values_list('group', flat=True))
            if obj.group.id not in del_groups:
                return False
        return super().has_change_permission(request, obj=obj)

# Templates; A MAC can have 1 Template (Shorthand way for Forescout admin to handle the MAC address in Policy)
@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    readonly_fields = ('created_by', 'created_date', 'modified_by', 'modified_date')
    list_display = ('id','name', 'notes', 'created_by', 'created_date', 'modified_by', 'modified_date')
    list_display_links = ('id', 'name')
    ordering = ('id',)
    def save_model(self, request, obj, form, change):
        obj.modified_by = request.user
        if not obj.pk:
            obj.created_by = request.user
        obj.save()

# Categories; A MAC can have 1 Category
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    readonly_fields = ('created_by', 'created_date', 'modified_by', 'modified_date')
    list_display = ('id', 'name', 'created_by', 'created_date', 'modified_by', 'modified_date')
    list_display_links = ('id', 'name')
    ordering = ('id',)
    def save_model(self, request, obj, form, change):
        obj.modified_by = request.user
        if not obj.pk:
            obj.created_by = request.user
        obj.save()

# Group; Each MAC is a member of 1 Group
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    readonly_fields = ('created_by', 'created_date', 'modified_by', 'modified_date')
    list_display = ('id', 'name', 'require_expiration', 'max_expire_days', 'created_by', 'created_date', 'modified_by', 'modified_date')
    list_display_links = ('id', 'name')
    ordering = ('id',)
    def save_model(self, request, obj, form, change):
        obj.modified_by = request.user
        if not obj.pk:
            obj.created_by = request.user
        obj.save()

# Group Permission (assignment of User permissions to Group of MACs)
@admin.register(GroupUserAssignment)
class GroupUserAssignmentAdmin(admin.ModelAdmin):
    readonly_fields = ('created_by', 'created_date', 'modified_by', 'modified_date')
    list_display = ('user', 'group', 'create', 'read', 'update', 'delete', 'created_by', 'created_date', 'modified_by', 'modified_date')
    list_display_links = ('user',)
    ordering = ('-user', 'group')
    def save_model(self, request, obj, form, change):
        obj.modified_by = request.user
        if not obj.pk:
            obj.created_by = request.user
        obj.save()