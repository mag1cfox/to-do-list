#!/usr/bin/env python3
import sys
import os

def main():
    print("Import Test for TimeBlock Module")
    print("=" * 40)

    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

        # Test core imports
        from backend.models.time_block import TimeBlock, BlockType
        print("SUCCESS: TimeBlock model imported")

        from backend.models.time_block_template import TimeBlockTemplate
        print("SUCCESS: TimeBlockTemplate model imported")

        from backend.services.category_timeblock_matching import category_timeblock_matcher
        print("SUCCESS: Matching service imported")

        from backend.services.conflict_resolution import conflict_resolution_service
        print("SUCCESS: Conflict service imported")

        from backend.routes.time_block_routes import bp as time_block_bp
        print("SUCCESS: TimeBlock routes imported")

        # Test enum
        types = [t.value for t in BlockType]
        expected = ['RESEARCH', 'GROWTH', 'REST', 'ENTERTAINMENT', 'REVIEW']

        if set(types) == set(expected):
            print("SUCCESS: BlockType enum correct")
        else:
            print(f"ERROR: BlockType enum incorrect: {types}")
            return

        # Test service methods exist
        if hasattr(category_timeblock_matcher, 'calculate_match_score'):
            print("SUCCESS: Matching service has calculate_match_score")
        else:
            print("ERROR: Matching service missing calculate_match_score")
            return

        if hasattr(conflict_resolution_service, 'detect_conflicts'):
            print("SUCCESS: Conflict service has detect_conflicts")
        else:
            print("ERROR: Conflict service missing detect_conflicts")
            return

        print("=" * 40)
        print("All imports and basic functionality tests passed!")
        print("TimeBlock module is ready for use.")
        print("=" * 40)

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()