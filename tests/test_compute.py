"""Tests for pixel_python.compute -- ComputeProgram, ComputePipeline, ComputeRunner."""

import pytest

from pixel_python.compute import (
    ComputePipeline,
    ComputeProgram,
    ComputeRunner,
    compute_program,
)


# ── Helpers ──────────────────────────────────────────────────────

class Incrementor(ComputeProgram):
    """Adds 1 to state['counter'] each frame."""

    def compute(self, state):
        state["counter"] = state.get("counter", 0) + 1
        return state


class Doubler(ComputeProgram):
    """Doubles state['value'] each frame."""

    def compute(self, state):
        state["value"] = state.get("value", 1) * 2
        return state


class AddPrefix(ComputeProgram):
    """Prepends a string to state['text']."""

    def __init__(self, prefix: str):
        self.prefix = prefix

    def compute(self, state):
        text = state.get("text", "")
        state["text"] = self.prefix + text
        return state


class LifecycleTracker(ComputeProgram):
    """Tracks setup/compute/teardown calls."""

    def __init__(self):
        self.setup_called = 0
        self.compute_called = 0
        self.teardown_called = 0

    def setup(self, state):
        self.setup_called += 1
        state.setdefault("lifecycle", []).append("setup")

    def compute(self, state):
        self.compute_called += 1
        state.setdefault("lifecycle", []).append("compute")
        return state

    def teardown(self, state):
        self.teardown_called += 1
        state.setdefault("lifecycle", []).append("teardown")


class FailProgram(ComputeProgram):
    """Raises during compute for error-path testing."""

    def compute(self, state):
        raise RuntimeError("compute failed")


# ── ComputeProgram base ──────────────────────────────────────────

class TestComputeProgramBase:
    def test_cannot_instantiate_abstract(self):
        with pytest.raises(TypeError, match="abstract"):
            ComputeProgram()

    def test_subclass_works(self):
        prog = Incrementor()
        result = prog.compute({"counter": 5})
        assert result["counter"] == 6

    def test_name_defaults_to_class_name(self):
        assert Incrementor().name == "Incrementor"

    def test_setup_teardown_default_noop(self):
        prog = Incrementor()
        prog.setup({})   # should not raise
        prog.teardown({})

    def test_state_is_returned(self):
        prog = Doubler()
        result = prog.compute({"value": 3, "extra": "kept"})
        assert result["value"] == 6
        assert result["extra"] == "kept"


# ── ComputePipeline ─────────────────────────────────────────────

class TestComputePipeline:
    def test_empty_pipeline_passes_state_through(self):
        pipe = ComputePipeline()
        result = pipe.compute({"x": 1})
        assert result == {"x": 1}

    def test_single_program(self):
        pipe = ComputePipeline([Incrementor()])
        result = pipe.compute({"counter": 9})
        assert result["counter"] == 10

    def test_sequential_chaining(self):
        """Two programs in sequence: increment then double."""
        pipe = ComputePipeline([Incrementor(), Doubler()])
        result = pipe.compute({"counter": 4, "value": 3})
        assert result["counter"] == 5   # Incrementor
        assert result["value"] == 6     # Doubler

    def test_three_programs_text_transform(self):
        pipe = ComputePipeline([
            AddPrefix("hello "),
            AddPrefix("world "),
        ])
        result = pipe.compute({"text": "test"})
        assert result["text"] == "world hello test"

    def test_add_appends_program(self):
        pipe = ComputePipeline()
        pipe.add(Incrementor())
        pipe.add(Doubler())
        assert len(pipe.programs) == 2

    def test_add_rejects_non_compute_program(self):
        pipe = ComputePipeline()
        with pytest.raises(TypeError, match="expected ComputeProgram"):
            pipe.add("not a program")  # type: ignore

    def test_constructor_with_programs(self):
        pipe = ComputePipeline([Incrementor(), Doubler()])
        result = pipe.compute({"counter": 0, "value": 2})
        assert result["counter"] == 1
        assert result["value"] == 4

    def test_setup_teardown_propagate(self):
        tracker = LifecycleTracker()
        pipe = ComputePipeline([tracker])
        state = {}
        pipe.setup(state)
        pipe.teardown(state)
        assert tracker.setup_called == 1
        assert tracker.teardown_called == 1
        assert state["lifecycle"] == ["setup", "teardown"]

    def test_setup_teardown_all_programs(self):
        t1 = LifecycleTracker()
        t2 = LifecycleTracker()
        pipe = ComputePipeline([t1, t2])
        state = {}
        pipe.setup(state)
        pipe.teardown(state)
        assert t1.setup_called == 1
        assert t2.setup_called == 1
        assert t1.teardown_called == 1
        assert t2.teardown_called == 1

    def test_programs_property_is_copy(self):
        pipe = ComputePipeline([Incrementor()])
        progs = pipe.programs
        progs.append(Doubler())  # modifying the copy
        assert len(pipe.programs) == 1  # original unchanged


