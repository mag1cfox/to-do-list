#!/usr/bin/env python3
import sys
import os

def main():
    print("Basic TimeBlock Test")
    print("=" * 30)

    try:
        # Test backend imports
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        from backend.app import create_app
        from backend.models.time_block import TimeBlock, BlockType
        from backend.services.category_timeblock_matching import category_timeblock_matcher
        from backend.services.conflict_resolution import conflict_resolution_service

        print("SUCCESS: All imports working")

        # Test enum values
        types = [t.value for t in BlockType]
        expected = ['RESEARCH', 'GROWTH', 'REST', 'ENTERTAINMENT', 'REVIEW']

        if set(types) == set(expected):
            print("SUCCESS: BlockType enum correct")
        else:
            print("ERROR: BlockType enum incorrect")
            return

        # Test services
        if hasattr(category_timeblock_matcher, 'calculate_match_score'):
            print("SUCCESS: Matching service available")
        else:
            print("ERROR: Matching service missing")
            return

        if hasattr(conflict_resolution_service, 'detect_conflicts'):
            print("SUCCESS: Conflict service available")
        else:
            print("ERROR: Conflict service missing")
            return

        # Test app creation
        app = create_app()
        if app:
            print("SUCCESS: Flask app created")
        else:
            print("ERROR: Flask app creation failed")
            return

        print("=" * 30)
        print("All tests passed!")
        print("TimeBlock module is ready!")
        print("=" * 30)

    except Exception as e:
        print(f"ERROR: {e}")
        return

if __name__ == "__main__":
    main()