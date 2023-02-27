# Routing Script for 3D Electronics Design
This is a Python script that generates a routing between two selected faces in a 3D model, specifically aimed at making the life easier for 3D electronics designers. The script automatically avoids intersections by jumping over the z-axis.

## Requirements
To use this script, you'll need:

- Fusion 360
- Python 3.x


## Installation
1. Clone or download this repository.
2. In Fusion 360, open the Utility tab and press the ADD-INS button them create a new script, select python as a programing language add a name and put a description on.
3. Copy the routing_script.py file to the scripts folder of your fusion 360 software. (usually on ~\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\Scripts\your_script_name)
4. use it.

## Usage
1. Open your 3D model in your Fusion 360 software.
2. In Fusion 360, open the Utility tab and press the ADD-INS button, select your_script_name and press run.
3. Select two faces that you want to connect with a routing.
4. wait till it finish the connection.


## Contributing
If you'd like to contribute to this project, feel free to fork this repository and submit a pull request with your changes.

## License
This script is released under the MIT License.
