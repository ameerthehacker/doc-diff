import json
import difflib
from typing import List, Dict, Optional
from diff_display import display_all_modifications


class SimpleDiffer:
    """Simple document differ following the 5-step approach"""
    
    def __init__(self, source_file: str, sourcemap_file: str, generated_file: str, user_modified_file: str):
        self.source_content = self._read_file(source_file)
        self.generated_content = self._read_file(generated_file)
        self.user_modified_content = self._read_file(user_modified_file)
        self.source_map = self._load_source_map(sourcemap_file)
        
    def _read_file(self, file_path: str) -> str:
        """Read file content"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _load_source_map(self, sourcemap_file: str) -> List[Dict]:
        """Load and parse source map"""
        with open(sourcemap_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('mappings', [])
    
    def _find_user_changes(self) -> List[Dict]:
        """Step 1-3: Compare user-modified and generated docs to identify user changes"""
        matcher = difflib.SequenceMatcher(None, self.generated_content, self.user_modified_content)
        changes = []
        
        for tag, gen_start, gen_end, user_start, user_end in matcher.get_opcodes():
            if tag != 'equal':
                change = {
                    'type': tag,
                    'gen_start': gen_start,
                    'gen_end': gen_end,
                    'user_start': user_start,
                    'user_end': user_end,
                    'removed_text': self.generated_content[gen_start:gen_end],
                    'added_text': self.user_modified_content[user_start:user_end]
                }
                changes.append(change)
        
        return changes
    
    def _find_source_mapping_for_position(self, pos: int) -> Optional[Dict]:
        """Step 4: Check if position falls within a source-mapped region"""
        for mapping in self.source_map:
            if mapping['transformed_start'] <= pos < mapping['transformed_end']:
                return mapping
        return None
    
    def _get_operation_description(self, operation: str, removed: str, added: str) -> str:
        """Generate human-readable description of the operation"""
        if operation == 'insert':
            return f"Insert '{added[:50]}{'...' if len(added) > 50 else ''}'"
        elif operation == 'delete':
            return f"Delete '{removed[:50]}{'...' if len(removed) > 50 else ''}'"
        elif operation == 'replace':
            return f"Replace '{removed[:30]}{'...' if len(removed) > 30 else ''}' with '{added[:30]}{'...' if len(added) > 30 else ''}'"
        return operation
    
    def generate_simple_diff_report(self) -> Dict:
        """Step 5: Generate simplified JSON with original content and user modifications"""
        user_changes = self._find_user_changes()
        results = []
        
        # Group changes by source mapping
        mapping_groups = {}
        
        for change in user_changes:
            # Check if this change is within a source-mapped region
            mapping = self._find_source_mapping_for_position(change['gen_start'])
            
            if mapping:
                # This change is within a replaced placeholder
                mapping_key = f"{mapping['original_start']}_{mapping['original_end']}"
                
                if mapping_key not in mapping_groups:
                    mapping_groups[mapping_key] = {
                        'original_content': {
                            'start': mapping['original_start'],
                            'end': mapping['original_end'],
                            'content': self.source_content[mapping['original_start']:mapping['original_end']]
                        },
                        'user_modifications': []
                    }
                
                # Add user modification with position info for applying the diff
                modification = {
                    'operation': change['type'],
                    'position_in_generated': change['gen_start'],
                    'length': change['gen_end'] - change['gen_start'],
                    'remove': change['removed_text'],
                    'insert': change['added_text'],
                    'description': self._get_operation_description(change['type'], change['removed_text'], change['added_text'])
                }
                mapping_groups[mapping_key]['user_modifications'].append(modification)
        
        # Convert to list and sort modifications within each group by position (reverse order)
        for group in mapping_groups.values():
            # Sort modifications in reverse order of position for safe application
            group['user_modifications'].sort(key=lambda x: x['position_in_generated'], reverse=True)
            results.append(group)
        
        return {
            'total_modifications': len(results),
            'modifications': results
        }

def main():
    # Hardcoded file paths
    source_file = 'playground/template.md'
    sourcemap_file = 'out/generated-doc.map'
    generated_file = 'out/generated-doc.md'
    user_modified_file = 'out/generated-doc-user-modified.md'
    output_file = 'out/diff-report.json'
    
    try:
        # Create simple differ and generate report
        differ = SimpleDiffer(
            source_file,
            sourcemap_file,
            generated_file,
            user_modified_file
        )
        
        report = differ.generate_simple_diff_report()
        
        # Save report to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Display git-like diff in console
        display_all_modifications(report['modifications'], differ.generated_content)
        
        print(f"\n📁 Full diff report saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
