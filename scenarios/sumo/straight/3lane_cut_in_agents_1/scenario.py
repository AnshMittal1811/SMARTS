# Copyright (C) 2022. Huawei Technologies Co., Ltd. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import random
from itertools import combinations
from pathlib import Path

from numpy import random

from smarts.sstudio import gen_scenario
from smarts.sstudio.sstypes import (
    Distribution,
    Flow,
    Mission,
    Route,
    Scenario,
    SmartsLaneChangingModel,
    Traffic,
    TrafficActor,
    TrapEntryTactic,
)

normal = TrafficActor(
    name="car",
    sigma=1,
    speed=Distribution(sigma=0.1, mean=1.5),
    min_gap=Distribution(sigma=0, mean=1),
    lane_changing_model=SmartsLaneChangingModel(
        cutin_prob=1, assertive=10, dogmatic=True, slow_down_after=0.5
    ),
)

# flow_name = (start_lane, end_lane)
route_opt = [
    (0, 0),
    (1, 1),
    (2, 2),
]

# Traffic combinations = 3C2 + 3C3 = 3 + 1 = 4
# Repeated traffic combinations = 4 * 100 = 400
min_flows = 3
max_flows = 3
route_comb = [
    com
    for elems in range(min_flows, max_flows + 1)
    for com in combinations(route_opt, elems)
] * 100

traffic = {}
for name, routes in enumerate(route_comb):
    traffic[str(name)] = Traffic(
        engine="SMARTS",
        flows=[
            Flow(
                route=Route(
                    begin=("gneE3", start_lane, 0),
                    end=("gneE3", end_lane, "max"),
                ),
                # Random flow rate, between x and y vehicles per minute.
                rate=60 * random.uniform(6, 14),
                # Random flow start time, between x and y seconds.
                begin=random.uniform(0, 5),
                # For an episode with maximum_episode_steps=3000 and step
                # time=0.1s, the maximum episode time=300s. Hence, traffic is
                # set to end at 900s, which is greater than maximum episode
                # time of 300s.
                end=60 * 15,
                actors={normal: 1},
                randomly_spaced=True,
            )
            for start_lane, end_lane in routes
        ],
    )


route = Route(begin=("gneE3", 1, 10), end=("gneE3", 1, "max"))
ego_missions = [
    Mission(
        route=route,
        entry_tactic=TrapEntryTactic(
            start_time=20
        ),  # Delayed start, to ensure road has prior traffic.
    )
]

gen_scenario(
    scenario=Scenario(
        traffic=traffic,
        ego_missions=ego_missions,
    ),
    output_dir=Path(__file__).parent,
)
