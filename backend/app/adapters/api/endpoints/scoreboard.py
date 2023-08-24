from attrs import asdict
from fastapi import APIRouter

from app.adapters.api.dependencies.dependencies import (
    ServiceAuthorizationDep,
    ServiceScoreboardGlobalDep,
    ServiceSessionDep,
)
from app.adapters.api.schemas.scoreboard import (
    RespScoreboard,
    TopUserRec,
    TopUsers,
    UserModeSummery,
    UserRank,
)
from app.system.config import Settings
from app.system.constants import SessionMode

router = APIRouter(prefix=f"/{Settings().general.BACKEND_API_PREFIX}/scoreboard")


@router.get("/{mode}", status_code=200)
async def show_scoreboard(
    mode: SessionMode,
    service_session: ServiceSessionDep,
    service_scoreboard_global: ServiceScoreboardGlobalDep,
    auth: ServiceAuthorizationDep,
) -> RespScoreboard:
    assert auth.user

    top_users = await service_scoreboard_global.show_top_users(mode)
    # If top users are not found, then it's obvious that the current user also doesn't have results
    if not top_users:
        return RespScoreboard(top_users=None, user_mode_summary=None, user_rank=None)

    top_users_records = {rank: TopUserRec(**asdict(rec)) for rank, rec in top_users.items()}
    top_users_resp = TopUsers(records=top_users_records)

    ums = await service_session.calc_user_mode_summary(auth.user, mode)
    ums_resp = UserModeSummery(**asdict(ums)) if ums else None

    user_rank = await service_scoreboard_global.get_user_rank(auth.user, mode)
    user_rank_resp = UserRank(mode=mode, rank=user_rank) if user_rank is not None else None

    return RespScoreboard(
        top_users=top_users_resp, user_mode_summary=ums_resp, user_rank=user_rank_resp
    )
