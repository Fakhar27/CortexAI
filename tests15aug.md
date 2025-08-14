(env) fakhar@DESKTOP-9H42JH4:/mnt/e/cortexAI/cortex$ pytest tests/ -vv
==================================================================================================== test session starts ====================================================================================================platform linux -- Python 3.12.3, pytest-8.4.1, pluggy-1.6.0 -- /mnt/e/cortexAI/env/bin/python
cachedir: .pytest_cache        
rootdir: /mnt/e/cortexAI/cortex
configfile: pyproject.toml     
plugins: anyio-4.9.0, langsmith-0.4.9, cov-6.2.1
collected 80 items

tests/test_core_functionality.py::TestBasicCreation::test_client_instantiation PASSED                                                                                                                                 [  1%]
tests/test_core_functionality.py::TestBasicCreation::test_basic_create_structure PASSED                                                                                                                               [  2%]
tests/test_core_functionality.py::TestBasicCreation::test_response_id_format PASSED                                                                                                                                   [  3%]
tests/test_core_functionality.py::TestBasicCreation::test_error_response_structure PASSED                                                                                                                             [  5%]
tests/test_core_functionality.py::TestConversationContinuity::test_basic_continuity PASSED                                                                                                                            [  6%]
tests/test_core_functionality.py::TestConversationContinuity::test_invalid_previous_response_id PASSED                                                                                                                [  7%]
tests/test_core_functionality.py::TestConversationContinuity::test_store_false_not_persisted PASSED                                                                                                                   [  8%]
tests/test_core_functionality.py::TestInputValidation::test_empty_input_rejected PASSED                                                                                                                               [ 10%]
tests/test_core_functionality.py::TestInputValidation::test_whitespace_input_rejected PASSED                                                                                                                          [ 11%]
tests/test_core_functionality.py::TestInputValidation::test_invalid_model_rejected PASSED                                                                                                                             [ 12%]
tests/test_core_functionality.py::TestInputValidation::test_invalid_temperature_rejected PASSED                                                                                                                       [ 13%]
tests/test_core_functionality.py::TestInputValidation::test_valid_temperature_accepted PASSED                                                                                                                         [ 15%]
tests/test_core_functionality.py::TestMetadata::test_metadata_stored PASSED                                                                                                                                           [ 16%]
tests/test_core_functionality.py::TestMetadata::test_empty_metadata PASSED                                                                                                                                            [ 17%]
tests/test_core_functionality.py::TestMetadata::test_no_metadata PASSED                                                                                                                                               [ 18%]
tests/test_core_functionality.py::TestMetadata::test_invalid_metadata_rejected PASSED                                                                                                                                 [ 20%]
tests/test_core_functionality.py::TestInstructions::test_instructions_in_new_conversation PASSED                                                                                                                      [ 21%]
tests/test_core_functionality.py::TestInstructions::test_instructions_discarded_on_continuation PASSED                                                                                                                [ 22%]
tests/test_db_url_parameter.py::TestDbUrlParameter::test_default_sqlite_without_db_url FAILED                                                                                                                         [ 23%]
tests/test_db_url_parameter.py::TestDbUrlParameter::test_db_url_override_per_request SKIPPED (PostgreSQL tests require DATABASE_URL environment variable)                                                             [ 25%]
tests/test_db_url_parameter.py::TestDbUrlParameter::test_conversation_continuation_with_matching_db_url SKIPPED (PostgreSQL tests require DATABASE_URL environment variable)                                          [ 26%]
tests/test_db_url_parameter.py::TestDbUrlParameter::test_conversation_fails_with_mismatched_db_url SKIPPED (PostgreSQL tests require DATABASE_URL environment variable)                                               [ 27%]
tests/test_db_url_parameter.py::TestDbUrlParameter::test_empty_db_url_uses_default PASSED                                                                                                                             [ 28%]
tests/test_db_url_parameter.py::TestDbUrlParameter::test_invalid_db_url_format PASSED                                                                                                                                 [ 30%]
tests/test_db_url_parameter.py::TestDbUrlParameter::test_valid_postgresql_url_formats PASSED                                                                                                                          [ 31%]
tests/test_db_url_parameter.py::TestDbUrlParameter::test_serverless_scenario_multiple_clients SKIPPED (PostgreSQL tests require DATABASE_URL environment variable)                                                    [ 32%]
tests/test_db_url_parameter.py::TestDbUrlParameter::test_db_url_with_store_false SKIPPED (PostgreSQL tests require DATABASE_URL environment variable)                                                                 [ 33%]
tests/test_db_url_parameter.py::TestDbUrlParameter::test_temporary_graph_creation PASSED                                                                                                                              [ 35%]
tests/test_db_url_parameter.py::TestDbUrlParameter::test_db_url_none_uses_instance_default PASSED                                                                                                                     [ 36%]
tests/test_db_url_parameter.py::TestDbUrlParameter::test_connection_error_handling PASSED                                                                                                                             [ 37%]
tests/test_db_url_parameter.py::TestDbUrlParameterIntegration::test_multiple_simultaneous_databases ERROR                                                                                                             [ 38%] 
tests/test_db_url_parameter.py::TestDbUrlParameterIntegration::test_conversation_isolation_between_databases ERROR                                                                                                    [ 40%] 
tests/test_edge_cases.py::TestLargeInputs::test_large_input_handling PASSED                                                                                                                                           [ 41%]
tests/test_edge_cases.py::TestLargeInputs::test_max_valid_input PASSED                                                                                                                                                [ 42%]
tests/test_edge_cases.py::TestLargeInputs::test_unicode_input PASSED                                                                                                                                                  [ 43%]
tests/test_edge_cases.py::TestConcurrency::test_sequential_rapid_requests PASSED                                                                                                                                      [ 45%]
tests/test_edge_cases.py::TestConcurrency::test_concurrent_requests_same_client PASSED                                                                                                                                [ 46%]
tests/test_edge_cases.py::TestAPIKeyHandling::test_missing_api_key_error FAILED                                                                                                                                       [ 47%]
tests/test_edge_cases.py::TestAPIKeyHandling::test_invalid_api_key_error PASSED                                                                                                                                       [ 48%]
tests/test_edge_cases.py::TestPersistence::test_persistence_across_clients PASSED                                                                                                                                     [ 50%]
tests/test_edge_cases.py::TestPersistence::test_memory_mode FAILED                                                                                                                                                    [ 51%]
tests/test_edge_cases.py::TestEdgeCaseInputs::test_only_punctuation PASSED                                                                                                                                            [ 52%]
tests/test_edge_cases.py::TestEdgeCaseInputs::test_sql_injection_attempt PASSED                                                                                                                                       [ 53%]
tests/test_edge_cases.py::TestEdgeCaseInputs::test_json_in_input PASSED                                                                                                                                               [ 55%]
tests/test_edge_cases.py::TestEdgeCaseInputs::test_code_in_input PASSED                                                                                                                                               [ 56%]
tests/test_edge_cases.py::TestEdgeCaseInputs::test_repeated_continuation PASSED                                                                                                                                       [ 57%]
tests/test_openai_compatibility.py::TestResponseFormat::test_all_required_fields_present PASSED                                                                                                                       [ 58%]
tests/test_openai_compatibility.py::TestResponseFormat::test_output_structure PASSED                                                                                                                                  [ 60%]
tests/test_openai_compatibility.py::TestResponseFormat::test_usage_structure PASSED                                                                                                                                   [ 61%]
tests/test_openai_compatibility.py::TestResponseFormat::test_reasoning_structure PASSED                                                                                                                               [ 62%]
tests/test_openai_compatibility.py::TestResponseFormat::test_text_format_structure PASSED                                                                                                                             [ 63%]
tests/test_openai_compatibility.py::TestResponseFormat::test_null_fields_exist PASSED                                                                                                                                 [ 65%]
tests/test_openai_compatibility.py::TestResponseFormat::test_default_values PASSED                                                                                                                                    [ 66%]
tests/test_openai_compatibility.py::TestErrorFormat::test_error_response_structure PASSED                                                                                                                             [ 67%]
tests/test_openai_compatibility.py::TestErrorFormat::test_error_object_fields PASSED                                                                                                                                  [ 68%]
tests/test_openai_compatibility.py::TestClientCompatibility::test_error_checking_pattern PASSED                                                                                                                       [ 70%]
tests/test_openai_compatibility.py::TestClientCompatibility::test_token_counting_pattern PASSED                                                                                                                       [ 71%]
tests/test_openai_compatibility.py::TestClientCompatibility::test_message_extraction_pattern PASSED                                                                                                                   [ 72%]
tests/test_persistence_comprehensive.py::TestPersistenceLayer::test_sqlite_default PASSED                                                                                                                             [ 73%]
tests/test_persistence_comprehensive.py::TestPersistenceLayer::test_postgresql_connection PASSED                                                                                                                      [ 75%]
tests/test_persistence_comprehensive.py::TestPersistenceLayer::test_empty_string_uses_default PASSED                                                                                                                  [ 76%] 
tests/test_persistence_comprehensive.py::TestPersistenceLayer::test_invalid_database_urls PASSED                                                                                                                      [ 77%] 
tests/test_persistence_comprehensive.py::TestPersistenceLayer::test_serverless_environment_detection PASSED                                                                                                           [ 78%] 
tests/test_persistence_comprehensive.py::TestPersistenceLayer::test_serverless_warning PASSED                                                                                                                         [ 80%] 
tests/test_persistence_comprehensive.py::TestPersistenceLayer::test_environment_variable_support PASSED                                                                                                               [ 81%]
tests/test_persistence_comprehensive.py::TestMultipleAgents::test_multiple_agents_sqlite PASSED                                                                                                                       [ 82%]
tests/test_persistence_comprehensive.py::TestMultipleAgents::test_conversation_isolation PASSED                                                                                                                       [ 83%]
tests/test_persistence_comprehensive.py::TestMultipleAgents::test_conversation_branching PASSED                                                                                                                       [ 85%]
tests/test_persistence_comprehensive.py::TestPersistenceAcrossRestarts::test_sqlite_persistence PASSED                                                                                                                [ 86%]
tests/test_persistence_comprehensive.py::TestPersistenceAcrossRestarts::test_postgresql_persistence PASSED                                                                                                            [ 87%]
tests/test_persistence_comprehensive.py::TestEdgeCases::test_very_long_input PASSED                                                                                                                                   [ 88%]
tests/test_persistence_comprehensive.py::TestEdgeCases::test_invalid_previous_response_id FAILED                                                                                                                      [ 90%]
tests/test_persistence_comprehensive.py::TestEdgeCases::test_store_false_persistence PASSED                                                                                                                           [ 91%]
tests/test_persistence_comprehensive.py::TestEdgeCases::test_rapid_conversation_switching PASSED                                                                                                                      [ 92%]
tests/test_persistence_comprehensive.py::TestConcurrency::test_concurrent_conversations_sqlite PASSED                                                                                                                 [ 93%]
tests/test_persistence_comprehensive.py::TestConcurrency::test_concurrent_conversations_postgresql PASSED                                                                                                             [ 95%]
tests/test_persistence_comprehensive.py::TestPostgreSQLSpecific::test_postgresql_wrapper_methods PASSED                                                                                                               [ 96%]
tests/test_persistence_comprehensive.py::TestPostgreSQLSpecific::test_supabase_compatibility PASSED                                                                                                                   [ 97%]
tests/test_persistence_comprehensive.py::TestMemoryPressure::test_many_conversations PASSED                                                                                                                           [ 98%]
tests/test_persistence_comprehensive.py::TestMemoryPressure::test_deep_conversation_chain PASSED                                                                                                                      [100%]