# ── ComputeRunner ────────────────────────────────────────────────

class TestComputeRunner:
    def test_single_frame(self):
        runner = ComputeRunner(Incrementor(), frames=1)
        result = runner.run({"counter": 0})
        assert result["counter"] == 1

    def test_multiple_frames(self):
        runner = ComputeRunner(Incrementor(), frames=5)
        result = runner.run({"counter": 0})
        assert result["counter"] == 5

    def test_meta_injected(self):
        runner = ComputeRunner(Incrementor(), frames=3)
        result = runner.run()
        assert "_meta" in result
        assert result["_meta"]["frame"] == 3
        assert "start_time" in result["_meta"]
        assert "elapsed" in result["_meta"]

    def test_on_frame_callback(self):
        frames_seen = []

        def on_frame(state, frame_num):
            frames_seen.append(frame_num)

        runner = ComputeRunner(Incrementor(), frames=4, on_frame=on_frame)
        runner.run()
        assert frames_seen == [1, 2, 3, 4]

    def test_on_frame_sees_state(self):
        states_seen = []

        def on_frame(state, frame_num):
            states_seen.append(dict(state))

        runner = ComputeRunner(Incrementor(), frames=3, on_frame=on_frame)
        runner.run({"counter": 0})
        assert states_seen[0]["counter"] == 1
        assert states_seen[1]["counter"] == 2
        assert states_seen[2]["counter"] == 3

    def test_default_empty_state(self):
        runner = ComputeRunner(Incrementor(), frames=1)
        result = runner.run()
        assert result["counter"] == 1

    def test_initial_state_not_mutated(self):
        initial = {"counter": 10, " preserved": "data"}
        runner = ComputeRunner(Incrementor(), frames=1)
        result = runner.run(initial)
        assert result["counter"] == 11
        assert initial["counter"] == 10  # original unchanged

    def test_invalid_frames_raises(self):
        with pytest.raises(ValueError, match="frames must be >= 1"):
            ComputeRunner(Incrementor(), frames=0)

    def test_setup_and_teardown_called(self):
        tracker = LifecycleTracker()
        runner = ComputeRunner(tracker, frames=2)
        runner.run()
        assert tracker.setup_called == 1
        assert tracker.teardown_called == 1
        assert tracker.compute_called == 2

    def test_teardown_called_on_error(self):
        class TeardownTracker(ComputeProgram):
            torn_down = False

            def compute(self, state):
                raise RuntimeError("boom")

            def teardown(self, state):
                TeardownTracker.torn_down = True

        prog = TeardownTracker()
        runner = ComputeRunner(prog, frames=1)
        with pytest.raises(RuntimeError):
            runner.run()
        assert TeardownTracker.torn_down

    def test_pipeline_in_runner(self):
        """Full integration: pipeline of 3 programs over 5 frames."""
        pipe = ComputePipeline([Incrementor(), Doubler()])
        runner = ComputeRunner(pipe, frames=5)
        result = runner.run({"counter": 0, "value": 1})
        # Incrementor runs 5 times: counter = 5
        assert result["counter"] == 5
        # Doubler runs 5 times: value = 1 * 2^5 = 32
        assert result["value"] == 32

    def test_state_persists_across_frames(self):
        """State from frame N is visible in frame N+1."""

        class AppendFrame(ComputeProgram):
            def compute(self, state):
                state.setdefault("log", []).append(state["_meta"]["frame"])
                return state

        runner = ComputeRunner(AppendFrame(), frames=3)
        result = runner.run()
        assert result["log"] == [1, 2, 3]

    def test_runner_state_attribute(self):
        runner = ComputeRunner(Incrementor(), frames=2)
        runner.run({"counter": 0})
        assert runner.state["counter"] == 2


