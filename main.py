import re
import json
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict

@dataclass
class SourceMapEntry:
    """Represents a mapping between original and transformed positions"""
    original_start: int
    original_end: int
    transformed_start: int
    transformed_end: int

class TemplateHydrator:
    """Template hydration system with source mapping"""
    
    def __init__(self):
        self.source_map: List[SourceMapEntry] = []
        self.transformed_content = ""
        self.original_content = ""
        
        # Data pipeline content replacements
        self.replacements = {
            "[OVERVIEW]()": """This document outlines our comprehensive data pipeline architecture designed to handle large-scale data processing and transformation workflows. Our pipeline supports real-time and batch processing capabilities, ensuring data quality, reliability, and scalability across multiple data sources and destinations.

The pipeline incorporates modern technologies including Apache Kafka for streaming, Apache Spark for distributed processing, and various storage solutions optimized for different data access patterns.""",
            
            "[TRANSFORMATION]()": """## Extract Phase
1. **Data Ingestion**: Collect data from multiple sources including APIs, databases, and file systems
2. **Data Validation**: Perform initial schema validation and data quality checks
3. **Data Staging**: Store raw data in staging area for processing

## Transform Phase
1. **Data Cleaning**: Remove duplicates, handle missing values, and standardize formats
2. **Data Enrichment**: Join with reference data and calculate derived metrics
3. **Data Aggregation**: Perform grouping and statistical calculations as needed
4. **Schema Transformation**: Convert data to target schema format

## Load Phase
1. **Data Partitioning**: Organize data for optimal query performance
2. **Data Loading**: Write processed data to target systems (data warehouse, data lake)
3. **Index Creation**: Create necessary indexes for query optimization
4. **Data Validation**: Perform final quality checks and data integrity validation"""
        }
    
    def hydrate_template(self, template_content: str) -> str:
        """
        Hydrate template with replacements and build source map
        """
        self.original_content = template_content
        self.transformed_content = template_content
        self.source_map = []
        
        # Track current position offset due to replacements
        offset = 0
        
        # Find and replace each placeholder
        for placeholder, replacement in self.replacements.items():
            # Find all occurrences of the placeholder
            start_pos = 0
            while True:
                match_pos = self.transformed_content.find(placeholder, start_pos)
                if match_pos == -1:
                    break
                
                # Calculate original position (before any transformations)
                original_start = match_pos - offset
                original_end = original_start + len(placeholder)
                
                # Perform replacement
                self.transformed_content = (
                    self.transformed_content[:match_pos] + 
                    replacement + 
                    self.transformed_content[match_pos + len(placeholder):]
                )
                
                # Calculate transformed positions
                transformed_start = match_pos
                transformed_end = match_pos + len(replacement)
                
                # Add to source map
                entry = SourceMapEntry(
                    original_start=original_start,
                    original_end=original_end,
                    transformed_start=transformed_start,
                    transformed_end=transformed_end
                )
                self.source_map.append(entry)
                
                # Update offset for next replacements
                offset += len(replacement) - len(placeholder)
                
                # Move start position for next search
                start_pos = match_pos + len(replacement)
        
        return self.transformed_content
    
    def get_original_position(self, transformed_pos: int) -> Tuple[int, str]:
        """
        Given a position in the transformed document, return the corresponding
        position in the original document and the type of content
        """
        for entry in self.source_map:
            if entry.transformed_start <= transformed_pos < entry.transformed_end:
                # Position is within a replacement
                relative_pos = transformed_pos - entry.transformed_start
                # Map to start of original placeholder (simplified mapping)
                return entry.original_start, "replacement"
        
        # Position is not in a replacement, calculate original position
        # by accounting for all replacements that came before this position
        original_pos = transformed_pos
        for entry in self.source_map:
            if entry.transformed_start < transformed_pos:
                # Adjustment: subtract the length difference of replacement
                transformed_length = entry.transformed_end - entry.transformed_start
                original_length = entry.original_end - entry.original_start
                length_diff = transformed_length - original_length
                original_pos -= length_diff
        
        return original_pos, "original"

    def save_source_map(self, file_path: str):
        """Save the source map to a JSON file"""
        source_map_data = {
            "version": 1,
            "mappings": [asdict(entry) for entry in self.source_map],
        }
        
        with open(file_path, 'w') as f:
            json.dump(source_map_data, f, indent=2)
        
        print(f"Source map saved to: {file_path}")

def main():
    # Read template file
    with open('playground/template.md', 'r') as f:
        template_content = f.read()
    
    # Create hydrator and process template
    hydrator = TemplateHydrator()
    transformed_content = hydrator.hydrate_template(template_content)
    
    # Save transformed content
    with open('out/generated-doc.md', 'w') as f:
        f.write(transformed_content)
    
    # Save source map
    hydrator.save_source_map('out/generated-doc.map')
    
    print(f"Transformed content saved to: out/generated-doc.md")

if __name__ == "__main__":
    main()