========================================================================================================== ERRORS ===========================================================================================================___________________________________________________________________ ERROR at setup of TestDbUrlParameterIntegration.test_multiple_simultaneous_databases ____________________________________________________________________file /mnt/e/cortexAI/cortex/tests/test_db_url_parameter.py, line 396
      @pytest.mark.integration
      def test_multiple_simultaneous_databases(self, mock_cohere_response):
E       fixture 'mock_cohere_response' not found
>       available fixtures: anyio_backend, anyio_backend_name, anyio_backend_options, cache, capfd, capfdbinary, caplog, capsys, capsysbinary, capteesys, client, client_memory, cov, doctest_namespace, free_tcp_port, free_tcp_port_factory, free_udp_port, free_udp_port_factory, mock_env, monkeypatch, no_cover, pytestconfig, record_property, record_testsuite_property, record_xml_attribute, recwarn, sample_response, temp_db_path, temp_sqlite_path, tmp_path, tmp_path_factory, tmpdir, tmpdir_factory
>       use 'pytest --fixtures [testpath]' for help on them.

/mnt/e/cortexAI/cortex/tests/test_db_url_parameter.py:396
_______________________________________________________________ ERROR at setup of TestDbUrlParameterIntegration.test_conversation_isolation_between_databases _______________________________________________________________file /mnt/e/cortexAI/cortex/tests/test_db_url_parameter.py, line 426
      @pytest.mark.integration
      def test_conversation_isolation_between_databases(self, postgres_url, mock_cohere_response):
