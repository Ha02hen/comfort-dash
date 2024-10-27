import dash_mantine_components as dmc
from pythermalcomfort.models import pmv_ppd, adaptive_ashrae
from pythermalcomfort.utilities import v_relative, clo_dynamic, mapping
from pythermalcomfort.models import adaptive_en, set_tmp, pmv_ppd, cooling_effect
from pythermalcomfort.psychrometrics import t_o
from dataclasses import dataclass
from typing import List

from utils.get_inputs import get_inputs
from utils.my_config_file import (
    Models,
    UnitSystem,
    UnitConverter,
    ElementsIDs,
    Functionalities,
    CompareInputColor,
    ComfortLevel,
    Charts,
)


def display_results(inputs: dict):
    selected_model: str = inputs[ElementsIDs.MODEL_SELECTION.value]
    units: str = inputs[ElementsIDs.UNIT_TOGGLE.value]

    results = []
    columns: int = 2
    if selected_model == Models.PMV_EN.name or selected_model == Models.PMV_ashrae.name:
        columns = 3
        standard = "ISO"
        if selected_model == Models.PMV_ashrae.name:
            standard = "ashrae"

        r_pmv = pmv_ppd(
            tdb=inputs[ElementsIDs.t_db_input.value],
            tr=inputs[ElementsIDs.t_r_input.value],
            vr=v_relative(
                v=inputs[ElementsIDs.v_input.value],
                met=inputs[ElementsIDs.met_input.value],
            ),
            rh=inputs[ElementsIDs.rh_input.value],
            met=inputs[ElementsIDs.met_input.value],
            clo=clo_dynamic(
                clo=inputs[ElementsIDs.clo_input.value],
                met=inputs[ElementsIDs.met_input.value],
            ),
            wme=0,
            limit_inputs=True,
            units=units,
            standard=standard,
        )
        r_set_tmp = set_tmp(
            tdb=inputs[ElementsIDs.t_db_input.value],
            tr=inputs[ElementsIDs.t_r_input.value],
            v=v_relative(
                v=inputs[ElementsIDs.v_input.value],
                met=inputs[ElementsIDs.met_input.value],
            ),
            rh=inputs[ElementsIDs.rh_input.value],
            met=inputs[ElementsIDs.met_input.value],
            clo=clo_dynamic(
                clo=inputs[ElementsIDs.clo_input.value],
                met=inputs[ElementsIDs.met_input.value],
            ),
            wme=0,
            limit_inputs=True,
            units=units,
            standard=standard,
        )
        r_cooling_effect = cooling_effect(
            tdb=inputs[ElementsIDs.t_db_input.value],
            tr=inputs[ElementsIDs.t_r_input.value],
            vr=v_relative(
                v=inputs[ElementsIDs.v_input.value],
                met=inputs[ElementsIDs.met_input.value],
            ),
            rh=inputs[ElementsIDs.rh_input.value],
            met=inputs[ElementsIDs.met_input.value],
            clo=clo_dynamic(
                clo=inputs[ElementsIDs.clo_input.value],
                met=inputs[ElementsIDs.met_input.value],
            ),
            wme=0,
            units=units,
        )

        # Standard Checker for PMV
        # todo: need to add standard for adaptive methods by ensure if the current red point out of area
        if selected_model == Models.PMV_ashrae.name:
            if -0.5 <= r_pmv["pmv"] <= 0.5:
                compliance_text = "✔  Complies with ASHRAE Standard 55-2023"
                compliance_color = "green"
            else:
                compliance_text = "✘  Does not comply with ASHRAE Standard 55-2023"
                compliance_color = "red"
        else:  # EN
            if -0.7 <= r_pmv["pmv"] <= 0.7:
                compliance_text = "✔  Complies with EN-16798"
                compliance_color = "green"
            else:
                compliance_text = "✘  Does not comply with EN-16798"
                compliance_color = "red"

        standard_checker = dmc.Text(
            compliance_text,
            c=compliance_color,
            ta="center",
            size="md",
            style={"width": "100%"},
        )
        temp_unit = "°F" if units == UnitSystem.IP.value else "°C"
        if selected_model == Models.PMV_ashrae.name:
            results = [
                standard_checker,
                dmc.SimpleGrid(
                    cols=2,
                    spacing="xs",
                    verticalSpacing="xs",
                    children=[
                        dmc.Center(dmc.Text(f"PMV: {r_pmv['pmv']:.2f}")),
                        dmc.Center(dmc.Text(f"PPD: {r_pmv['ppd']:.1f} %")),
                        dmc.Center(dmc.Text(f"SET: {r_set_tmp:.1f} {temp_unit}")),
                    ],
                ),
            ]
        elif selected_model == Models.PMV_EN.name:
            results = [
                standard_checker,
                dmc.SimpleGrid(
                    cols=columns,
                    spacing="xs",
                    verticalSpacing="xs",
                    children=[
                        dmc.Center(dmc.Text(f"PMV: {r_pmv['pmv']:.2f}")),
                        dmc.Center(dmc.Text(f"PPD: {r_pmv['ppd']:.1f} %")),
                    ],
                ),
            ]

        if selected_model == Models.PMV_ashrae.name:
            comfort_category = mapping(
                r_pmv["pmv"],
                {
                    -2.5: "Cold",
                    -1.5: "Cool",
                    -0.5: "Slightly Cool",
                    0.5: "Neutral",
                    1.5: "Slightly Warm",
                    2.5: "Warm",
                    10: "Hot",
                },
            )
            results[1].children.append(
                dmc.Center(dmc.Text(f"Sensation: {comfort_category}"))
            )
        elif selected_model == Models.PMV_EN.name:
            comfort_category = mapping(
                abs(r_pmv["pmv"]), {0.2: "I", 0.5: "II", 0.7: "III", float("inf"): "IV"}
            )
            results[1].children.append(
                dmc.Center(dmc.Text(f"Category: {comfort_category}"))
            )
        # Modify the colour
        for i in range(1, len(results)):
            if i == 1 or i == 2:
                color = (
                    CompareInputColor.InputColor1.value
                    if i == 1
                    else CompareInputColor.InputColor2.value
                )
                for child in results[i].children:
                    if isinstance(child, dmc.Center) and isinstance(
                        child.children, dmc.Text
                    ):
                        child.children.style = {"color": color}

        if (
            inputs[ElementsIDs.functionality_selection.value]
            == Functionalities.Compare.value
            and selected_model == Models.PMV_ashrae.name
        ):
            if -0.5 <= r_pmv["pmv"] <= 0.5:
                compliance_text = "✔"
                compliance_color = "green"
            else:
                compliance_text = "✘"
                compliance_color = "red"
        else:  # en
            if -0.7 <= r_pmv["pmv"] <= 0.7:
                compliance_text = "✔"
                compliance_color = "green"
            else:
                compliance_text = "✘"
                compliance_color = "red"
        if (
            inputs[ElementsIDs.functionality_selection.value]
            == Functionalities.Compare.value
            and selected_model == Models.PMV_ashrae.name
        ):

            if units == UnitSystem.SI.value:
                results_title = [
                    dmc.Stack(
                        children=[
                            dmc.Center(dmc.Text("Compliance")),
                            dmc.Center(dmc.Text("PMV")),
                            dmc.Center(dmc.Text("PPD")),
                            dmc.Center(dmc.Text("Sensation")),
                            dmc.Center(dmc.Text("SET")),
                        ],
                        gap=5,
                        style={"textAlign": "left", "width": "100%"},
                    ),
                ]
            else:
                results_title = [
                    dmc.Stack(
                        children=[
                            dmc.Center(dmc.Text("Compliance")),
                            dmc.Center(dmc.Text("PMV with elevated air speed")),
                            dmc.Center(dmc.Text("PPD with elevated air speed")),
                            dmc.Center(dmc.Text("Sensation")),
                            dmc.Center(dmc.Text("SET")),
                            dmc.Center(dmc.Text("Dry-bulb temp at still air")),
                            dmc.Center(dmc.Text("Cooling effect")),
                        ],
                        gap=5,
                        style={"textAlign": "left", "width": "100%"},
                    ),
                ]

            results = [
                dmc.Stack(
                    children=[
                        dmc.Center(
                            dmc.Text(
                                f"{compliance_text}", style={"color": compliance_color}
                            )
                        ),
                        dmc.Center(dmc.Text(f"{r_pmv['pmv']:.2f}")),
                        dmc.Center(dmc.Text(f"{r_pmv['ppd']:.1f} %")),
                    ],
                    gap=5,
                    style={"textAlign": "center", "width": "100%"},
                ),
            ]

            results[0].children.append(dmc.Center(dmc.Text(f"{comfort_category}")))

            temp_unit = "°F" if units == UnitSystem.IP.value else "°C"
            if units == UnitSystem.SI.value:

                results[0].children.append(
                    dmc.Center(dmc.Text(f"{r_set_tmp:.1f} {temp_unit}"))
                )

            else:

                results[0].children.append(
                    dmc.Center(dmc.Text(f"{r_set_tmp:.1f} {temp_unit}"))
                )
                results[0].children.append(
                    dmc.Center(
                        dmc.Text(f"{inputs[ElementsIDs.t_db_input.value]} {temp_unit}")
                    )
                )
                results[0].children.append(
                    dmc.Center(dmc.Text(f"{r_cooling_effect:.1f} {temp_unit}"))
                )

            for i in range(0, len(results)):
                if i == 0:

                    color = CompareInputColor.InputColor1.value
                    for child in results[i].children[1:]:
                        if isinstance(child, dmc.Center) and isinstance(
                            child.children, dmc.Text
                        ):
                            child.children.style = {"color": color}

            r_pmv_input2 = pmv_ppd(
                tdb=inputs[ElementsIDs.t_db_input_input2.value],
                tr=inputs[ElementsIDs.t_r_input_input2.value],
                vr=v_relative(
                    v=inputs[ElementsIDs.v_input_input2.value],
                    met=inputs[ElementsIDs.met_input_input2.value],
                ),
                rh=inputs[ElementsIDs.rh_input_input2.value],
                met=inputs[ElementsIDs.met_input_input2.value],
                clo=clo_dynamic(
                    clo=inputs[ElementsIDs.clo_input_input2.value],
                    met=inputs[ElementsIDs.met_input_input2.value],
                ),
                wme=0,
                limit_inputs=True,
                units=units,
                standard=standard,
            )
            r_set_tmp_input2 = set_tmp(
                tdb=inputs[ElementsIDs.t_db_input_input2.value],
                tr=inputs[ElementsIDs.t_r_input_input2.value],
                v=v_relative(
                    v=inputs[ElementsIDs.v_input_input2.value],
                    met=inputs[ElementsIDs.met_input_input2.value],
                ),
                rh=inputs[ElementsIDs.rh_input_input2.value],
                met=inputs[ElementsIDs.met_input_input2.value],
                clo=clo_dynamic(
                    clo=inputs[ElementsIDs.clo_input_input2.value],
                    met=inputs[ElementsIDs.met_input_input2.value],
                ),
                wme=0,
                limit_inputs=True,
                units=units,
                standard=standard,
            )

            r_cooling_effect_input2 = cooling_effect(
                tdb=inputs[ElementsIDs.t_db_input_input2.value],
                tr=inputs[ElementsIDs.t_r_input_input2.value],
                vr=v_relative(
                    v=inputs[ElementsIDs.v_input_input2.value],
                    met=inputs[ElementsIDs.met_input_input2.value],
                ),
                rh=inputs[ElementsIDs.rh_input_input2.value],
                met=inputs[ElementsIDs.met_input_input2.value],
                clo=clo_dynamic(
                    clo=inputs[ElementsIDs.clo_input_input2.value],
                    met=inputs[ElementsIDs.met_input_input2.value],
                ),
                wme=0,
                units=units,
            )

            if (
                inputs[ElementsIDs.functionality_selection.value]
                == Functionalities.Compare.value
                and selected_model == Models.PMV_ashrae.name
            ):
                if -0.5 <= r_pmv_input2["pmv"] <= 0.5:
                    compliance_text2 = "✔"
                    compliance_color = "green"
                else:
                    compliance_text2 = "✘"
                    compliance_color = "red"
            else:  # EN
                if -0.7 <= r_pmv_input2["pmv"] <= 0.7:
                    compliance_text2 = "✔"
                    compliance_color = "green"
                else:
                    compliance_text2 = "✘"
                    compliance_color = "red"

            # arrange the relative display of column2
            results2 = [
                dmc.Stack(
                    children=[
                        dmc.Center(
                            dmc.Text(
                                f"{compliance_text2}", style={"color": compliance_color}
                            )
                        ),
                        dmc.Center(dmc.Text(f"{r_pmv_input2['pmv']:.2f}")),
                        dmc.Center(dmc.Text(f"{r_pmv_input2['ppd']:.1f} %")),
                    ],
                    gap=5,
                    style={"textAlign": "right", "width": "50%"},
                ),
            ]

            results2[0].children.append(dmc.Center(dmc.Text(f"{comfort_category}")))

            temp_unit = "°F" if units == UnitSystem.IP.value else "°C"
            if units == UnitSystem.SI.value:

                results2[0].children.append(
                    dmc.Center(dmc.Text(f"{r_set_tmp_input2:.1f} {temp_unit}"))
                )

            else:

                results2[0].children.append(
                    dmc.Center(dmc.Text(f"{r_set_tmp_input2:.1f} {temp_unit}"))
                )
                results2[0].children.append(
                    dmc.Center(
                        dmc.Text(
                            f"{inputs[ElementsIDs.t_db_input_input2.value]} {temp_unit}"
                        )
                    )
                )
                results2[0].children.append(
                    dmc.Center(dmc.Text(f"{r_cooling_effect_input2:.1f} {temp_unit}"))
                )

            for i in range(0, len(results2)):
                if i == 0:

                    color = CompareInputColor.InputColor2.value
                    for child in results2[i].children[1:]:
                        if isinstance(child, dmc.Center) and isinstance(
                            child.children, dmc.Text
                        ):
                            child.children.style = {"color": color}

            # arrange the title column1 and column2 onto the same level
            return dmc.Grid(
                children=[
                    dmc.Stack(
                        children=results_title,
                        style={"flex": "1", "display": "inline-block"},
                    ),
                    dmc.Stack(
                        children=results,
                        style={"flex": "1", "display": "inline-block"},
                    ),
                    dmc.Stack(
                        children=results2,
                        style={"flex": "1", "display": "inline-block"},
                    ),
                ],
                style={"display": "flex"},
            )

    elif selected_model == Models.Adaptive_EN.name:
        results = gain_adaptive_hover_text(
            tdb=inputs[ElementsIDs.t_db_input.value],
            tr=inputs[ElementsIDs.t_r_input.value],
            trm=inputs[ElementsIDs.t_rm_input.value],
            v=inputs[ElementsIDs.v_input.value],
            units=units,
        )

    elif selected_model == Models.Adaptive_ASHRAE.name:
        results = gain_adaptive_hover_text(
            tdb=inputs[ElementsIDs.t_db_input.value],
            tr=inputs[ElementsIDs.t_r_input.value],
            trm=inputs[ElementsIDs.t_rm_input.value],
            v=inputs[ElementsIDs.v_input.value],
            units=units,
        )

    if selected_model == Models.PMV_ashrae.name:
        if (
            inputs[ElementsIDs.chart_selected.value] == Charts.set_outputs.value.name
            or inputs[ElementsIDs.chart_selected.value]
            == Charts.thl_psychrometric.value.name
        ):
            return None

    return dmc.Stack(
        children=results,
        gap=0,
        align="stretch",
    )


