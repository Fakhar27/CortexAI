"""
AWS Lambda handler for Django + Cortex integration
Handles both API Gateway events and direct Lambda invocations
"""

import json
import os
import sys
import traceback
from pathlib import Path

# Add paths for Lambda environment
sys.path.insert(0, '/opt/python')  # Lambda layer path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_django():
    """Initialize Django settings for Lambda"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
    
    try:
        import django
        django.setup()
    except ImportError:
        # Django not needed for standalone cortex
        pass

def lambda_handler(event, context):
    """
    Main Lambda handler that routes requests
    
    Supports:
    1. API Gateway HTTP events -> Django
    2. Direct Lambda invocations -> Cortex tests
    3. EventBridge scheduled events -> Maintenance tasks
    """
    
    # Detect event type
    if 'httpMethod' in event or 'requestContext' in event:
        # API Gateway event - route to Django
        return handle_django_request(event, context)
    elif 'test_type' in event and event['test_type'] == 'cortex_pooler':
        # Direct Cortex pooler test
        return handle_cortex_test(event, context)
    elif 'source' in event and event['source'] == 'aws.events':
        # EventBridge scheduled event
        return handle_scheduled_task(event, context)
    else:
        # Default to Cortex test for backwards compatibility
        return handle_cortex_test(event, context)

def handle_django_request(event, context):
    """Handle Django/API Gateway requests"""
    try:
        setup_django()
        from mangum import Mangum
        from myproject.asgi import application
        
        # Mangum adapter for ASGI
        handler = Mangum(application, lifespan="off")
        return handler(event, context)
        
    except ImportError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Django dependencies not installed',
                'details': str(e),
                'hint': 'Ensure Django and Mangum are in requirements-lambda.txt'
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Django request failed',
                'details': str(e),
                'traceback': traceback.format_exc()
            })
        }

def handle_cortex_test(event, context):
    """Handle Cortex pooler tests"""
    try:
        from cortex import Client
        
        # Get test configuration
        db_url = event.get('db_url')
        if not db_url:
            # Try environment variable
            db_url = os.environ.get('DATABASE_URL')
            if not db_url:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'error': 'db_url required',
                        'hint': 'Pass db_url in event or set DATABASE_URL environment variable'
                    })
                }
        
        # Initialize client
        client = Client(db_url=db_url)
        
        # Run simple test
        test_results = []
        
        # Test 1: Create initial response
        try:
            response1 = client.create(
                model=event.get('model', 'gpt-4o-mini'),
                input=event.get('input', 'Hello, remember my name is Lambda Test'),
                store=True,
                temperature=0.5
            )
            
            test_results.append({
                'test': 'initial_response',
                'success': True,
                'response_id': response1.get('id'),
                'output': str(response1.get('output', []))[:500]  # Truncate for logs
            })
            
            # Test 2: Memory check (if previous response exists)
            if response1.get('id'):
                response2 = client.create(
                    model='gemini-1.5-flash',
                    input='What is my name?',
                    previous_response_id=response1['id'],
                    store=True,
                    temperature=0.5
                )
                
                output_text = str(response2.get('output', []))
                remembers = 'Lambda Test' in output_text or 'lambda test' in output_text.lower()
                
                test_results.append({
                    'test': 'memory_check',
                    'success': remembers,
                    'response_id': response2.get('id'),
                    'remembers_name': remembers,
                    'output': output_text[:500]
                })
                
        except Exception as e:
            test_results.append({
                'test': 'cortex_operation',
                'success': False,
                'error': str(e)
            })
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': all(t.get('success', False) for t in test_results),
                'test_results': test_results,
                'environment': {
                    'python_version': sys.version,
                    'lambda_root': os.environ.get('LAMBDA_TASK_ROOT', 'not_in_lambda'),
                    'has_django': 'django' in sys.modules,
                    'has_cortex': 'cortex' in sys.modules,
                    'has_langgraph': 'langgraph' in sys.modules
                }
            }, default=str)
        }
        
    except ImportError as e:
        missing_module = str(e).split("'")[1] if "'" in str(e) else 'unknown'
        
        # Specific error messages for common issues
        error_hints = {
            'langgraph': 'Install: pip install langgraph langgraph-checkpoint langgraph-checkpoint-postgres',
            'cortex': 'Ensure cortex package is included in Lambda deployment',
            'psycopg': 'Install: pip install psycopg[binary] psycopg2-binary',
            'langchain': 'Install: pip install langchain-core langchain-community'
        }
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Module not found: {missing_module}',
                'hint': error_hints.get(missing_module, f'Add {missing_module} to requirements-lambda.txt'),
                'full_error': str(e),
                'sys_path': sys.path,
                'pip_packages': get_installed_packages()
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Cortex test failed',
                'details': str(e),
                'traceback': traceback.format_exc()
            })
        }

def handle_scheduled_task(event, context):
    """Handle scheduled maintenance tasks"""
    task_name = event.get('detail', {}).get('task_name', 'unknown')
    
    try:
        if task_name == 'cleanup_old_checkpoints':
            # Cleanup old checkpoints
            from cortex.responses.persistence import cleanup_old_checkpoints
            result = cleanup_old_checkpoints(days_old=30)
            return {
                'statusCode': 200,
                'body': json.dumps({'task': task_name, 'result': result})
            }
        else:
            return {
                'statusCode': 200,
                'body': json.dumps({'task': task_name, 'status': 'no action'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'task': task_name,
                'error': str(e)
            })
        }

def get_installed_packages():
    """Get list of installed packages for debugging"""
    try:
        import pkg_resources
        return [f"{pkg.key}=={pkg.version}" for pkg in pkg_resources.working_set]
    except:
        return []

# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        'test_type': 'cortex_pooler',
        'db_url': os.environ.get('DATABASE_URL', ''),
        'model': 'gpt-4o-mini',
        'input': 'Hello from local test'
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))