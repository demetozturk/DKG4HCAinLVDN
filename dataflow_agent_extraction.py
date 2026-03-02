import ast
import google.generativeai as genai
from rdflib import Graph, Namespace

# Configuration and Namespace Definition
GRID = Namespace("http://mygrid.com/")
GRAPH_FILE = "dynamic_grid.ttl"

def update_topology_from_text(api_key, text_file_path):
    # Initiating Topological Extraction
    print("Initiating Topological Extraction...")
    
    # Initialize the LLM
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-XXXX') #update based on your selected model
    
    # Read the textual topology description
    with open(text_file_path, 'r') as file:
        topology_text = file.read()
        
    # Formulate the extraction prompt
    prompt = f"""
    You are a Knowledge Graph extraction agent. 
    Analyze the text and extract relationships in the format: (Subject, Predicate, Object).
    Rules:
    1. Identify consumers (e.g., H1) and assets (e.g., EV, PV).
    2. Extract the relationship verb (e.g., 'owns', 'has').
    3. If a count is given (e.g., "2 EVs"), create unique IDs (H1_EV_1, H1_EV_2).
    4. Return ONLY a Python list of tuples.
    Text: {topology_text}
    """
    
    # Generate and parse the response
    response = model.generate_content(prompt)
    clean_text = response.text.replace("```python", "").replace("```", "").strip()
    
    try:
        extracted_relations = ast.literal_eval(clean_text)
    except Exception as e:
        print(f"Parsing error: {e}")
        return
        
    # Construct the foundational RDF Graph
    base_graph = Graph()
    base_graph.bind("grid", GRID)
    
    for subject, predicate, obj in extracted_relations:
        s_node = GRID[str(subject).replace(" ", "_")]
        p_node = GRID[str(predicate).replace(" ", "_")]
        o_node = GRID[str(obj).replace(" ", "_")]
        base_graph.add((s_node, p_node, o_node))
        
    # Save the static topology
    base_graph.serialize(destination=GRAPH_FILE, format="turtle")
    print(f"Topological extraction complete. Static graph saved to {GRAPH_FILE}.")

if __name__ == "__main__":
    api_key = "YOUR_GEMINI_API_KEY"
    topology_file = "topology_input.txt"

    update_topology_from_text(api_key, topology_file)
