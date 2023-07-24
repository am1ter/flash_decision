import pandas as pd
from uuid6 import UUID

from app.domain.iteration import DomainIteration, DomainIterationCollection
from app.infrastructure.repositories.base import RepositoryNoSqlMongo


class RepositoryNoSqlIteration(RepositoryNoSqlMongo):
    def get_all_by_session_id(self, session_id: UUID) -> DomainIterationCollection:
        assert DomainIteration.__attrs_attrs__.session_id.name, "Only dataclasses allowed"
        field_key = DomainIteration.__attrs_attrs__.session_id.name
        field_to_find = {field_key: session_id}
        documents = self._select_all(entity_class=DomainIteration, field=field_to_find)
        iteration_collection = DomainIterationCollection(session=None)
        for doc in documents:
            doc_updated = self._convert_binary_to_uuid(doc)
            iteration = DomainIteration(
                id=doc_updated["_id"],
                session_id=doc_updated["session_id"],
                iteration_num=doc_updated["iteration_num"],
                df_quotes=pd.read_json(doc_updated["df_quotes"]),
                session=None,
                bar_price_start=doc_updated["bar_price_start"],
                bar_price_finish=doc_updated["bar_price_finish"],
                bar_price_fix=doc_updated["bar_price_fix"],
            )
            iteration_collection.append(iteration)
        return iteration_collection
