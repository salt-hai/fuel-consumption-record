from .common import ApiResponse
from .auth import RegisterRequest, LoginRequest, ChangePasswordRequest, AuthResponse
from .vehicle import VehicleCreate, VehicleUpdate, VehicleResponse
from .record import RecordCreate, RecordUpdate, RecordResponse, RecordListParams, RecordListResponse
from .maintenance import MaintenanceCreate, MaintenanceUpdate, MaintenanceResponse

__all__ = [
    'ApiResponse',
    'RegisterRequest', 'LoginRequest', 'ChangePasswordRequest', 'AuthResponse',
    'VehicleCreate', 'VehicleUpdate', 'VehicleResponse',
    'RecordCreate', 'RecordUpdate', 'RecordResponse', 'RecordListParams', 'RecordListResponse',
    'MaintenanceCreate', 'MaintenanceUpdate', 'MaintenanceResponse',
]