# ── @compute_program decorator ───────────────────────────────────

class TestComputeProgramDecorator:
    def test_basic_decorator(self):
        @compute_program
        def add_counter(state):
            state["counter"] = state.get("counter", 0) + 1
            return state

        prog = add_counter()
        result = prog.compute({"counter": 5})
        assert result["counter"] == 6

    def test_decorator_name(self):
        @compute_program
        def my_program(state):
            return state

        assert my_program.__name__ == "my_program"
        assert my_program().name == "my_program"

    def test_decorator_doc(self):
        @compute_program
        def documented(state):
            """This is documented."""
            return state

        assert documented.__doc__ == "This is documented."

    def test_decorator_with_kwargs(self):
        @compute_program
        def add_tag(state):
            return state

        prog = add_tag(tag="test")
        assert prog._extra["tag"] == "test"

    def test_decorator_in_runner(self):
        @compute_program
        def increment(state):
            state["n"] = state.get("n", 0) + 1
            return state

        runner = ComputeRunner(increment(), frames=3)
        result = runner.run()
        assert result["n"] == 3

    def test_decorator_in_pipeline(self):
        @compute_program
        def step_a(state):
            state["a"] = True
            return state

        @compute_program
        def step_b(state):
            state["b"] = True
            return state

        pipe = ComputePipeline([step_a(), step_b()])
        result = pipe.compute({})
        assert result == {"a": True, "b": True}


# ── Integration: AIPM-like pipeline simulation ───────────────────

class TestAIPMIntegration:
    """Simulate the AIPM v5 scheduler pattern using compute programs."""

    def test_full_aipm_cycle(self):
        """Mimics one AIPM cycle: route -> read spec -> execute -> detect."""

        class ModelRouter(ComputeProgram):
            def compute(self, state):
                state["model"] = "claude-sonnet"
                state["routing_reason"] = "default"
                return state

        class SpecReader(ComputeProgram):
            def compute(self, state):
                state["task"] = {"name": "add-auth", "section": "SEC-1"}
                state["prompt"] = f"Implement {state['task']['name']}"
                return state

        class AgentExecutor(ComputeProgram):
            def compute(self, state):
                # Simulate agent output
                state["exit_code"] = 0
                state["files_changed"] = ["src/auth.ts"]
                state["commit_hash"] = "abc123"
                return state

        class OutcomeDetector(ComputeProgram):
            def compute(self, state):
                if state.get("exit_code") == 0:
                    state["outcome"] = "success"
                else:
                    state["outcome"] = "failure"
                return state

        pipeline = ComputePipeline([
            ModelRouter(),
            SpecReader(),
            AgentExecutor(),
            OutcomeDetector(),
        ])

        runner = ComputeRunner(pipeline, frames=1)
        result = runner.run({"project": "my-app"})

        assert result["model"] == "claude-sonnet"
        assert result["task"]["name"] == "add-auth"
        assert result["outcome"] == "success"
        assert result["files_changed"] == ["src/auth.ts"]

    def test_aipm_retry_cycle(self):
        """Simulate: first attempt fails, second succeeds."""

        attempt = {"count": 0}

        class FlakyExecutor(ComputeProgram):
            """Fails on first attempt, succeeds on second."""

            def compute(self, state):
                attempt["count"] += 1
                if attempt["count"] <= 1:
                    state["exit_code"] = 1
                    state["outcome"] = "failure"
                else:
                    state["exit_code"] = 0
                    state["outcome"] = "success"
                return state

        class StrategyPicker(ComputeProgram):
            def compute(self, state):
                if state.get("outcome") == "failure":
                    state["strategy"] = "retry"
                    state["attempt"] = state.get("attempt", 1) + 1
                else:
                    state["strategy"] = "fresh"
                    state.setdefault("attempt", 1)
                return state

        pipeline = ComputePipeline([FlakyExecutor(), StrategyPicker()])

        runner = ComputeRunner(pipeline, frames=3)
        result = runner.run({})

        # After 3 frames: attempt 1 failed, attempt 2+ succeeded
        assert result["outcome"] == "success"
        assert result["attempt"] == 2
