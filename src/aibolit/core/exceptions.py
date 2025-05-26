from datetime import date


class ScheduleExpiredError(Exception):
    def __init__(self, medication_name: str, end_date: date) -> None:
        self.status_code = 410
        super().__init__(f"The medication '{medication_name}' intake ended on {end_date}")


class ScheduleNotFoundError(Exception):
    def __init__(self, schedule_id: int, user_id: int) -> None:
        self.status_code = 404
        super().__init__(f"The medication schedule with id={schedule_id} for user={user_id} not found")


class ScheduleNotStartedError(Exception):
    def __init__(self, medication_name: str, start_date: date) -> None:
        self.status_code = 409
        super().__init__(f"The medication '{medication_name}' intake will begin {start_date}")
