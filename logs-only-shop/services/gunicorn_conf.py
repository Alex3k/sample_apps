from services import telemetry


def post_fork(server, worker):
    telemetry.configure()


def worker_exit(server, worker):
    telemetry.shutdown()
