import os
import pandas as pd
from rdflib import Graph, Namespace, Literal

# Semantic Namespace Definition
GRID = Namespace("http://UKLVgrid.com/")
GRAPH_FILE = "dynamic_grid.ttl"
OPENDSS_RESULT_FILE = "opendss_example_results.csv"

# Operational Thresholds
V_MIN = 216.2
V_MAX = 253.0

def update_graph_with_simulation_results(target_time):
    # Initialize and load the Knowledge Graph
    dkg = Graph()
    if os.path.exists(GRAPH_FILE):
        dkg.parse(GRAPH_FILE, format="turtle")
        dkg.bind("grid", GRID)
    else:
        print("Error: Knowledge Graph not found.")
        return

    # Read the manual OpenDSS results
    if not os.path.exists(OPENDSS_RESULT_FILE):
        print(f"Error: Simulation results file {OPENDSS_RESULT_FILE} not found.")
        return
        
    results_df = pd.read_csv(OPENDSS_RESULT_FILE)
    
    for index, row in results_df.iterrows():
        consumer = str(row['Consumer'])
        voltage = float(row['Simulated_Voltage'])
        consumer_node = GRID[consumer]
        
        # Step 1: Identify and purge preceding analysis nodes for this specific consumer
        query_obsolete = f"""
            PREFIX grid: <http://UKLVgrid.com/>
            SELECT ?analysis
            WHERE {{
                ?analysis grid:analyzes grid:{consumer} .
            }}
        """
        obsolete_nodes = dkg.query(query_obsolete)
        
        for obs_row in obsolete_nodes:
            old_node = obs_row.analysis
            # Erase all semantic triplets where the obsolete node acts as the subject
            for s, p, o in list(dkg.triples((old_node, None, None))):
                dkg.remove((s, p, o))
                
        # Step 2: Determine updated operational status
        if voltage < V_MIN:
            status = "Violation"
            reason = "UnderVoltage"
        elif voltage > V_MAX:
            status = "Violation"
            reason = "OverVoltage"
        else:
            status = "Safe"
            reason = "None"
            
        # Step 3: Synthesize and append the current analytical state
        clean_time = target_time.replace(" ", "_").replace("/", "").replace(":", "").replace("-", "")
        new_analysis_id = f"Analysis_{consumer}_{clean_time}"
        new_node = GRID[new_analysis_id]
        
        dkg.add((new_node, GRID.analyzes, consumer_node))
        dkg.add((new_node, GRID.hasStatus, Literal(status)))
        
        if status == "Violation":
            dkg.add((new_node, GRID.limitedBy, Literal(reason)))
            dkg.add((new_node, GRID.violationValue, Literal(voltage)))

    # Persist the structural updates to the foundational database
    dkg.serialize(destination=GRAPH_FILE, format="turtle")

    print(f"Knowledge Graph updated. Obsolete states deleted and new OpenDSS outcomes applied for {target_time}.")