E       fixture 'postgres_url' not found
>       available fixtures: anyio_backend, anyio_backend_name, anyio_backend_options, cache, capfd, capfdbinary, caplog, capsys, capsysbinary, capteesys, client, client_memory, cov, doctest_namespace, free_tcp_port, free_tcp_port_factory, free_udp_port, free_udp_port_factory, mock_env, monkeypatch, no_cover, pytestconfig, record_property, record_testsuite_property, record_xml_attribute, recwarn, sample_response, temp_db_path, temp_sqlite_path, tmp_path, tmp_path_factory, tmpdir, tmpdir_factory
>       use 'pytest --fixtures [testpath]' for help on them.

/mnt/e/cortexAI/cortex/tests/test_db_url_parameter.py:426
========================================================================================================= FAILURES ==========================================================================================================___________________________________________________________________________________ TestDbUrlParameter.test_default_sqlite_without_db_url ___________________________________________________________________________________
self = <test_db_url_parameter.TestDbUrlParameter object at 0x7fdd2329cc50>, client = <cortex.responses.api.ResponsesAPI object at 0x7fdd23004cb0>
mock_cohere_response = <MagicMock name='get_llm().invoke()' id='140587751858704'>

    def test_default_sqlite_without_db_url(self, client, mock_cohere_response):
        """Test that default SQLite works when no db_url is provided"""
        with patch('cortex.responses.llm.get_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = mock_cohere_response
            mock_get_llm.return_value = mock_llm

            # Create response without db_url
            response = client.create(
                input="Test message",
                model="cohere",
                store=True
            )

            assert response is not None
            assert response['id'] is not None
            assert response['status'] == 'completed'
>           assert response['output'][0]['content'][0]['text'] == "This is a test response from the AI"
E           AssertionError: assert 'Hello! This is indeed a test message, how exciting! I hope you are doing well and having a fantastic day today! 😊🌟' == 'This is a test response from the AI'
E
E             - This is a test response from the AI
E             + Hello! This is indeed a test message, how exciting! I hope you are doing well and having a fantastic day today! 😊🌟

tests/test_db_url_parameter.py:55: AssertionError
--------------------------------------------------------------------------------------------------- Captured stdout setup ---------------------------------------------------------------------------------------------------✅ Using SQLite for local persistence (conversations.db)
_______________________________________________________________________________________ TestAPIKeyHandling.test_missing_api_key_error _______________________________________________________________________________________
self = <test_edge_cases.TestAPIKeyHandling object at 0x7fdd2329f170>, client = <cortex.responses.api.ResponsesAPI object at 0x7fdd215e7890>, mock_env = <function mock_env.<locals>._mock_env at 0x7fdd23155300>

    @pytest.mark.requires_api_key
    def test_missing_api_key_error(self, client, mock_env):
        """Test helpful error when API key missing"""
        # Remove API key
        mock_env(CO_API_KEY=None)

        response = client.create(
            model="cohere",
            input="Test without API key"
        )

>       assert response.get("error") is not None
E       AssertionError: assert None is not None
E        +  where None = <built-in method get of dict object at 0x7fdd23299580>('error')
E        +    where <built-in method get of dict object at 0x7fdd23299580> = {'id': 'resp_6cb0ee300f29', 'object': 'response', 'created_at': 1755209671, 'status': 'completed', 'error': None, 'incomplete_details': None, 'instructions': None, 'max_output_tokens': None, 'model': 'cohere', 'output': [{'type': 'message', 'id': 'msg_195eaad194954bb58d5632f1', 'status': 'completed', 'role': 'assistant', 'content': [{'type': 'output_text', 'text': 'System error: status_code: None, body: The client must be instantiated be either passing in token or setting CO_API_KEY', 'annotations': []}]}], 'parallel_tool_calls': True, 'previous_response_id': None, 'reasoning': {'effort': None, 'summary': None}, 'store': True, 'temperature': 0.7, 'text': {'format': {'type': 'text'}}, 'tool_choice': 'auto', 'tools': [], 'top_p': 1.0, 'truncation': 'disabled', 'usage': {'input_tokens': 5, 'input_tokens_details': {'cached_tokens': 0}, 'output_tokens': 23, 'output_tokens_details': {'reasoning_tokens': 0}, 'total_tokens': 28}, 'user': None, 'metadata': {}}.get

tests/test_edge_cases.py:132: AssertionError
--------------------------------------------------------------------------------------------------- Captured stdout setup ---------------------------------------------------------------------------------------------------✅ Using SQLite for local persistence (conversations.db)
_____________________________________________________________________________________________ TestPersistence.test_memory_mode ______________________________________________________________________________________________
self = <test_edge_cases.TestPersistence object at 0x7fdd2329f710>

    def test_memory_mode(self):
        """Test memory mode (no persistence)"""
        # Create client with no DB
        client = Client(db_path=None)

        response = client.create(
            model="cohere",
            input="Memory mode test",
            store=True  # Even with store=True, won't persist
        )

        assert not response.get("error")

        # Create new client, try to continue
        client2 = Client(db_path=None)
        response2 = client2.create(
            model="cohere",
            input="Continue",
            previous_response_id=response["id"]
        )

        # Should fail - not persisted
>       assert response2.get("error") is not None
E       assert None is not None
E        +  where None = <built-in method get of dict object at 0x7fdd22fccf80>('error')
E        +    where <built-in method get of dict object at 0x7fdd22fccf80> = {'id': 'resp_6ba63a6f52c7', 'object': 'response', 'created_at': 1755209676, 'status': 'completed', 'error': None, 'incomplete_details': None, 'instructions': None, 'max_output_tokens': None, 'model': 'cohere', 'output': [{'type': 'message', 'id': 'msg_1fa67ff994404ff8b9727e29', 'status': 'completed', 'role': 'assistant', 'content': [{'type': 'output_text', 'text': "Great! Let's begin! In our last conversation, what color dress was Emma wearing?", 'annotations': []}]}], 'parallel_tool_calls': True, 'previous_response_id': 'resp_715a7e511e47', 'reasoning': {'effort': None, 'summary': None}, 'store': True, 'temperature': 0.7, 'text': {'format': {'type': 'text'}}, 'tool_choice': 'auto', 'tools': [], 'top_p': 1.0, 'truncation': 'disabled', 'usage': {'input_tokens': 1, 'input_tokens_details': {'cached_tokens': 0}, 'output_tokens': 16, 'output_tokens_details': {'reasoning_tokens': 0}, 'total_tokens': 17}, 'user': None, 'metadata': {}}.get

tests/test_edge_cases.py:202: AssertionError
--------------------------------------------------------------------------------------------------- Captured stdout call ----------------------------------------------------------------------------------------------------✅ Using SQLite for local persistence (conversations.db)
✅ Using SQLite for local persistence (conversations.db)
______________________________________________________________________________________ TestEdgeCases.test_invalid_previous_response_id ______________________________________________________________________________________
self = <test_persistence_comprehensive.TestEdgeCases object at 0x7fdd232b1b20>, client = <cortex.responses.api.ResponsesAPI object at 0x7fdd215de9c0>

    def test_invalid_previous_response_id(self, client):
        """Test handling of invalid previous_response_id"""
>       with pytest.raises(Exception) as exc_info:
E       Failed: DID NOT RAISE <class 'Exception'>

tests/test_persistence_comprehensive.py:335: Failed
--------------------------------------------------------------------------------------------------- Captured stdout setup ---------------------------------------------------------------------------------------------------✅ Using SQLite for local persistence (conversations.db)
===================================================================================================== warnings summary ======================================================================================================tests/test_core_functionality.py: 18 warnings
tests/test_db_url_parameter.py: 15 warnings
tests/test_edge_cases.py: 16 warnings
tests/test_openai_compatibility.py: 12 warnings
tests/test_persistence_comprehensive.py: 30 warnings
  /mnt/e/cortexAI/env/lib/python3.12/site-packages/langgraph/graph/state.py:911: LangGraphDeprecatedSinceV10: `config_type` is deprecated and will be removed. Please use `context_schema` instead. Deprecated in LangGraph V1.0 to be removed in V2.0.
    super().__init__(**kwargs)

tests/test_core_functionality.py: 17 warnings
tests/test_edge_cases.py: 12 warnings
tests/test_openai_compatibility.py: 12 warnings
  /mnt/e/cortexAI/cortex/tests/conftest.py:30: DeprecationWarning: db_path parameter is deprecated. Use db_url for PostgreSQL or leave empty for local SQLite.
    return Client(db_path=temp_db_path)

tests/test_edge_cases.py::TestPersistence::test_persistence_across_clients
  /mnt/e/cortexAI/cortex/tests/test_edge_cases.py:162: DeprecationWarning: db_path parameter is deprecated. Use db_url for PostgreSQL or leave empty for local SQLite.
    client1 = Client(db_path=temp_db_path)

tests/test_edge_cases.py::TestPersistence::test_persistence_across_clients
  /mnt/e/cortexAI/cortex/tests/test_edge_cases.py:171: DeprecationWarning: db_path parameter is deprecated. Use db_url for PostgreSQL or leave empty for local SQLite.
    client2 = Client(db_path=temp_db_path)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================================================================================================== short test summary info ==================================================================================================FAILED tests/test_db_url_parameter.py::TestDbUrlParameter::test_default_sqlite_without_db_url - AssertionError: assert 'Hello! This is indeed a test message, how exciting! I hope you are doing well and having a fantastic 
day today! 😊🌟' == 'This is a test response from the AI'

  - This is a test response from the AI
  + Hello! This is indeed a test message, how exciting! I hope you are doing well and having a fantastic day today! 😊🌟
FAILED tests/test_edge_cases.py::TestAPIKeyHandling::test_missing_api_key_error - AssertionError: assert None is not None
 +  where None = <built-in method get of dict object at 0x7fdd23299580>('error')
 +    where <built-in method get of dict object at 0x7fdd23299580> = {'id': 'resp_6cb0ee300f29', 'object': 'response', 'created_at': 1755209671, 'status': 'completed', 'error': None, 'incomplete_details': None, 'instructions': None, 'max_output_tokens': None, 'model': 'cohere', 'output': [{'type': 'message', 'id': 'msg_195eaad194954bb58d5632f1', 'status': 'completed', 'role': 'assistant', 'content': [{'type': 'output_text', 'text': 'System error: status_code: None, body: The client must be instantiated be either passing in token or setting CO_API_KEY', 'annotations': []}]}], 'parallel_tool_calls': True, 'previous_response_id': None, 'reasoning': {'effort': None, 'summary': None}, 'store': True, 'temperature': 0.7, 'text': {'format': {'type': 'text'}}, 'tool_choice': 'auto', 'tools': [], 'top_p': 1.0, 'truncation': 'disabled', 'usage': {'input_tokens': 5, 'input_tokens_details': {'cached_tokens': 0}, 'output_tokens': 23, 'output_tokens_details': {'reasoning_tokens': 0}, 'total_tokens': 28}, 'user': None, 'metadata': {}}.get
FAILED tests/test_edge_cases.py::TestPersistence::test_memory_mode - assert None is not None
 +  where None = <built-in method get of dict object at 0x7fdd22fccf80>('error')
 +    where <built-in method get of dict object at 0x7fdd22fccf80> = {'id': 'resp_6ba63a6f52c7', 'object': 'response', 'created_at': 1755209676, 'status': 'completed', 'error': None, 'incomplete_details': None, 'instructions': None, 'max_output_tokens': None, 'model': 'cohere', 'output': [{'type': 'message', 'id': 'msg_1fa67ff994404ff8b9727e29', 'status': 'completed', 'role': 'assistant', 'content': [{'type': 'output_text', 'text': "Great! Let's begin! In our last conversation, what color dress was Emma wearing?", 'annotations': []}]}], 'parallel_tool_calls': True, 'previous_response_id': 'resp_715a7e511e47', 'reasoning': {'effort': None, 'summary': None}, 'store': True, 'temperature': 0.7, 'text': {'format': {'type': 'text'}}, 'tool_choice': 'auto', 'tools': [], 'top_p': 1.0, 'truncation': 'disabled', 'usage': {'input_tokens': 1, 'input_tokens_details': {'cached_tokens': 0}, 'output_tokens': 16, 'output_tokens_details': {'reasoning_tokens': 0}, 'total_tokens': 17}, 'user': None, 'metadata': {}}.get
FAILED tests/test_persistence_comprehensive.py::TestEdgeCases::test_invalid_previous_response_id - Failed: DID NOT RAISE <class 'Exception'>
ERROR tests/test_db_url_parameter.py::TestDbUrlParameterIntegration::test_multiple_simultaneous_databases
ERROR tests/test_db_url_parameter.py::TestDbUrlParameterIntegration::test_conversation_isolation_between_databases
======================================================================== 4 failed, 69 passed, 5 skipped, 134 warnings, 2 errors in 712.44s (0:11:52) =================================================