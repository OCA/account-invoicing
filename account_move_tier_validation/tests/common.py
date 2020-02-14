# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def setup_test_model(env, model_clses):
    for model_cls in model_clses:
        model_cls._build_model(env.registry, env.cr)

    env.registry.setup_models(env.cr)
    env.registry.init_models(
        env.cr,
        [model_cls._name for model_cls in model_clses],
        dict(env.context, update_custom_fields=True),
    )


def teardown_test_model(env, model_clses):
    for model_cls in model_clses:
        del env.registry.models[model_cls._name]
    env.registry.setup_models(env.cr)
