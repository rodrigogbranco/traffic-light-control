#!/usr/bin/env python

import os
import sys
import traceback

from classes.kapustaimp import KapustaImpStrategy

# we need to import python modules from the $SUMO_HOME/tools directory
if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa

import logging
import optparse
from distutils.util import strtobool

import time

from classes.logger import Logger
from classes.statistics_values import StatisticsValues
from classes.configuration2 import Configuration2
from classes.no_preemption import NoPreemptionStrategy
from classes.rfid_preemption import RfidPreemptionStrategy

from classes.fuzzy import FuzzyStrategy
from classes.timed_petri4 import TimedPetriStrategy4
from classes.middleware_adaptor import MiddlewareAdaptor
from classes.base_orchestrator2 import BaseOrchestrator2
from classes.kapusta2 import KapustaStrategy2
from classes.allgreen import AllGreenStrategy
from classes.kapustaimp import KapustaImpStrategy

import random
import numpy as np


logger = None


def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option(
        "--nogui",
        action="store_true",
        default=False,
        help="run the commandline version of sumo",
    )
    opt_parser.add_option(
        "--scenario",
        dest="scenario_folder",
        help="Scenario folder which the simulation will use",
        metavar="FILE",
    )
    opt_parser.add_option("--sm", "--seed-sumo", type="int", dest="seedsumo", default=0)
    opt_parser.add_option(
        "--evs",
        type="string",
        dest="evs",
        default="veh1",
        help="comma separated value of EVs",
    )
    opt_parser.add_option(
        "--alg",
        type="string",
        dest="algorithm",
        default="no-preemption",
        help="Allowed Algorithms: no-preemption, rfid, fuzzy and tpn",
    )
    opt_parser.add_option(
        "--distancedetection", type="float", dest="distancedetection", default=50.0
    )
    opt_parser.add_option("--ncycles", type="int", dest="ncycles", default=2)
    opt_parser.add_option(
        "--override",
        action="store_true",
        default=False,
        help="run only if .json doesn't exist",
    )
    opt_parser.add_option(
        "--skip",
        action="store_true",
        default=False,
        help="json file is not generated in the end",
    )
    opt_parser.add_option(
        "--prefix",
        type="string",
        dest="prefix",
        default="staticdynamic",
        help="Choose between static/dynamic scenarios",
    )
    opt_parser.add_option(
        "--el",
        type="string",
        dest="el",
        default="low",
        help="Emergency Level for Fuzzy (low, medium, high)",
    )
    opt_parser.add_option(
        "--id",
        type="int",
        dest="id",
        default=0,
        help="Id of running, used to group outcomes of different seeds",
    )
    opt_parser.add_option(
        "--trackev", type="string", dest="trackev", help="Track EV when using GUI"
    )
    opt_parser.add_option(
        "--always",
        help="Always ask to clear path",
        type="string",
        dest="always",
        default="False",
    )
    opt_parser.add_option(
        "--prt",
        help="Percentage to reduce time in T0 computing",
        type="float",
        dest="prt",
        default=0.0,
    )
    opt_parser.add_option(
        "--clear",
        help="Ask to ahead vehicles to clear the lanes",
        type="string",
        dest="clear",
        default="False",
    )
    opt_parser.add_option(
        "--begin",
        help="Start simulation at given time (seconds)",
        type="int",
        dest="begin",
        default=0,
    )
    opt_parser.add_option(
        "--end",
        help="End simulation at given time (seconds)",
        type="float",
        dest="end",
        default=float("inf"),
    )
    opt_parser.add_option(
        "--stats", action="store_true", default=False, help="Compute stats"
    )
    opt_parser.add_option(
        "--stopsoon",
        action="store_true",
        default=False,
        help="Stop simulation as soon as EV leaves the network",
    )
    opt_parser.add_option(
        "--save",
        action="store_true",
        default=False,
        help="Save state until before EV enters",
    )
    opt_parser.add_option(
        "--noload", action="store_true", default=False, help="Don't load state"
    )
    opt_parser.add_option(
        "--gengps", action="store_true", default=False, help="Generate GPS trace for EV"
    )
    opt_parser.add_option(
        "--tmpdir",
        type="string",
        dest="tmpdir",
        default=None,
        help="Folder for storing temp files",
    )
    (options, _) = opt_parser.parse_args()
    return options


def clear_logs(logfile, logfile_server, logger):
    if os.path.isfile(logfile):
        logger.info("Deleting {}...".format(logfile))
        os.remove(logfile)
    if os.path.isfile(logfile_server):
        logger.info("Deleting {}...".format(logfile_server))
        os.remove(logfile_server)


