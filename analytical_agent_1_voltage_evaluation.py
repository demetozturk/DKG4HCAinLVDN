import os
from rdflib import Graph, Namespace

# Semantic Namespace Definition
GRID = Namespace("http://mygrid.com/")
GRAPH_FILE = "dynamic_grid.ttl"

# Operational Thresholds
V_MIN = 216.2
V_MAX = 253.0

def evaluate_baseline_voltages(target_time):
    # Initialize and load the Knowledge Graph
    dkg = Graph()
    if os.path.exists(GRAPH_FILE):
        dkg.parse(GRAPH_FILE, format="turtle")
        dkg.bind("grid", GRID)
    else:
        print("Error: Knowledge Graph not found.")
        return

    # Formulate SPARQL query to extract consumer voltages
    query = f"""
        PREFIX grid: <http://mygrid.com/>
        SELECT ?consumer ?v
        WHERE {{
            ?meas grid:hasTime "{target_time}" .
            ?meas grid:isMeasurementOf ?consumer .
            ?meas grid:hasVoltage ?v .
        }}
    """
    
    results = dkg.query(query)
    
    print(f"Baseline Voltage Evaluation for {target_time}:")
    for row in results:
        consumer_id = str(row.consumer).split("/")[-1]
        voltage_magnitude = float(row.v)
        
        if voltage_magnitude < V_MIN:
            print(f"Alert: Consumer {consumer_id} exhibits undervoltage ({voltage_magnitude}V).")
        elif voltage_magnitude > V_MAX:
            print(f"Alert: Consumer {consumer_id} exhibits overvoltage ({voltage_magnitude}V).")
        else:
            print(f"Status Normal: Consumer {consumer_id} operates within limits ({voltage_magnitude}V).")