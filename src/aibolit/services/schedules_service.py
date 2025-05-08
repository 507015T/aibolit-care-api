# from aibolit.dependencies import get_schedules_repo


class ScheduleExpiredError(Exception):
    pass


# class ScheduleService:
#     def __init__(
#         self,
#         schedules_repo: Annotated[SchedulesRepo, Depends(get_schedules_repo)],
#     ) -> None:
#         self._schedules_repo = schedules_repo
#
#     async def create_schedule(self, schedule: MedicationScheduleCreateRequest) -> MedicationScheduleCreateResponse:
#         schedule = await self._schedules_repo.create_schedule(schedule)
#         return MedicationScheduleCreateResponse(schedule_id=schedule.id)
#
#     async def get_all_user_schedules(self, user_id: int) -> MedicationScheduleIdsResponse:
#         db_schedules = await self._schedules_repo.get_all_user_schedules(user_id)
#         schedules = [MedicationSchedule.model_validate(schedule).id for schedule in db_schedules]
#         return MedicationScheduleIdsResponse(user_id=user_id, schedules=schedules)
#
#     async def get_user_schedule(self, user_id: int, schedule_id: int) -> MedicationSchedule:
#         db_schedule = await self._schedules_repo.get_user_schedule(schedule_id, user_id)
#         schedule = MedicationSchedule.model_validate(db_schedule)
#         if schedule.end_date and schedule.end_date < date.today():
#             raise ScheduleExpiredError(
#                 f"The medication '{schedule.medication_name}' intake ended on {schedule.end_date}"
#             )
#         return schedule
#
#     async def get_user_next_takings(self, user_id: int) -> NextTakingsMedicationsResponse:
#         user_schedules = await self._schedules_repo.get_all_user_schedules(user_id)
#         schedules = [MedicationSchedule.model_validate(schedule) for schedule in user_schedules]
#         next_takings = [
#             NextTakingsMedications(
#                 schedule_id=next_taking.id,
#                 schedule_name=next_taking.medication_name,
#                 schedule_times=next_taking.daily_plan,
#             )
#             for next_taking in schedules
#             if any(map(is_within_timeframe, next_taking.daily_plan))
#         ]
#
#         return NextTakingsMedicationsResponse(user_id=user_id, next_takings=next_takings)
