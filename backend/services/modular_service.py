from services.xyz_builder_service import build_xyz_session


def handle_modular_job(job):
    return build_xyz_session(job)