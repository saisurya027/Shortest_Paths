# AI_MapSolver_MK1
A primitive Google Maps substitute.

The aim of the project is to create a primitive yet efficient substitute for Google Maps. 
The geolocations/node data is fetched from OpenStreetMap API and stored in PostgreSQL with a PostGIS extension.
Distances between these nodes are taken from Google Developer's Distance Matrix. 
Source and Destination for now are hardcoded in (Mainly because of the limitations of computational power and memory)

The quadrilateral extracted from OSM had to be as compact as possible and should've incorporated the both source and destination, 
due to that reasons we lost couple of best results that Google shows.

The route which is displayed is a shorter path (red dotted line on GoogleMap screenshot), although it might take more time.
Regardless, the objective of the script, i.e., to find the shortest path using A* implementation was acheived.

