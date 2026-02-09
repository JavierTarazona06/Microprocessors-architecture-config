# RISCV_se.py (stdlib, non-deprecated)
# Minimal RISC-V SE config for TD/TP1+TD/TP2 stats

import argparse

from gem5.utils.requires import requires
from gem5.isas import ISA
from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.memory import SingleChannelDDR3_1600
from gem5.components.cachehierarchies.classic.private_l1_cache_hierarchy import (
    PrivateL1CacheHierarchy,
)
from gem5.resources.resource import BinaryResource
from gem5.simulate.simulator import Simulator

parser = argparse.ArgumentParser()
parser.add_argument("-b", "--binary", required=True, help="Path to RISC-V user ELF")
args = parser.parse_args()

requires(isa_required=ISA.RISCV)

# This gem5 version's PrivateL1CacheHierarchy supports sizes (not assoc).
cache_hierarchy = PrivateL1CacheHierarchy(
    l1i_size="32kB",
    l1d_size="32kB",
)

memory = SingleChannelDDR3_1600(size="8GB")

processor = SimpleProcessor(
    cpu_type=CPUTypes.O3,   # Rich op_class stats
    isa=ISA.RISCV,
    num_cores=1,
)

board = SimpleBoard(
    clk_freq="1GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

board.set_se_binary_workload(BinaryResource(args.binary))

sim = Simulator(board=board)
sim.run()
