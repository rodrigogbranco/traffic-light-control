"""
Process sparse json files into a single csv

Usage: python summary-jsonpath2.py <input_dir> <output_dir>
"""

import json
import os
import sys
import pandas as pd
from jsonpath_ng import parse
import numpy as np

if __name__ == "__main__":
    input_dir = sys.argv[1]

    if len(sys.argv) != 3:
        sys.exit("Usage: summary-jsonpath2.py <input_dir> <output_dir>")

    csvdata = {
        "scenario": [],
        "instance": [],
        "ev": [],
        "alg": [],
        "seed": [],
        "tl": [],
        "rt": [],
        "ttt": [],
        "eff": [],
        "imp": [],
        "perc": [],
        "teleported": [],
        "preemptime": [],
    }

    # scenarios = ["sp", "ny"]
    # instance = [1, 2, 3, 4, 5]

    # scenarios = ["oneintersection", "turinkap", "colognekap"]
    scenarios = ["colognekap"]
    instance = [1]

    total_vehs = []

    for scenario in scenarios:
        for i in instance:
            base_path = f"{input_dir}/{scenario}/{scenario}-{i}/results/staticdynamic"

            for r in os.listdir(base_path):
                if r.split(".")[-1] != "json":
                    continue

                params = r.split("!")
                ev = params[1].split("_")[0]
                seed = params[2].split("_")[0]
                alg = params[3].split(".json")[0].split("_")[0]

                print(f"processing {base_path}/{r}...")

                tmp = open(f"{base_path}/{r}", "r", encoding="utf-8")
                data = json.loads(tmp.read())
                tmp.close()
                teleporteds = parse("$.teleported").find(data)[0].value
                vehs_data = parse("$.vehs").find(data)[0].value

                teleported = ev in teleporteds

                total_vehs.append(len(teleporteds) + len(vehs_data))

                tls = parse("$.tls").find(data)[0].value

                preemption_time = []
                for tl in tls:
                    total = 0
                    for actindex in range(1, len(tls[tl]), 2):
                        if tls[tl][actindex - 1] != -1 and tls[tl][actindex] != -1:
                            total += tls[tl][actindex] - tls[tl][actindex - 1]
                    preemption_time.append(total)

                csvdata["scenario"].append(scenario)
                csvdata["instance"].append(i)
                csvdata["ev"].append(ev)
                csvdata["alg"].append(alg)
                csvdata["seed"].append(seed)
                csvdata["teleported"].append(teleported)
                csvdata["rt"].append(parse("$.param[2]").find(data)[0].value)
                csvdata["imp"].append(np.NaN)
                csvdata["perc"].append(np.NaN)
                csvdata["preemptime"].append(
                    np.mean(preemption_time) if len(preemption_time) > 0 else np.NaN
                )
                if not teleported:
                    csvdata["tl"].append(vehs_data[ev][2])
                    csvdata["ttt"].append(vehs_data[ev][1])
                    csvdata["eff"].append(
                        float(vehs_data[ev][1]) - float(vehs_data[ev][2])
                    )
                else:
                    csvdata["tl"].append(np.NaN)
                    csvdata["ttt"].append(np.NaN)
                    csvdata["eff"].append(np.NaN)

    df = pd.DataFrame(csvdata)

    df_other = df[(df["alg"] != "no-preemption") & (~df["teleported"])]

    tl_imp = []

    for index, row in df_other.iterrows():
        df_nopreempt = df[
            (df["alg"] == "no-preemption")
            & (df["scenario"] == row.scenario)
            & (df["ev"] == row.ev)
            & (df["seed"] == row.seed)
            & (~df["teleported"])
        ]

        if not df_nopreempt.empty:
            tl_before = float(df_nopreempt["tl"].iloc[0])
            tl_after = float(row.tl)
            df.loc[index, "imp"] = (
                tl_before / tl_after
                if tl_after < tl_before
                else -1 * (tl_after / tl_before)
            )
            df.loc[index, "perc"] = (1 - (tl_after / tl_before)) * 100

    print(np.mean(total_vehs))

    df.to_csv(sys.argv[2], index=False)
