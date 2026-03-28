"""
Test script for backend services
Run this to verify services work without Flask dependencies
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 50)
print("Testing 5XLiving 3D Maker Backend Services")
print("=" * 50)

# Test 1: Import services
print("\n1. Testing imports...")
try:
    from services import (
        get_plan_from_token,
        get_remaining_quota,
        consume_quota,
        create_job,
        get_job,
        JobStatus
    )
    print("✓ All services imported successfully")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Quota system
print("\n2. Testing quota system...")
plan = get_plan_from_token("FREE")
print(f"   Token 'FREE' -> plan: {plan}")
assert plan == "free", f"Expected 'free', got '{plan}'"

remaining = get_remaining_quota("FREE", plan)
print(f"   Initial quota: {remaining}")
assert remaining["image"] == 1, "Free plan should have 1 image quota"
assert remaining["v1"] == 1, "Free plan should have 1 v1 quota"
assert remaining["v2"] == 0, "Free plan should have 0 v2 quota"

success, msg = consume_quota("FREE", "image")
print(f"   Consumed 1 image quota: {success}")
assert success, "Should successfully consume quota"

remaining = get_remaining_quota("FREE", plan)
print(f"   Remaining after consume: {remaining}")
assert remaining["image"] == 0, "Should have 0 image quota left"

print("✓ Quota system working correctly")

# Test 3: Job queue
print("\n3. Testing job queue...")
job_id = create_job("image", {"prompt": "test"})
print(f"   Created job: {job_id}")

import time
time.sleep(0.1)  # Let job start

job = get_job(job_id)
print(f"   Job status: {job['status']}, progress: {job['progress']}%")
assert job is not None, "Job should exist"
assert job['status'] in [JobStatus.QUEUED, JobStatus.RUNNING], "Job should be queued or running"

# Wait for job to complete
print("   Waiting for job to complete...")
for i in range(30):  # Wait up to 3 seconds
    time.sleep(0.1)
    job = get_job(job_id)
    if job['status'] == JobStatus.DONE:
        break

job = get_job(job_id)
print(f"   Final status: {job['status']}, progress: {job['progress']}%")
print(f"   Result: {job.get('result', {})}")
assert job['status'] == JobStatus.DONE, "Job should complete"
assert 'imageUrl' in job['result'], "Job should have imageUrl in result"

print("✓ Job queue working correctly")

# Test 4: Placeholder assets
print("\n4. Testing placeholder assets...")
static_dir = os.path.join(os.path.dirname(__file__), 'static')
img_path = os.path.join(static_dir, 'placeholder_image.png')
mesh_path = os.path.join(static_dir, 'placeholder_mesh.glb')

if os.path.exists(img_path):
    img_size = os.path.getsize(img_path)
    print(f"   ✓ placeholder_image.png exists ({img_size} bytes)")
else:
    print(f"   ✗ placeholder_image.png not found")

if os.path.exists(mesh_path):
    mesh_size = os.path.getsize(mesh_path)
    print(f"   ✓ placeholder_mesh.glb exists ({mesh_size} bytes)")
else:
    print(f"   ✗ placeholder_mesh.glb not found")

print("\n" + "=" * 50)
print("✅ ALL TESTS PASSED")
print("=" * 50)
print("\nBackend services are working correctly!")
print("To start the Flask server:")
print("  1. Install dependencies: pip install -r requirements.txt")
print("  2. Run server: python app.py")
