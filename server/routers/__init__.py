from .auth import router as auth_router
from .vehicles import router as vehicles_router
from .records import router as records_router
from .stats import router as stats_router
from .maintenance import router as maintenance_router
from .export import router as export_router

__all__ = ['auth_router', 'vehicles_router', 'records_router', 'stats_router', 'maintenance_router', 'export_router']
