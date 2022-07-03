import xml.etree.ElementTree
import os
import numpy as np


def is_g(state):
    return "g" in state.lower()


def is_y(state):
    return not is_g(state) and "y" in state.lower()


def is_r(state):
    return not is_g(state) and not is_y(state)


def create_r_phase(count):
    return "".join(np.repeat("r", count))


if __name__ == "__main__":

    net_xml = "/home/rodrigo/oneintersection/osm.net.xml"
    net_file = xml.etree.ElementTree.parse(net_xml).getroot()

    edges_with_tl = {}
    number_of_tls_x_evs = {}

    tlslogic = net_file.findall("./tlLogic")

    file_tmp = open("/home/rodrigo/newtllogic.txt", "w")
    for tl_logic in tlslogic:
        phases = tl_logic.findall("./phase")
        file_tmp.write(
            '    <tlLogic id="{}" type="static" programID="{}" offset="{}">\n'.format(
                tl_logic.get("id"), tl_logic.get("programID"), tl_logic.get("offset")
            )
        )
        count = 1
        total = len(phases)
        first_phase = None
        for phase in phases:
            state = phase.get("state")
            file_tmp.write(
                '        <phase duration="{}" state="{}"/>\n'.format(
                    phase.get("duration"), state
                )
            )

            if count < total and is_y(state) and not is_r(phases[count].get("state")):
                file_tmp.write(
                    '        <phase duration="3" state="{}"/>\n'.format(
                        create_r_phase(len(state))
                    )
                )
            elif (
                count == total
                and not is_r(state)
                and not is_r(first_phase.get("state"))
            ):
                file_tmp.write(
                    '        <phase duration="3" state="{}"/>\n'.format(
                        create_r_phase(len(state))
                    )
                )

            count += 1
            if not first_phase:
                first_phase = phase

        file_tmp.write("    </tlLogic>\n")

    file_tmp.close()
