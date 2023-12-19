from fullcontrol.gcode import Printer, Extruder, ManualGcode, PrinterCommand, GcodeComment, Buildplate, Hotend, Fan
import fullcontrol.gcode.printer_library.singletool.base_settings as base_settings


def set_up(user_overrides: dict):
    ''' DO THIS
    '''

    # overrides for this specific printer relative those defined in base_settings.py
    printer_overrides = {'primer': 'no_primer'}
    # update default initialization settings with printer-specific overrides and user-defined overrides
    initialization_data = {**base_settings.default_initial_settings, **printer_overrides}
    initialization_data = {**initialization_data, **user_overrides}

    starting_procedure_steps = []
    starting_procedure_steps.append(ManualGcode(
        text='; Time to print!!!!!\n; GCode created with FullControl - tell us what you\'re printing!\n; info@fullcontrol.xyz or tag FullControlXYZ on Twitter/Instagram/LinkedIn/Reddit/TikTok \n'))

    starting_procedure_steps.append(PrinterCommand(id='absolute_coords'))
    starting_procedure_steps.append(PrinterCommand(id='units_mm'))
    starting_procedure_steps.append(Extruder(relative_gcode=initialization_data["relative_e"]))


    print_area = initialization_data["print_area"]
    starting_procedure_steps.append(ManualGcode(
        text=f"M555 X{print_area.minx} Y{print_area.miny} W{print_area.maxx-print_area.minx} H{print_area.maxy-print_area.miny} ; set up print area"
    ))

    starting_procedure_steps.append(Buildplate(temp=initialization_data["bed_temp"], wait=False))
    starting_procedure_steps.append(Hotend(tool=0, temp=initialization_data["nozzle_temp"] - 10, wait=True))
    starting_procedure_steps.append(GcodeComment(end_of_previous_line="; bed leveling temp"))

    starting_procedure_steps.append(ManualGcode(text='G28 XY ; home XY'))

    # Mesh bed leveling
    starting_procedure_steps.append(ManualGcode(text='T0 S1 L0 D0; pick up tool'))
    starting_procedure_steps.append(ManualGcode(text='M84 E ; disable extruder'))
    starting_procedure_steps.append(ManualGcode(text='G28 Z; home Z'))
    starting_procedure_steps.append(ManualGcode(text='G0 Z5 ; add Z clearance'))
    starting_procedure_steps.append(Buildplate(temp=initialization_data["bed_temp"], wait=True))
    starting_procedure_steps.append(ManualGcode(text='G29 G; absorb heat'))

    nozzle_cleanup_x = print_area.minx
    nozzle_cleanup_y = print_area.miny - 5

    starting_procedure_steps.append(ManualGcode(text=f'G1 X{nozzle_cleanup_x} Y{nozzle_cleanup_y} F5000 ; move to nozzle cleanup position'))
    starting_procedure_steps.append(ManualGcode(text='G1 E-2 F2400; retract'))
    starting_procedure_steps.append(ManualGcode(text='M84 E ; disable extruder'))
    starting_procedure_steps.append(ManualGcode(text=f'G29 P9 X{nozzle_cleanup_x + 32} Y{nozzle_cleanup_y} W32 H7 ; nozzle cleanup'))
    starting_procedure_steps.append(ManualGcode(text='G0 Z5 F480; move away from bed'))
    starting_procedure_steps.append(ManualGcode(text='M107; turn off fan'))
    starting_procedure_steps.append(ManualGcode(text='M84 E ; disable extruder'))

    starting_procedure_steps.append(ManualGcode(text='G29 P1 ; invalidate mbl & probe print area'))
    starting_procedure_steps.append(ManualGcode(text='G29 P1 X30 Y0 W50 H20 C ; probe near purge place'))
    starting_procedure_steps.append(ManualGcode(text='G29 P3.2 ; interpolate mbl probes'))
    starting_procedure_steps.append(ManualGcode(text='G29 P3.13 ; extrapolate mbl outside probe area'))
    starting_procedure_steps.append(ManualGcode(text='G29 A ; activate mbl'))

    starting_procedure_steps.append(ManualGcode(text='G1 Z10 F720 ; move away in Z'))
    starting_procedure_steps.append(ManualGcode(text='G1 F24000 ; set speed'))
    starting_procedure_steps.append(ManualGcode(text='P0 S1 L1 D0; park tool'))

    starting_procedure_steps.append(Hotend(tool=0, temp=initialization_data["nozzle_temp"], wait=True))

    starting_procedure_steps.append(ManualGcode(text='T0 S1 L0 D0; pick up tool'))

    if initialization_data["primer"] == 'no_primer':
        starting_procedure_steps.append(ManualGcode(text='G92 E0 ; reset extruder position'))
        starting_procedure_steps.append(ManualGcode(text='G0 X30 Y-7 Z10 F24000 ; move close to the sheets edge'))
        starting_procedure_steps.append(ManualGcode(text='G0 E30 X40 Z0.2 F170 ; purge while moving towards the sheet'))
        starting_procedure_steps.append(ManualGcode(text='G0 X70 E9 F800 ; continue purging and wipe the nozzle'))
        starting_procedure_steps.append(ManualGcode(text='M73 P2 R3'))
        starting_procedure_steps.append(ManualGcode(text='G0 X73 Z0.05 F8000 ; wipe, move close to the bed'))
        starting_procedure_steps.append(ManualGcode(text='M73 P3 R3'))
        starting_procedure_steps.append(ManualGcode(text='G0 X76 Z0.2 F8000 ; wipe, move quickly away from the bed'))
        starting_procedure_steps.append(ManualGcode(text='G1 E-1.05 F2400 ; retract'))
        starting_procedure_steps.append(ManualGcode(text='G92 E0 ; reset extruder position'))

    starting_procedure_steps.append(PrinterCommand(id='absolute_coords'))
    starting_procedure_steps.append(PrinterCommand(id='units_mm'))
    starting_procedure_steps.append(Extruder(relative_gcode=initialization_data["relative_e"]))

    starting_procedure_steps.append(Fan(speed_percent=initialization_data["fan_percent"]))
    starting_procedure_steps.append(ManualGcode(
        text='M220 S' + str(initialization_data["print_speed_percent"])+' ; set speed factor override percentage'))
    starting_procedure_steps.append(ManualGcode(
        text='M221 S' + str(initialization_data["material_flow_percent"])+' ; set extrude factor override percentage'))
    starting_procedure_steps.append(Printer(travel_speed=initialization_data["travel_speed"]))
    starting_procedure_steps.append(Extruder(on=True))
    starting_procedure_steps.append(ManualGcode(text=';-----\n; END OF STARTING PROCEDURE\n;-----\n'))

    ending_procedure_steps = []
    ending_procedure_steps.append(ManualGcode(text='\n;-----\n; START OF ENDING PROCEDURE\n;-----'))
    ending_procedure_steps.append(ManualGcode(text='G4; wait'))
    ending_procedure_steps.append(PrinterCommand(id='retract'))
    ending_procedure_steps.append(ManualGcode(text='G91 ; relative coordinates'))
    ending_procedure_steps.append(ManualGcode(text='G0 Z20 F8000 ; drop bed'))
    ending_procedure_steps.append(ManualGcode(text='G90 ; absolute coordinates'))

    ending_procedure_steps.append(ManualGcode(text='P0 S1; park tool'))

    ending_procedure_steps.append(Fan(speed_percent=0))
    ending_procedure_steps.append(Buildplate(temp=0, wait=False))
    ending_procedure_steps.append(Hotend(tool=0, temp=0, wait=False))
    ending_procedure_steps.append(ManualGcode(text='M221 S100 ; reset flow'))
    ending_procedure_steps.append(ManualGcode(text='M900 K0 ; reset LA'))
    ending_procedure_steps.append(ManualGcode(text='M84 ; disable steppers'))

    initialization_data['starting_procedure_steps'] = starting_procedure_steps
    initialization_data['ending_procedure_steps'] = ending_procedure_steps

    return initialization_data
