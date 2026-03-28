"""Services package for 5XLiving 3D Maker backend"""
from .quota import (
    get_plan_from_token,
    get_quota_limits,
    get_remaining_quota,
    consume_quota,
    reset_quota,
    cleanup_old_dates,
    get_usage_stats
)

from .jobs import (
    create_job,
    get_job,
    cleanup_old_jobs,
    cancel_job,
    get_all_jobs,
    JobStatus
)

from .placeholders import (
    generate_placeholder_image,
    generate_placeholder_glb,
    save_placeholder_image,
    save_placeholder_glb
)

__all__ = [
    # Quota
    'get_plan_from_token',
    'get_quota_limits',
    'get_remaining_quota',
    'consume_quota',
    'reset_quota',
    'cleanup_old_dates',
    'get_usage_stats',
    
    # Jobs
    'create_job',
    'get_job',
    'cleanup_old_jobs',
    'cancel_job',
    'get_all_jobs',
    'JobStatus',
    
    # Placeholders
    'generate_placeholder_image',
    'generate_placeholder_glb',
    'save_placeholder_image',
    'save_placeholder_glb',
]
