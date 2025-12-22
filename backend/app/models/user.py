from tortoise import fields, models


class Permission(models.Model):
    id = fields.UUIDField(pk=True)
    scope = fields.CharField(max_length=50, description="Permission scope (e.g., user, kb)")
    code = fields.CharField(max_length=100, unique=True, description="Unique permission code (e.g., user:create)")
    description = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "permissions"

    def __str__(self):
        return self.code


class Role(models.Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=50, unique=True)
    description = fields.CharField(max_length=255, null=True)
    is_system_role = fields.BooleanField(default=False, description="If True, cannot be deleted/modified")
    permissions = fields.ManyToManyField("models.Permission", related_name="roles", through="role_permissions")

    class Meta:
        table = "roles"

    def __str__(self):
        return self.name


class User(models.Model):
    id = fields.UUIDField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=255, unique=True)
    hashed_password = fields.CharField(max_length=255)
    is_active = fields.BooleanField(default=True)
    is_superuser = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    last_login = fields.DatetimeField(null=True)
    
    # Extended fields
    department_id = fields.CharField(max_length=50, null=True, description="Reserved for department ID")
    auth_source = fields.CharField(max_length=20, default="local", description="Auth source: local, ldap, github, etc.")
    external_id = fields.CharField(max_length=255, null=True, description="ID from external auth provider")
    avatar_url = fields.CharField(max_length=512, null=True)

    roles = fields.ManyToManyField("models.Role", related_name="users", through="user_roles")

    class Meta:
        table = "users"

    def __str__(self):
        return self.username
