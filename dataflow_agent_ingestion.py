import os
import pandas as pd
from datetime import datetime, timedelta
from rdflib import Graph, Namespace, Literal

# Configuration and Namespace Definition
GRID = Namespace("http://UKLVgrid.com/")
GRAPH_FILE = "dynamic_grid.ttl"

def prune_outdated_measurements(dkg, current_sim_time):
    # Calculate the retention threshold of 365 days prior to current ingestion time
    threshold_time = current_sim_time - timedelta(days=365)
    
    # Query the graph to identify all measurement timestamps
    query = """
        PREFIX grid: <http://mygrid.com/>
        SELECT ?meas ?time
        WHERE {
            ?meas grid:hasTime ?time .
        }
    """
    results = dkg.query(query)
    
    triples_removed = 0
    
    for row in results:
        meas_node = row.meas
        time_str = str(row.time)
        
        try:
            # Parse the stored string back into a datetime object for comparison
            node_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
            
            # Delete all facts associated with the node if it violates the retention policy
            if node_time < threshold_time:
                for s, p, o in dkg.triples((meas_node, None, None)):
                    dkg.remove((s, p, o))
                    triples_removed += 1
        except ValueError:
            # Skip entries with anomalous timestamp formatting
            continue
            
    if triples_removed > 0:
        print(f"Retention policy enforced: Erased {triples_removed} expired triplets.")
    
    return dkg

def process_incremental_readings(csv_file_path, target_date_str, target_hour):
    # Simulates the incremental ingestion of smart meter data for a specific hour
    print(f"Processing Incremental Data for {target_date_str} at {target_hour}:00...")
    
    # Load the active Knowledge Graph
    dkg = Graph()
    if os.path.exists(GRAPH_FILE):
        dkg.parse(GRAPH_FILE, format="turtle")
        dkg.bind("grid", GRID)
    else:
        print("Error: Topological graph not found. Execute topology extraction first.")
        return

    # Read the empirical smart meter dataset
    df = pd.read_csv(csv_file_path)
    df['TimeStamp'] = pd.to_datetime(df['TimeStamp'])
    
    # Filter data strictly for the specified operational windows
    valid_hours = list(range(10, 15)) + list(range(16, 21))
    if target_hour not in valid_hours:
        print(f"Hour {target_hour} is outside the defined critical operational windows. Skipping.")
        return
        
    # Isolate the data corresponding to the exact target date and hour
    target_datetime = datetime.strptime(f"{target_date_str} {target_hour}:00", "%Y-%m-%d %H:%M")
    hourly_data = df[(df['TimeStamp'].dt.date == target_datetime.date()) & (df['TimeStamp'].dt.hour == target_hour)]
    
    if hourly_data.empty:
        print(f"No consumer readings documented for this timestamp.")
        return
        
    # Enforce the one-year data retention policy before appending new data
    dkg = prune_outdated_measurements(dkg, target_datetime)
        
    # Synthesize RDF Triplets for the extracted subset
    new_triplets_count = 0
    for index, row in hourly_data.iterrows():
        consumer = str(row['Customer'])
        time_str = row['TimeStamp'].strftime("%Y-%m-%d %H:%M")
        
        # Generate a unique temporal identifier
        clean_time = time_str.replace(" ", "_").replace(":", "").replace("-", "")
        measurement_id = f"Meas_{consumer}_{clean_time}"
        meas_node = GRID[measurement_id]
        
        # Append parameters to the graph mapping
        dkg.add((meas_node, GRID.isMeasurementOf, GRID[consumer]))
        dkg.add((meas_node, GRID.hasTime, Literal(time_str)))
        dkg.add((meas_node, GRID.hasActivePower, Literal(float(row['P']))))
        dkg.add((meas_node, GRID.hasReactivePower, Literal(float(row['Q']))))
        dkg.add((meas_node, GRID.hasVoltage, Literal(float(row['V']))))
        
        new_triplets_count += 5

    # Commit updates to the persistent graph file
    dkg.serialize(destination=GRAPH_FILE, format="turtle")
    print(f"Ingestion successful. Appended {new_triplets_count} discrete facts.")

if __name__ == "__main__":
    readings_file = "readings.csv"
    
    # Example simulation trigger
    simulated_date = "2025-11-26"
    simulated_trigger_hours = [10, 11, 12, 13, 14, 16, 17, 18, 19, 20]
    
    for hour in simulated_trigger_hours:

        process_incremental_readings(readings_file, simulated_date, hour)
