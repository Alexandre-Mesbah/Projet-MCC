# Example Inputs

## CLI examples

```bash
python -m tm_project.cli run --machine machines/demo_flip_bits.tm --input 0101
python -m tm_project.cli run --machine machines/demo_flip_bits.tm --input 0101 --verbose
python -m tm_project.cli encode --machine machines/demo_flip_bits.tm
python -m tm_project.cli universal --machine machines/demo_flip_bits.tm --input 0101
python -m tm_project.cli bounded-universal --machine machines/demo_flip_bits.tm --input 0101 --steps 5
python -m tm_project.cli part2-report --machine machines/part2_flip_bits.tm2 --input 0101
python -m tm_project.cli strict-universal --machine machines/part2_flip_bits.tm2 --input 0101
python -m tm_project.cli strict-bounded-universal --machine machines/part2_flip_bits.tm2 --input 0101 --steps 5
```

## Machine inputs

- `demo_flip_bits.tm`: `0101`
- `part2_flip_bits.tm2`: `0101`
- `demo_copy_2tapes.tm`: `10#01`
- `compare_binary_1bit_demo.tm`: `0#1`
- `search_list_1symbol_demo.tm`: `1#0#0#1`
- `unary_multiply_left1_demo.tm`: `1#111`
