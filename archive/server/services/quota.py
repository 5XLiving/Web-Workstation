"""
Quota management for 5XLiving 3D Maker
Tracks daily usage limits per plan tier
"""
from datetime import datetime, date
from typing import Dict, Tuple

# Plan quota limits (per day)
PLAN_QUOTAS = {
    "free": {
        "image": 1,
        "v1": 1,
        "v2": 0
    },
    "year": {
        "image": 10,
        "v1": 10,
        "v2": 5
    },
    "vip": {
        "image": 50,
        "v1": 50,
        "v2": 25
    }
}

# In-memory usage tracker: {token: {date: {type: count}}}
_usage_tracker: Dict[str, Dict[str, Dict[str, int]]] = {}


def _get_today() -> str:
    """Get today's date as string YYYY-MM-DD"""
    return date.today().isoformat()


def get_plan_from_token(token: str) -> str:
    """
    Extract plan tier from token
    MVP implementation: token IS the plan name
    """
    token_upper = token.upper()
    if token_upper == "FREE":
        return "free"
    elif token_upper == "YEAR":
        return "year"
    elif token_upper == "VIP":
        return "vip"
    else:
        # Unknown tokens default to free
        return "free"


def get_quota_limits(plan: str) -> Dict[str, int]:
    """Get daily quota limits for a plan"""
    return PLAN_QUOTAS.get(plan, PLAN_QUOTAS["free"]).copy()


def get_remaining_quota(token: str, plan: str) -> Dict[str, int]:
    """
    Calculate remaining quota for today
    Returns: {"image": int, "v1": int, "v2": int}
    """
    today = _get_today()
    limits = get_quota_limits(plan)
    
    # Get today's usage
    if token not in _usage_tracker:
        _usage_tracker[token] = {}
    
    if today not in _usage_tracker[token]:
        # No usage today, return full limits
        return limits
    
    today_usage = _usage_tracker[token][today]
    
    # Calculate remaining
    remaining = {}
    for quota_type in ["image", "v1", "v2"]:
        used = today_usage.get(quota_type, 0)
        remaining[quota_type] = max(0, limits[quota_type] - used)
    
    return remaining


def consume_quota(token: str, quota_type: str) -> Tuple[bool, str]:
    """
    Attempt to consume 1 unit of quota
    
    Args:
        token: User token
        quota_type: "image", "v1", or "v2"
    
    Returns:
        (success: bool, error_message: str)
    """
    plan = get_plan_from_token(token)
    today = _get_today()
    
    # Initialize tracking structures
    if token not in _usage_tracker:
        _usage_tracker[token] = {}
    
    if today not in _usage_tracker[token]:
        _usage_tracker[token][today] = {}
    
    # Check limit
    limits = get_quota_limits(plan)
    used = _usage_tracker[token][today].get(quota_type, 0)
    
    if used >= limits[quota_type]:
        return False, f"Daily {quota_type} quota exceeded. Limit: {limits[quota_type]}"
    
    # Consume quota
    _usage_tracker[token][today][quota_type] = used + 1
    
    return True, ""


def reset_quota(token: str):
    """Reset all quotas for a token (admin/testing)"""
    if token in _usage_tracker:
        del _usage_tracker[token]


def cleanup_old_dates():
    """Remove usage data older than 7 days (memory management)"""
    today = date.today()
    cutoff_days = 7
    
    for token in list(_usage_tracker.keys()):
        for date_str in list(_usage_tracker[token].keys()):
            try:
                usage_date = date.fromisoformat(date_str)
                age_days = (today - usage_date).days
                if age_days > cutoff_days:
                    del _usage_tracker[token][date_str]
            except ValueError:
                # Invalid date format, remove it
                del _usage_tracker[token][date_str]
        
        # Remove token if no dates left
        if not _usage_tracker[token]:
            del _usage_tracker[token]


def get_usage_stats(token: str) -> Dict:
    """Get usage statistics for debugging/admin"""
    today = _get_today()
    plan = get_plan_from_token(token)
    
    return {
        "token": token,
        "plan": plan,
        "today": today,
        "usage": _usage_tracker.get(token, {}).get(today, {}),
        "limits": get_quota_limits(plan),
        "remaining": get_remaining_quota(token, plan)
    }
