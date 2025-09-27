"""
Diff display utilities for console output with git-like coloring
"""

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    
    # Background colors
    RED_BG = '\033[41m'
    GREEN_BG = '\033[42m'

def apply_user_modifications_to_content(generated_content: str, modifications: list) -> str:
    """
    Apply user modifications to generated content and return colored diff string
    """
    if not modifications:
        return generated_content
    
    # Apply modifications in reverse order (by position) to avoid position shifts
    result = generated_content
    colored_segments = []
    
    # Sort modifications by position (reverse order for safe application)
    sorted_mods = sorted(modifications, key=lambda x: x['position_in_generated'], reverse=True)
    
    last_pos = len(generated_content)
    
    for mod in sorted_mods:
        pos = mod['position_in_generated']
        length = mod['length']
        operation = mod['operation']
        remove_text = mod['remove']
        insert_text = mod['insert']
        
        # Add unchanged content after this modification
        if last_pos > pos + length:
            colored_segments.insert(0, result[pos + length:last_pos])
        
        # Add the modification with coloring
        if operation == 'insert':
            # Green for inserted text
            colored_segments.insert(0, f"{Colors.GREEN}+{insert_text}{Colors.RESET}")
        elif operation == 'delete':
            # Red for deleted text  
            colored_segments.insert(0, f"{Colors.RED}-{remove_text}{Colors.RESET}")
        elif operation == 'replace':
            # Red for removed, green for added
            colored_segments.insert(0, f"{Colors.RED}-{remove_text}{Colors.RESET}{Colors.GREEN}+{insert_text}{Colors.RESET}")
        
        last_pos = pos
    
    # Add any remaining content at the beginning
    if last_pos > 0:
        colored_segments.insert(0, result[0:last_pos])
    
    return ''.join(colored_segments)

def display_modification_diff(original_content: dict, user_modifications: list, generated_content: str) -> None:
    """
    Display a git-like diff for a single modification group
    """
    print(f"\n{Colors.BOLD}{Colors.CYAN}Original content{Colors.RESET}")
    print("-" * 50)
    print(f"{Colors.YELLOW}{original_content['content']}{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}Transformed Content{Colors.RESET}")
    print("-" * 50)
    
    # Find the section of generated content that corresponds to this placeholder
    # We'll show some context around the modifications
    if not user_modifications:
        print("No modifications found")
        return
    
    # Get the range of positions affected by modifications
    min_pos = min(mod['position_in_generated'] for mod in user_modifications)
    max_pos = max(mod['position_in_generated'] + mod['length'] for mod in user_modifications)
    
    # Add some context (100 chars before and after)
    context_start = max(0, min_pos - 100)
    context_end = min(len(generated_content), max_pos + 100)
    
    # Extract the relevant section
    section = generated_content[context_start:context_end]
    
    # Adjust modification positions relative to the section
    adjusted_modifications = []
    for mod in user_modifications:
        adjusted_mod = mod.copy()
        adjusted_mod['position_in_generated'] = mod['position_in_generated'] - context_start
        adjusted_modifications.append(adjusted_mod)
    
    # Apply coloring to show modifications
    colored_section = apply_user_modifications_to_content(section, adjusted_modifications)
    
    # Show context indicators if we're not showing the full content
    if context_start > 0:
        print(f"{Colors.BLUE}... (content before) ...{Colors.RESET}")
    
    print(colored_section)
    
    if context_end < len(generated_content):
        print(f"{Colors.BLUE}... (content after) ...{Colors.RESET}")

def display_all_modifications(modifications: list, generated_content: str) -> None:
    """
    Display all modifications with git-like diff formatting
    """    
    for i, mod_group in enumerate(modifications, 1):
        print(f"\n{Colors.BOLD}{Colors.WHITE}[{i}] Placeholder: {mod_group['original_content']['content']}{Colors.RESET}")
        
        # Display the actual diff
        display_modification_diff(
            mod_group['original_content'],
            mod_group['user_modifications'],
            generated_content
        )

def display_summary_stats(report: dict) -> None:
    """
    Display summary statistics
    """
    print(f"\n{Colors.BOLD}{Colors.CYAN}=== SUMMARY ==={Colors.RESET}")
    print(f"📊 Modified placeholders: {Colors.BOLD}{report['total_modifications']}{Colors.RESET}")
    
    total_operations = sum(len(mod['user_modifications']) for mod in report['modifications'])
    print(f"🔧 Total operations: {Colors.BOLD}{total_operations}{Colors.RESET}")
    
    operation_counts = {}
    for mod in report['modifications']:
        for op in mod['user_modifications']:
            op_type = op['operation']
            operation_counts[op_type] = operation_counts.get(op_type, 0) + 1
    
    print(f"📈 Operation breakdown:")
    for op_type, count in operation_counts.items():
        color = Colors.GREEN if op_type == 'insert' else Colors.RED if op_type == 'delete' else Colors.YELLOW
        print(f"   {color}{op_type}: {count}{Colors.RESET}")
