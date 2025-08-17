(env) fakhar@DESKTOP-9H42JH4:/mnt/e/cortexAI/cortex$ python -m pytest tests/test_multi_provider.py::TestModelRegistry -v
===================================== test session starts =====================================platform linux -- Python 3.12.3, pytest-8.4.1, pluggy-1.6.0 -- /mnt/e/cortexAI/env/bin/python  
cachedir: .pytest_cache
rootdir: /mnt/e/cortexAI/cortex
configfile: pyproject.toml
plugins: anyio-4.9.0, langsmith-0.4.9, cov-6.2.1
collected 7 items

tests/test_multi_provider.py::TestModelRegistry::test_all_providers_registered PASSED [ 14%]
tests/test_multi_provider.py::TestModelRegistry::test_openai_models_configured PASSED [ 28%]
tests/test_multi_provider.py::TestModelRegistry::test_google_models_configured PASSED [ 42%]
tests/test_multi_provider.py::TestModelRegistry::test_cohere_models_configured PASSED [ 57%]
tests/test_multi_provider.py::TestModelRegistry::test_deprecated_model_warning PASSED [ 71%]
tests/test_multi_provider.py::TestModelRegistry::test_invalid_model_raises_error PASSED [ 85%]
tests/test_multi_provider.py::TestModelRegistry::test_list_available_models FAILED [100%]

========================================== FAILURES ===========================================**********\_\_\_\_********** TestModelRegistry.test_list_available_models ************\_************
self = <test_multi_provider.TestModelRegistry object at 0x7f491f5d7bf0>

    def test_list_available_models(self):
        """Test listing available models with configuration status"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            models = list_available_models()

            # Should have multiple models
            assert len(models) > 5

            # Check structure
            for model in models:
                assert "model" in model
                assert "provider" in model
                assert "configured" in model
                assert "requires" in model
                assert "max_tokens" in model

            # OpenAI models should show as configured
            openai_models = [m for m in models if m["provider"] == "openai"]
            for model in openai_models:
                assert model["configured"] == True

            # Other providers without keys should show as not configured
            google_models = [m for m in models if m["provider"] == "google"]
            for model in google_models:

>               assert model["configured"] == False
>
> E assert True == False

tests/test_multi_provider.py:103: AssertionError
=================================== short test summary info ===================================FAILED tests/test_multi_provider.py::TestModelRegistry::test_list_available_models - assert True == False
================================ 1 failed, 6 passed in 16.41s =================================(env) fakhar@DESKTOP-9H42JH4:/mnt/e/cortexAI/cortex$
