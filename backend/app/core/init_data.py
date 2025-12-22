import logging

from app.models.user import Role, Permission

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# System role name constant
SUPER_ADMIN_ROLE = "Super Admin"


async def init_db():
    """
    Initialize database with default permissions and roles.
    The first registered user will be promoted to Super Admin automatically.
    """
    # 1. Initialize Permissions
    permissions_data = [
        {"code": "user:read", "scope": "user", "description": "Read users"},
        {"code": "user:create", "scope": "user", "description": "Create users"},
        {"code": "user:update", "scope": "user", "description": "Update users"},
        {"code": "user:delete", "scope": "user", "description": "Delete users"},
        {"code": "user:manage", "scope": "user", "description": "Manage users, roles, permissions"},
        {"code": "*", "scope": "system", "description": "All permissions (superuser)"},
    ]
    
    logger.info("Initializing permissions...")
    for perm_data in permissions_data:
        await Permission.get_or_create(
            code=perm_data["code"],
            defaults={
                "scope": perm_data["scope"],
                "description": perm_data["description"]
            }
        )

    # 2. Initialize System Roles
    logger.info("Initializing roles...")
    
    # Super Admin - has all permissions
    super_admin_role, created = await Role.get_or_create(
        name=SUPER_ADMIN_ROLE,
        defaults={"description": "Full system control with all permissions", "is_system_role": True}
    )
    if created:
        all_perm = await Permission.get(code="*")
        await super_admin_role.permissions.add(all_perm)
        logger.info(f"Created system role: {SUPER_ADMIN_ROLE}")

    # Viewer - read-only access
    viewer_role, created = await Role.get_or_create(
        name="Viewer",
        defaults={"description": "Read-only access", "is_system_role": True}
    )
    if created:
        read_perm = await Permission.get(code="user:read")
        await viewer_role.permissions.add(read_perm)
        logger.info("Created system role: Viewer")
    
    logger.info("Database initialization complete.")