def get_alg_class(alg):
    algs_class = {
        "no-preemption": NoPreemptionStrategy,
        "rfid": RfidPreemptionStrategy,
        "fuzzy": FuzzyStrategy,
        "tpn4": TimedPetriStrategy4,
        "kapusta2": KapustaStrategy2,
        "allgreen": AllGreenStrategy,
        "kapustaimp": KapustaImpStrategy,
    }

    return None if alg not in algs_class else algs_class[alg]


def continue_running(mw, evs_in_sim, step, options, algs_by_ev):

    if options.save and step >= float(options.end):
        return False

    if (
        evs_in_sim["timeout"] != None
        and evs_in_sim["timeout"] <= step
        and options.end <= step
    ):
        return False
    elif evs_in_sim["timeout"] != None and options.stopsoon:
        return False

    some_ev_entered = False

    for ev in algs_by_ev:
        ev_in_sim = mw.vehicle_in_simulation(ev)

        if ev_in_sim:
            some_ev_entered = True
            if evs_in_sim[ev]["start"] == None:
                evs_in_sim[ev]["start"] = step
        elif evs_in_sim[ev]["start"] != None and evs_in_sim[ev]["stop"] == None:
            evs_in_sim[ev]["stop"] = step

    if some_ev_entered:
        return True

    some_ev_not_left = False
    for ev in algs_by_ev:
        if evs_in_sim[ev]["start"] == None or evs_in_sim[ev]["stop"] == None:
            some_ev_not_left = True

    if not some_ev_not_left and evs_in_sim["timeout"] == None:
        evs_in_sim["timeout"] = step + 600

    return True


