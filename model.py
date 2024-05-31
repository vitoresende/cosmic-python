from dataclasses import dataclass
from datetime import date
from typing import List, NewType, Optional

'''
For value objects, the hash should be based on all the value attributes, 
and we should ensure that the objects are immutable. 
We get this for free by specifying @frozen=True on the dataclass.
'''
@dataclass(frozen=True)
class OrderLine:
    """
    Represents a line in an order with an order ID, SKU, and quantity.
    This class is immutable and its hash is based on its value attributes.
    """
    orderid: str
    sku: str
    qty: int

'''
That would allow our type checker to make sure that we don’t pass a Sku where a Reference is expected, for example.

Whether you think this is wonderful or appalling is a matter of debate.
'''
Quantity = NewType("Quantity", int)
Sku = NewType("Sku", str)
Reference = NewType("Reference", str)

class Batch:
    """
    Represents a batch of stock. A batch has a unique reference ID, a SKU, a quantity,
    and an optional estimated time of arrival (ETA). 
    """
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
    
    '''
    You may or may not like the use of next() in the allocate method, but we're pretty sure you'll agree that being able to use sorted()
      on our list of batches is nice, idiomatic Python. To make it work, we implement __gt__ on our domain model:
    '''
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