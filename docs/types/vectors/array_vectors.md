# ArrayVectors

## Creation

### ArrayVector(value: any=None, name: str=None, n: str=None)
### fromQuery(query, column='v')
### rand(start, end, length)
### range(start, end)
### norm(mean, stddev, length)

## Methods

### agg(agg)
### alias(alias)
### cache
### exec
### index_agg(agg)
### join(N)
### peek(count=10, max_block_size=30000)
### show(count=10, max_block_size=30000)
### toColumnVector

## Operations

### cast(to_type)
### cut(cut_length)
### delta
### flatten
### maplag(func)
### maplead(func)
### map(func, *args)
### move(positions)
### next
### prev
### shuffle
### sort_reverse
### sort
### take(length)
