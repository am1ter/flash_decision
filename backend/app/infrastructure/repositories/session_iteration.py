from uuid import UUID

import pandas as pd

from app.domain.repository import RepositoryIteration
from app.domain.session_iteration import DomainIteration, DomainIterationCollection
from app.infrastructure.repositories.base import RepositoryNoSqlMongo
from app.system.exceptions import IterationNotFoundError


class RepositoryNoSqlIteration(RepositoryNoSqlMongo, RepositoryIteration):
    def _create_iteration_by_document(self, document: dict) -> DomainIteration:
        document_updated = self._convert_binary_to_uuid(document)
        return DomainIteration(
            id=document_updated["_id"],
            session_id=document_updated["session_id"],
            iteration_num=document_updated["iteration_num"],
            df_quotes=pd.read_json(document_updated["df_quotes"]),
            session=None,
            bar_price_start=document_updated["bar_price_start"],
            bar_price_finish=document_updated["bar_price_finish"],
            bar_price_fix=document_updated["bar_price_fix"],
        )

    def get_iteration_collection(self, session_id: UUID) -> DomainIterationCollection:
        assert DomainIteration.__attrs_attrs__.session_id.name, "Only dataclasses allowed"
        field_key = DomainIteration.__attrs_attrs__.session_id.name
        field_to_find = {field_key: session_id}
        documents = self._select_all(entity_class=DomainIteration, field=field_to_find)
        iteration_collection = DomainIterationCollection(session_quotes=None)
        for document in documents:
            iteration = self._create_iteration_by_document(document)
            iteration_collection.append(iteration)
        return iteration_collection

    def get_iteration(self, session_id: UUID, iteration_num: int) -> DomainIteration:
        assert DomainIteration.__attrs_attrs__.session_id.name, "Only dataclasses allowed"
        session_id_key = DomainIteration.__attrs_attrs__.session_id.name
        iteration_num_key = DomainIteration.__attrs_attrs__.iteration_num.name
        field_to_find = {session_id_key: session_id, iteration_num_key: iteration_num}
        document = self._select_one(entity_class=DomainIteration, field=field_to_find)
        if not document:
            raise IterationNotFoundError
        iteration = self._create_iteration_by_document(document)
        return iteration
