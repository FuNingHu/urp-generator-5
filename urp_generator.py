import json
import xml.etree.ElementTree as ET


def create_kinematics(kinematics_data):
    kinematics = ET.Element('kinematics', status=kinematics_data['status'], validChecksum=kinematics_data['validChecksum'])
    sub_nodes = ['deltaTheta', 'a', 'd', 'alpha', 'jointChecksum']
    for node in sub_nodes:
        sub_elem = ET.SubElement(kinematics, node)
        sub_elem.set('value', kinematics_data[node])
    return kinematics


def create_feature(feature_data):
    feature = ET.Element('feature', **{'class': 'GeomFeatureReference'})
    if 'referencedName' in feature_data:
        feature.set('referencedName', feature_data['referencedName'])
    return feature


def create_waypoint(waypoint_data):
    waypoint = ET.Element('Waypoint', type=waypoint_data['type'], name=waypoint_data['name'],
                          kinematicsFlags=waypoint_data['kinematicsFlags'])
    motion_params = ET.SubElement(waypoint, 'motionParameters')
    for param, value in waypoint_data.get('motionParameters', {}).items():
        motion_params.set(param, str(value))

    position = ET.SubElement(waypoint, 'position')

    joint_angles = ET.SubElement(position, 'JointAngles')
    joint_angles.set('angles', waypoint_data['position']['JointAngles']['angles'])

    tcp_offset = ET.SubElement(position, 'TCPOffset')
    tcp_offset.set('pose', waypoint_data['position']['TCPOffset']['pose'])

    # 修改此处，将标签名改为 'Kinematics'
    kinematics = ET.Element('Kinematics', status=waypoint_data['position']['Kinematics']['status'],
                            validChecksum=waypoint_data['position']['Kinematics']['validChecksum'])
    sub_nodes = ['deltaTheta', 'a', 'd', 'alpha', 'jointChecksum']
    for node in sub_nodes:
        sub_elem = ET.SubElement(kinematics, node)
        sub_elem.set('value', waypoint_data['position']['Kinematics'][node])
    position.append(kinematics)

    if 'BaseToFeature' in waypoint_data:
        base_to_feature = ET.SubElement(waypoint, 'BaseToFeature')
        base_to_feature.set('pose', waypoint_data['BaseToFeature']['pose'])
    return waypoint


def create_move(move_data):
    move = ET.Element('Move', motionType=move_data['motionType'], speed=move_data['speed'],
                      acceleration=move_data['acceleration'], useActiveTCP=move_data['useActiveTCP'],
                      positionType=move_data['positionType'])
    feature = create_feature(move_data['feature'])
    move.append(feature)

    children = ET.SubElement(move, 'children')
    waypoints = move_data['children'].get('Waypoint', [])
    if not isinstance(waypoints, list):
        waypoints = [waypoints]
    for waypoint in waypoints:
        waypoint_elem = create_waypoint(waypoint)
        children.append(waypoint_elem)
    return move


def create_wait(wait_data):
    wait = ET.Element('Wait', type=wait_data['type'])
    if wait_data['type'] == 'Sleep':
        wait_time = ET.SubElement(wait, 'waitTime')
        wait_time.text = str(wait_data['waitTime'])
    elif wait_data['type'] == 'DigitalInput':
        pin = ET.SubElement(wait, 'pin')
        pin.set('referencedName', wait_data['pin']['referencedName'])
        digital_value = ET.SubElement(wait, 'digitalValue')
        digital_value.text = str(wait_data['digitalValue'])
    elif wait_data['type'] == 'AnalogInput':
        pin = ET.SubElement(wait, 'pin')
        pin.set('referencedName', wait_data['pin']['referencedName'])
        analog_comparison = ET.SubElement(wait, 'analogComparison')
        analog_comparison.text = str(wait_data['analogComparison'])
        analog_value = ET.SubElement(wait, 'analogValue')
        analog_value.text = str(wait_data['analogValue'])
    elif wait_data['type'] == 'Condition':
        expression = ET.SubElement(wait, 'expression')
        for char in wait_data['expression']:
            expr_char = ET.SubElement(expression, 'ExpressionChar')
            expr_char.set('character', char)
    return wait


def create_special_sequence(special_sequence_data):
    special_sequence = ET.Element('SpecialSequence', type=special_sequence_data['type'])
    children = ET.SubElement(special_sequence, 'children')
    waits = special_sequence_data['children'].get('Wait', [])
    if not isinstance(waits, list):
        waits = [waits]
    for wait in waits:
        wait_elem = create_wait(wait)
        children.append(wait_elem)
    return special_sequence


def create_main_program(main_program_data):
    main_program = ET.Element('MainProgram', runOnlyOnce=main_program_data['runOnlyOnce'],
                              InitVariablesNode=main_program_data['InitVariablesNode'])
    children = ET.SubElement(main_program, 'children')
    for key, value in main_program_data['children'].items():
        if key == 'Move':
            if not isinstance(value, list):
                value = [value]
            for move in value:
                move_elem = create_move(move)
                children.append(move_elem)
        elif key == 'Wait':
            if not isinstance(value, list):
                value = [value]
            for wait in value:
                wait_elem = create_wait(wait)
                children.append(wait_elem)
    return main_program


def create_children(children_data):
    children = ET.Element('children')
    if 'InitVariablesNode' in children_data:
        ET.SubElement(children, 'InitVariablesNode')
    if 'SpecialSequence' in children_data:
        special_sequence = create_special_sequence(children_data['SpecialSequence'])
        children.append(special_sequence)
    if 'MainProgram' in children_data:
        main_program = create_main_program(children_data['MainProgram'])
        children.append(main_program)
    return children


def generate_urp(json_data, save_path):
    ur_program = ET.Element('URProgram', **json_data['URProgram'])

    kinematics = create_kinematics(json_data['URProgram']['kinematics'])
    ur_program.append(kinematics)

    children = create_children(json_data['URProgram']['children'])
    ur_program.append(children)

    tree = ET.ElementTree(ur_program)
    ET.indent(tree, space="\t", level=0)
    # 去掉 XML 声明
    with open(save_path, 'wb') as f:
        tree.write(f, encoding='utf-8', xml_declaration=False)


def main(json_path, save_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        generate_urp(json_data, save_path)
        print(f"URP文件生成成功，文件保存路径为：{save_path}")
    except FileNotFoundError:
        print(f"未找到JSON文件: {json_path}")
    except json.JSONDecodeError:
        print("JSON文件解析出错，请检查JSON文件格式。")
    except KeyError as e:
        print(f"JSON数据缺少必要的键: {e}")


if __name__ == "__main__":
    json_path = r'C:\Users\funh\myWork\zw_urcap_projects\urp-generator\urpRecipt.json'
    save_path = r'C:\Users\funh\myWork\zw_urcap_projects\urp-generator\output_1.urp'
    main(json_path, save_path)