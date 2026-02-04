# hash.py
import random
from typing import List

# seed = int.from_bytes(random.randbytes(8), "little") | 1
seed = 0x9e3779b97f4a7c15

def hash(seq: str, k: int) -> List[int]:
  n = len(seq)
  if n < k:
    return []
  
  values = []
  for i in range(n - k + 1):
    h = seed
    for c in seq[i: i + k]:
      h = (h * 1315423911) ^ ord(c)
    values.append(h & ((1 << 64) - 1))

  return values