@dataclass
class ComfortRange:
    low: float
    up: float
    label: str


def gain_adaptive_hover_text(
    tdb: float, tr: float, trm: float, v: float, units: str, model: Models
) -> List:
    y = t_o(tdb=tdb, tr=tr, v=v)
    temp_unit = "°F" if units == UnitSystem.IP.value else "°C"

    if model == Models.Adaptive_EN:
        result = adaptive_en(tdb=tdb, tr=tr, t_running_mean=trm, v=v, units=units)
        ranges = [
            ComfortRange(
                result["tmp_cmf_cat_iii_low"], result["tmp_cmf_cat_iii_up"], "Class III"
            ),
            ComfortRange(
                result["tmp_cmf_cat_ii_low"], result["tmp_cmf_cat_ii_up"], "Class II"
            ),
            ComfortRange(
                result["tmp_cmf_cat_i_low"], result["tmp_cmf_cat_i_up"], "Class I"
            ),
        ]
        standard_text = "EN 16798"
    elif model == Models.Adaptive_ASHRAE:
        result = adaptive_ashrae(tdb=tdb, tr=tr, t_running_mean=trm, v=v, units=units)
        ranges = [
            ComfortRange(result["tmp_cmf_80_low"], result["tmp_cmf_80_up"], "80%"),
            ComfortRange(result["tmp_cmf_90_low"], result["tmp_cmf_90_up"], "90%"),
        ]
        standard_text = "ASHRAE 55"
    else:
        raise ValueError(f"Unsupported model: {model}")

    main_range = ranges[0]
    compliant = main_range.low <= y <= main_range.up

    results = [
        dmc.Text(
            f"{'✔' if compliant else '✘'} {'Complies with' if compliant else 'Does not comply with'} {standard_text}",
            c="green" if compliant else "red",
            ta="center",
            size="md",
            style={"width": "100%"},
        )
    ]

    for range_info in ranges:
        if range_info.low <= y <= range_info.up:
            comfort_level = ComfortLevel.COMFORTABLE
        elif y > range_info.up:
            comfort_level = ComfortLevel.TOO_WARM
        else:
            comfort_level = ComfortLevel.TOO_COOL

        results.extend(
            [
                dmc.Center(
                    dmc.Text(
                        f"{range_info.label} acceptability limits = Operative temperature: "
                        f"{range_info.low:.1f} to {range_info.up:.1f} {temp_unit}"
                    )
                ),
                dmc.Center(
                    dmc.Text(comfort_level.description, fz="xs", c=comfort_level.color)
                ),
            ]
        )

    return results
