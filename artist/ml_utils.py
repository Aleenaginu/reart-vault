from collections import defaultdict
import random

# Simple keyword-based recommendation system
art_projects = {
    'Plastic Bottle Planter': ['plastic', 'bottle', 'container'],
    'Paper Mache Art': ['paper', 'newspaper', 'cardboard'],
    'Fabric Collage': ['fabric', 'cloth', 'textile'],
    'Glass Mosaic': ['glass', 'bottle', 'mirror'],
    'Metal Sculpture': ['metal', 'wire', 'can'],
    'Wood Craft': ['wood', 'stick', 'bamboo'],
    'Mixed Media Art': ['mixed', 'various', 'multiple'],
}

# Create reverse mapping of materials to projects
material_to_projects = defaultdict(list)
for project, materials in art_projects.items():
    for material in materials:
        material_to_projects[material.lower()].append(project)

def get_art_project_recommendations(waste_material, top_k=3):
    """
    Get art project recommendations based on waste materials.
    
    Args:
        waste_material (str): Input waste material description
        top_k (int): Number of recommendations to return
        
    Returns:
        list: List of recommended art projects
    """
    # Convert input to lowercase and split into words
    materials = set(word.lower() for word in waste_material.split())
    
    # Collect all matching projects
    matching_projects = []
    for material in materials:
        matching_projects.extend(material_to_projects[material])
    
    # If no matches found, return random suggestions
    if not matching_projects:
        return random.sample(list(art_projects.keys()), min(top_k, len(art_projects)))
    
    # Count project occurrences and sort by frequency
    project_counts = defaultdict(int)
    for project in matching_projects:
        project_counts[project] += 1
    
    # Sort projects by count (descending) and alphabetically for ties
    sorted_projects = sorted(
        project_counts.items(),
        key=lambda x: (-x[1], x[0])
    )
    
    # Return top k projects
    return [project for project, _ in sorted_projects[:top_k]]
