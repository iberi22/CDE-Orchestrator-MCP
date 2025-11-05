#!/usr/bin/env python3
"""
Basic integration test for the Rust core module.
Tests that the high-performance functions are available and working.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def test_rust_core_import():
    """Test that the Rust core module can be imported."""
    try:
        import cde_rust_core
        print("✅ Rust core module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Rust core module: {e}")
        return False

def test_documentation_functions():
    """Test that documentation functions are available."""
    try:
        import cde_rust_core

        # Check if documentation submodule exists
        if hasattr(cde_rust_core, 'documentation'):
            print("✅ Documentation submodule available")

            # Check if functions exist
            doc_module = cde_rust_core.documentation
            if hasattr(doc_module, 'scan_documentation_fast'):
                print("✅ scan_documentation_fast function available")
            else:
                print("❌ scan_documentation_fast function missing")
                return False

            if hasattr(doc_module, 'analyze_documentation_fast'):
                print("✅ analyze_documentation_fast function available")
            else:
                print("❌ analyze_documentation_fast function missing")
                return False

            return True
        else:
            print("❌ Documentation submodule not available")
            return False

    except Exception as e:
        print(f"❌ Error testing documentation functions: {e}")
        return False

def test_filesystem_functions():
    """Test that filesystem functions are available."""
    try:
        import cde_rust_core

        if hasattr(cde_rust_core, 'filesystem'):
            print("✅ Filesystem submodule available")

            fs_module = cde_rust_core.filesystem
            if hasattr(fs_module, 'find_files_fast'):
                print("✅ find_files_fast function available")
                return True
            else:
                print("❌ find_files_fast function missing")
                return False
        else:
            print("❌ Filesystem submodule not available")
            return False

    except Exception as e:
        print(f"❌ Error testing filesystem functions: {e}")
        return False

def test_text_functions():
    """Test that text processing functions are available."""
    try:
        import cde_rust_core

        if hasattr(cde_rust_core, 'text'):
            print("✅ Text submodule available")

            text_module = cde_rust_core.text
            functions_to_check = [
                'extract_metadata_fast',
                'analyze_text_fast'
            ]

            for func_name in functions_to_check:
                if hasattr(text_module, func_name):
                    print(f"✅ {func_name} function available")
                else:
                    print(f"❌ {func_name} function missing")
                    return False

            return True
        else:
            print("❌ Text submodule not available")
            return False

    except Exception as e:
        print(f"❌ Error testing text functions: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality of one function."""
    try:
        import cde_rust_core
        import json

        # Test extract_metadata_fast with empty content
        result = cde_rust_core.text.extract_metadata_fast("")
        parsed = json.loads(result)

        if isinstance(parsed, dict):
            print("✅ extract_metadata_fast returns valid JSON")
            return True
        else:
            print(f"❌ extract_metadata_fast returned invalid result: {result}")
            return False

    except Exception as e:
        print(f"❌ Error testing basic functionality: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing CDE Rust Core Integration")
    print("=" * 40)

    tests = [
        test_rust_core_import,
        test_documentation_functions,
        test_filesystem_functions,
        test_text_functions,
        test_basic_functionality,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        print(f"\n🔍 Running {test.__name__}...")
        if test():
            passed += 1
        print()

    print("=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Rust core is ready for use.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())