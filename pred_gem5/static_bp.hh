#ifndef __CPU_PRED_STATIC_BP_HH__
#define __CPU_PRED_STATIC_BP_HH__

#include "cpu/pred/bpred_unit.hh"

// Generated from StaticBP.py:
#include "params/StaticTakenBP.hh"
#include "params/StaticNotTakenBP.hh"

namespace gem5
{
namespace branch_prediction
{

class StaticTakenBP : public BPredUnit
{
  public:
    explicit StaticTakenBP(const StaticTakenBPParams &p);

    bool lookup(ThreadID tid, Addr branch_addr, void *&bp_history) override;

    void update(ThreadID tid, Addr branch_addr, bool taken, void *bp_history,
                bool squashed, const StaticInstPtr &inst,
                Addr corrTarget = MaxAddr) override;

    void squash(ThreadID tid, void *bp_history) override;

    void btbUpdate(ThreadID tid, Addr branch_addr, void *&bp_history) override;

    void uncondBranch(ThreadID tid, Addr pc, void *&bp_history) override;
};

class StaticNotTakenBP : public BPredUnit
{
  public:
    explicit StaticNotTakenBP(const StaticNotTakenBPParams &p);

    bool lookup(ThreadID tid, Addr branch_addr, void *&bp_history) override;

    void update(ThreadID tid, Addr branch_addr, bool taken, void *bp_history,
                bool squashed, const StaticInstPtr &inst,
                Addr corrTarget = MaxAddr) override;

    void squash(ThreadID tid, void *bp_history) override;

    void btbUpdate(ThreadID tid, Addr branch_addr, void *&bp_history) override;

    void uncondBranch(ThreadID tid, Addr pc, void *&bp_history) override;
};

} // namespace branch_prediction
} // namespace gem5

#endif
