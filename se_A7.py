# -*- coding: utf-8 -*-

import argparse
import m5
from m5.objects import *

class L1ICache(Cache):
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 8
    is_read_only = True
    writeback_clean = True
    def connectCPU(self, cpu): self.cpu_side = cpu.icache_port
    def connectBus(self, bus): self.mem_side = bus.cpu_side_ports

class L1DCache(Cache):
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 8
    tgts_per_mshr = 8
    writeback_clean = True
    def connectCPU(self, cpu): self.cpu_side = cpu.dcache_port
    def connectBus(self, bus): self.mem_side = bus.cpu_side_ports

class L2Cache(Cache):
    tag_latency = 10
    data_latency = 10
    response_latency = 10
    mshrs = 16
    tgts_per_mshr = 12
    writeback_clean = True
    def connectCPUSideBus(self, bus): self.cpu_side = bus.mem_side_ports
    def connectMemSideBus(self, bus): self.mem_side = bus.cpu_side_ports

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cmd", required=True)
    ap.add_argument("--options", nargs=argparse.REMAINDER, default=[])
    ap.add_argument("--clock", default="2GHz")
    ap.add_argument("--mem-size", default="2GB")
    ap.add_argument("--maxinsts", type=int, default=0)
    return ap.parse_args()

def build_system(args):
    system = System()
    system.clk_domain = SrcClockDomain(clock=args.clock, voltage_domain=VoltageDomain())
    system.mem_mode = "timing"
    system.mem_ranges = [AddrRange(args.mem_size)]

    # Cortex A7: blocs 32B
    system.cache_line_size = 32

    system.cpu = DerivO3CPU()

    # IMPORTANT: O3 default fetch buffer = 64B dans certaines versions gem5.
    # Avec des lignes de cache 32B, ca declenche le fatal "fetch buffer 64 > block 32".
    system.cpu.fetchBufferSize = 32

    # Fetch queue
    system.cpu.fetchQueueSize = 8

    # Decode / Issue / Commit : 2 / 4 / 2
    system.cpu.decodeWidth  = 2
    system.cpu.issueWidth   = 4
    system.cpu.commitWidth  = 2

    # Coherence autres largeurs
    system.cpu.fetchWidth    = 2
    system.cpu.renameWidth   = 4
    system.cpu.dispatchWidth = 4
    system.cpu.wbWidth       = 2

    # RUU/LSQ : 2 / 8  (interpretation gem5: ROB=2, LQ=8, SQ=8)
    system.cpu.numROBEntries = 2
    system.cpu.LQEntries = 8
    system.cpu.SQEntries = 8

    # Branch predictor : bimodal, BTB=256
    # BiModeBP correspond au "bimodal/bi-mode" cote gem5 classic.
    system.cpu.branchPred = BiModeBP()
    system.cpu.branchPred.BTBEntries = 256

    # -------- Caches C-A7 --------
    # I-L1: 32KB / 32 / 2
    system.cpu.icache = L1ICache()
    system.cpu.icache.size = "32kB"
    system.cpu.icache.assoc = 2

    # D-L1: 32KB / 32 / 2
    system.cpu.dcache = L1DCache()
    system.cpu.dcache.size = "32kB"
    system.cpu.dcache.assoc = 2

    # L2: 512KB / 32 / 8
    system.l2bus = L2XBar()
    system.l2cache = L2Cache()
    system.l2cache.size = "512kB"
    system.l2cache.assoc = 8

    system.cpu.icache.connectCPU(system.cpu)
    system.cpu.dcache.connectCPU(system.cpu)
    system.cpu.icache.connectBus(system.l2bus)
    system.cpu.dcache.connectBus(system.l2bus)
    system.l2cache.connectCPUSideBus(system.l2bus)

    system.membus = SystemXBar()
    system.l2cache.connectMemSideBus(system.membus)
    system.system_port = system.membus.cpu_side_ports

    # DRAM
    system.mem_ctrl = MemCtrl()
    system.mem_ctrl.dram = DDR3_1600_8x8()
    system.mem_ctrl.dram.range = system.mem_ranges[0]
    system.mem_ctrl.port = system.membus.mem_side_ports

    process = Process()
    process.cmd = [args.cmd] + args.options
    system.workload = SEWorkload.init_compatible(args.cmd)
    system.cpu.workload = process
    system.cpu.createThreads()
    system.cpu.createInterruptController()

    return system

def main():
    args = parse_args()
    system = build_system(args)
    root = Root(full_system=False, system=system)
    m5.instantiate()

    if args.maxinsts > 0:
        ev = m5.simulate(args.maxinsts)
    else:
        ev = m5.simulate()

    m5.stats.dump()
    print(f"Exiting @ tick {m5.curTick()} because {ev.getCause()}")

main()
