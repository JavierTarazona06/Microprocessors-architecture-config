# configs/example/se_fu.py
#
# Run a RISC-V SE workload on DerivO3CPU with a configurable functional-unit pool.
#
# Example:
# build/RISCV/gem5.opt -d m5out \
#   configs/example/se_fu.py --cmd=program.riscv --caches \
#   --ialu=4 --imult=1 --fpalu=4 --fpmult=1 --memport=2
print("SE_FU: script loaded")

import argparse
import m5
from m5.objects import (
    System, Root, Process, SEWorkload,
    SrcClockDomain, VoltageDomain, AddrRange,
    DerivO3CPU, TimingSimpleCPU, MinorCPU,
    SystemXBar, MemCtrl, DDR3_1600_8x8,
    Cache, L2XBar,
    FUPool, FUDesc, OpDesc
)

# ----------------------------
# Minimal caches
# ----------------------------
class L1ICache(Cache):
    size = "32kB"
    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 8
    is_read_only = True

class L1DCache(Cache):
    size = "32kB"
    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 8
    tgts_per_mshr = 8

class L2Cache(Cache):
    size = "256kB"
    assoc = 8
    tag_latency = 10
    data_latency = 10
    response_latency = 10
    mshrs = 16
    tgts_per_mshr = 12


def build_fu_pool(ialu: int, imult: int, fpalu: int, fpmult: int, memport: int) -> FUPool:
    """
    Build FU pool for DerivO3CPU.
    opClass names may vary across gem5 versions; adjust if your build errors.
    """

    class IntALU(FUDesc):
        count = ialu
        opList = [OpDesc(opClass="IntAlu", opLat=1)]

    class IntMultDiv(FUDesc):
        count = imult
        opList = [
            OpDesc(opClass="IntMult", opLat=3),
            OpDesc(opClass="IntDiv",  opLat=12),
        ]

    class FPALU(FUDesc):
        count = fpalu
        opList = [
            OpDesc(opClass="FloatAdd", opLat=2),
            OpDesc(opClass="FloatCmp", opLat=2),
            OpDesc(opClass="FloatCvt", opLat=2),
        ]

    class FPMultDiv(FUDesc):
        count = fpmult
        opList = [
            OpDesc(opClass="FloatMult", opLat=4),
            OpDesc(opClass="FloatDiv",  opLat=12),
        ]

    class MemPort(FUDesc):
        count = memport
        opList = [
            OpDesc(opClass="MemRead",  opLat=1),
            OpDesc(opClass="MemWrite", opLat=1),
        ]

    return FUPool(FUList=[IntALU(), IntMultDiv(), FPALU(), FPMultDiv(), MemPort()])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cmd", required=True, help="RISC-V binary to run (static recommended)")
    ap.add_argument("--args", default="", help="Arguments to pass to program (single string)")
    ap.add_argument("--cpu-type", choices=["O3", "TimingSimpleCPU", "MinorCPU"], default="O3")
    ap.add_argument("--cpu-clock", default="1GHz")
    ap.add_argument("--mem-size", default="8GB")
    ap.add_argument("--caches", action="store_true", help="Enable simple private L1 + shared L2")

    # FU knobs
    ap.add_argument("--ialu", type=int, default=4)
    ap.add_argument("--imult", type=int, default=1)
    ap.add_argument("--fpalu", type=int, default=1)
    ap.add_argument("--fpmult", type=int, default=1)
    ap.add_argument("--memport", type=int, default=2)

    args = ap.parse_args()

    print("SE_FU: parsed args", args)


    system = System()
    system.clk_domain = SrcClockDomain(clock=args.cpu_clock, voltage_domain=VoltageDomain())
    system.mem_mode = "timing"
    system.mem_ranges = [AddrRange(args.mem_size)]

    # CPU
    if args.cpu_type == "O3":
        system.cpu = DerivO3CPU()
        system.cpu.fuPool = build_fu_pool(args.ialu, args.imult, args.fpalu, args.fpmult, args.memport)
    elif args.cpu_type == "Minor":
        system.cpu = MinorCPU()
    else:
        system.cpu = TimingSimpleCPU()

    # Buses + memory
    system.membus = SystemXBar()
    system.system_port = system.membus.cpu_side_ports

    # Interrupts (important)
    system.cpu.createInterruptController()

    if args.caches:
        system.cpu.icache = L1ICache()
        system.cpu.dcache = L1DCache()
        system.l2bus = L2XBar()
        system.l2cache = L2Cache()

        # CPU <-> L1
        system.cpu.icache_port = system.cpu.icache.cpu_side
        system.cpu.dcache_port = system.cpu.dcache.cpu_side

        # L1 <-> L2 bus
        system.cpu.icache.mem_side = system.l2bus.cpu_side_ports
        system.cpu.dcache.mem_side = system.l2bus.cpu_side_ports

        # L2 <-> buses
        system.l2cache.cpu_side = system.l2bus.mem_side_ports
        system.l2cache.mem_side = system.membus.cpu_side_ports
    else:
        # No caches: CPU directly to membus
        system.cpu.icache_port = system.membus.cpu_side_ports
        system.cpu.dcache_port = system.membus.cpu_side_ports

    system.mem_ctrl = MemCtrl()
    system.mem_ctrl.dram = DDR3_1600_8x8()
    system.mem_ctrl.dram.range = system.mem_ranges[0]
    system.mem_ctrl.port = system.membus.mem_side_ports

    # Workload (SE)
    system.workload = SEWorkload.init_compatible(args.cmd)
    process = Process()
    process.cmd = [args.cmd] + (args.args.split() if args.args else [])
    system.cpu.workload = process
    system.cpu.createThreads()

    root = Root(full_system=False, system=system)
    print("SE_FU: instantiating")

    m5.instantiate()
    print("SE_FU: simulating")

    exit_event = m5.simulate()
    print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")

main()

