# Layer Painter

Layer Painter is a addon for blender, made to bring a workflow similar to a tool like substance painter or armor paint directly inside blender.

This doc talks about some of the design decisions as well as the structure to get you started with adding features.



## Contributing

Contributions are always welcome!
See below for ways to get started.

To start developing for this project I recommend using the [VS Code Extension](https://marketplace.visualstudio.com/items?itemName=JacquesLucke.blender-development) by Jacques Lucke.


Layer Painter is usually maintained for the latest LTS release, meaning that you should always test for this version and above.

  
## Design

### Overview

Layer Painter is designed to be easy to use and highly customizable. We want to add a layer of abstraction from the node editor but still leave all the possibilities of nodes open. This can happen in the form of custom masks or similar which can be created with nodes and then used with our UI.

It should be very modular in it's design. An example of that is in the channels which the user can define and therefore use to fit with their workflow and materials.

### Materials

This is the connection between blender and our tool. Materials work the same and are the same as in blender which should make it easier for users to understand.

### Channels

Channels in Layer Painter are simply input sockets of nodes. This input socket is where the color information will go and change the material. A layer node group has an output for each channel which connects to this input or the layer above.

### Layers



### Baking

### Interface



## Documentation

