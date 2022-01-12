import stormpy
import stormpy.logic
from helpers.helper import get_example_path

import math
from configurations import dft


@dft
class TestAnalysis:

    def test_analyze_mttf(self):
        dft = stormpy.dft.load_dft_json_file(get_example_path("dft", "and.json"))
        formulas = stormpy.parse_properties("T=? [ F \"failed\" ]")
        assert dft.nr_elements() == 3
        results = stormpy.dft.analyze_dft(dft, [formulas[0].raw_formula])
        assert math.isclose(results[0], 3)

    def test_build_model(self):
        dft = stormpy.dft.load_dft_json_file(get_example_path("dft", "and.json"))
        symmetries = stormpy.dft.DFTSymmetries()
        model = stormpy.dft.build_model(dft, symmetries)
        assert model.model_type == stormpy.ModelType.CTMC
        assert type(model) is stormpy.SparseCtmc
        assert model.nr_states == 4
        assert model.nr_transitions == 5
        assert not model.supports_parameters

    def test_explicit_model_builder(self):
        dft = stormpy.dft.load_dft_json_file(get_example_path("dft", "and.json"))
        symmetries = stormpy.dft.DFTSymmetries()
        builder = stormpy.dft.ExplicitDFTModelBuilder_double(dft, symmetries)
        builder.build(0)
        model = builder.get_model()
        assert model.model_type == stormpy.ModelType.CTMC
        assert type(model) is stormpy.SparseCtmc
        assert model.nr_states == 4
        assert model.nr_transitions == 5
        assert not model.supports_parameters

    def test_explicit_model_builder_approximation(self):
        dft = stormpy.dft.load_dft_galileo_file(get_example_path("dft", "rc.dft"))
        symmetries = stormpy.dft.DFTSymmetries()
        builder = stormpy.dft.ExplicitDFTModelBuilder_double(dft, symmetries)
        builder.build(0, 1.0)
        model_low = builder.get_partial_model(True, False)
        assert model_low.model_type == stormpy.ModelType.CTMC
        assert type(model_low) is stormpy.SparseCtmc
        assert model_low.nr_states == 25
        assert model_low.nr_transitions == 46
        assert not model_low.supports_parameters
        model_up = builder.get_partial_model(True, False)
        assert model_up.model_type == stormpy.ModelType.CTMC
        assert type(model_up) is stormpy.SparseCtmc
        assert model_up.nr_states == 25
        assert model_up.nr_transitions == 46
        assert not model_up.supports_parameters

    def test_relevant_events_property(self):
        dft = stormpy.dft.load_dft_json_file(get_example_path("dft", "and.json"))
        properties = stormpy.parse_properties("P=? [ F<=1 \"A_failed\" ]")
        formulas = [p.raw_formula for p in properties]
        relevant_events = stormpy.dft.compute_relevant_events(dft, formulas)
        assert relevant_events.is_relevant("A")
        assert not relevant_events.is_relevant("B")
        assert not relevant_events.is_relevant("C")
        results = stormpy.dft.analyze_dft(dft, formulas, relevant_events = relevant_events)
        assert math.isclose(results[0], 0.1548181217)

    def test_relevant_events_additional(self):
        dft = stormpy.dft.load_dft_json_file(get_example_path("dft", "and.json"))
        properties = stormpy.parse_properties("P=? [ F<=1 \"failed\" ]")
        formulas = [p.raw_formula for p in properties]
        relevant_events = stormpy.dft.compute_relevant_events(dft, formulas, ["B", "C"])
        assert relevant_events.is_relevant("B")
        assert relevant_events.is_relevant("C")
        assert not relevant_events.is_relevant("A")
        results = stormpy.dft.analyze_dft(dft, formulas, relevant_events = relevant_events)
        assert math.isclose(results[0], 0.1548181217)

    def test_transformation(self):
        dft = stormpy.dft.load_dft_galileo_file(get_example_path("dft", "rc2.dft"))
        valid, output = stormpy.dft.is_well_formed(dft)
        assert not valid
        assert "not binary" in output
        dft = stormpy.dft.transform_dft(dft, unique_constant_be=True, binary_fdeps=True)
        valid, output = stormpy.dft.is_well_formed(dft)
        assert valid
        formulas = stormpy.parse_properties("Tmin=? [ F \"failed\" ]")
        results = stormpy.dft.analyze_dft(dft, [formulas[0].raw_formula])
        assert math.isclose(results[0], 6.380930905)

    def test_fdep_conflicts(self):
        dft = stormpy.dft.load_dft_galileo_file(get_example_path("dft", "rc2.dft"))
        dft = stormpy.dft.transform_dft(dft, unique_constant_be=True, binary_fdeps=True)
        has_conflicts = stormpy.dft.compute_dependency_conflicts(dft, use_smt=False, solver_timeout=0)
        assert not has_conflicts
        formulas = stormpy.parse_properties("T=? [ F \"failed\" ]")
        results = stormpy.dft.analyze_dft(dft, [formulas[0].raw_formula])
        assert math.isclose(results[0], 6.380930905)
