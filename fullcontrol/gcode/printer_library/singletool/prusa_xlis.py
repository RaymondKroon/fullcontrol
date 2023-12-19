from fullcontrol.gcode import ManualGcode


def set_up(user_overrides: dict):
    ''' DO THIS
    '''

    # Append input shaping to end of starting procedure of prusa_xl
    import fullcontrol.gcode.printer_library.singletool.prusa_xl
    initialization_data = fullcontrol.gcode.printer_library.singletool.prusa_xl.set_up(user_overrides)
    initialization_data['starting_procedure_steps'].append(ManualGcode(text='M593 X T2 F35.8'))
    initialization_data['starting_procedure_steps'].append(ManualGcode(text='M593 Y T2 F35.4'))

    return initialization_data
