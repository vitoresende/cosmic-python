from dataclasses import dataclass
from datetime import date
from typing import List, NewType, Optional


@dataclass(unsafe_hash=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int

Quantity = NewType("Quantity", int)
Sku = NewType("Sku", str)
Reference = NewType("Reference", str)

class Batch:
    def __init__(self, ref: Reference, sku: Sku, qty: Quantity, eta: Optional[date]):
        """
        :param ref: Unique reference ID of the batch.
        :param sku: Stock keeping unit identifier.
        :param qty: Initial quantity of the batch.
        :param eta: Estimated time of arrival (ETA) of the batch.
        """
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._allocations = set()  # type: Set[OrderLine]

    def __repr__(self):
        return f"<Batch {self.reference}>"
    
    def __gt__(self, other):
        """
        Compare batches based on their ETA. A batch with no ETA is considered less than a batch with an ETA.
        """
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty
    
    '''
    Entities, unlike values, have identity equality. We can change their values, 
    and they are still recognizably the same thing. Batches, in our example, are entities. 
    We can allocate lines to a batch, or change the date that we expect it to arrive, 
    and it will still be the same entity.

    We usually make this explicit in code by implementing equality operators on entities:
    '''
    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)
    
class OutOfStock(Exception):
    pass

def allocate(line: OrderLine, batches: List[Batch]) -> str:
    """
    Allocate an order line to the first batch that can fulfill it.
    """
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
        return batch.reference
    except StopIteration:
        raise OutOfStock(f"Out of stock for sku {line.sku}")