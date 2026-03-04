# DKN4HCAinLVDN
# Dynamic Knowledge Graph Framework for Hosting Capacity Analysis in LV Networks 

This repository contains the codebase and foundational data structures for the methodology proposed in the manuscript "Dynamic Knowledge Graph Framework for Hosting Capacity Analysis in LV Networks with Low-Carbon Technologies" by Demet Ozturk, Nuh Erdogan, Reza Vatankhah Barenji.

The framework employs a multi-agent system to dynamically construct a Resource Description Framework (RDF) Knowledge Graph from unstructured topological descriptions and empirical smart meter data. This semantic structure subsequently drives OpenDSS simulations to assess hosting capacity and identify grid violations associated with the integration of low-carbon technologies by the consumer.

#### Scripts provide a general framework implementation, which should be updated based on your specific network configuration, power system features, and PFA output.

## Prerequisites and Initial Setup
Prior to executing the analytical scripts, the following foundational files and credentials must be established within the primary repository directory.

### 1. Grid Topology Description
A plain text file (e.g., topology_input.txt) containing the unstructured linguistic description of the low-voltage feeder topology. The extraction module will parse this text to map consumer assets.

Example format:

In this feeder there are 5 households. H means Households. EV = electrical vehicle. PV, HP, ESS...
H1 has 2 EVs and PV.
H2 has EV and HP.
H3 has EV, PV, HP.
H4 has HP and ESS...

### 2. Google Gemini API Key
The topology extraction agent necessitates authorized access to the Google Gemini models.

Generation Instructions:

Navigate to Google AI Studio (https://aistudio.google.com/ ) .

Authenticate utilizing a registered Google account.

Select the "Get API key" interface and generate a new cryptographic key for the project.

Retain this key securely; it will be declared within the Python execution environment.

### 3. Empirical Smart Meter Readings (readings.csv)
A structured dataset representing the operational state of the network consumers. The file must adhere strictly to the following comma-separated variable structure.

Required Columns:

Customer: The identifier corresponding to the topology file (e.g., H1, H2).

P: Active power value.

Q: Reactive power value.

V: Measured voltage magnitude.

### 4. OpenDSS Scenario Output Files
To evaluate the network hosting capacity under varying boundary conditions, distinct scenario configurations are required. These parameters dictate the asset states during the OpenDSS power flow execution.

You should preprocess the output file of the OpenDSS according to the structure required by the analytical agent.

#### Note: run openDSS for analytical_agent_2 can be implemented according to https://opendss.epri.com/PythontoOpenDSSInterface.html 
####       expectedresults are given in the example csv file to run analytical_agent_3
.......

### 5. OpenDSS 
Install program https://www.epri.com/pages/sa/opendss 
