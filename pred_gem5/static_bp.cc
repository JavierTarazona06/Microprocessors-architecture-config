#include "cpu/pred/static_bp.hh"

namespace gem5
{
namespace branch_prediction
{

StaticTakenBP::StaticTakenBP(const StaticTakenBPParams &p) : BPredUnit(p) {}

bool
StaticTakenBP::lookup(ThreadID, Addr, void *&bp_history)
{
    bp_history = nullptr;
    return true;
}

void
StaticTakenBP::update(ThreadID, Addr, bool, void*, bool, const StaticInstPtr&, Addr)
{
}

void
StaticTakenBP::squash(ThreadID, void*)
{
}

void
StaticTakenBP::btbUpdate(ThreadID, Addr, void *&bp_history)
{
    bp_history = nullptr;
}

void
StaticTakenBP::uncondBranch(ThreadID, Addr, void *&bp_history)
{
    bp_history = nullptr;
}


StaticNotTakenBP::StaticNotTakenBP(const StaticNotTakenBPParams &p) : BPredUnit(p) {}

bool
StaticNotTakenBP::lookup(ThreadID, Addr, void *&bp_history)
{
    bp_history = nullptr;
    return false;
}

void
StaticNotTakenBP::update(ThreadID, Addr, bool, void*, bool, const StaticInstPtr&, Addr)
{
}

void
StaticNotTakenBP::squash(ThreadID, void*)
{
}

void
StaticNotTakenBP::btbUpdate(ThreadID, Addr, void *&bp_history)
{
    bp_history = nullptr;
}

void
StaticNotTakenBP::uncondBranch(ThreadID, Addr, void *&bp_history)
{
    bp_history = nullptr;
}

} // namespace branch_prediction
} // namespace gem5
