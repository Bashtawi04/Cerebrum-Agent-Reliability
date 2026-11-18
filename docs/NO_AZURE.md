# Doing Phase 3 without a model key

Most of Phase 3 needs no language model. Only **running an agent** does. Everything else works on files:

| You do | Needs a model? |
|---|---|
| Write `lab/stats.py`, `aggregate.py`, `honesty.py`, `gate.py` and pass the tests | no |
| Measure and classify the runs we recorded for you (below) | no |
| Run the honesty checker and the gate over recorded results and traces | no |
| Write scenarios and check them with `tools/validate_scenarios.py` | no |
| Show that a scenario can pass and can fail, with a scripted agent (`templates/scripted_<track>.py`) | no |
| Run a real agent on a scenario | **yes**: a local model, or us (below) |

## What we recorded for you

`recorded/<target folder>/` holds runs of the frozen target agent that we made with a real model (`gpt-5.4-mini` on our own deployment), in
November 2026, one job at a time:

* `public_a.json` and `public_b.json`: six runs of every public scenario of the target's track, twice, so **12 runs per scenario**.
  Use the pair for "baseline versus current" in the gate, or merge them for the measurement.
* `suite.json`: six runs of a small suite written by a previous reviewer (`scenarios/colleague_suite_<track>.jsonl`). Read the scenarios
  first, then read what the target did.
* `traces/public_a/`, `traces/public_b/`, `traces/suite/`: one trace file per run (see `docs/TRACE_FORMAT.md`).

```
python3 -m lab.aggregate recorded/<target folder>/public_a.json recorded/<target folder>/public_b.json --title "Target, public scenarios"
python3 -m lab.aggregate recorded/<target folder>/suite.json --title "Target, colleague suite"
```

These are recordings, so you cannot rerun the same run, and a different model gives different numbers. **Never mix numbers from different
models in one table**, and always say in your report which numbers come from our recordings and which from your own runs.

## If you want to run an agent yourself

**A. A free local model.** Install Ollama (ollama.com), then `ollama pull qwen2.5:7b`. Your agents call an Azure-style address
(`<endpoint>/openai/v1/...`), which Ollama does not serve, so run the small translator we give you, in a second terminal:

```
python3 tools/local_model_proxy.py --model qwen2.5:7b
```

and put this in the `.env` of the lab folder (the runner passes it to the agent):

```
AZURE_OPENAI_ENDPOINT=http://127.0.0.1:8099
AZURE_OPENAI_API_KEY=local
AZURE_OPENAI_DEPLOYMENT=qwen2.5:7b
```

What we measured, on one machine with 20 CPU cores, 30 GB of memory and no graphics card: about **two minutes per conversation** with `qwen2.5:7b`
(so ten runs of eight scenarios is a night, not an hour), and on two scenarios of the frozen Learning agent one passed and one failed because
the model did not call the booking tool. A 4-billion-parameter model timed out inside the agent's 60-second client limit. Expect a laptop to be
slower still. So: use it for a few scenarios and a few runs, say so in your report, and do not compare its numbers with ours.

**B. Ask us.** When your scenarios pass `tools/validate_scenarios.py`, send us the file. We run it on the frozen target with our deployment and
send back a results file and traces in the same format as the recordings. This is the way to get real runs of your new scenarios.

## What to write when you could not run something

Say so, and say what you did instead. "I could not run my own agent, so Level 1 is on the recorded target" is a complete and honest sentence. A
report that claims numbers it did not measure is the only thing here that will count against you.
