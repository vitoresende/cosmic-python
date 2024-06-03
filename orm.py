from sqlalchemy import Table, MetaData, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import mapper, relationship

import model

"""
Object-relational mappers (ORMs) because they exist to bridge the conceptual 
gap between the world of objects and domain modeling and the world of databases 
and relational algebra.

The most important thing an ORM gives us is persistence ignorance: the idea 
that our fancy domain model doesn't need to know anything about how data is 
loaded or persisted. This helps keep our domain clean of direct dependencies 
on particular database technologies
"""

metadata = MetaData()

order_lines = Table(
    "order_lines",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255)),
    Column("qty", Integer, nullable=False),
    Column("orderid", String(255)),
)

batches = Table(
    "batches",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("reference", String(255)),
    Column("sku", String(255)),
    Column("_purchased_quantity", Integer, nullable=False),
    Column("eta", Date, nullable=True),
)

allocations = Table(
    "allocations",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderline_id", ForeignKey("order_lines.id")),
    Column("batch_id", ForeignKey("batches.id")),
)


def start_mappers():
    """
    Configure mappers to associate Python classes with database tables.
    
    This function sets up the mapping between the domain model classes
    and the corresponding database tables using SQLAlchemy's ORM.

    If we call start_mappers, we will be able to easily load and save domain model instances from and to the database. 
    But if we never call that function, our domain model classes stay blissfully unaware of the database.
    """
    lines_mapper = mapper(model.OrderLine, order_lines)

    # Map Batch class to the batches table with a relationship to OrderLine through the allocations table
    mapper(
        model.Batch,
        batches,
        properties={
            "_allocations": relationship(
                lines_mapper, secondary=allocations, collection_class=set,
            )
        },
    )
