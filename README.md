# Useful Pandas Examples

Pandas recipes I have found useful and general but not immediately obvious.

## [Custom Rolling Window Bounds](custom_rolling_indexer.py)

An example custom indexer to calculate rolling window bounds that always start
at the beginning of a day and still end at the current time.

## [Preserving the Index](index_order.py)

Shows how to reassign to and keep the DataFrame in the original order after
doing groupby and rolling operations (when the rolling index isn't unique).