#from ninja import Router
from django.utils import timezone
from django.db.models import Q, Count
from .models import Mac, Template, Category, Group, GroupUserAssignment
from django.contrib.auth.models import User
from ninja.pagination import RouterPaginated
from typing import List, Optional
from ninja import ModelSchema
import logging
logger = logging.getLogger('console')

router = RouterPaginated()

# Define Schemas
class GroupSchema(ModelSchema):
    class Meta:
        model = Group
        fields = ['id', 'name']
class CategorySchema(ModelSchema):
    class Meta:
        model = Category
        fields = ['id', 'name']
class TemplateSchema(ModelSchema):
    class Meta:
        model = Template
        fields = ['id', 'name']
class UserSchema(ModelSchema):
    class Meta:
        model = User
        fields = ['id', 'username']
class MacSchema(ModelSchema):
    group: GroupSchema
    template: Optional[TemplateSchema] = None
    category: Optional[CategorySchema] = None
    created_by: UserSchema
    modified_by: UserSchema
    class Meta:
        model = Mac
        # add: created_by, modified_by
        fields = ['mac', 'comment', 'created_date', 'created_by', 'modified_date', 'modified_by', 'effective_date',
                  'expire_date', 'authorization_parameters', 'deny', 'vlan_num', 'vlan_name',
                  'mar_comment']

# API calls
@router.get('/', response=List[MacSchema], summary="Get currently active MAR Entries")
def effective(request):
    now = timezone.now()
    query = Mac.objects.filter(Q(Q(expire_date__gte=now) | Q(expire_date__isnull=True))).filter(effective_date__lte=now).order_by('mac', '-effective_date', 'expire_date', 'mac').distinct('mac')

    if request.user.is_superuser:
        # Return all if super admin
        return query
    else:
        # Otherwise filter to just MACs that are part of a Group that the User (by GroupUserAssignment) has Read to
        # Get list of Groups the User has GroupUserAssignment:Read
        read_groups = list(GroupUserAssignment.objects.filter(user=request.user).filter(read=True).all().values_list('group', flat=True))
        return query.filter(group__in=read_groups)

    return query

@router.get('/all', response=List[MacSchema], summary="Get all MAR Entries")
def all(request):
    query = Mac.objects.order_by("-effective_date").all()
    if request.user.is_superuser:
        # Return all if super admin
        return query
    else:
        # Otherwise filter to just MACs that are part of a Group that the User (by GroupUserAssignment) has Read to
        # Get list of Groups the User has GroupUserAssignment:Read
        read_groups = list(GroupUserAssignment.objects.filter(user=request.user).filter(read=True).all().values_list('group', flat=True))
        return query.filter(group__in=read_groups)

@router.get('/expired', response=List[MacSchema], summary="Get all expired MAR Entries")
def expired(request):
    now = timezone.now()
    query = Mac.objects.filter(expire_date__lte=now).order_by("-expire_date").all()
    if request.user.is_superuser:
        # Return all if super admin
        return query
    else:
        # Otherwise filter to just MACs that are part of a Group that the User (by GroupUserAssignment) has Read to
        # Get list of Groups the User has GroupUserAssignment:Read
        read_groups = list(GroupUserAssignment.objects.filter(user=request.user).filter(read=True).all().values_list('group', flat=True))
        return query.filter(group__in=read_groups)