def run(options, statistics_values, instance_name):
    enter_time = {}

    for ev in statistics_values.evs_data:
        if statistics_values.evs_data[ev]["depart"] not in enter_time:
            et = int(float(statistics_values.evs_data[ev]["depart"]))
            enter_time[et] = set()
        enter_time[et].add(ev)

    mw = MiddlewareAdaptor()
    orch = BaseOrchestrator2(mw)
    mw.set_options(folder=options.scenario_folder)

    scenario_str = options.scenario_folder.split("/")[-1].split("-")[0]

    logger.info("algorithm: {}".format(options.algorithm))

    logger.info("Chosen EVs: {}".format(statistics_values.evs))

    logger.info("track ev: {}".format(options.trackev))

    if options.trackev and options.trackev not in statistics_values.evs:
        sys.exit(
            "Error: --trackev option invalid. Given: {}. Allowed: {}".format(
                options.trackev, statistics_values.evs
            )
        )

    algs_by_ev = {}

    for ev in statistics_values.evs:
        conf = Configuration2(ev, options.scenario_folder, mw)

        if options.prefix == "staticdynamic":
            conf.set_staticdynamic()

        alg_class = get_alg_class(options.algorithm)

        if not alg_class:
            sys.exit("Error: --alg was not recognized: {}".format(options.algorithm))

        alg = alg_class(options, orch)
        alg.setup(conf, statistics_values, ev)
        alg.configure()
        algs_by_ev[ev] = alg

    tracked = set()

    step = 0

    start_time = time.time()

    evs_in_sim = {}
    for ev in algs_by_ev:
        evs_in_sim[ev] = {}
        evs_in_sim[ev]["start"] = None
        evs_in_sim[ev]["stop"] = None
    evs_in_sim["timeout"] = None

    while continue_running(mw, evs_in_sim, step, options, algs_by_ev):
        step = mw.get_time()

        if step in enter_time:
            for ev in enter_time[step]:
                route_name = "route_{}".format(ev)
                ev_data = statistics_values.evs_data[ev]
                traci.route.add(route_name, ev_data["route"].split(" "))
                traci.vehicle.add(
                    vehID=ev,
                    routeID=route_name,
                    typeID="ev_passenger",
                    departLane=ev_data["departLane"],
                    departSpeed=ev_data["departSpeed"],
                )

        cars_in_simulation = mw.get_nvec()
        logger.info("step {} - #vehs {}".format(step, cars_in_simulation))

        orch.execute_before_step_simulation(step)

        for ev in algs_by_ev:
            ev_in_simulation = (
                evs_in_sim[ev]["start"] != None and evs_in_sim[ev]["stop"] == None
            )
            alg = algs_by_ev[ev]
            alg.execute_before_step_simulation(step)

            if ev_in_simulation and ev not in tracked:
                mw.track_vehicle(ev, not options.nogui, ev == options.trackev)
                tracked.add(ev)

        mw.do_simulation_step()
        cars_in_simulation = mw.get_nvec()

        if options.stats:
            if statistics_values.edges_id == None:
                all_edges = mw.get_edges_id()
                edge_more_than = set()
                for ex in all_edges:
                    if mw.get_length_of_lane("{}_0".format(ex)) >= 250:
                        edge_more_than.add(ex)
                        logger.debug("{} added".format(ex))

                statistics_values.edges_id = edge_more_than

            most_occupancy_edge = None
            most_ocuppancy_value = None

            shuffled = list(statistics_values.edges_id)
            random.shuffle(shuffled)

            for ex in shuffled:
                occ_value = mw.get_edge_occupancy(ex)
                if most_occupancy_edge == None or occ_value > most_ocuppancy_value:
                    most_occupancy_edge = ex
                    most_ocuppancy_value = occ_value
                if occ_value >= 1:
                    break

            statistics_values.compute_stats(
                step,
                cars_in_simulation,
                mw.get_departed_vehs_number(),
                most_occupancy_edge,
                most_ocuppancy_value,
            )

        for ev in algs_by_ev:
            ev_in_simulation = mw.vehicle_in_simulation(ev)
            alg = algs_by_ev[ev]

            if ev_in_simulation:
                statistics_values.evs_data[ev]["last_edge"] = mw.get_edge_of_vehicle(ev)
                statistics_values.evs_data[ev]["last_lane"] = mw.get_lane_of_vehicle(ev)
                if statistics_values.evs_data[ev]["ev_start"] == -1:
                    statistics_values.evs_data[ev]["ev_start"] = step

                alg.conf.update_values()
                statistics_values.evs_data[ev]["n_when_ev_enter"] = (
                    cars_in_simulation - 1
                )
                statistics_values.evs_data[ev][
                    "distance_travelled"
                ] = mw.get_distance_travelled_by_vehicle(ev)

                if options.gengps:
                    x, y = mw.get_vehicle_position(ev)
                    lon, lat = traci.simulation.convertGeo(x, y)
                    statistics_values.set_gps_step(scenario_str, ev, step, lat, lon)

                logger.info(
                    "{} - {}m - l:{}".format(
                        ev,
                        statistics_values.evs_data[ev]["distance_travelled"],
                        statistics_values.evs_data[ev]["last_lane"],
                    )
                )

            alg.execute_step(step, ev, ev_in_simulation)

            if mw.vehicle_was_teleported(ev):
                statistics_values.evs_data[ev]["was_teleported"] = True

            if alg.ev_entered and alg.ev_exited:
                if statistics_values.evs_data[ev]["ev_end"] == -1:
                    statistics_values.evs_data[ev]["ev_end"] = step

                if statistics_values.evs_data[ev]["n_when_ev_left"] == -1:
                    statistics_values.evs_data[ev]["n_when_ev_left"] = (
                        cars_in_simulation - 1
                    )
                alg.finish()

            if statistics_values.evs_data[ev]["was_teleported"]:
                logger.info("{} has been teleported!".format(ev))

            affected_vehs = set()
            for tl in orch.active_tls:
                links = mw.get_controlled_links_of_tl(tl)
                for l in links:
                    if len(l) > 0:
                        tuples = mw.get_vehicles_on_lane(l[0][0])
                        affected_vehs |= set(tuples)

            statistics_values.update_affected_vehs(affected_vehs)

        if np.all(
            [
                statistics_values.evs_data[ev]["was_teleported"]
                for ev in statistics_values.evs_data
            ]
        ):
            break

    mw.finish_simulation()

    statistics_values.teleported = mw.get_teleported_vehicles()

    statistics_values.set_active_time(orch.tls_active_time)

    statistics_values.set_crossed_tls(ev, len(algs_by_ev[ev].conf.edges_with_tl))

    statistics_values.print_summary(ev)

    if options.gengps:
        statistics_values.gps_to_file()

    logger.info("finished!")

    for ev in algs_by_ev:
        logger.info(
            "ev({}) started {} and ended {}".format(
                ev,
                statistics_values.evs_data[ev]["ev_start"],
                statistics_values.evs_data[ev]["ev_end"],
            )
        )
        statistics_values.get_results(ev, step)
        if statistics_values.evs_data[ev]["was_teleported"]:
            logger.info(
                "Last edge: {}".format(statistics_values.evs_data[ev]["last_edge"])
            )

        logger.info("")

    runtime = time.time() - start_time

    print("Total runtime: {}".format(runtime))

    statistics_values.generate_json(
        options.skip, instance_name, statistics_values.evs, step, runtime
    )


# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    if not options.scenario_folder:
        sys.exit(
            "Error: You must specify the Scenario Folder using the '--scenario' option"
        )

    if options.prefix not in ["static", "dynamic", "staticdynamic"]:
        sys.exit("Error: --prefix should be 'static', 'dynamic' or 'staticdynamic'")

    if options.el not in ["low", "medium", "high"]:
        sys.exit(
            "Error: Emergency Level must be one of those options: low, medium or high"
        )

    try:
        always = strtobool(options.always)
        options.always = always
    except:
        sys.exit("Error: Always value must be True or False")

    try:
        clear = strtobool(options.clear)
        options.clear = clear
    except:
        sys.exit("Error: Clear must be True or False")

    sumoBinary = checkBinary("sumo") if options.nogui else checkBinary("sumo-gui")

    alg_class = get_alg_class(options.algorithm)

    if not alg_class:
        sys.exit("Error: --alg was not recognized: {}".format(options.algorithm))

    instance_name = alg_class(options, None).instance_name()

    scenario_str = options.scenario_folder.split("/")[-1].split("-")[0]
    tmp_folder = (
        "{}/{}".format(options.tmpdir, scenario_str)
        if options.tmpdir
        else options.scenario_folder
    )

    instance_folder = os.path.join(options.scenario_folder, "results")
    instance_folder = os.path.join(instance_folder, options.prefix)

    if not os.path.exists(instance_folder):
        os.makedirs(instance_folder, exist_ok=True)

    if not os.path.exists(tmp_folder):
        os.makedirs(tmp_folder, exist_ok=True)

    instance_opts = "tripinfo_{}".format(instance_name)

    logfile = os.path.join(tmp_folder, "{}.log".format(instance_opts))
    logfile_server = os.path.join(tmp_folder, "{}-server.log".format(instance_opts))

    Logger.set_globals(logfile, logging.INFO)

    logger = Logger("Runner").get()

    logger.info(options)

    trip_file = "{}/{}.xml".format(tmp_folder, instance_opts)

    statistics_values = StatisticsValues(
        options.scenario_folder,
        instance_folder,
        trip_file,
        options.algorithm,
        options.evs,
    )

    if statistics_values.skip_because_json_file(
        options.override, options.skip, instance_name
    ):
        logger.info("Nothing to do, exiting...")
        clear_logs(logfile, logfile_server, logger)
        sys.exit(0)

    statistics_values.load_and_parse_xmls(options.evs)

    try:
        save_load_options = []
        real_seed = str(options.seedsumo)
        if not options.noload:
            if options.save:
                real_seed = str(42)
                save_load_options = [
                    "--save-state.times",
                    str(options.end),
                    "--save-state.files",
                ]
            else:
                save_load_options = ["--load-state"]

            save_load_options += ["{}/state.xml.gz".format(options.scenario_folder)]

        traci.start(
            [
                sumoBinary,
                "-v",
                "true",
                "-c",
                "{}/osm-{}.sumocfg".format(options.scenario_folder, options.prefix),
                "--duration-log.statistics",
                "--error-log",
                logfile_server,
                "--tripinfo-output",
                trip_file,
                "--start",
                "--begin",
                str(options.begin),
                "--time-to-teleport",
                "150",
                "--seed",
                real_seed,
                "--ignore-junction-blocker",
                "5",
            ]
            + save_load_options
        )

        logger.info("SUMO Version: {}".format(traci.getVersion()))

        statistics_values.set_tl_number(traci.trafficlight.getIDCount(), options.evs)

        run(options, statistics_values, instance_name)

        if os.path.isfile(trip_file):
            os.remove(trip_file)
            logger.info("File {} was deleted".format(trip_file))

        clear_logs(logfile, logfile_server, logger)
        sys.exit(0)
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        if logger != None:
            logger.error(
                "{}\nExiting on error\n{}\n{}, {}".format(
                    traceback.format_exc(), exc_type, fname, exc_tb.tb_lineno
                )
            )
        else:
            print(
                "{}\nExiting on error\n{}\n{}, {}".format(
                    traceback.format_exc(), exc_type, fname, exc_tb.tb_lineno
                )
            )

        sys.exit(1)
