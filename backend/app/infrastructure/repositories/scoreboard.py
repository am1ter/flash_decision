from decimal import Decimal
from typing import ClassVar
from uuid import UUID

import bson
from pymongo import DESCENDING, ReturnDocument

from app.domain.scoreboard import ScoreboardRecord, ScoreboardRecords
from app.domain.session_result import SessionResult
from app.domain.user import DomainUser
from app.infrastructure.repositories.base import RepositoryNoSqlMongo
from app.system.constants import SessionMode
from app.system.exceptions import DbObjectNotFoundError


class RepositoryNoSqlScoreboard(RepositoryNoSqlMongo):
    collection_name: ClassVar[str] = ScoreboardRecords.__name__

    @staticmethod
    def _create_scoreboard_record_from_raw_dict(rec: dict) -> ScoreboardRecord:
        return ScoreboardRecord(
            mode=rec["mode"],
            user_id=UUID(bytes=bson.BSON(rec["user_id"])),
            user_name=rec["user_name"],
            result=rec["result"].to_decimal(),
        )

    @RepositoryNoSqlMongo.catch_db_errors
    def update_score(self, session_result: SessionResult) -> Decimal:
        mode = {"mode": session_result.session.mode.value}
        user_id = {"user_id": bson.Binary.from_uuid(session_result.session.user._id)}
        user_name = {"user_name": session_result.session.user.name}
        result = {"result": bson.Decimal128(session_result.total_result)}

        updated = self._db[self.collection_name].find_one_and_update(
            filter=mode | user_id,
            update={"$set": user_name, "$inc": result},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return updated["result"].to_decimal()

    @RepositoryNoSqlMongo.catch_db_errors
    def get_full_scoreboard(self, mode: SessionMode) -> ScoreboardRecords:
        find_query = {"mode": mode}
        raw_scoreboard = self._db[self.collection_name].find(find_query).sort("result", DESCENDING)
        scoreboard_records = ScoreboardRecords([])
        for obj in raw_scoreboard:
            scoreboard_record = self._create_scoreboard_record_from_raw_dict(obj)
            scoreboard_records.append(scoreboard_record)
        if not scoreboard_records:  # If objects are not found in the database, raise an exception
            raise DbObjectNotFoundError
        return scoreboard_records

    @RepositoryNoSqlMongo.catch_db_errors
    def get_scoreboard_record(self, user: DomainUser, mode: SessionMode) -> ScoreboardRecord:
        find_query = {"user_id": bson.Binary.from_uuid(user._id), "mode": mode}
        raw_scoreboard = self._db[self.collection_name].find_one(find_query)
        if not raw_scoreboard:  # If objects are not found in the database, raise an exception
            raise DbObjectNotFoundError
        scoreboard_record = self._create_scoreboard_record_from_raw_dict(raw_scoreboard)
        return scoreboard_record
