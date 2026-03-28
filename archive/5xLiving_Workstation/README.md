# 5xLiving_Workstation

Root for the 5xLiving workstation project. This folder contains the core runtime, UI and module code used to run the Workstation environment.

Structure (high level):

- CoreRoom/: scene parts (Floor, Walls, Ceiling, Lights, Screens)
- ControlCenter/: operator UI panels and consoles
- BuildStage/: preview and simulation spaces (World/Model/Simulation)
- CoreSystems/: core runtime systems (ProjectManager, CommandRouter, ModuleManager, SaveLoadManager, CameraRig, UIManager)
- Modules/: pluggable modules (WorldBuilderModule, ModelMakerModule, DressingRoomModule, SimulationModule, FutureModules)

This is intentionally a lightweight placeholder tree. Add actual Unity Scenes, scripts and prefabs under these folders as needed.
