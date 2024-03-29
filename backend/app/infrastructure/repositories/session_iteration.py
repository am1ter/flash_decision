from uuid import UUID

import pandas as pd

from app.domain.interfaces.repository import RepositoryIteration
from app.domain.session_iteration import Iteration, IterationCollection
from app.infrastructure.repositories.base import RepositoryNoSqlMongo
from app.system.exceptions import IterationNotFoundError


class RepositoryNoSqlIteration(RepositoryNoSqlMongo, RepositoryIteration):
    def _create_iteration_by_document(self, document: dict) -> Iteration:
        document_updated = self._convert_binary_to_uuid(document)
        return Iteration(
            id=document_updated["_id"],
            session_id=document_updated["session_id"],
            iteration_num=document_updated["iteration_num"],
            df_quotes=pd.read_json(document_updated["df_quotes"]),
            session=None,
            bar_price_start=document_updated["bar_price_start"],
            bar_price_finish=document_updated["bar_price_finish"],
            bar_price_fix=document_updated["bar_price_fix"],
        )

    def get_iteration_collection(self, session_id: UUID) -> IterationCollection:
        assert Iteration.__attrs_attrs__.session_id.name, "Only dataclasses allowed"
        field_key = Iteration.__attrs_attrs__.session_id.name
        field_to_find = {field_key: session_id}
        documents = self._select_all(entity_class=Iteration, field=field_to_find)
        iteration_collection = IterationCollection(session_quotes=None)
        for document in documents:
            iteration = self._create_iteration_by_document(document)
            iteration_collection.append(iteration)
        return iteration_collection

    def get_iteration(self, session_id: UUID, iteration_num: int) -> Iteration:
        assert Iteration.__attrs_attrs__.session_id.name, "Only dataclasses allowed"
        session_id_key = Iteration.__attrs_attrs__.session_id.name
        iteration_num_key = Iteration.__attrs_attrs__.iteration_num.name
        field_to_find = {session_id_key: session_id, iteration_num_key: iteration_num}
        document = self._select_one(entity_class=Iteration, field=field_to_find)
        if not document:
            raise IterationNotFoundError
        iteration = self._create_iteration_by_document(document)
        return iteration
