from dataclasses import dataclass
from typing import NamedTuple
from collections import namedtuple

import pytest

'''
Value Object
Whenever we have a business concept that has data but no identity, we often choose to represent 
it using the Value Object pattern. A value object is any domain object that is uniquely identified by 
the data it holds; we usually make them immutable.

One of the nice things that dataclasses (or namedtuples) give us is value equality, 
which is the fancy way of saying, "Two lines with the same orderid, sku, and qty are equal."
'''
@dataclass(frozen=True)
class Name:
    first_name: str
    surname: str

class MoneyTuple(NamedTuple):
    currency: str
    value: int

Line = namedtuple('Line', ['sku', 'qty'])


def test_equality():
    assert MoneyTuple('gbp', 10) == MoneyTuple('gbp', 10)
    assert Name('Harry', 'Percival') != Name('Bob', 'Gregory')
    assert Line('RED-CHAIR', 5) == Line('RED-CHAIR', 5)


'''
These value objects match our real-world intuition about how their values work. 
It doesn't matter which £10 note we're talking about, because they all have the same value. 
Likewise, two names are equal if both the first and last names match; and two lines are equivalent 
if they have the same customer order, product code, and quantity. 
We can still have complex behavior on a value object, though. 
In fact, it's common to support operations on values; for example, mathematical operators:
'''
@dataclass(frozen=True)
class Money:
    currency: str
    value: int

    def __add__(self, other):
        if other.currency != self.currency:
            raise ValueError(f"Cannot add {self.currency} to {other.currency}")
        return Money(self.currency, self.value + other.value)
    
    def __sub__(self, other):
        if other.currency != self.currency:
            raise ValueError(f"Cannot subtract {other.currency} from {self.currency}")
        return Money(self.currency, self.value - other.value)
    
    def __mul__(self, multiplier):
        if not isinstance(multiplier, (int, float)):
            raise TypeError("Can only multiply Money by a number")
        return Money(self.currency, self.value * multiplier)
    
fiver = Money('gbp', 5)
tenner = Money('gbp', 10)

def test_can_add_money_values_for_the_same_currency():
    assert fiver + fiver == tenner

def test_can_subtract_money_values():
    assert tenner - fiver == fiver

def test_adding_different_currencies_fails():
    with pytest.raises(ValueError):
        Money('usd', 10) + Money('gbp', 10)

def test_can_multiply_money_by_a_number():
    assert fiver * 5 == Money('gbp', 25)

def test_multiplying_two_money_values_is_an_error():
    with pytest.raises(TypeError):
        tenner * fiver