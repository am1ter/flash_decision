from typing import Annotated

from fastapi import APIRouter, Depends
from uuid6 import UUID

from app.api.schemas.session_decision import ReqRecordDecision, RespDecision
from app.services.session import ServiceSession
from app.services.session_decision import ServiceDecision
from app.services.session_iteration import ServiceIteration
from app.services.user_authorization import ServiceAuthorization, verify_authorization
from app.system.config import Settings
from app.system.constants import DecisionAction

router = APIRouter(prefix=f"/{Settings().general.BACKEND_API_PREFIX}/decision")

# Internal dependencies
ServiceSessionDep = Annotated[ServiceSession, Depends()]
ServiceIterationDep = Annotated[ServiceIteration, Depends()]
ServiceDecisionDep = Annotated[ServiceDecision, Depends()]
ServiceAuthorizationDep = Annotated[ServiceAuthorization, Depends(verify_authorization)]


@router.post("/")
async def record_decision(
    decision_params: ReqRecordDecision,
    service_session: ServiceSessionDep,
    service_iteration: ServiceIterationDep,
    service_decision: ServiceDecisionDep,
) -> RespDecision:
    session_id = UUID(decision_params.session_id)
    session = await service_session.get_session(session_id)
    iteration = await service_iteration.get_iteration(session_id, decision_params.iteration_num)
    decision = await service_decision.record_decision(
        session, iteration, DecisionAction(decision_params.action), decision_params.time_spent
    )
    return RespDecision(result_final=decision.result_final)
